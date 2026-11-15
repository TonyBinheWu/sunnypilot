import asyncio
import importlib
from pathlib import Path
import sys
import threading
import time
import types

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = '_carrot_self_diagnostics_tests'
for suffix, directory in [('', ROOT), ('.services', ROOT/'services'), ('.features', ROOT/'features')]:
  module = types.ModuleType(PACKAGE+suffix)
  module.__path__ = [str(directory)]
  sys.modules[module.__name__] = module
rules = importlib.import_module(PACKAGE+'.services.self_diagnostics')
feature = importlib.import_module(PACKAGE+'.features.self_diagnostics')
params_module = importlib.import_module(PACKAGE+'.services.params')
history = importlib.import_module(PACKAGE+'.services.param_changes')


def codes(facts): return {row['code'] for row in rules.diagnose(facts)['checks']}


def test_offroad_absence_is_not_a_can_or_model_failure_and_missing_data_is_not_healthy():
  assert 'can_invalid' not in codes({'device': {'fresh':True,'started':False},'car':{'fresh':False}})
  assert 'vehicle_unknown' in codes({'device': {'fresh':True,'started':True},'car':{'fresh':False}})
  assert 'device_unknown' in codes({})
  assert not rules.diagnose({})['actions']
  assert 'offroad' not in codes({'device': {'fresh':True}})
  assert 'device_unknown' in codes({'device': {'fresh':True}})


@pytest.mark.parametrize('facts,expected', [
  ({'device':{'fresh':True,'started':True},'car':{'fresh':True,'canValid':False,'canTimeout':True}},'can_timeout'),
  ({'device':{'fresh':True,'started':True},'car':{'fresh':True,'canValid':False}},'can_invalid'),
  ({'device':{'fresh':True,'started':True},'car':{'fresh':True,'canValid':True,'canTimeout':True}},'can_timeout'),
  ({'device':{'fresh':True,'started':True},'car':{'fresh':True}},'vehicle_unknown'),
  ({'alert':{'fresh':True,'type':'commIssue/noEntry'}},'processing_delay'),
  ({'alert':{'fresh':False,'type':'commIssue/noEntry'}},None),
  ({'manager':{'fresh':True,'failed':['camerad']}},'process_stopped'),
  ({'manager':{'fresh':False,'failed':['camerad']}},None),
  ({'device':{'fresh':True,'thermal':'danger','freeSpace':2,'memory':97}},'thermal_high'),
  ({'formosa':{'enabled':True,'paired':True,'online':False}},'formosa_offline'),
  ({'formosa':{'enabled':False,'paired':False}},None),
  ({'model':{'available':True,'state':'compiling'}},'model_busy'),
  ({'model':{'available':False,'state':'error'}},None),
])
def test_observations_respect_freshness_enablement_and_expected_runtime(facts, expected):
  found = codes(facts)
  if expected: assert expected in found
  else: assert not found.intersection({'processing_delay','process_stopped','formosa_unpaired','model_error'})


def test_tickets_expire_are_single_use_bounded_and_do_not_admit_other_actions():
  now = [0]
  bank = rules.RepairTickets(clock=lambda:now[0])
  token = bank.issue(['enable_vision'])
  with pytest.raises(ValueError): bank.consume(token, 'reboot')
  with pytest.raises(ValueError): bank.consume(token, 'enable_vision')
  token = bank.issue(['reboot']); now[0] = 61
  with pytest.raises(ValueError): bank.consume(token, 'reboot')
  for _ in range(40): bank.issue(['reboot'])
  assert len(bank.pending) == 32


class FakeParams:
  def __init__(self): self.values={'IsOffroad':True,'IsOnroad':False,'CarrotVisionEnabled':False};self.writes=[]
  def get_bool(self,key): return self.values.get(key,False)
  def put_bool(self,key,value): self.writes.append((key,value));self.values[key]=value


def test_actual_http_report_and_repairs_are_guarded_readback_verified_and_never_replayed(monkeypatch):
  p = FakeParams()
  values={'deviceState':types.SimpleNamespace(started=False),
    'carState':types.SimpleNamespace(canValid=True,gearShifter='park',standstill=True,vEgo=0.,vEgoRaw=0.),
    'carControl':types.SimpleNamespace(enabled=False,latActive=False,longActive=False),
    'selfdriveState':types.SimpleNamespace(enabled=False)}
  sm=type('SM',(dict,),{})(values)
  sm.seen=dict.fromkeys(values,True);sm.valid=dict.fromkeys(values,True);sm.logMonoTime={}
  def update(_): sm.logMonoTime.update(dict.fromkeys(values,int(time.monotonic()*1e9)))
  sm.update=update
  native=types.SimpleNamespace(lock=threading.RLock(),tickets=rules.RepairTickets(),sm=sm,cached=None)
  def snapshot():
    report={'ok':True,'version':1,**rules.diagnose({'visionEnabled':p.get_bool('CarrotVisionEnabled'),'manager':{'fresh':True,'failed':['camerad']}})}
    report['ticket']=native.tickets.issue(report['actions']);return report
  native.snapshot=snapshot
  monkeypatch.setattr(feature,'service',native)
  monkeypatch.setattr(params_module,'Params',lambda:p)
  events=[];monkeypatch.setattr(history,'append_param_change',lambda *args,**kwargs:events.append((args,kwargs)))
  async def run():
    app=web.Application();feature.register(app)
    async with TestClient(TestServer(app)) as client:
      report=await(await client.get('/api/device/diagnostics')).json()
      assert not p.writes
      body={'ticket':report['ticket'],'action':'enable_vision'}
      assert (await client.post('/api/device/diagnostics/repair',json=body,headers={'Origin':'https://other.invalid'})).status==403
      assert (await client.post('/api/device/diagnostics/repair',json={**body,'action':'disable_can_checks'})).status==409
      sm['carState'].gearShifter='drive'
      assert (await client.post('/api/device/diagnostics/repair',json=body)).status==409
      assert not p.writes
      sm['carState'].gearShifter='park'
      report=await(await client.get('/api/device/diagnostics')).json();body['ticket']=report['ticket']
      result=await(await client.post('/api/device/diagnostics/repair',json=body)).json()
      assert result=={'ok':True,'result':'vision_enabled'}
      assert p.writes==[('CarrotVisionEnabled',True)] and events[0][1]['source']=='web_ui'
      assert (await client.post('/api/device/diagnostics/repair',json=body)).status==409
      assert len(p.writes)==1
      report=await(await client.get('/api/device/diagnostics')).json()
      body={'ticket':report['ticket'],'action':'reboot'}
      sm['carControl'].latActive=True
      assert (await client.post('/api/device/diagnostics/repair',json=body)).status==409
      assert len(p.writes)==1
      sm['carControl'].latActive=False
      report=await(await client.get('/api/device/diagnostics')).json();body['ticket']=report['ticket']
      result=await(await client.post('/api/device/diagnostics/repair',json=body)).json()
      assert result=={'ok':True,'result':'reboot_requested'} and p.writes[-1]==('DoReboot',True)
      assert (await client.post('/api/device/diagnostics/repair',data='x'*2049,headers={'Content-Type':'application/json'})).status==413
  asyncio.run(run())


def test_fresh_invalid_can_event_still_reports_can_failure_instead_of_silent_success(monkeypatch):
  native_module=importlib.import_module(PACKAGE+'.services.native_diagnostics')
  service=native_module.NativeDiagnostics()
  values={'deviceState':types.SimpleNamespace(started=True,thermalStatus='green',freeSpacePercent=30,memoryUsagePercent=40),
    'carState':types.SimpleNamespace(canValid=False,canTimeout=True),
    'selfdriveState':types.SimpleNamespace(alertType='canError/noEntry',alertStatus='normal'),
    'managerState':types.SimpleNamespace(rebootRequired=False,processes=[]),
    'liveCalibration':types.SimpleNamespace(calStatus='calibrated')}
  sm=type('SM',(dict,),{})(values);sm.seen=dict.fromkeys(values,True);sm.valid=dict.fromkeys(values,True)
  sm.valid['carState']=False;sm.logMonoTime=dict.fromkeys(values,int(time.monotonic()*1e9));sm.update=lambda _:None
  service.sm=sm
  monkeypatch.setattr(params_module,'HAS_PARAMS',True);monkeypatch.setattr(params_module,'Params',FakeParams)
  monkeypatch.setitem(sys.modules,PACKAGE+'.features.egpu_model',types.SimpleNamespace(build_status_payload=lambda:{'available':False}))
  report=service.snapshot()
  assert report['facts']['car']['fresh'] and not report['facts']['car']['messageValid']
  assert 'can_timeout' in {row['code'] for row in report['checks']}
