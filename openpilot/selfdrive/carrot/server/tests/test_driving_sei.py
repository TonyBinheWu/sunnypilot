import json
import asyncio
import threading
from types import SimpleNamespace
from aiohttp import web
import pytest
from openpilot.system.loggerd.driving_metadata import UUID, packet_metadata
from openpilot.selfdrive.carrot.server.services.driving_sei import timeline_from_native


def packet(hevc=False,length_size=4,**changes):
  row={'schema':'formosa.drive.v1','frame_id':4,'frame_mono_ns':1000000000,'car_mono_ns':1000000000,'control_mono_ns':1000000000,
       'speed_mps':20,'steering_angle_deg':-31.5,'gas':.3,'brake':0,'gas_pressed':True,'brake_pressed':False,
       'control_enabled':True,'lateral_active':True,'longitudinal_active':False,'cruise_enabled':False}|changes
  payload=UUID+json.dumps(row).encode()
  unit=(b'\x4e\x01' if hevc else b'\x06')+b'\x05'+b'\xff'*(len(payload)//255)+bytes([len(payload)%255])+payload+b'\x80'
  return len(unit).to_bytes(length_size,'big')+unit


def hexdump(data):
  return '\n'+ '\n'.join(f'{i:08x}: '+data[i:i+16].hex(' ')+'  ASCII' for i in range(0,len(data),16))


def probe(data,hevc=False,time='0.350000'):
  return f"{time}\t{'hevc' if hevc else 'h264'}\t{data[4:].hex()}\n".encode()


def test_actual_pts_missing_prefix_false_flags_and_no_location_leak():
  for hevc in (False,True):
    result=timeline_from_native(probe(packet(hevc=hevc,gps='private'),hevc))
    assert result['status']=='ready';row=result['samples'][0]
    assert row['time_s']==.35 and row['speed_mps']==20 and row['steering_angle_deg']==-31.5
    assert row['brake_pressed'] is False and row['cruise_enabled'] is False and row['longitudinal_active'] is False
    assert 'gps' not in row
  assert timeline_from_native(probe(b''))['status']=='no_sei'


def test_stale_future_and_invalid_values_are_unknown_without_dropping_frame_time():
  for changes in ({'car_mono_ns':700000000},{'car_mono_ns':1000000001},{'car_mono_ns':None}):
    row=timeline_from_native(probe(packet(**changes)))['samples'][0]
    assert row['time_s']==.35 and row['gas_pressed'] is None and row['speed_mps'] is None
    assert row['control_enabled'] is True
  row=timeline_from_native(probe(packet(speed_mps=float('nan'),steering_angle_deg=9000,gas=2)))['samples'][0]
  assert row['speed_mps'] is None and row['steering_angle_deg'] is None and row['gas'] is None


def test_mp4_nal_length_sizes_and_truncation():
  for size in (1,2,3,4):
    if size==1:continue  # real v1 JSON is larger than a one-byte NAL
    assert len(list(packet_metadata(packet(length_size=size),'h264',size)))==1
  assert list(packet_metadata(packet()[:-4],'h264',4))==[]
  assert list(packet_metadata(b'\0\0\0\0','h264',4))==[]


def test_http_admission_shares_inflight_and_survives_viewer_cancel(monkeypatch):
  from openpilot.selfdrive.carrot.server.services import driving_sei as service
  entered=threading.Event();release=threading.Event();calls=[]
  def load(segment):
    calls.append(segment);entered.set();assert release.wait(3)
    return {'status':'no_sei','samples':[]}
  monkeypatch.setattr(service,'load_sei',load)
  async def scenario():
    app={}
    def request(segment):return SimpleNamespace(app=app,match_info={'segment':segment})
    first=asyncio.create_task(service.api_dashcam_sei(request('one')))
    assert await asyncio.to_thread(entered.wait,2)
    busy=await service.api_dashcam_sei(request('two'))
    assert json.loads(busy.body)['status']=='busy'
    second=asyncio.create_task(service.api_dashcam_sei(request('one')))
    await asyncio.sleep(0);first.cancel()
    with pytest.raises(asyncio.CancelledError):await first
    assert not app['dashcam_sei_task'].cancelled()
    release.set();result=await second
    assert json.loads(result.body)['status']=='no_sei'
    assert result.headers['Cache-Control']=='no-store' and calls==['one']
  try:asyncio.run(scenario())
  finally:release.set()


def test_http_keeps_not_found_and_reports_native_failure(monkeypatch):
  from openpilot.selfdrive.carrot.server.services import driving_sei as service
  async def scenario():
    def missing(_):raise web.HTTPNotFound()
    monkeypatch.setattr(service,'load_sei',missing)
    with pytest.raises(web.HTTPNotFound):
      await service.api_dashcam_sei(SimpleNamespace(app={},match_info={'segment':'missing'}))
    def failed(_):raise OSError('native unavailable')
    monkeypatch.setattr(service,'load_sei',failed)
    result=await service.api_dashcam_sei(SimpleNamespace(app={},match_info={'segment':'one'}))
    assert json.loads(result.body)=={'ok':True,'status':'unavailable','samples':[]}
  asyncio.run(scenario())
