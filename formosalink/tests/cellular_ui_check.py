"""Native-only cellular preference and C3X/C4 widget integration checks."""
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from openpilot.common.params import Params
from openpilot.system.ui.lib.cellular_data import CellularDataPreference


class TestCellularUI(unittest.TestCase):
  def test_native_default_and_persistent_preference(self):
    with tempfile.TemporaryDirectory() as directory:
      params=Params(directory)
      pref=CellularDataPreference(params,lambda:True)
      self.assertTrue(pref.enabled)
      self.assertTrue(pref.set_enabled(False))
      self.assertFalse(CellularDataPreference(Params(directory),lambda:True).enabled)
      self.assertTrue(pref.set_enabled(True));self.assertTrue(pref.enabled)

  def test_actual_network_callbacks_and_onroad_guard(self):
    from openpilot.system.ui.widgets.network import AdvancedNetworkSettings
    from openpilot.selfdrive.ui.mici.layouts.settings.network.network_layout import NetworkLayoutMici
    with tempfile.TemporaryDirectory() as directory:
      params=Params(directory);parked=[True]
      pref=CellularDataPreference(params,lambda:parked[0])
      action=SimpleNamespace(get_state=lambda:False,set_state=lambda value:None)
      tici=SimpleNamespace(_cellular_data=pref,_cellular_data_action=action)
      AdvancedNetworkSettings._toggle_cellular_data(tici)
      self.assertFalse(pref.enabled)
      button=SimpleNamespace(set_checked=lambda value:None)
      mici=SimpleNamespace(_cellular_data=pref,_cellular_data_btn=button)
      NetworkLayoutMici._toggle_cellular_data(mici,True);self.assertTrue(pref.enabled)
      parked[0]=False
      NetworkLayoutMici._toggle_cellular_data(mici,False);self.assertTrue(pref.enabled)

  def test_native_modem_disabled_does_not_dial_or_send_at(self):
    from openpilot.common.hardware.comma.modem import Modem,State
    from unittest.mock import Mock
    modem=Modem();modem._ppp=Mock();modem._read_param=Mock(return_value='0');modem._publish_state=Mock();modem._at=Mock()
    modem._ppp.data_session_active.return_value=False
    self.assertEqual(modem._step(State.CONNECTED,{}),State.DATA_DISABLED)
    self.assertEqual(modem._step(State.DATA_DISABLED,{}),State.DATA_DISABLED)
    modem._ppp.kill.assert_called_once();modem._ppp.start.assert_not_called();modem._at.assert_not_called()
