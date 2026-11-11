"""Native-only cellular preference and C3X/C4 widget integration checks."""
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from openpilot.common.params import Params
from openpilot.system.ui.lib.cellular_data import CellularDataPreference


class TestCellularToggleLifecycle(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    import pyray as rl
    from openpilot.system.ui.lib.application import gui_app
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_HIDDEN)
    gui_app.init_window("Cellular toggle lifecycle")

  @classmethod
  def tearDownClass(cls):
    from openpilot.system.ui.lib.application import gui_app
    gui_app.close()

  def test_native_touch_survives_parent_refresh(self):
    import pyray as rl
    from unittest.mock import Mock
    from openpilot.system.ui.widgets.network import AdvancedNetworkSettings
    from openpilot.selfdrive.ui.ui_state import ui_state
    with tempfile.TemporaryDirectory() as directory:
      params = Params(directory)
      params.put_bool("GsmDataEnabled", True)
      with patch("openpilot.common.params.Params", return_value=params), patch.object(ui_state, "is_offroad", return_value=True):
        panel = AdvancedNetworkSettings(Mock(ipv4_address="127.0.0.1"))
        panel._cellular_data_btn.set_parent_rect(rl.Rectangle(0, 0, 1500, 1000))
        for requested in (False, True, False):
          panel._cellular_data_action.toggle._handle_mouse_release(rl.Vector2(0, 0))
          # Native rendering refreshes the parent before rendering the child on
          # the next frame; a delayed row callback used to lose this click.
          panel._update_state()
          rl.begin_drawing()
          panel._cellular_data_btn.render(rl.Rectangle(0, 0, 1500, 200))
          rl.end_drawing()
          self.assertEqual(params.get_bool("GsmDataEnabled"), requested)
          self.assertEqual(panel._cellular_data_action.get_state(), requested)

  def test_esim_card_uses_fresh_data_status_for_physical_and_esim(self):
    import importlib
    network = importlib.import_module("openpilot.selfdrive.ui.mici.layouts.settings.network")
    from openpilot.system.ui.lib.cellular_data import label
    from openpilot.system.ui.lib.multilang import multilang
    with tempfile.TemporaryDirectory() as directory:
      params = Params(directory)
      manager = SimpleNamespace(is_euicc=False, active_profile=None, modem_state={})
      with patch.object(network, "Params", return_value=params), patch.object(network.time, "monotonic", return_value=101):
        button = network.EsimNetworkButton(manager)
        with patch.object(button, "_cell_icon", return_value=None):
          for locale in ("zh-CHT", "en", "ja"):
            with patch.object(multilang, "_language", locale):
              for enabled, fields, expected in (
                (False, {"state":"DATA_DISABLED", "connected":False}, "disabled"),
                (True, {"state":"CONNECTED", "connected":False}, "starting"),
                (True, {"state":"CONNECTED", "connected":False, "ip_address":"10.1.2.3"}, "starting"),
                (True, {"state":"CONNECTED", "connected":True, "ip_address":"10.1.2.3"}, "connected"),
                (True, {"state":"SEARCHING", "registration":"denied"}, "denied"),
                (True, {"state":"CONNECTED", "connected":True, "ip_address":"10.1.2.3", "seconds_since_boot":80}, "unknown"),
              ):
                params.put_bool("GsmDataEnabled", enabled)
                manager.modem_state = {"iccid":"DEMO0000", "seconds_since_boot":100, **fields}
                for euicc in (False, True):
                  manager.is_euicc = euicc
                  manager.active_profile = SimpleNamespace(display_name="DEMO") if euicc else None
                  self.assertEqual(button._compute_state()[1], label(expected))

  def test_data_feedback_refreshes_during_busy_esim_operation(self):
    from openpilot.system.ui.lib.cellular_manager import CellularManager
    from openpilot.common.hardware import HARDWARE
    for busy, polling in ((True, False), (False, True), (True, True)):
      manager = CellularManager()
      manager._busy, manager._polling = busy, polling
      state = {"state":"DATA_DISABLED", "connected":False, "seconds_since_boot":100}
      with patch.object(HARDWARE, "get_modem_state", return_value=state), patch("openpilot.system.ui.lib.cellular_manager.time.monotonic", return_value=101), patch.object(manager, "_poll_profiles") as profiles:
        manager.process_callbacks()
        self.assertEqual(manager.modem_state, state)
        profiles.assert_not_called()


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
      AdvancedNetworkSettings._toggle_cellular_data(tici, False)
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
