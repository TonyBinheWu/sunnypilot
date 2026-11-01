"""Actionable settings status shared by the C3X and C4 steering pages."""
from openpilot.sunnypilot.selfdrive.controls.lib.low_speed_steering import low_speed_tune_block_reason
from openpilot.system.ui.lib.multilang import tr


def low_speed_tune_status(CP, params, offroad: bool) -> str:
  reason = low_speed_tune_block_reason(CP, params, offroad)
  if reason == "onroad":
    return tr("Leave onroad mode before changing steering tuning.")
  if reason == "no_car":
    return tr("Start the vehicle once to identify it, then return offroad.")
  if reason == "nnlc":
    return tr("Turn off NNLC to use low-speed steering tuning.")
  if reason == "jerk":
    return tr("Turn off Lateral Jerk Torque Controller to use low-speed steering tuning.")
  if reason == "angle":
    return tr("Low-speed steering tuning is unavailable for angle steering.")
  if reason == "dashcam":
    return tr("Steering tuning is unavailable in dashcam-only mode.")
  if reason == "configuration":
    return tr("Steering control is unavailable. Check that sunnypilot is enabled, then restart the vehicle to refresh identification.")
  if reason == "unsupported":
    return tr("This vehicle is not supported by low-speed steering tuning.")
  if CP.lateralTuning.which() != "torque":
    return tr("Enable torque lateral control; low-speed tuning will apply on the next drive.")
  return tr("Low-speed steering tuning is available. Changes apply on the next drive.")
