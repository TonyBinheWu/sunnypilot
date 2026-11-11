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
      from openpilot.sunnypilot.formosalink.ui import FormosaPairingDialog
      cloud = layout._panels[OP.PanelType.SUNNYLINK]
      self.assertEqual(cloud.name, "FormosaLink")
      self.assertIsInstance(cloud.instance, FormosaPairingDialog)
      device = layout._panels[OP.PanelType.DEVICE].instance
      self.assertNotIn(device._pair_device_btn, device._scroller._items)
      layout.set_current_panel(OP.PanelType.FORMOSAPILOT)
    else:
      from openpilot.selfdrive.ui.sunnypilot.mici.layouts.settings import SettingsLayoutSP
      layout = SettingsLayoutSP()
      self.assertTrue(any(getattr(item, "text", None) == "FormosaPilot" for item in layout._scroller._items))
      self.assertTrue(any(getattr(item, "text", None) == "FormosaLink" for item in layout._scroller._items))
      self.assertFalse(any("sunnylink" in str(getattr(item, "text", "")).lower() for item in layout._scroller._items))
      from openpilot.selfdrive.ui.sunnypilot.mici.layouts.settings import DeviceLayoutSP
      from openpilot.selfdrive.ui.mici.layouts.settings.device import PairBigButton
      self.assertFalse(any(isinstance(item, PairBigButton) for item in DeviceLayoutSP()._scroller._items))
      button = next(item for item in layout._scroller._items if getattr(item, "text", None) == "FormosaLink")
      with patch.object(ui.ui_state, "is_offroad", return_value=True), patch.object(gui_app, "push_widget") as push:
        button._click_callback()
        self.assertIsInstance(push.call_args.args[0], ui.FormosaPairingDialog)
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

  def test_product_wordmark_spinner_and_translated_text(self):
    from types import SimpleNamespace
    from openpilot.system.ui.lib.branding import LOGO_ASSET, display_text
    from openpilot.system.ui.lib.multilang import multilang, tr
    from openpilot.system.ui.lib.text_measure import measure_text_cached
    from openpilot.system.ui.widgets.label import UnifiedLabel
    from openpilot.system.ui.spinner import Spinner, TEXTURE_SIZE
    from openpilot.system.ui.sunnypilot.widgets.screen_saver import ScreenSaverSP
    from openpilot.system.ui.lib.application import FontWeight
    self.assertEqual(Spinner()._comma_texture.id, gui_app.texture(LOGO_ASSET, TEXTURE_SIZE, TEXTURE_SIZE).id)
    font = gui_app.font(FontWeight.NORMAL)
    for locale in ("zh-CHT", "en", "ja"):
      with patch.object(multilang, "_language", locale):
        self.assertNotIn("sunnypilot", tr("Enable sunnypilot").lower())
        self.assertEqual(UnifiedLabel("sunnypilot").text, "FormosaPilot")
        self.assertEqual(measure_text_cached(font, "sunnypilot", 30).x, measure_text_cached(font, "FormosaPilot", 30).x)
    saver = ScreenSaverSP()
    self.assertEqual(saver.text, "FormosaPilot")
    rl.begin_drawing()
    rl.clear_background(rl.BLACK)
    if gui_app.big_ui():
      from openpilot.selfdrive.ui.sunnypilot.layouts.home import HomeLayoutSP
      header = SimpleNamespace(header_rect=rl.Rectangle(20, 20, gui_app.width-40, 120), update_available=False,
                               alert_count=0, params=SimpleNamespace(get=lambda _:"hkg-enhanced / DEMO"))
      HomeLayoutSP._render_header(header)
    else:
      from openpilot.selfdrive.ui.sunnypilot.mici.layouts.home import MiciHomeLayoutSP
      from openpilot.system.ui.widgets.branding import FormosaWordmark
      home = MiciHomeLayoutSP()
      self.assertIsInstance(home._openpilot_label, FormosaWordmark)
      home._openpilot_label.render(rl.Rectangle(16, 10, 480, 80))
    rl.end_drawing()
    output = Path(os.environ.get("FORMOSALINK_QR_OUTPUT", "build/native-brand"))
    image = rl.load_image_from_screen()
    try:
      self.assertTrue(rl.export_image(image, str(output / "home-wordmark.png")))
    finally:
      rl.unload_image(image)
