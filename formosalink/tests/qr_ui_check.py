"""Explicit native C3X/C4 QR UI integration suite; not a host pytest module."""
import os
import time
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pyray as rl
from PIL import Image

from openpilot.common.qrcode import decode
from openpilot.sunnypilot.formosalink.pairing import pairing_url
from openpilot.sunnypilot.formosalink import ui
from openpilot.system.ui.lib.application import gui_app


class FakeParams:
  def __init__(self):
    self.enabled = False

  def get_bool(self, key):
    return self.enabled if key == "FormosaLinkEnabled" else False

  def put_bool(self, key, value, block=False):
    assert key in ("FormosaLinkEnabled", "FormosaLinkRemoteSettings"), "QR UI must not write driving parameters"
    self.enabled = value


class TestQRScreen(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_HIDDEN)
    gui_app.init_window("FormosaLink QR profile test")

  @classmethod
  def tearDownClass(cls):
    gui_app.close()

  def setUp(self):
    self.params = FakeParams()
    self.params_patch = patch.object(ui.ui_state, "params", self.params)
    self.offroad_patch = patch.object(ui.ui_state, "is_offroad", return_value=True)
    self.params_patch.start()
    self.offroad = self.offroad_patch.start()
    self.addCleanup(self.params_patch.stop)
    self.addCleanup(self.offroad_patch.stop)

  def pending(self, dialog):
    result = {"state":"pending","pair_code":"A1B2C3D4E5F6","fingerprint":"a"*24,"expires_at":time.time()+600}
    result["url"] = pairing_url("https://formosapilot.dinglu-t.com",result)
    dialog._events.put((dialog._generation,"enroll",result))
    dialog._update_state()
    self.addCleanup(dialog.hide_event)
    return result["url"]

  def test_native_qr_decodes_on_all_three_languages(self):
    output = Path(os.environ.get("FORMOSALINK_QR_OUTPUT","build/formosalink-qr-native"))
    output.mkdir(parents=True,exist_ok=True)
    for code in ("zh-CHT","en","ja"):
      with self.subTest(language=code), patch.object(ui.multilang,"_language",code):
        dialog = ui.FormosaPairingDialog()
        url = self.pending(dialog)
        rect = rl.Rectangle(0,0,gui_app.width,gui_app.height)
        for _ in range(2):
          rl.begin_drawing()
          dialog.render(rect)
          rl.end_drawing()
        qr = dialog._last_qr_rect
        self.assertGreaterEqual(qr.height, rect.height*.7)
        self.assertGreaterEqual(qr.x,0)
        self.assertGreaterEqual(qr.y,0)
        self.assertLessEqual(qr.x+qr.width,rect.width)
        self.assertLessEqual(qr.y+qr.height,rect.height)
        path = output / (code + ".png")
        screen = rl.load_image_from_screen()
        try:
          self.assertTrue(rl.export_image(screen,str(path.resolve())))
        finally:
          rl.unload_image(screen)
        image = np.asarray(Image.open(path).convert("L"))
        # Render output is decoded, rather than the source QR matrix.
        crop = image[int(qr.y):int(qr.y+qr.height),int(qr.x):int(qr.x+qr.width)]
        self.assertEqual(decode(crop),url)
        dialog.hide_event()

  def test_onroad_cannot_enroll_or_enable(self):
    # Exercise each profile's actual settings-entry constructor as well.
    if gui_app.big_ui():
      self.assertIsNotNone(ui.formosalink_button())
    else:
      entries=[]
      ui.add_mici_pair_button(SimpleNamespace(add_widget=entries.append))
      self.assertEqual(entries[0].text,"FormosaLink")
    dialog = ui.FormosaPairingDialog()
    self.offroad.return_value = False
    with patch.object(ui,"request_pairing") as request:
      dialog._request()
      dialog._worker("enroll")
      dialog._events.put((0,"enroll",{"state":"paired"}))
      dialog._update_state()
      request.assert_not_called()
    self.assertFalse(self.params.enabled)
    self.assertEqual(dialog._state,"offroad")

  def test_responsive_controls_and_status_fit(self):
    # Include a nonzero origin, as when a host supplies a panel rather than the
    # entire screen. Verify real font measurements, not just layout constants.
    rect = rl.Rectangle(8, 4, gui_app.width-16, gui_app.height-8)
    scale = min(rect.width/536, rect.height/240)
    for code in ("zh-CHT", "en", "ja"):
      with patch.object(ui.multilang, "_language", code):
        dialog = ui.FormosaPairingDialog()
        self.pending(dialog)
        for state in ("pending", "paired", "error", "intro", "revoked", "expired", "disabled", "offroad", "loading"):
          if state == "intro":
            dialog._clear_qr()
          dialog._state = state
          rl.begin_drawing()
          dialog.render(rect)
          rl.end_drawing()
          with self.subTest(language=code, state=state):
            status = dialog._last_status_rect
            self.assertLessEqual(status.x+status.width, rect.x+rect.width)
            self.assertLessEqual(status.y+status.height, dialog._remote.rect.y-3*scale)
            for button in (dialog._remote, dialog._start, dialog._close):
              bounds = button.rect
              self.assertGreaterEqual(bounds.x, rect.x)
              self.assertGreaterEqual(bounds.y, rect.y)
              self.assertLessEqual(bounds.x+bounds.width, rect.x+rect.width)
              self.assertLessEqual(bounds.y+bounds.height, rect.y+rect.height)
              self.assertGreaterEqual(bounds.height, 33*scale)
              self.assertGreaterEqual(button._label._font_size, 16*scale)
            qr = dialog._last_qr_rect
            if qr:
              self.assertGreater(qr.x, dialog._start.rect.x+dialog._start.rect.width)
        dialog.hide_event()

  def test_closed_dialog_ignores_late_pair_result(self):
    dialog = ui.FormosaPairingDialog()
    dialog.hide_event()
    dialog._events.put((0,"enroll",{"state":"paired"}))
    dialog._update_state()
    self.assertFalse(self.params.enabled)

  def test_embedded_panel_can_be_opened_again_without_accepting_old_results(self):
    dialog = ui.FormosaPairingDialog(embedded=True)
    previous = dialog._generation
    dialog.hide_event()
    dialog.show_event()
    self.assertTrue(dialog._active)
    self.assertEqual(dialog._state, "intro")
    dialog._events.put((previous, "enroll", {"state":"paired"}))
    dialog._update_state()
    self.assertFalse(self.params.enabled)
    with patch.object(dialog, "_worker") as worker:
      dialog._request()
      worker.assert_called_once_with("enroll")
    dialog.hide_event()

  def test_local_disable_wins_over_old_result_and_revoke_disables(self):
    dialog = ui.FormosaPairingDialog()
    self.pending(dialog)
    self.assertTrue(self.params.enabled)
    old = dialog._generation
    dialog._disable_monitoring()
    dialog._events.put((old,"status",{"state":"paired"}))
    dialog._update_state()
    self.assertFalse(self.params.enabled)
    dialog._events.put((dialog._generation,"status",{"state":"paired"}))
    dialog._update_state()
    self.assertTrue(self.params.enabled)
    dialog._events.put((dialog._generation,"status",{"state":"revoked"}))
    dialog._update_state()
    self.assertFalse(self.params.enabled)


if __name__ == "__main__":
  unittest.main(verbosity=2)
