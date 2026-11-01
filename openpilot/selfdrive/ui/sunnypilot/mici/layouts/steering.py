"""Offroad settings for the opt-in Honda/Toyota low-speed controller tuning."""
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigParamControl, GreyBigButton
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.selfdrive.controls.lib.low_speed_steering import low_speed_tune_block_reason
from openpilot.system.ui.sunnypilot.lib.low_speed_steering import low_speed_tune_status
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller


def can_change_low_speed_tune() -> bool:
  return low_speed_tune_block_reason(ui_state.CP, ui_state.params, ui_state.is_offroad()) is None


def clear_low_speed_tune_conflicts() -> bool:
  # Explicit offroad user action. Never enable the new tuning or change torque limits here.
  reason = low_speed_tune_block_reason(ui_state.CP, ui_state.params, ui_state.is_offroad())
  if reason not in ("nnlc", "jerk"):
    return False
  ui_state.params.put_bool("NeuralNetworkLateralControl", False, block=True)
  ui_state.params.put_bool("LateralJerkTorqueController", False, block=True)
  return True


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
    self._status = GreyBigButton("", "")
    self._resolve = BigButton(tr("Turn off NNLC / Jerk"), description=tr("Turn off conflicting steering tuning. The low-speed tuning switch stays unchanged."))
    self._resolve.set_click_callback(self._clear_conflicts)
    self._resolve.set_visible(lambda: low_speed_tune_block_reason(ui_state.CP, ui_state.params, ui_state.is_offroad()) in ("nnlc", "jerk"))
    self._scroller.add_widgets([self._status, self._resolve, self._force_torque, self._tune])
    self._refresh_status()

  def _refresh_status(self):
    status = low_speed_tune_status(ui_state.CP, ui_state.params, ui_state.is_offroad())
    if self._status.get_value() != status:
      self._status.set_value(status)

  def _clear_conflicts(self):
    if clear_low_speed_tune_conflicts():
      self._tune.refresh()
      self._force_torque.refresh()
    self._refresh_status()

  def _update_state(self):
    super()._update_state()
    self._refresh_status()

  def show_event(self):
    super().show_event()
    self._tune.refresh()
    self._force_torque.refresh()
    self._refresh_status()
