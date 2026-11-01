"""Regression tests for optional QCOM fallback during Chestnut model startup."""
import unittest
from unittest import mock

import openpilot.sunnypilot.modeld_v2.modeld as modeld


class TestQcomFallback(unittest.TestCase):
  def test_success_keeps_qcom_fallback(self):
    fallback = object()
    with mock.patch.object(modeld, "ModelState", return_value=fallback) as factory:
      actual = modeld._load_qcom_fallback(1928, 1208, big_model_ready=True)
    self.assertIs(actual, fallback)
    factory.assert_called_once_with(cam_w=1928, cam_h=1208, chestnut=False)

  def test_missing_optional_qcom_does_not_crash_loaded_chestnut(self):
    with (mock.patch.object(modeld, "ModelState", side_effect=AssertionError("No driving pkl found for small model")),
          mock.patch.object(modeld.cloudlog, "exception") as logger):
      self.assertIsNone(modeld._load_qcom_fallback(1928, 1208, big_model_ready=True))
    self.assertTrue(logger.call_args.args[0].startswith("QCOM fallback unavailable"))

  def test_invalid_qcom_is_fatal_without_big_model(self):
    failure = RuntimeError("QCOM model incompatible")
    with (mock.patch.object(modeld, "ModelState", side_effect=failure),
          mock.patch.object(modeld.cloudlog, "exception") as logger):
      with self.assertRaisesRegex(RuntimeError, "QCOM model incompatible"):
        modeld._load_qcom_fallback(1928, 1208, big_model_ready=False)
    self.assertTrue("no Chestnut model" in logger.call_args.args[0])
