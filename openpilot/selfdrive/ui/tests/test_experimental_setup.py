from types import SimpleNamespace

import pytest

from opendbc.car.hyundai.values import HyundaiFlags
from openpilot.selfdrive.ui.layouts.settings import experimental_setup as setup


@pytest.mark.parametrize("release,offroad,camera,passive,brand,alpha,expect", [
  (False, True, 0, False, "hyundai", False, True),  # manual HDA2 needs a firmware query
  (False, True, 3, False, "hyundai", True, True),  # verify wiring; vehicle interface keeps stock cruise
  (False, True, 0, False, "toyota", True, True),
  (False, True, 0, False, "toyota", False, False),
  (True, True, 0, False, "hyundai", True, False),
  (False, False, 0, False, "hyundai", True, False),
  (False, True, 0, True, "hyundai", True, False),
  (False, True, 0, False, "mock", False, False),
])
def test_auto_setup_only_records_per_vehicle_consent(monkeypatch, release, offroad, camera, passive, brand, alpha, expect):
  monkeypatch.setattr(setup, "tr", lambda text: text)
  values = {}
  cp = SimpleNamespace(brand=brand, carFingerprint="test car", passive=passive, dashcamOnly=False,
                       openpilotLongitudinalControl=False, alphaLongitudinalAvailable=alpha,
                       flags=HyundaiFlags.CANFD, fingerprintSource="fixed", carFw=[])
  params = SimpleNamespace(get=values.get, put=values.__setitem__, remove=values.pop, get_int=lambda key: camera)
  ui = SimpleNamespace(CP=cp, params=params, is_release=release, is_offroad=lambda: offroad)
  setup.set_auto_setup(True, ui)
  assert values == ({"AutoExperimentalPlatform": cp.carFingerprint} if expect else {})
  ui.CP = None
  setup.set_auto_setup(False, ui)
  assert not values


@pytest.mark.parametrize("brand,platform", [("mock", "MOCK"), ("hyundai", "KIA_EV6")])
def test_retry_detected_ev6_only_records_request(monkeypatch, brand, platform):
  monkeypatch.setattr(setup, "tr", lambda text: text)
  values = {"CarSelected3": "AUTO", "CarName": platform, "AutoCarModelResult": "KIA_EV6"}
  params = SimpleNamespace(get=values.get, put=values.__setitem__, get_int=lambda key: 0)
  cp = SimpleNamespace(brand=brand, carFingerprint=platform, dashcamOnly=False, passive=False, openpilotLongitudinalControl=False,
                       alphaLongitudinalAvailable=False, fingerprintSource="fw", flags=HyundaiFlags.CANFD)
  ui = SimpleNamespace(CP=cp, params=params, is_release=False, is_offroad=lambda: True)
  setup.set_auto_setup(True, ui)
  assert values == {"CarSelected3": "AUTO", "CarName": platform, "AutoCarModelResult": "KIA_EV6", "AutoExperimentalPlatform": "KIA_EV6"}
