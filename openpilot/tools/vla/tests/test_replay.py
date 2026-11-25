import math
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.tools.vla.model import prompts
from openpilot.tools.vla.replay import decode, verify, ARTIFACTS, resize_road
from openpilot.tools.vla.segment import history_at, recorded_pairs


def test_model_input_contains_only_observed_pose_and_image_context():
  before, questions = prompts([[-i, 0, 0] for i in range(8,-1,-1)])
  assert len(questions) == 3 and all(t.count('<wp>') == 9 for t in questions)
  assert 'camera' in before and all('[-8.00,0.00,0.0000]' in t for t in questions)


@pytest.mark.parametrize('history', [[], [[0,0,0]]*8, [[0,0,0]]*8 + [[0,0,1]], [[float('nan'),0,0]]*9, [[True,0,0]]*9])
def test_rejects_missing_or_ambiguous_motion(history):
  with pytest.raises(ValueError):
    prompts(history)


@pytest.mark.parametrize(('words','long','lat'), [
  (['track','keep','straight'], 'cruise','keep lane'), (['stop','turn','left'], 'stop','turn left'),
  (['follow','change','straight'], 'follow', None), (['c','merge','right'], None, 'merge'),
  (['adapt','out','right'], 'adapt speed','nudge out right'), (['','?','left'], None,None)])
def test_unknown_axis_abstains_independently(words, long, lat):
  assert decode(words) == {'longitudinal': long, 'lateral': lat}


@pytest.mark.parametrize(('width', 'height'), [(1344,760), (1928,1208)])
def test_device_road_aspects(width, height):
  result = resize_road(np.zeros((height, width, 3), dtype=np.uint8))
  assert result.shape == (192,320,3)


def test_checksum_failure(tmp_path, monkeypatch):
  monkeypatch.setitem(ARTIFACTS, next(iter(ARTIFACTS)), (3, '0'*64))
  (tmp_path/next(iter(ARTIFACTS))).write_bytes(b'bad')
  with pytest.raises(ValueError, match='checksum'):
    verify(tmp_path)


def test_history_uses_current_vehicle_frame_and_only_causal_samples():
  ts = [1_000_000_000 + i*50_000_000 for i in range(43)]
  poses = history_at(ts[40], ts, [(10., 0.)]*41 + [None,None])
  assert poses[0] == pytest.approx([-20.,0.,0.])
  assert poses[-1] == [0.,0.,0.]
  turning = history_at(ts[40], ts, [(10., .4)]*len(ts))
  assert turning[0][2] == pytest.approx(.8)
  assert turning[0][0] == pytest.approx(-10/.4*math.sin(.8), abs=.01)
  assert turning[0][1] < 0
  assert history_at(ts[40], ts, [(10.,0.)]*21 + [None] + [(10.,0.)]*21) is None
  assert history_at(ts[40], ts[:20], [(10.,0.)]*20) is None


def event(kind, t, value):
  return NS(which=lambda:kind, logMonoTime=t, valid=True, **{kind:value})


def replay_events(compute):
  times = [1_000_000_000+i*50_000_000 for i in range(41)]
  events = [event('liveCalibration', times[0], NS(calStatus='calibrated', rpyCalib=[0.,0.,0.]))]
  for t in times:
    events += [event('carState',t,NS(vEgo=4., canValid=True, gearShifter='drive')),
               event('livePose',t,NS(timestamp=t, posenetOK=True, sensorsOK=True, inputsOK=True,
                                     angularVelocityDevice=NS(valid=True,x=0.,y=0.,z=0.)))]
  eof = times[-1]
  events += [event('roadEncodeIdx', eof+1, NS(type='fullHEVC', frameId=48, timestampEof=eof, segmentNum=7, segmentId=3)),
             event('modelV2', eof+2, NS(visionCameraInputs='roadWide', visionCompute=compute, timestampEof=eof, frameId=48, leadsV3=[],
                                        action=NS(desiredAcceleration=-.5,desiredCurvature=0.,shouldStop=False)))]
  return events


@pytest.mark.parametrize('compute', ['nonUsb','usbGpu'])
def test_matches_small_and_large_primary_to_recorded_camera(compute):
  (frame,row), = recorded_pairs(replay_events(compute))
  assert frame == 3 and row['frame_id'] == 48 and row['timestamp_eof_ns'] == 3_000_000_000
  assert row['primary']['compute'] == compute and row['egomotion'][0] == pytest.approx([-8.,0.,0.])


def test_recorded_scene_uses_only_the_route_available_at_camera_exposure():
  events = replay_events('usbGpu')
  eof = events[-1].modelV2.timestampEof
  events[-1].modelV2.leadsV3 = [NS(prob=.8, x=[22.])]
  report = NS(carrotRouteId=100, routeMatch='matched', locationMonoTime=eof-30_000_000, approachManeuver='turn right')
  def instruction(side):
    return NS(allManeuvers=[NS(distance=10., type='turn', modifier=side)])
  events.extend([event('navRoute', eof-50_000_000, NS(carrotRouteId=100, coordinates=[0,1])),
                 event('navInstructionCarrot', eof-40_000_000, instruction('right')), event('mapRenderState', eof-20_000_000, report),
                 event('navInstructionCarrot', eof+1, instruction('left'))])
  _, row = next(recorded_pairs(sorted(events, key=lambda e:e.logMonoTime)))
  assert row['primary']['visual_lead'] and row['primary']['route_maneuver'] == 'turn right'
  report.routeMatch = 'offRoute'
  _, row = next(recorded_pairs(sorted(events, key=lambda e:e.logMonoTime)))
  assert row['primary']['route_maneuver'] is None


@pytest.mark.parametrize('problem', ['wrong_eof','wrong_frame','duplicate','wide','bad_pose','old_pose'])
def test_refuses_invalid_frame_pair(problem):
  events = replay_events('usbGpu')
  if problem == 'wrong_eof':
    events[-1].modelV2.timestampEof += 1
  elif problem == 'wrong_frame':
    events[-1].modelV2.frameId += 1
  elif problem == 'duplicate':
    events.append(events[-2])
  elif problem == 'wide':
    events[-1].modelV2.visionCameraInputs = 'wide'
  elif problem == 'bad_pose':
    events[20].livePose.sensorsOK = False
  else:
    events[20].livePose.timestamp -= 120_000_000
  assert list(recorded_pairs(events)) == []
