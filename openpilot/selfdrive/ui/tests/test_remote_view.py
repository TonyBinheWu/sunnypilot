import time
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pyray as rl
import pytest

from openpilot.selfdrive.ui import device_screen
from openpilot.system.ui import widgets
from openpilot.system.ui.lib.application import MouseEvent, MousePos


class MenuItem(widgets.Widget):
  def _render(self, rect):
    pass


class Messages(dict):
  def __init__(self):
    super().__init__(deviceState=NS(started=True), selfdriveState=NS(alertSize="none"))
    self.valid = dict.fromkeys(self, True)
    self.logMonoTime = dict.fromkeys(self, time.monotonic_ns())


@pytest.fixture
def paired(monkeypatch):
  state = NS(started=True, sm=Messages())
  gui = NS(width=536, height=240, mouse_events=[], show_touches=False)
  monkeypatch.setattr(device_screen, "ui_state", state)
  monkeypatch.setattr(device_screen, "gui_app", gui)
  monkeypatch.setattr(widgets, "gui_app", gui)
  monkeypatch.setattr(widgets, "device", NS(awake=True))
  display = device_screen.DeviceScreen()
  display.listener = Mock()
  display.auth = True
  monkeypatch.setattr(display, "tick", lambda physical: [])
  return display, gui, state.sm


@pytest.mark.parametrize("width,height", [(536, 240), (2160, 1080)])
@pytest.mark.parametrize("enabled", [True, False])
def test_native_menu_handles_remote_gestures_and_enforces_its_own_lock(monkeypatch, paired, width, height, enabled):
  display, gui, _ = paired
  gui.width, gui.height = width, height
  item = MenuItem()
  clicked = Mock()
  item.set_click_callback(clicked)
  item.set_enabled(enabled)
  monkeypatch.setattr(display, "tick", lambda physical: [("down", .4, .5), ("move", .5, .5), ("up", .5, .5)])
  gui.mouse_events = display.inputs([])
  assert display.mode == "road"
  assert gui.mouse_events[1].left_down and gui.mouse_events[1].pos == MousePos((width-1)/2, (height-1)/2)
  item.render(rl.Rectangle(0, 0, width, height))
  assert clicked.call_count == int(enabled)


@pytest.mark.parametrize("reason", ["mid", "full", "invalid", "stale", "staleDevice", "missingDevice"])
def test_priority_alert_or_stale_state_cancels_a_held_onroad_gesture(monkeypatch, paired, reason):
  display, _, sm = paired
  display.inputs([])
  old_epoch = display.epoch
  display.down = display.touch_active = True
  if reason in ("mid", "full"):
    sm["selfdriveState"].alertSize = reason
  elif reason == "invalid":
    sm.valid["selfdriveState"] = False
  elif reason == "stale":
    sm.logMonoTime["selfdriveState"] -= 1_000_000_000
  elif reason == "staleDevice":
    sm.logMonoTime["deviceState"] -= 4_000_000_000
  else:
    sm.valid["deviceState"] = False
  monkeypatch.setattr(display, "tick", lambda physical: [("up", .5, .5)])
  result = display.inputs([])
  assert display.mode == "waiting" and display.epoch != old_epoch
  assert len(result) == 1 and result[0].left_released and result[0].pos == MousePos(-1, -1)
  assert display.inputs([]) == [] and not display.touch_active
  sm.valid.update(dict.fromkeys(sm, True))
  sm.logMonoTime.update(dict.fromkeys(sm, time.monotonic_ns()))
  sm["selfdriveState"].alertSize = "none"
  assert display.inputs([]) == [] and display.mode == "road"


def test_park_to_drive_cannot_finish_previous_gesture(monkeypatch, paired):
  display, _, _ = paired
  display.mode = "park"
  display.down = display.touch_active = True
  monkeypatch.setattr(display, "tick", lambda physical: [("up", .5, .5)])
  result = display.inputs([])
  assert len(result) == 1 and result[0].pos == MousePos(-1, -1)
  assert display.mode == "road" and not display.down


def test_real_touch_during_remote_drag_takes_over_immediately(monkeypatch, paired):
  display, _, _ = paired
  display.inputs([])
  display.down = display.touch_active = True
  def revoke(physical):
    assert physical
    display.close()
    return [("cancel", -1., -1.)]
  monkeypatch.setattr(display, "tick", revoke)
  local = MouseEvent(MousePos(4, 12), 0, True, False, True, time.monotonic())
  result = display.inputs([local])
  assert len(result) == 2 and result[0].pos == MousePos(-1, -1) and result[1] == local
  assert not display.auth and not display.touch_active


def test_disconnect_cancels_press_even_without_more_packets(monkeypatch, paired):
  display, _, _ = paired
  display.inputs([])
  display.touch_active = True
  display.close()
  result = display.inputs([])
  assert len(result) == 1 and result[0].left_released and result[0].pos == MousePos(-1, -1)
