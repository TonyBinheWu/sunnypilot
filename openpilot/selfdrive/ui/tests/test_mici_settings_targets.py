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


def test_pager_accepts_edge_taps_and_small_jitter_but_cancels_a_drag(drawing):
  following, previous = Mock(), Mock()
  bar = navigation.SettingsToolbar(lambda: "Settings", Mock(), previous, following)
  bar._render(rl.Rectangle(0, 0, 536, 58))
  next_box = bar.targets["next"]
  edge = rl.Vector2(535, 1)
  bar._handle_mouse_press(edge)
  bar._handle_mouse_release(edge)
  following.assert_called_once()
  start = rl.Vector2(next_box.x+1, 22)
  for excursion in (4, 30):
    bar._handle_mouse_press(start)
    bar._handle_mouse_event(SimpleNamespace(left_down=True, pos=rl.Vector2(next_box.x-excursion, 22)))
    bar._handle_mouse_release(start)
  bar._handle_mouse_press(start)
  bar._handle_mouse_release(rl.Vector2(next_box.x-2, 22))
  assert following.call_count == 2
  previous.assert_not_called()


def test_page_buttons_queue_and_reverse_without_waiting_for_animation(drawing):
  page = Scroller()
  body = page._scroller
  body.set_rect(rl.Rectangle(0, 58, 536, 182))
  body._content_size = 3 * 536
  page.page_by(1)
  page.page_by(-1)
  assert body.target_offset == 0
  page.page_by(1)
  page.page_by(1)
  assert body.target_offset == -1072
  assert not page.can_page(1)
  page.page_by(1)
  assert body.target_offset == -1072
  page.page_by(-1)
  assert body.target_offset == -536


@pytest.mark.parametrize("device", ["c4", "c3x"])
def test_master_switch_only_persists_a_confirmed_disable(device, drawing, monkeypatch):
  from openpilot.selfdrive.ui.layouts.settings import common, toggles
  from openpilot.selfdrive.ui.mici.layouts.settings import toggles as mici
  from openpilot.selfdrive.ui.mici.widgets import button
  from openpilot.system.ui.widgets import DialogResult

  key = "OpenpilotEnabledToggle"
  values = {key: True}
  params = Mock()
  params.get_bool.side_effect = lambda name, *args: bool(values.get(name))
  params.get.return_value = 0
  params.put_bool.side_effect = values.__setitem__
  state = SimpleNamespace(params=params, engaged=False, add_engaged_transition_callback=Mock())
  for module in (common, toggles, mici):
    monkeypatch.setattr(module, "ui_state", state)
  if device == "c4":
    monkeypatch.setattr(button, "Params", lambda: params)
    monkeypatch.setattr(button, "UnifiedLabel", Mock())
    page = mici.TogglesLayoutMici()
    page._enable_openpilot.set_checked(True)
    dialog = Mock()
    monkeypatch.setattr(mici, "BigConfirmationDialog", dialog)

    def tap(value):
      assert page._enable_openpilot._checked != value
      page._enable_openpilot._handle_mouse_release(rl.Vector2(0, 0))

    def confirm():
      dialog.call_args.args[2]()
  else:
    page = SimpleNamespace(_params=params, _toggles={key: SimpleNamespace(action_item=Mock())})
    dialog = Mock()
    monkeypatch.setattr(toggles, "ConfirmDialog", dialog)

    def tap(value):
      toggles.TogglesLayout._toggle_callback(page, value, key)

    def confirm():
      dialog.call_args.kwargs["callback"](DialogResult.CONFIRM)

  tap(False)
  dialog.assert_called_once()
  if device == "c3x":
    dialog.call_args.kwargs["callback"](DialogResult.CANCEL)
  params.put_bool.assert_not_called()
  tap(False)
  state.engaged = True
  confirm()
  params.put_bool.assert_not_called()
  state.engaged = False
  tap(False)
  confirm()
  assert [entry.args for entry in params.put_bool.call_args_list] == [(key, False), ("OnroadCycleRequested", True)]
  dialog.reset_mock()
  params.put_bool.reset_mock()
  tap(True)
  dialog.assert_not_called()
  assert [entry.args for entry in params.put_bool.call_args_list] == [(key, True), ("OnroadCycleRequested", True)]
