from types import SimpleNamespace

import pytest

from opendbc.car import car_helpers
from opendbc.car.structs import CarParams
from opendbc.car.vin import VIN_UNKNOWN


def test_skip_fw_query_keeps_can_fingerprint(monkeypatch):
  fingerprint = {0: {0x123: 8}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}}
  obd_multiplexing = []

  def unexpected_query(*args, **kwargs):
    raise AssertionError("active vehicle query was called")

  monkeypatch.setattr(car_helpers, "get_vin", unexpected_query)
  monkeypatch.setattr(car_helpers, "get_present_ecus", unexpected_query)
  monkeypatch.setattr(car_helpers, "get_fw_versions_ordered", unexpected_query)
  monkeypatch.setattr(car_helpers, "get_fw_versions", unexpected_query)
  monkeypatch.setattr(car_helpers, "can_fingerprint", lambda can_recv: (None, fingerprint))

  result = car_helpers.fingerprint(lambda **kwargs: [], lambda msg: None, obd_multiplexing.append, 1, None, skip_fw_query=True, verify_ev6=True)

  assert result[1] == fingerprint
  assert result[2] == VIN_UNKNOWN
  assert result[3] == []
  assert obd_multiplexing == [False]


@pytest.mark.parametrize(("forced_candidate", "expected_candidate", "expected_skip", "expected_source"), [
  ("FORCED_CAR", "FORCED_CAR", True, CarParams.FingerprintSource.fixed),
  (None, "AUTO_CAR", False, CarParams.FingerprintSource.can),
])
def test_only_valid_manual_selection_skips_fw_query(monkeypatch, forced_candidate, expected_candidate, expected_skip, expected_source):
  fingerprint = {0: {0x123: 8}}
  fingerprint_args = {}

  class FakeParams:
    def get(self, key):
      return "Selected Car" if key == "CarSelected3" else ""

    def put(self, key, value):
      pass

  class FakeCarInterface:
    @staticmethod
    def get_params(candidate, fingerprints, car_fw, alpha_long_allowed, is_release, docs):
      return SimpleNamespace(carFingerprint=candidate)

    def __init__(self, CP):
      self.CP = CP

  def fake_fingerprint(*args, **kwargs):
    fingerprint_args.update(kwargs)
    return "AUTO_CAR", fingerprint, VIN_UNKNOWN, [], CarParams.FingerprintSource.can, True

  monkeypatch.setattr(car_helpers, "Params", FakeParams)
  monkeypatch.setattr(car_helpers, "get_selected_car_platform", lambda selected_car: forced_candidate)
  monkeypatch.setattr(car_helpers, "fingerprint", fake_fingerprint)
  monkeypatch.setattr(car_helpers, "interfaces", {"FORCED_CAR": FakeCarInterface, "AUTO_CAR": FakeCarInterface})

  CI = car_helpers.get_car(lambda **kwargs: [], lambda msg: None, lambda enabled: None, False, False)

  assert fingerprint_args["skip_fw_query"] is expected_skip
  assert CI.CP.carFingerprint == expected_candidate
  assert CI.CP.fingerprintSource == expected_source
  assert CI.CP.carFw == []
  assert CI.CP.carVin == VIN_UNKNOWN


@pytest.mark.parametrize("detected,source,exact,release,wanted,expect_alpha", [
  ("CAR", "fw", True, False, "CAR", True),
  ("CAR", "can", True, False, "CAR", True),
  ("OTHER", "fw", True, False, "MOCK", False),
  ("CAR", "fw", False, False, "MOCK", False),
  ("CAR", "fixed", True, False, "MOCK", False),
  (None, "can", True, False, "MOCK", False),
  ("CAR", "fw", True, True, "CAR", False),
])
def test_vehicle_scoped_alpha_identification(monkeypatch, detected, source, exact, release, wanted, expect_alpha):
  class Params:
    def get(self, key):
      return {"CarSelected3": "Selected car", "AutoExperimentalPlatform": "CAR"}.get(key)

    def get_bool(self, key):
      assert key == "IsReleaseBranch"
      return release

    def put(self, key, value):
      pass

  cached = object()
  def fingerprint(*args, skip_fw_query, verify_ev6):
    assert not verify_ev6
    assert args[-1] is (cached if release else None)
    assert skip_fw_query == release
    return detected, {}, VIN_UNKNOWN, [], getattr(CarParams.FingerprintSource, source), exact

  class Interface:
    @staticmethod
    def get_params(platform, fp, fw, alpha, is_release, docs):
      assert alpha == expect_alpha
      return SimpleNamespace(carFingerprint=platform, brand="test")

    def __init__(self, cp):
      self.CP = cp

  monkeypatch.setattr(car_helpers, "Params", Params)
  monkeypatch.setattr(car_helpers, "fingerprint", fingerprint)
  monkeypatch.setattr(car_helpers, "get_selected_car_platform", lambda name: "CAR")
  monkeypatch.setattr(car_helpers, "interfaces", {"CAR": Interface, "MOCK": Interface})
  assert car_helpers.get_car(None, None, None, False, True, cached_params=cached).CP.carFingerprint == wanted
