"""Compact device home wordmark with the bundled FormosaPilot symbol."""
import pyray as rl
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.branding import LOGO_ASSET, PRODUCT
from openpilot.system.ui.widgets import Widget


class FormosaWordmark(Widget):
  font_size = 64  # The native home uses this to position version information.
  text = PRODUCT

  def __init__(self):
    super().__init__()
    self._rect.width, self._rect.height = 480, 80
    self.logo = gui_app.texture(LOGO_ASSET, 64, 64)

  def _render(self, rect):
    rl.draw_texture_ex(self.logo, rl.Vector2(rect.x, rect.y+8), 0, 1, rl.WHITE)
    rl.draw_text_ex(gui_app.font(FontWeight.BOLD), PRODUCT, rl.Vector2(rect.x+72, rect.y+5), 48, 0, rl.WHITE)
