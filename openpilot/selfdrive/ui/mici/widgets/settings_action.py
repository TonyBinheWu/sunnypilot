import pyray as rl

from openpilot.selfdrive.ui.device_design import BAR, INK, SELECTED, TILE, caption
from openpilot.system.ui.widgets.button import Button


class SettingsAction(Button):
  """A compact full-target action that retains the caller's enable and release rules."""
  def __init__(self, text, *args, **kwargs):
    kwargs["font_size"] = 21
    super().__init__(text, *args, **kwargs)
    self.title = text
    self.cancel_touch_on_exit = True

  def set_text(self, text):
    self.title = text

  def _render(self, rect):
    rl.draw_rectangle_rounded(rect, .18, 5, (SELECTED if self.is_pressed else TILE) if self.enabled else BAR)
    caption(rect, self.title() if callable(self.title) else self.title, 21, INK if self.enabled else rl.GRAY, centered=True)
