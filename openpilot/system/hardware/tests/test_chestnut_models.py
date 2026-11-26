import pickle
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from openpilot.common.hardware.usb import CHESTNUT_USB_IDS, CHESTNUT_USB_PRODUCT
from openpilot.common.params import Params
from openpilot.selfdrive.modeld import helpers as stock
from openpilot.sunnypilot.modeld_v2 import artifacts
from openpilot.sunnypilot.modeld_v2.helpers import write_bundle
from openpilot.sunnypilot.models.helpers import ACTIVE_BUNDLE_KEYS, REQUIRED_JSON_VERSION
from openpilot.system.hardware.chestnut.status import ChestnutStatus


class TestChestnutModels(unittest.TestCase):
  def setUp(self):
    self.tmp = self.enterContext(tempfile.TemporaryDirectory())
    self.root = Path(self.tmp)
    self.params = Params(str(self.root / "params"))
    self.status = ChestnutStatus(self.params)
    self.enterContext(patch.object(stock, "MODELS_DIR", self.root))
    self.warps = self.root / "selector"
    self.warps.mkdir()
    self.enterContext(patch.object(artifacts, "MODELS_DIR", self.warps))
    self.enterContext(patch("openpilot.common.hardware.hw.Paths.model_root", return_value=self.tmp))
    self.enterContext(patch("openpilot.system.hardware.chestnut.status.get_build_metadata", return_value=SimpleNamespace(channel="ccnc-port")))
    self.enterContext(patch.dict("os.environ", COMBINED_MODEL_PKL=""))
    self.vendor, self.product = CHESTNUT_USB_IDS[0]
    self.pointer = b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"0" * 64 + b"\nsize 900000\n"

  def warning(self, *, offroad=True, usb=True, fw_product=CHESTNUT_USB_PRODUCT):
    device = {"vendorId": self.vendor, "productId": self.product, "product": fw_product, "speedMbps": 5000}
    alerts = {}
    self.status.update(offroad, "ccnc-port", [device] if usb else [], False, False, None, None,
                       lambda key, active, *_: alerts.update({key: active}))
    return alerts["Offroad_ChestnutUncompiled"]

  def install_stock(self):
    opcodes = pickle.dumps({"run": None})
    model = stock.modeld_pkl_path(True)
    model.write_bytes(len(opcodes).to_bytes(8, "little") + opcodes + b"weights")
    for w, h in stock.CHESTNUT_CAMERA_SIZES:
      (self.root / f"big_driving_warp_{w}x{h}_tinygrad.pkl").write_bytes(opcodes)
    return model

  def test_stock_update_and_incomplete_files(self):
    self.assertTrue(self.warning())
    self.assertFalse(self.warning(usb=False))
    self.assertFalse(self.warning(fw_product="bootloader"))
    self.assertFalse(self.warning(offroad=False))
    model = self.install_stock()
    self.assertFalse(self.warning())
    for w, h in stock.CHESTNUT_CAMERA_SIZES:
      warp = self.root / f"big_driving_warp_{w}x{h}_tinygrad.pkl"
      warp.unlink()
      self.assertTrue(self.warning())
      warp.write_bytes(self.pointer)
      self.assertTrue(self.warning())
      self.install_stock()
    model.write_bytes(self.pointer)
    self.assertTrue(self.warning())

  def test_selected_chestnut_bundle_and_qcom_slot(self):
    path = self.root / "selected.pkl"
    bundle = {"minimumSelectorVersion": REQUIRED_JSON_VERSION, "runner": "tinygrad", "models": [{"artifact": {"fileName": path.name}}]}
    self.params.put(ACTIVE_BUNDLE_KEYS["qcom"], bundle, block=True)
    write_bundle(str(path), {"run": ({}, b"")})
    self.assertTrue(self.warning())
    self.params.put(ACTIVE_BUNDLE_KEYS["chestnut"], bundle, block=True)
    self.install_stock()
    self.assertTrue(self.warning())  # selected native model still needs its own warp format
    for w, h in stock.CHESTNUT_CAMERA_SIZES:
      write_bundle(str(self.warps / f"big_driving_warp_{w}x{h}_tinygrad.pkl"), {"run": ({}, b"")})
    self.assertFalse(self.warning())
    path.write_bytes(self.pointer)
    self.assertTrue(self.warning())
    path.unlink()
    self.assertTrue(self.warning())
    self.params.remove(ACTIVE_BUNDLE_KEYS["chestnut"])
    self.assertFalse(self.warning())

  def test_legacy_selected_model_can_supply_its_own_warps(self):
    path = self.root / "legacy.pkl"
    bundle = {"minimumSelectorVersion": REQUIRED_JSON_VERSION, "runner": "tinygrad", "models": [{"artifact": {"fileName": path.name}}]}
    self.params.put(ACTIVE_BUNDLE_KEYS["chestnut"], bundle, block=True)
    parts = {size: ({}, b"") for size in stock.CHESTNUT_CAMERA_SIZES}
    write_bundle(str(path), parts)
    self.assertFalse(self.warning())
    parts.pop(stock.CHESTNUT_CAMERA_SIZES[0])
    write_bundle(str(path), parts)
    self.assertTrue(self.warning())
