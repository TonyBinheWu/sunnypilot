"""Native Park-only offroad controls for both device layouts."""
import time

from openpilot.common.forced_offroad import get_service
from openpilot.system.ui.lib.multilang import tr

TITLE = "Force offroad (Park only)"
DESCRIPTION = "Park and stop, then disengage all assistance. Normal driving processes and driving recording stop. Leaving Park or losing vehicle data cancels this mode. Resets after restart."
REASONS = {
  "vehicle_unavailable": "Fresh vehicle data is required.",
  "park_required": "Only available in P gear.",
  "moving": "Stop the vehicle before changing this switch.",
  "controls_unavailable": "Waiting for assistance status.",
  "controls_active": "Disengage steering and cruise assistance first.",
  "pending": "Switching mode...",
}


class OffroadView:
  def __init__(self):
    self.next_refresh = 0.0
    self.state = {"requested": False, "active": False, "can_toggle": False, "reason": "vehicle_unavailable"}

  def refresh(self):
    if time.monotonic() >= self.next_refresh:
      self.next_refresh = time.monotonic() + 0.25
      try:
        self.state = get_service().status()
      except Exception:
        self.state = {"requested": False, "active": False, "can_toggle": False, "reason": "vehicle_unavailable"}
    return self.state

  def change(self, checked):
    try:
      get_service().request(bool(checked))
    except (PermissionError, ValueError):
      pass  # The authoritative refresh restores the actual switch value.
    self.next_refresh = 0
    self.refresh()

  def detail(self):
    state = self.refresh()
    label = tr("Forced offroad is active.") if state["active"] else tr("Normal automatic mode.")
    reason = REASONS.get(state["reason"])
    return label + (" " + tr(reason) if reason else "")


def offroad_item():
  from openpilot.system.ui.widgets.list_view import ListItem, ToggleAction
  view = OffroadView()

  class OffroadItem(ListItem):
    def _update_state(self):
      state = view.refresh()
      self.action_item.set_state(state["requested"])
      super()._update_state()

  return OffroadItem(title=lambda: tr(TITLE), description=lambda: view.detail() + " " + tr(DESCRIPTION),
                     action_item=ToggleAction(callback=view.change, enabled=lambda: view.refresh()["can_toggle"]))


def offroad_big_toggle():
  from openpilot.selfdrive.ui.mici.widgets.button import BigToggle
  view = OffroadView()

  class OffroadToggle(BigToggle):
    def _get_label_font_size(self):
      return 56

    def _update_state(self):
      state = view.refresh()
      self.set_text(tr(TITLE))
      self.set_value(view.detail())
      self._checked = state["requested"]
      self.set_enabled(state["can_toggle"])
      super()._update_state()

  return OffroadToggle(tr(TITLE), view.detail(), toggle_callback=view.change)
