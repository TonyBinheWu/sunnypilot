from openpilot.selfdrive.ui.ui_state import ui_state


def restart_needed_callback(_):
  ui_state.params.put_bool("OnroadCycleRequested", True)


def set_openpilot_enabled(enabled: bool) -> bool:
  """Recheck at confirmation time, since engagement can change with the dialog open."""
  current = ui_state.params.get_bool("OpenpilotEnabledToggle")
  if ui_state.engaged or enabled == current:
    return current
  ui_state.params.put_bool("OpenpilotEnabledToggle", enabled)
  restart_needed_callback(enabled)
  return enabled
