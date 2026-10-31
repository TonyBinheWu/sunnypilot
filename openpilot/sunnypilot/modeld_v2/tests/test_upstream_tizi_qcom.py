"""Check upstream QCOM startup on C3X and unchanged C4 Chestnut fallback."""
import unittest
from unittest import mock

import openpilot.sunnypilot.modeld_v2.modeld as modeld


class TestUpstreamQcomDeviceSplit(unittest.TestCase):
  def test_tizi_directly_loads_qcom_as_upstream(self):
    qcom = object()
    with (mock.patch.object(modeld.HARDWARE, "get_device_type", return_value="tizi"),
          mock.patch.object(modeld, "ModelState", return_value=qcom) as factory,
          mock.patch.object(modeld, "_load_qcom_fallback") as optional):
      self.assertIs(modeld._load_qcom_for_device(1928, 1208, big_model_ready=False), qcom)
      factory.assert_called_once_with(cam_w=1928, cam_h=1208, chestnut=False)
      optional.assert_not_called()

  def test_tizi_never_hides_qcom_failure_when_chestnut_is_ready(self):
    with (mock.patch.object(modeld.HARDWARE, "get_device_type", return_value="tizi"),
          mock.patch.object(modeld, "ModelState", side_effect=RuntimeError("QCOM startup failure")),
          mock.patch.object(modeld, "_load_qcom_fallback") as optional):
      with self.assertRaisesRegex(RuntimeError, "QCOM startup failure"):
        modeld._load_qcom_for_device(1928, 1208, big_model_ready=True)
      optional.assert_not_called()

  def test_mici_preserves_existing_optional_fallback(self):
    sentinel = object()
    with (mock.patch.object(modeld.HARDWARE, "get_device_type", return_value="mici"),
          mock.patch.object(modeld, "_load_qcom_fallback", return_value=sentinel) as existing,
          mock.patch.object(modeld, "ModelState") as factory):
      self.assertIs(modeld._load_qcom_for_device(1344, 760, big_model_ready=True), sentinel)
      existing.assert_called_once_with(1344, 760, True)
      factory.assert_not_called()

  def test_mici_keeps_optional_failure_semantics(self):
    with (mock.patch.object(modeld.HARDWARE, "get_device_type", return_value="mici"),
          mock.patch.object(modeld, "ModelState", side_effect=RuntimeError("QCOM missing")),
          mock.patch.object(modeld.cloudlog, "exception")):
      self.assertIsNone(modeld._load_qcom_for_device(1344, 760, big_model_ready=True))
      with self.assertRaisesRegex(RuntimeError, "QCOM missing"):
        modeld._load_qcom_for_device(1344, 760, big_model_ready=False)


if __name__ == "__main__":
  unittest.main(verbosity=2)
