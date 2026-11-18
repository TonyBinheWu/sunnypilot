import json
from types import SimpleNamespace
from openpilot.common.auto_hotspot import AutoHotspotPolicy
from openpilot.system.ui.lib import wifi_manager as wifi


def manager():
  wm=wifi.WifiManager.__new__(wifi.WifiManager)
  wm._exit=False;wm._auto_share=False;wm._ipv4_forward=False;wm._hotspot_policy=AutoHotspotPolicy()
  wm._tethering_ssid='existing-hotspot';wm._wifi_state=wifi.WifiState(status=wifi.ConnectStatus.DISCONNECTED)
  return wm


def test_sim_late_arrival_shares_after_activation_and_disabled_stops_owned_ap(mocker,tmp_path):
  wm=manager();flag={'value':1};actions=[];ticks={'n':0}
  mocker.patch.object(wifi,'Params',return_value=SimpleNamespace(get_int=lambda key:flag['value']))
  mocker.patch.object(wifi,'cellular_ready',side_effect=[False,True,True,True])
  mocker.patch.object(wifi,'direct_ap_active',return_value=False)
  mocker.patch.object(wifi,'HOTSPOT_STATUS_PATH',tmp_path/'status.json')
  forwarding=tmp_path/'forward';forwarding.write_text('0')
  mocker.patch.object(wifi,'IP_FORWARD_PATH',forwarding)
  def activate(active,**kw):
    actions.append(active)
    wm._wifi_state=wifi.WifiState(ssid=wm._tethering_ssid if active else None,status=wifi.ConnectStatus.CONNECTED if active else wifi.ConnectStatus.DISCONNECTED)
  wm.set_tethering_active=activate
  def wait(_seconds):
    ticks['n']+=1
    if ticks['n']==3:flag['value']=0
    if ticks['n']==4:wm._exit=True
    return wm._exit
  wm._auto_stop=SimpleNamespace(wait=wait)
  run=mocker.patch.object(wifi.subprocess,'run')
  try:wm._auto_hotspot_loop()
  finally:wm._exit=True
  assert actions==[True,False]
  assert run.call_args.args[0]==['sudo','sysctl','net.ipv4.ip_forward=1']
  report=json.loads((tmp_path/'status.json').read_text())
  assert report['state']=='stop' and report['enabled'] is False
  assert set(report)=={'enabled','cellular_ready','active','state','updated'}


def test_disabling_during_activation_cannot_leave_a_late_auto_hotspot(mocker):
  wm=manager();flag={'value':1}
  mocker.patch.object(wifi,'Params',return_value=SimpleNamespace(get_int=lambda key:flag['value']))
  class Immediate:
    def __init__(self,target,**kwargs):self.target=target
    def start(self):self.target()
  mocker.patch.object(wifi.threading,'Thread',Immediate)
  def activate(*args,**kwargs):flag['value']=0
  wm.activate_connection=activate
  wm._deactivate_connection=mocker.Mock()
  run=mocker.patch.object(wifi.subprocess,'run')
  try:wm.set_tethering_active(True,automatic=True)
  finally:wm._exit=True
  wm._deactivate_connection.assert_called_once_with(wm._tethering_ssid)
  run.assert_not_called()


def test_shared_profile_has_dhcp_nat_and_keeps_the_existing_security_contract(mocker):
  wm=manager();wm._router_main=mocker.Mock()
  call=mocker.patch.object(wifi,'new_method_call')
  try:wm._add_tethering_connection()
  finally:wm._exit=True
  profile=call.call_args.args[-1][0]
  assert profile['ipv4']['method']==('s','shared') and profile['ipv4']['never-default']==('b',True)
  assert 'gateway' not in profile['ipv4']
  assert profile['802-11-wireless']['ssid'][1]==b'existing-hotspot'
  assert profile['802-11-wireless-security']['psk'][1]==wifi.DEFAULT_TETHERING_PASSWORD
  assert profile['802-11-wireless-security']['proto']==('as',['rsn'])
