"""Render and check C3X/C4 update UI on a Linux host; no GPU/vehicle test."""
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import pyray as rl

from openpilot.common.basedir import BASEDIR
from openpilot.common.version import get_release_notes, get_version
from openpilot.system.updated.updated import parse_release_notes
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import multilang, tr


class TestDeviceUpdates(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    multilang.change_language("zh-CHT")
    gui_app.init_window("Device update compatibility")

  def test_ui_profile_and_hardware_identity(self):
    from openpilot.common.hardware.comma.hardware import get_device_type
    expected = os.environ["EXPECTED_DEVICE"]
    self.assertEqual(gui_app.big_ui(), expected == "tizi")
    for device in ("mici", "tizi"):
      get_device_type.cache_clear()
      with patch("builtins.open", unittest.mock.mock_open(read_data=f"comma {device}\x00")):
        self.assertEqual(get_device_type(), device)
      get_device_type.cache_clear()

  def test_version_and_utf8_notes_use_same_release(self):
    notes = get_release_notes()
    self.assertTrue(get_version() in notes.splitlines()[0])
    html = parse_release_notes(BASEDIR).decode("utf-8")
    self.assertTrue(get_version() in html and "C3X" in html and "C4" in html)
    self.assertEqual(tr("Update notes"), "更新項目")
    self.assertEqual(tr("Installed version notes"), "目前版本更新說明")

  def test_render_update_notes(self):
    description = f"{get_version()} / test-branch / abc1234 / Oct 31"
    notes = parse_release_notes(BASEDIR)
    params = Mock()
    params.get.side_effect = lambda key: description if key.endswith("Description") else notes
    params.get_bool.return_value = True
    state = SimpleNamespace(params=params, is_offroad=lambda: True, is_onroad=lambda: False, started=False)
    if gui_app.big_ui():
      from openpilot.selfdrive.ui.widgets.offroad_alerts import UpdateAlert
      view = UpdateAlert()
      view.params = params
      self.assertTrue(view.refresh())
      self.assertEqual(view.release_notes, notes.decode("utf-8").strip())
      def render():
        view._render_content(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
    else:
      from openpilot.selfdrive.ui.mici.layouts.settings import software
      with patch.object(software, "ui_state", state):
        button = software.ReleaseNotesButton(available=True)
        button._update_state()
        self.assertTrue(get_version() in button.get_value())
        with patch.object(gui_app, "push_widget") as push:
          button._show_notes()
        view = push.call_args.args[0]
      self.assertFalse(view._scroller._horizontal)
      labels = view._scroller._items
      self.assertTrue(any("C3X" in label._text for label in labels))
      self.assertTrue(any("C4" in label._text for label in labels))
      self.assertGreater(sum(label.rect.height for label in labels), gui_app.height)
      def render():
        view.render(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
    for _ in range(3):
      rl.begin_drawing()
      rl.clear_background(rl.BLACK)
      render()
      rl.end_drawing()
    screenshot = Path(f"update-notes-{os.environ['EXPECTED_DEVICE']}.png")
    rl.take_screenshot(str(screenshot))
    self.assertTrue(screenshot.is_file() and screenshot.stat().st_size > 0)


if __name__ == "__main__":
  unittest.main(verbosity=2)
