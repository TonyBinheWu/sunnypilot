"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from openpilot.selfdrive.ui.layouts.home import HomeLayout, HomeLayoutState, HEAD_BUTTON_FONT_SIZE, SPACING
from openpilot.system.ui.lib.application import gui_app, FontWeight, TextAlignment
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.multilang import tr, trn
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.lib.branding import LOGO_ASSET

BRAND_FONT_SIZE = 48
BRAND_DESC_SPACING = 12


class HomeLayoutSP(HomeLayout):
  def __init__(self):
    super().__init__()
    from openpilot.sunnypilot.formosalink.ui import FormosaConnectionCard
    self._prime_widget = FormosaConnectionCard()

  def _render_header(self):
    font = gui_app.font(FontWeight.MEDIUM)

    version_text_width = self.header_rect.width

    if self.update_available:
      version_text_width -= self.update_notif_rect.width

      highlight_color = rl.Color(75, 95, 255, 255) if self.current_state == HomeLayoutState.UPDATE else rl.Color(54, 77, 239, 255)
      rl.draw_rectangle_rounded(self.update_notif_rect, 0.3, 10, highlight_color)

      text = tr("UPDATE")
      text_size = measure_text_cached(font, text, HEAD_BUTTON_FONT_SIZE)
      text_x = self.update_notif_rect.x + (self.update_notif_rect.width - text_size.x) // 2
      text_y = self.update_notif_rect.y + (self.update_notif_rect.height - text_size.y) // 2
      rl.draw_text_ex(font, text, rl.Vector2(int(text_x), int(text_y)), HEAD_BUTTON_FONT_SIZE, 0, rl.WHITE)

    if self.alert_count > 0:
      version_text_width -= self.alert_notif_rect.width

      highlight_color = rl.Color(255, 70, 70, 255) if self.current_state == HomeLayoutState.ALERTS else rl.Color(226, 44, 44, 255)
      rl.draw_rectangle_rounded(self.alert_notif_rect, 0.3, 10, highlight_color)

      alert_text = trn("{} ALERT", "{} ALERTS", self.alert_count).format(self.alert_count)
      text_size = measure_text_cached(font, alert_text, HEAD_BUTTON_FONT_SIZE)
      text_x = self.alert_notif_rect.x + (self.alert_notif_rect.width - text_size.x) // 2
      text_y = self.alert_notif_rect.y + (self.alert_notif_rect.height - text_size.y) // 2
      rl.draw_text_ex(font, alert_text, rl.Vector2(int(text_x), int(text_y)), HEAD_BUTTON_FONT_SIZE, 0, rl.WHITE)

    if self.update_available or self.alert_count > 0:
      version_text_width -= SPACING * 1.5

    version_right = self.header_rect.x + self.header_rect.width
    version_left = version_right - version_text_width

    brand = "FormosaPilot"
    description = self.params.get("UpdaterCurrentDescription") or ""

    logo_size = min(64, self.header_rect.height-12)
    brand_size = measure_text_cached(gui_app.font(FontWeight.BOLD), brand, BRAND_FONT_SIZE)
    max_desc_width = max(0, version_text_width-brand_size.x-logo_size-2*BRAND_DESC_SPACING)
    desc_width = 0
    if description:
      desc_size = measure_text_cached(gui_app.font(FontWeight.NORMAL), description, BRAND_FONT_SIZE)
      desc_width = min(desc_size.x, max_desc_width)
      desc_rect = rl.Rectangle(version_right - desc_width, self.header_rect.y, desc_width, self.header_rect.height)
      gui_label(desc_rect, description, BRAND_FONT_SIZE, rl.WHITE, alignment=TextAlignment.RIGHT)

    spacing = BRAND_DESC_SPACING if description else 0
    brand_x = version_right - desc_width - spacing - brand_size.x
    brand_rect = rl.Rectangle(max(version_left+logo_size+BRAND_DESC_SPACING, brand_x), self.header_rect.y, brand_size.x, self.header_rect.height)
    gui_label(brand_rect, brand, BRAND_FONT_SIZE, rl.WHITE, font_weight=FontWeight.BOLD)
    logo = gui_app.texture(LOGO_ASSET, logo_size, logo_size)
    rl.draw_texture_ex(logo, rl.Vector2(brand_rect.x-logo_size-BRAND_DESC_SPACING, self.header_rect.y+(self.header_rect.height-logo_size)/2), 0, 1, rl.WHITE)
