import ast
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from openpilot.system.ui.lib.cellular_data import CellularDataPreference, TEXT, label


def modem_module():
  spec=importlib.util.spec_from_file_location('formosa_test_modem',Path('openpilot/common/hardware/comma/modem.py'))
  module=importlib.util.module_from_spec(spec)
  with patch.dict(sys.modules,{'fcntl':Mock(),'termios':Mock()}):
    spec.loader.exec_module(module)
  return module


def fake(modem, flag):
  value=modem.Modem()
  value._ppp=Mock()
  value._ppp.data_session_active.return_value=False
  value._read_param=Mock(return_value=flag)
  value._publish_state=Mock()
  value._check_iccid=Mock()
  return value


@pytest.mark.parametrize('flag',['','1'])
def test_upgrade_and_enabled_flag_preserve_native_handler(flag):
  m=modem_module();obj=fake(m,flag);handler=Mock(return_value=m.State.CONNECTED)
  assert obj._step(m.State.SEARCHING,{m.State.SEARCHING:handler})==m.State.CONNECTED
  handler.assert_called_once();obj._check_iccid.assert_called_once_with(m.State.SEARCHING);obj._ppp.kill.assert_not_called()


@pytest.mark.parametrize('state',['INITIALIZING','SEARCHING','CONNECTING','CONNECTED','DISCONNECTING'])
def test_disable_from_every_state_stops_only_ppp_once(state):
  m=modem_module();obj=fake(m,'0');handler=Mock()
  assert obj._step(m.State[state],{m.State[state]:handler})==m.State.DATA_DISABLED
  assert obj._step(m.State.DATA_DISABLED,{})==m.State.DATA_DISABLED
  obj._ppp.kill.assert_called_once();obj._ppp.cleanup_routes.assert_called_once();obj._ppp.reset_data_port.assert_called_once()
  handler.assert_not_called();obj._check_iccid.assert_not_called()
  assert obj._publish_state.call_args.kwargs=={'data_enabled':False,'connected':False,'ip_address':''}
  obj._ppp.start.assert_not_called()


def test_reenable_returns_to_original_initialization_path():
  m=modem_module();obj=fake(m,'1')
  assert obj._step(m.State.DATA_DISABLED,{})==m.State.INITIALIZING
  obj._ppp.start.assert_not_called()
  handler=Mock(return_value=m.State.SEARCHING)
  assert obj._step(m.State.INITIALIZING,{m.State.INITIALIZING:handler})==m.State.SEARCHING
  handler.assert_called_once()


def test_failed_cleanup_does_not_claim_disabled():
  m=modem_module();obj=fake(m,'0');obj._ppp.kill.side_effect=OSError('fixture')
  with pytest.raises(OSError):obj._step(m.State.CONNECTED,{})
  obj._publish_state.assert_not_called()


def test_lingering_ppp_interface_does_not_claim_disabled():
  m=modem_module();obj=fake(m,'0');obj._ppp.data_session_active.return_value=True
  with pytest.raises(RuntimeError):obj._step(m.State.CONNECTED,{})
  obj._publish_state.assert_not_called()


def test_local_preference_rejects_onroad_and_non_boolean():
  params=Mock();params.get.return_value=True;parked=[False]
  pref=CellularDataPreference(params,lambda:parked[0])
  assert pref.enabled is True
  assert pref.set_enabled(False) is False;params.put_bool.assert_not_called()
  parked[0]=True
  assert pref.set_enabled(0) is False;params.put_bool.assert_not_called()
  assert pref.set_enabled(False) is True;params.put_bool.assert_called_once_with('GsmDataEnabled',False,block=True)


def test_three_languages_and_no_rf_sim_or_gnss_power_command():
  assert set(TEXT)=={'zh-TW','en','ja'}
  for language in TEXT:
    assert all(label(key,language) for key in ('title','description','on','off'))
  tree=ast.parse(Path('openpilot/common/hardware/comma/modem.py').read_text(encoding='utf-8'))
  step=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='_step')
  called={n.func.attr for n in ast.walk(step) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
  assert called=={'_read_param','kill','cleanup_routes','reset_data_port','data_session_active','_publish_state','_check_iccid'}
  from openpilot.sunnypilot.formosalink.settings import LOCAL_ONLY
  assert 'GsmDataEnabled' in LOCAL_ONLY


@pytest.mark.parametrize('enabled,state,expected',[
  (True,{},'unknown'),
  (False,{'seconds_since_boot':100,'state':'DATA_DISABLED'},'disabled'),
  (False,{'seconds_since_boot':100,'connected':True},'connected'),
  (False,{'seconds_since_boot':100,'connected':False},'pending'),
  (True,{'seconds_since_boot':100,'connected':False},'disconnected'),
  (False,{'seconds_since_boot':80,'state':'DATA_DISABLED'},'unknown'),
])
def test_web_status_reports_fresh_effective_state_not_only_the_preference(enabled,state,expected):
  from openpilot.system.ui.lib.cellular_data import modem_data_state
  assert modem_data_state(enabled,state,101)==expected
