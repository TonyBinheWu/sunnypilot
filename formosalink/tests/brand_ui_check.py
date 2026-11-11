"""Render the real native brand panel and verify the pairing safety boundary."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import pyray as rl
from openpilot.system.ui.lib.application import gui_app
from openpilot.sunnypilot.formosalink import brand_ui, ui


class TestNativeBrand(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_HIDDEN)
    gui_app.init_window("FormosaPilot native brand")

  @classmethod
  def tearDownClass(cls):
    gui_app.close()

  def test_logo_and_three_languages(self):
    output = Path(os.environ.get("FORMOSALINK_QR_OUTPUT", "build/native-brand"))
    output.mkdir(parents=True, exist_ok=True)
    panel = brand_ui.FormosaPilotPanel(embedded=gui_app.big_ui())
    self.assertGreater(panel.logo.id, 0)
    self.assertNotEqual(panel.branch, "unknown")
    for lang in ("zh-CHT", "en", "ja"):
      with patch.object(ui.multilang, "_language", lang):
        for _ in range(2):
          rl.begin_drawing()
          panel.render(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
          rl.end_drawing()
        image = rl.load_image_from_screen()
        try:
          self.assertTrue(rl.export_image(image, str(output / f"brand-{lang}.png")))
        finally:
          rl.unload_image(image)

  def test_pairing_guard_and_no_writes(self):
    with patch.object(ui.ui_state, "is_offroad", return_value=False), patch.object(ui.gui_app, "push_widget") as push:
      panel = brand_ui.FormosaPilotPanel()
      self.assertFalse(panel._pair.enabled)
      ui.open_pairing()
      push.assert_not_called()

  def test_native_top_level_entry(self):
    if gui_app.big_ui():
      from openpilot.selfdrive.ui.sunnypilot.layouts.settings.settings import SettingsLayoutSP, OP
      layout = SettingsLayoutSP()
      self.assertIsInstance(layout._panels[OP.PanelType.FORMOSAPILOT].instance, brand_ui.FormosaPilotPanel)
      self.assertEqual(next(iter(layout._panels)), OP.PanelType.FORMOSAPILOT)
      layout.set_current_panel(OP.PanelType.FORMOSAPILOT)
    else:
      from openpilot.selfdrive.ui.sunnypilot.mici.layouts.settings import SettingsLayoutSP
      layout = SettingsLayoutSP()
      self.assertTrue(any(getattr(item, "text", None) == "FormosaPilot" for item in layout._scroller._items))
    output = Path(os.environ.get("FORMOSALINK_QR_OUTPUT", "build/native-brand"))
    output.mkdir(parents=True, exist_ok=True)
    with patch.object(ui.multilang, "_language", "zh-CHT"), patch.object(ui.ui_state, "always_offroad", False, create=True):
      for _ in range(2):
        rl.begin_drawing()
        layout.render(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
        rl.end_drawing()
      image = rl.load_image_from_screen()
      try:
        self.assertTrue(rl.export_image(image, str(output / "settings-brand.png")))
      finally:
        rl.unload_image(image)
