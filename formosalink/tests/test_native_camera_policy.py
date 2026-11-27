import json
from types import SimpleNamespace
from unittest.mock import patch

from openpilot.sunnypilot.formosalink.cameras import save_lease, camera_requested
from openpilot.system.ui.lib.cellular_data import connection_status


def test_camera_power_lease_expires_and_clears(tmp_path,monkeypatch):
  path=tmp_path/'lease.json';monkeypatch.setenv('FORMOSALINK_CAMERA_LEASE',str(path))
  with patch('time.monotonic',return_value=100):
    save_lease(['driver','wide-road'])
    assert camera_requested()
  with patch('time.monotonic',return_value=116):assert not camera_requested()
  save_lease([]);assert not path.exists()


def test_slow_modem_serial_queries_do_not_falsify_fresh_kernel_link():
  state={'seconds_since_boot':1,'data_checked_at':100,'state':'CONNECTED','connected':True,'ip_address':'10.1.2.3'}
  assert connection_status(True,state,101) == 'connected'
  state.update(connected=False,ip_address='')
  assert connection_status(True,state,101) == 'starting'
  assert connection_status(True,state,111) == 'unknown'
  assert connection_status(False,state,101) == 'stopping'


def test_upgrade_enables_background_but_preserves_remote_setting_consent():
  from openpilot.sunnypilot.formosalink.service_policy import disable_legacy
  state={'FormosaLinkEnabled':False, 'FormosaLinkRemoteSettings':False}
  params=SimpleNamespace(get_bool=lambda key:state.get(key,False),put_bool=lambda key,value,block:state.update({key:value}))
  disable_legacy(params)
  assert state['FormosaLinkEnabled'] is True
  assert state['FormosaLinkRemoteSettings'] is False
