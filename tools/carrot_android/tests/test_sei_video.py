"""Real codec round trips, including the normally-built local playback helper."""
import os
from pathlib import Path
import shutil
import subprocess
import json

import pytest
from openpilot.selfdrive.carrot.server.services.driving_sei import timeline_from_native

ROOT=Path(__file__).resolve().parents[3]
READER=Path(os.environ.get('SEI_READER_TEST_BINARY',ROOT/'openpilot/system/loggerd/sei_reader'))
FFMPEG=os.environ.get('SEI_FFMPEG_TEST_BINARY') or shutil.which('ffmpeg')
FFPROBE=os.environ.get('SEI_FFPROBE_TEST_BINARY') or shutil.which('ffprobe')


@pytest.fixture(scope='module')
def codec_tools(tmp_path_factory):
  ready=READER.is_file() and FFMPEG and FFPROBE and shutil.which('g++')
  if not ready:
    if os.environ.get('CARROT_REQUIRE_SEI_CODECS')=='1':pytest.fail('Native SEI reader, ffmpeg and g++ are required')
    pytest.skip('Run after building the native reader with FFmpeg test tools')
  work=tmp_path_factory.mktemp('sei-codec')
  injector=work/'injector'
  subprocess.run(['g++','-std=c++17','-I'+str(ROOT/'openpilot'),str(ROOT/'openpilot/system/loggerd/tests/test_driving_sei.cc'),'-o',str(injector)],check=True)
  return work,injector


def run(*args):
  command=[str(a) for a in args]
  if command[0] in ('ffmpeg','ffprobe'):
    command[0]=FFMPEG if command[0]=='ffmpeg' else FFPROBE
  return subprocess.check_output(command,stderr=subprocess.PIPE,timeout=30)


@pytest.mark.parametrize('codec,encoder,setting',[('h264','libx264','x264-params'),('hevc','libx265','x265-params')])
def test_native_reader_remux_keeps_pixels_and_pts_with_dynamic_pedals(codec_tools,codec,encoder,setting):
  work,injector=codec_tools
  original=work/('plain.'+codec);annotated=work/('annotated.'+codec)
  run('ffmpeg','-y','-v','error','-f','lavfi','-i','testsrc2=size=160x96:rate=20','-frames:v','12','-c:v',encoder,'-preset','ultrafast',
      '-'+setting,'aud=1:bframes=0:repeat-headers=1:log-level=error','-f',codec,original)
  run(injector,original,annotated,codec)
  ts=work/(codec+'.ts');mp4=work/(codec+'.mp4')
  run('ffmpeg','-y','-v','error','-i',annotated,'-c','copy',ts)
  run(READER,'--remux',ts,mp4)
  before=run('ffmpeg','-v','error','-i',annotated,'-f','framemd5','-')
  after=run('ffmpeg','-v','error','-i',mp4,'-f','framemd5','-')
  assert before==after
  rows=timeline_from_native(run(READER,mp4))['samples']
  assert len(rows)==12 and rows==timeline_from_native(run(READER,ts))['samples']
  # Raw elementary fixtures have no PTS. Compare with the actual muxed packet
  # timestamps, rather than assuming FFmpeg synthesizes a uniform first step.
  reference=json.loads(run('ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time','-of','json',mp4))
  assert [r['time_s'] for r in rows]==pytest.approx([float(p['pts_time']) for p in reference['packets']])
  assert [r['speed_mps'] for r in rows]==pytest.approx([20+i*.1 for i in range(12)])
  assert [r['gas_pressed'] for r in rows]==[i%3==0 for i in range(12)]
  assert [r['brake_pressed'] for r in rows]==[i%3==1 for i in range(12)]
  assert [r['cruise_enabled'] for r in rows]==[i%4<2 for i in range(12)]
  assert [r['longitudinal_active'] for r in rows]==[i%2==0 for i in range(12)]
  shifted=work/(codec+'-shifted.mp4')
  run('ffmpeg','-y','-v','error','-i',mp4,'-c','copy','-output_ts_offset','0.35',shifted)
  delayed=timeline_from_native(run(READER,shifted))['samples']
  assert delayed[0]['time_s']==pytest.approx(.35)  # missing initial time is never rebased to zero
  plain_mp4=work/(codec+'-plain.mp4')
  run('ffmpeg','-y','-v','error','-i',original,'-c','copy',plain_mp4)
  assert timeline_from_native(run(READER,plain_mp4))['status']=='no_sei'
