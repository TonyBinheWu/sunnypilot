from types import SimpleNamespace
from unittest.mock import Mock  # noqa: TID251 - pytest tests use stdlib spies for drawing and alerts

import pyray as rl
import pytest

from openpilot.selfdrive.ui.mici.onroad.debug_plot import DebugPlot
from openpilot.selfdrive.ui.widgets import body_eyes as eyes


class SpeedMessages(dict):
  def __init__(self, speed):
    super().__init__(carState=SimpleNamespace(vEgo=speed))
    self.alive = {"carState": True}
    self.valid = {"carState": True}
    self.recv_time = {"carState": 20.0}
    self.recv_frame = {"carState": 11}


def test_speed_requires_fresh_data_from_this_drive():
  sm = SpeedMessages(25.0)
  state = SimpleNamespace(started=True, started_frame=10, sm=sm)
  assert eyes.face_speed(state, 20.1) == 25
  assert eyes.face_speed(state, 20.6) == eyes.face_speed(state, 19.9) == 0
  for flags in (sm.alive, sm.valid):
    flags["carState"] = False
    assert eyes.face_speed(state, 20.1) == 0
    flags["carState"] = True
  sm.recv_frame["carState"] = 9
  assert eyes.face_speed(state, 20.1) == 0
  sm.recv_frame["carState"] = 11
  for speed in (-4, float('nan'), float('inf')):
    sm["carState"].vEgo = speed
    assert eyes.face_speed(state, 20.1) == 0
  state.started = False
  sm["carState"].vEgo = 30.0
  assert eyes.face_speed(state, 20.1) == 0


@pytest.mark.parametrize("width,height", [(536, 240), (2160, 1080)])
def test_pose_fits_scrolling_page_blinks_and_focuses_with_speed(monkeypatch, width, height):
  rect = rl.Rectangle(75, 33, width, height)
  dots = []
  monkeypatch.setattr(rl, "draw_ellipse", lambda x, y, rx, ry, _: dots.append((x, y, rx, ry)))
  def render(speed, now):
    dots.clear()
    eyes.draw_eyes(rect, speed, now)
    assert all(rect.x < x-rx < x+rx < rect.x+width and rect.y < y-ry < y+ry < rect.y+height for x, y, rx, ry in dots)
    return tuple(dots)

  idle = render(0, 1)
  street = render(12, 1)
  highway = render(30, 1)
  assert len(idle) == len(street) == len(highway) == 24
  assert idle[0][3] > street[0][3] > highway[0][3]
  assert render(50, 1) == highway
  assert len(render(0, .05)) == 8
  assert len(render(0, .15)) == 12


def test_c4_idle_page_yields_to_native_alerts_and_leaves_diagnostic_modes_alone(monkeypatch):
  state = SimpleNamespace(started=True, started_frame=0, sm=SpeedMessages(10))
  monkeypatch.setattr(eyes, "ui_state", state)
  monkeypatch.setattr(rl, "draw_rectangle_rec", Mock())
  draw = Mock()
  monkeypatch.setattr(eyes, "draw_eyes", draw)
  alert = Mock(return_value=True)
  plot = SimpleNamespace(params=Mock(), _render_alert=alert)
  rect = rl.Rectangle(0, 0, 536, 240)
  plot.params.get_int.return_value = 0
  DebugPlot._render(plot, rect)
  alert.assert_called_once_with(rect)
  draw.assert_not_called()
  alert.return_value = False
  DebugPlot._render(plot, rect)
  draw.assert_called_once()
  state.started = False
  DebugPlot._render(plot, rect)
  assert draw.call_count == 2 and alert.call_count == 2
  monkeypatch.setattr("openpilot.selfdrive.ui.mici.onroad.debug_plot.ui_state", state)
  plot.params.get_int.return_value = 1
  DebugPlot._render(plot, rect)  # no longitudinalPlan to graph
  assert draw.call_count == 2 and alert.call_count == 2


def test_c3x_rightmost_page_only_returns_on_tap_or_swipe_back():
  page = eyes.BodyEyesPage()
  page.set_rect(rl.Rectangle(0, 0, 2160, 1080))
  back = Mock()
  page.set_click_callback(back)
  start = rl.Vector2(1024, 400)
  for end, finger_direction, exits in [(rl.Vector2(280, 410), -1, False), (rl.Vector2(630, 820), 0, False),
                                       (rl.Vector2(1600, 410), 1, True), (rl.Vector2(1027, 400), 0, True)]:
    back.reset_mock()
    assert eyes.horizontal_swipe(start, end, page.rect.width) == finger_direction
    page._handle_mouse_press(start)
    page._handle_mouse_release(end)
    assert back.called == exits


def test_c3x_swipes_enter_from_home_and_road_and_an_alert_restores_the_hud(monkeypatch):
  from openpilot.selfdrive.ui.layouts import main
  from openpilot.selfdrive.ui.layouts.home import HomeLayout, HomeLayoutState
  from openpilot.selfdrive.ui.onroad.augmented_road_view import AugmentedRoadView

  state = SimpleNamespace(started=True, sm={}, params=Mock(), show_camera_with_cluster=False)
  monkeypatch.setattr(main, "ui_state", state)
  monkeypatch.setattr(main, "draw_b1_badge", Mock())
  rect = rl.Rectangle(0, 0, 2160, 1080)
  start, end = rl.Vector2(1500, 400), rl.Vector2(700, 410)
  layout = main.MainLayout.__new__(main.MainLayout)
  layout._layouts = {mode: Mock() for mode in main.MainState}
  road = layout._layouts[main.MainState.ONROAD]
  road.alert_renderer.get_alert.return_value = None
  layout._sidebar = Mock(is_visible=False)
  layout._content_rect = layout._rect = rect
  layout._prev_onroad = True
  layout._handle_carrot_record_cmd = Mock()
  layout._current_mode = main.MainState.HOME
  home = SimpleNamespace(home=Mock(), current_state=HomeLayoutState.HOME, rect=rect, _on_swipe_left=layout._show_body_eyes)
  HomeLayout._handle_mouse_press(home, start)
  HomeLayout._handle_mouse_release(home, end)
  assert layout._current_mode == main.MainState.BODY_EYES
  layout._set_mode_for_state()
  road.rect, road._on_swipe_left = rect, layout._show_body_eyes
  road._selector.begin.return_value = road._selector.finish.return_value = road._hud_renderer.user_interacting.return_value = False
  AugmentedRoadView._handle_mouse_press(road, start)
  AugmentedRoadView._handle_mouse_release(road, end)
  assert layout._current_mode == main.MainState.BODY_EYES
  road._click_callback.assert_not_called()
  layout._render(rect)
  layout._layouts[main.MainState.BODY_EYES].render.assert_called_once_with(rect)
  road.alert_renderer.get_alert.return_value = "takeover"
  layout._render(rect)
  assert layout._current_mode == main.MainState.ONROAD
  road.render.assert_called_once_with(rect)
  layout._show_body_eyes()
  assert layout._current_mode == main.MainState.ONROAD
