from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from opendbc.car import car_helpers as helpers
from openpilot.common.driving_planner import active_planner_mode


@pytest.mark.parametrize("case,provider,calls", [
  ("supported", "alpha", [False, True]), ("native", "native", [False]),
  ("no_support", "stock", [False]), ("declined", "stock", [False, True]),
  ("fuzzy", "stock", [False]), ("fixed", "stock", [False]), ("dashcam", "stock", [False]),
  ("release", "stock", [False]), ("stock_request", "stock", [False]), ("disabled", "stock", [False]),
  ("excluded", "stock", [False]),
])
def test_auto_setup(monkeypatch, case, provider, calls):
  candidate = next(iter(helpers.UNSUPPORTED_LONGITUDINAL_CAR)) if case == "excluded" else "TEST"
  params = Mock()
  params.get.return_value = ""
  params.get_bool.side_effect = {"IsReleaseBranch": case == "release", "OpenpilotEnabledToggle": case != "disabled"}.__getitem__
  params.get_int.return_value = 3 if case == "stock_request" else 0
  monkeypatch.setattr(helpers, "Params", lambda: params)
  source = helpers.CarParams.FingerprintSource.fixed if case == "fixed" else helpers.CarParams.FingerprintSource.fw
  monkeypatch.setattr(helpers, "fingerprint", lambda *a, **kw: (candidate, {}, "", [], source, case != "fuzzy"))
  requested = []

  def get_params(candidate, fingerprint, fw, alpha, release, docs):
    requested.append(alpha)
    return SimpleNamespace(carFingerprint=candidate, brand="hyundai", alphaLongitudinalAvailable=case != "no_support",
                           dashcamOnly=case == "dashcam", openpilotLongitudinalControl=case == "native" or (alpha and case != "declined"))

  interface = Mock(side_effect=lambda cp: cp)
  interface.get_params = get_params
  monkeypatch.setitem(helpers.interfaces, candidate, interface)
  cp = helpers.get_car(None, None, None, True, True, auto_long=True)
  assert cp.visionPlannerSetup == provider
  assert requested == calls


@pytest.mark.parametrize("saved_mode", [-1, 0, 1, 2, 3, 4, 99])
def test_trip_always_uses_blended_planning(saved_mode):
  params = Mock()
  assert active_planner_mode(SimpleNamespace(drivingPlannerMode=saved_mode), params) == 4
  params.get_int.assert_not_called()
