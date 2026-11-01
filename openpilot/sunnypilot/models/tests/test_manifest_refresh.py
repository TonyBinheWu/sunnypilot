import unittest
from unittest.mock import Mock, patch

from openpilot.sunnypilot.models.fetcher import ModelCache, ModelFetcher


class TestManifestRefresh(unittest.TestCase):
  def test_monotonic_clock_reset_expires_cache(self):
    params = Mock()
    params.get.return_value = 20_000_000_000
    cache = ModelCache(params)
    with patch("openpilot.sunnypilot.models.fetcher.time.monotonic", return_value=10):
      self.assertTrue(cache._is_expired())

  def test_current_timestamp_keeps_cache(self):
    params = Mock()
    params.get.return_value = 3_000_000_000
    cache = ModelCache(params)
    with patch("openpilot.sunnypilot.models.fetcher.time.monotonic", return_value=4):
      self.assertFalse(cache._is_expired())

  def test_catalog_url_change_forces_new_fetch(self):
    params = Mock()
    params.get.return_value = {"qcom": "old", "chestnut": "old"}
    ModelFetcher(params)
    writes = [call.args[:2] for call in params.put.call_args_list]
    self.assertTrue(("ModelManager_LastSyncTime", 0) in writes)
    self.assertTrue(("ModelManager_LastSyncTime_Chestnut", 0) in writes)

  def test_same_catalog_urls_do_not_force_new_fetch(self):
    params = Mock()
    params.get.return_value = {
      "qcom": ModelFetcher.MODEL_URL,
      "chestnut": ModelFetcher.MODEL_URL_CHESTNUT,
    }
    ModelFetcher(params)
    sync_keys = {"ModelManager_LastSyncTime", "ModelManager_LastSyncTime_Chestnut"}
    self.assertFalse(any(call.args[0] in sync_keys for call in params.put.call_args_list))


if __name__ == "__main__":
  unittest.main()
