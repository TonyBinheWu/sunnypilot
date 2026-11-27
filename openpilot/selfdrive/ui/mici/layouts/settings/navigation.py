import pyray as rl

from openpilot.selfdrive.ui.device_design import BASE, BAR, INK, MINT, SELECTED, TILE, TouchMenu, caption
from openpilot.system.ui.lib.multilang import tr

HEADER_HEIGHT = 58


class DeviceTouchMenu(TouchMenu):
  def _handle_mouse_event(self, event):
    key = self._pressed_target
    if event.left_down and key is not None and self._hit(event.pos) != key:
      self._pressed_target = None


class SettingsToolbar(DeviceTouchMenu):
  background = BASE

  def _handle_mouse_event(self, event):
    # A finger can drift across the edge and settle back before release.
    # TouchMenu still requires the release to be on the original button.
    if event.left_down and self._pressed_target is not None:
      box = self.targets.get(self._pressed_target)
      slop = 8
      if box is None or not (box.x-slop <= event.pos.x < box.x+box.width+slop and
                             box.y-slop <= event.pos.y < box.y+box.height+slop):
        self._pressed_target = None

  def __init__(self, title, back, previous=None, following=None, can_page=None):
    super().__init__()
    self.title, self.back = title, back
    self.previous, self.following = previous, following
    self.can_page = can_page

  def activate(self, key):
    {"back": self.back, "previous": self.previous, "next": self.following}[key]()

  def _render(self, rect):
    rl.draw_rectangle_rec(rect, BAR)
    self.targets.clear()
    self.targets["back"] = rl.Rectangle(rect.x, rect.y, 103, rect.height)
    box = rl.Rectangle(rect.x+6, rect.y+4, 94, rect.height-8)
    rl.draw_rectangle_rounded(box, .25, 5, SELECTED if self._pressed_target == "back" else TILE)
    caption(box, tr("Back"), 22, centered=True)
    right = rect.x + rect.width
    if self.following is not None:
      width = min(116, rect.width * .22)
      for key, sign in (("next", 1), ("previous", -1)):
        right -= width
        box = rl.Rectangle(right+3, rect.y+4, width-6, rect.height-8)
        active = self.can_page is None or self.can_page(sign)
        if active:
          self.targets[key] = rl.Rectangle(right, rect.y, width, rect.height)
        rl.draw_rectangle_rounded(box, .25, 5, SELECTED if self._pressed_target == key else TILE)
        ink = MINT if active else (103, 121, 110, 255)
        caption(box, tr("Next page" if sign == 1 else "Previous page"), 19, ink, centered=True)
    left = rect.x+112
    caption(rl.Rectangle(left, rect.y, right-left, rect.height), self.title(), 22, INK)


def style_card(item):
  item.cancel_touch_on_exit = True
  if hasattr(item, "use_settings_style"):
    item.use_settings_style()


def add_section_navigation(page, title, back=None):
  page._scroller.set_page_style(style_card)

  def page_title():
    scroller = page._scroller
    count = len(scroller._visible_items)
    index = round(-scroller.scroll_panel.get_offset() / max(1, scroller.rect.width))
    label = tr(title).replace("\n", " ")
    return f"{label}   {min(count, max(1, index+1))}/{count}" if count > 1 else label

  bar = SettingsToolbar(page_title, back or page.dismiss, lambda: page.page_by(-1), lambda: page.page_by(1), page.can_page)
  page.set_header(bar, HEADER_HEIGHT)


def info_fields(rect, fields):
  rl.draw_rectangle_rounded(rect, .13, 6, TILE)
  height = rect.height / len(fields)
  for i, (label, value) in enumerate(fields):
    line = rl.Rectangle(rect.x+16, rect.y+i*height, rect.width-32, height)
    left = line.width * .28
    caption(rl.Rectangle(line.x, line.y, left, height), label, 23, MINT)
    caption(rl.Rectangle(line.x+left+8, line.y, line.width-left-8, height), value, 26)


class SettingsDetail:
  """Fixed return action around a live camera, document or confirmation body."""
  def init_settings_header(self, title):
    self.header = self._child(SettingsToolbar(lambda: tr(title).replace("\n", " "), self.dismiss))
    self.header.set_enabled(lambda: self.enabled and not self.is_dismissing)

  def _render(self, rect):
    rl.draw_rectangle_rec(rect, BASE)
    body = rl.Rectangle(rect.x, rect.y+HEADER_HEIGHT, rect.width, rect.height-HEADER_HEIGHT)
    self._render_body(body)
    self.header.render(rl.Rectangle(rect.x, rect.y, rect.width, HEADER_HEIGHT))
