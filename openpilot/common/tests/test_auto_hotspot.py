import json
from openpilot.common.auto_hotspot import AutoHotspotPolicy, cellular_ready


def test_sim_presence_alone_never_starts_sharing(tmp_path):
  p=tmp_path/'modem'
  state={'sim_state':'READY','connected':True,'seconds_since_boot':100,'ip_address':'10.2.3.4'}
  p.write_text(json.dumps(state));assert cellular_ready(105,p)
  for change in [{'sim_state':'ABSENT'},{'connected':False},{'seconds_since_boot':80},{'seconds_since_boot':110},{'ip_address':'127.0.0.1'},{'ip_address':'0.0.0.0'}]:
    p.write_text(json.dumps(state|change));assert not cellular_ready(105,p)
  p.write_text('broken');assert not cellular_ready(105,p)


def test_off_boot_late_sim_backoff_reconnect_and_manual_override():
  p=AutoHotspotPolicy()
  def step(t=0,**kw):return p.step(enabled=True,cellular=True,active=False,now=t,**kw)
  assert p.step(enabled=False,cellular=True,active=True,now=0)=='disabled'
  assert p.step(enabled=True,cellular=False,active=False,now=1)=='waiting_cellular'
  assert step(2)=='activate';assert step(3)=='connecting';assert step(12)=='activate'
  assert p.step(enabled=True,cellular=True,active=True,now=13)=='share'
  assert p.step(enabled=True,cellular=False,active=True,now=14)=='share'  # keep LAN through brief cellular loss
  p.manual(False);assert step(100)=='manual_pause'
  assert p.step(enabled=False,cellular=True,active=False,now=101)=='disabled'
  assert step(102)=='activate'
  assert p.step(enabled=False,cellular=True,active=True,now=103)=='stop'


def test_radio_coexistence_and_failure_budget():
  p=AutoHotspotPolicy()
  assert p.step(enabled=True,cellular=True,active=False,now=0,radio_busy=True)=='radio_busy'
  attempts=[]
  for t in range(300):
    if p.step(enabled=True,cellular=True,active=False,now=t)=='activate':attempts.append(t)
  assert attempts==[0,10,30,70,130,190,250]
