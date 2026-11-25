import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pyray as rl
import pytest

from openpilot.selfdrive.ui.mici.layouts.settings import menu, navigation
from openpilot.system.ui.widgets.scroller import Scroller


def center(rect):
  return rl.Vector2(rect.x+rect.width/2, rect.y+rect.height/2)


@pytest.fixture
def drawing(monkeypatch):
  for method in ("draw_rectangle_rec", "draw_rectangle_rounded", "draw_rectangle", "draw_texture_v"):
    monkeypatch.setattr(rl, method, Mock())
  monkeypatch.setattr(menu, "caption", Mock())
  monkeypatch.setattr(navigation, "caption", Mock())
  monkeypatch.setattr(menu.gui_app, "texture", Mock(return_value=SimpleNamespace(width=47, height=47)))
  monkeypatch.setattr(menu.gui_app, "push_widget", Mock())


def test_all_home_pages_and_drag_out_and_back(drawing):
  order = ["display", "network", "egpu", "device", "camera", "software", "toggles", "language", "developer", "firehose", "pair"]
  grid = menu.SettingsGrid({key: (key, object()) for key in order}, order)
  visited = []
  for i in range(4):
    grid._render(rl.Rectangle(8, 66, 520, 166))
    visited.extend(grid.targets)
    for key, rect in grid.targets.items():
      assert rect.width >= 165 and rect.height >= 166
      point = center(rect)
      grid._handle_mouse_press(point)
      grid._handle_mouse_event(SimpleNamespace(left_down=True, pos=rl.Vector2(0, 5)))
      grid._handle_mouse_release(point)
      menu.gui_app.push_widget.assert_not_called()
      grid._handle_mouse_press(point)
      grid._handle_mouse_release(point)
      menu.gui_app.push_widget.assert_called_once_with(grid.pages[key][1])
      menu.gui_app.push_widget.reset_mock()
    assert grid.can_page(-1) == (i > 0)
    assert grid.can_page(1) == (i < 3)
    grid.move(1)
  assert visited == order


def test_display_picker_back_and_no_write_when_locked_or_moving(drawing, monkeypatch):
  monkeypatch.setitem(sys.modules, "openpilot.common.params", SimpleNamespace(UnknownKeyName=KeyError))
  params = Mock()
  params.get_bool.return_value = True
  state = SimpleNamespace(params=params, is_offroad=Mock(return_value=True))
  picker = menu.DisplayPicker(state, Mock())
  picker.activate(0)
  picker.activate(1)
  params.put_bool.assert_not_called()
  picker.activate(1)
  picker._render(rl.Rectangle(8, 65, 520, 167))
  assert len(picker.targets) == 3
  state.is_offroad.return_value = False
  picker.activate(2)
  params.put.assert_not_called()
  picker.activate(1)
  picker.back()
  picker.close.assert_not_called()
  picker.back()
  picker.close.assert_called_once()


def test_detail_toolbar_edges_and_aligned_paging_after_a_drag(drawing):
  scroll = Scroller()
  body = scroll._scroller
  navigation.add_section_navigation(scroll, "Wi-Fi", Mock())
  body.set_rect(rl.Rectangle(0, 58, 536, 182))
  body._content_size = 3*536
  bar = scroll._header
  for offset, previous, following in [(0, 0, 536), (-723, -187, 349), (-1072, -536, 0)]:
    body.scroll_panel.set_offset(offset)
    assert scroll._page_distance(-1) == previous
    assert scroll._page_distance(1) == following
    bar._render(rl.Rectangle(0, 0, 536, 58))
    assert ("previous" in bar.targets) == bool(previous)
    assert ("next" in bar.targets) == bool(following)
    assert all(box.height >= 50 for box in bar.targets.values())
