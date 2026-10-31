"""Host-only optional onroad overlay regression; never starts vehicle processes."""
import time
import unittest
from unittest import mock

from openpilot.cereal import messaging
from openpilot.selfdrive.ui.ui_state import ui_state
from tools.diagnostics import check_calibrated_onroad


class TestOnroadOptions(check_calibrated_onroad.TestCalibratedOnroad):
  def test_calibration_transition_and_overlays(self):
    refresh_params = ui_state.update_params

    def enable_options():
      refresh_params()
      ui_state.developer_ui = 3
      ui_state.torque_bar = True
      ui_state.blindspot = True
      ui_state.turn_signals = True
      ui_state.standstill_timer = True
      ui_state.road_name_toggle = True
      ui_state.rocket_fuel = True
      ui_state.true_v_ego_ui = True

      def message(service):
        event = messaging.new_message(service)
        data = getattr(event, service)
        ui_state.sm.data[service] = data
        for checks in (ui_state.sm.valid, ui_state.sm.alive, ui_state.sm.seen, ui_state.sm.updated):
          checks[service] = True
        ui_state.sm.recv_frame[service] = 10
        ui_state.sm.recv_time[service] = time.monotonic()
        return data

      message("controlsState").lateralControlState.init("torqueState")
      message("carControl").latActive = True
      message("lateralTorqueParameters").valid = True
      message("vehicleParameters")
      message("gpsLocationExternal")
      message("longitudinalPlanSP").e2eAlerts.greenLightAlert = True
      print("Enabled developer BOTH, torque bar, turn signals, blindspot, timer, road name and acceleration overlays", flush=True)

    with mock.patch.object(ui_state, "update_params", side_effect=enable_options):
      super().test_calibration_transition_and_overlays()


if __name__ == "__main__":
  unittest.main(verbosity=2)
