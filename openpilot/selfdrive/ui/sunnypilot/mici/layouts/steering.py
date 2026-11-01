"""Offroad settings for the opt-in Honda/Toyota low-speed controller tuning."""
from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.selfdrive.controls.lib.low_speed_steering import supports_low_speed_tune
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller


def can_change_low_speed_tune() -> bool:
  return (ui_state.is_offroad() and supports_low_speed_tune(ui_state.CP) and
          not ui_state.params.get_bool("NeuralNetworkLateralControl") and
          not ui_state.params.get_bool("LateralJerkTorqueController"))


class LowSpeedTuneControl(BigParamControl):
  def _handle_mouse_release(self, mouse_pos):
    if can_change_low_speed_tune():
      super()._handle_mouse_release(mouse_pos)


class SteeringTuneLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    description = "Honda / Toyota\n\n" + tr("Improve low-speed steering while keeping vehicle torque limits.")
    description += "\n\n" + tr("Default off. Offroad changes apply next drive. Torque control only; disabled with NNLC or Lateral Jerk Torque Controller.")
    self._tune = LowSpeedTuneControl(tr("Low-Speed Steering Tune"), "LowSpeedSteeringTune", description=description)
    self._force_torque = LowSpeedTuneControl(tr("Enforce Torque Lateral Control"), "EnforceTorqueControl",
                                            description=tr("Enable this to enforce sunnypilot to steer with Torque lateral control."))
    self._force_torque.set_enabled(can_change_low_speed_tune)
    self._tune.set_enabled(can_change_low_speed_tune)
    self._scroller.add_widgets([self._force_torque, self._tune])

  def show_event(self):
    super().show_event()
    self._tune.refresh()
    self._force_torque.refresh()
