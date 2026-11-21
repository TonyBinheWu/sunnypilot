"""Sorento non-HDA-II catalog port from TonyBinheWu/opendbc@2a565d34.

Firmware evidence is from the source database, not a claim of road acceptance
or support for the separate 2025 HEV/HDA-II variants.
"""
import importlib.util
from pathlib import Path
import tomllib

import pytest

from opendbc.car import Bus, STD_CARGO_KG, gen_empty_fingerprint
from opendbc.car.hyundai.fingerprints import FW_VERSIONS
from opendbc.car.hyundai.values import CAR, CANFD_CAR, CANFD_FUZZY_WHITELIST, CarControllerParams, HyundaiFlags, get_platform_codes
from opendbc.car.selected_car import get_selected_car_platform
from opendbc.car.structs import CarParams


def test_manual_selection_keeps_sorento_variants_distinct():
  name = "Kia Sorento (without HDA II) 2024-25"
  assert get_selected_car_platform(name) == CAR.KIA_SORENTO_2024
  doc = CAR.KIA_SORENTO_2024.config.car_docs[0]
  assert doc.year_list == ["2024", "2025"]
  assert CAR.KIA_SORENTO_2024 in CANFD_CAR
  assert CAR.KIA_SORENTO_2024.config.dbc_dict[Bus.pt] == "hyundai_canfd_generated"
  assert get_selected_car_platform("Kia Sorento 2021-23") == CAR.KIA_SORENTO_4TH_GEN
  assert get_selected_car_platform("Kia Sorento Hybrid 2021-23") == CAR.KIA_SORENTO_HEV_4TH_GEN
  assert get_selected_car_platform("Kia Sorento Hybrid 2025") is None


def test_remote_web_exposes_the_same_selection(monkeypatch):
  # Import the actual catalog endpoint without unrelated hardware/upload routes.
  path = Path(__file__).resolve().parents[5]/"openpilot/selfdrive/carrot/server/features/cars.py"
  spec = importlib.util.spec_from_file_location("sorento_web_car_catalog", path)
  cars = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(cars)

  monkeypatch.setattr(cars.glob, "glob", lambda _: [])
  _, makers = cars.load_supported_cars()
  assert "Kia Sorento (without HDA II) 2024-25" in makers["Kia"]
  assert "Kia Sorento Hybrid 2021-23" in makers["Kia"]


def test_firmware_evidence_is_separate_from_old_sorento_and_hev():
  ecus = FW_VERSIONS[CAR.KIA_SORENTO_2024]
  assert set(ecus) == {(CarParams.Ecu.fwdCamera, 0x7c4, None), (CarParams.Ecu.fwdRadar, 0x7d0, None)}
  versions = {fw for values in ecus.values() for fw in values}
  assert len(versions) == 4
  for older in (CAR.KIA_SORENTO_4TH_GEN, CAR.KIA_SORENTO_HEV_4TH_GEN):
    assert versions.isdisjoint(fw for values in FW_VERSIONS[older].values() for fw in values)
  camera = ecus[(CarParams.Ecu.fwdCamera, 0x7c4, None)]
  assert {date for _, date in get_platform_codes(camera)} == {b"231127"}
  assert all(b"MQ4 " in fw and b"MQ4H" not in fw for fw in camera)
  # Keep the source port's conservative CAN-FD fuzzy matching policy.
  assert CAR.KIA_SORENTO_2024 not in CANFD_FUZZY_WHITELIST


def test_port_has_source_torque_baseline_without_duplicate_mapping():
  root = Path(__file__).resolve().parents[2]/"torque_data"
  tables = [tomllib.loads((root/name).read_text()) for name in ("params.toml", "substitute.toml", "override.toml")]
  assert sum("KIA_SORENTO_2024" in table for table in tables) == 1
  assert tables[2]["KIA_SORENTO_2024"] == [2.5, 2.5, 0.1]


@pytest.mark.parametrize("variant", [0, 1])
def test_firmware_exact_match_identifies_new_platform_only(variant):
  from opendbc.car.fw_versions import match_fw_to_car_exact

  live = {ecu[1:]: {versions[variant]} for ecu, versions in FW_VERSIONS[CAR.KIA_SORENTO_2024].items()}
  assert match_fw_to_car_exact(live, match_brand="hyundai", log=False) == {CAR.KIA_SORENTO_2024}
  live[(0x7c4, None)] = {b"unknown camera firmware"}
  assert CAR.KIA_SORENTO_2024 not in match_fw_to_car_exact(live, match_brand="hyundai", log=False)


@pytest.mark.parametrize("angle", [False, True])
@pytest.mark.parametrize("alpha_long", [False, True])
@pytest.mark.parametrize("camera_scc", [0, 1])
def test_interface_uses_existing_capability_and_safety_paths(monkeypatch, angle, alpha_long, camera_scc):
  from opendbc.car import interfaces
  from opendbc.car.hyundai import interface, hyundaicanfd

  fingerprint = gen_empty_fingerprint()
  fingerprint[0] = {0x1cf: 8, 0x40: 32}
  if angle:
    fingerprint[2][0xcb] = 24
  values = {"HyundaiCameraSCC": camera_scc, "CanfdHDA2": 0, "FingerPrints": repr(fingerprint)}

  class Params:
    def get_int(self, key): return int(values.get(key, 0))
    def get_bool(self, key): return bool(values.get(key, False))
    def get(self, key): return values.get(key, "")
    def put_bool(self, key, value): pass

  for module in (interface, interfaces, hyundaicanfd):
    monkeypatch.setattr(module, "Params", Params)
  cp = interface.CarInterface.get_params(CAR.KIA_SORENTO_2024, fingerprint, [], alpha_long, False, False)
  assert cp.mass == pytest.approx(1794.86500809 + STD_CARGO_KG)
  assert cp.wheelbase == pytest.approx(2.81)
  assert cp.steerRatio == pytest.approx(13.5)
  assert cp.steerActuatorDelay == pytest.approx(0.1)
  assert cp.steerLimitTimer == pytest.approx(0.4)
  limits = CarControllerParams(cp)
  assert (limits.STEER_MAX, limits.STEER_DELTA_UP, limits.STEER_DELTA_DOWN) == (270, 2, 3)
  assert not cp.flags & (HyundaiFlags.CANFD_HDA2 | HyundaiFlags.HYBRID | HyundaiFlags.EV)
  assert cp.safetyConfigs[-1].safetyModel == CarParams.SafetyModel.hyundaiCanfd
  assert cp.openpilotLongitudinalControl == bool(alpha_long or camera_scc)
  assert bool(cp.flags & HyundaiFlags.CAMERA_SCC) == bool(camera_scc)
  assert bool(cp.flags & HyundaiFlags.ANGLE_CONTROL) == angle
  assert interfaces.get_torque_params()[CAR.KIA_SORENTO_2024] == interfaces.get_torque_params()[CAR.KIA_SORENTO_4TH_GEN]


@pytest.mark.parametrize("model,camera,angle,active_gain,inactive_gain", [
  (CAR.KIA_SORENTO_2024, True, False, 100, 100),
  (CAR.KIA_SORENTO_2024, False, False, 100, 100),
  (CAR.KIA_SORENTO_2024, True, True, 43, 43),
  (CAR.KIA_EV6, True, False, 0, 100),
])
def test_lfa_rack_damping(monkeypatch, model, camera, angle, active_gain, inactive_gain):
  from opendbc.car.hyundai.tests.test_steering_handover_controller import setup_controller, step

  flags = HyundaiFlags.CANFD
  if camera:
    flags |= HyundaiFlags.CAMERA_SCC
  if angle:
    flags |= HyundaiFlags.ANGLE_CONTROL
  specs = model.config.specs
  cp = CarParams(brand="hyundai", carFingerprint=model, flags=int(flags), steerControlType="angle" if angle else "torque",
                 wheelbase=specs.wheelbase, steerRatio=specs.steerRatio)
  controller, cs, cc, _ = setup_controller(monkeypatch, angle=angle, camera=camera, cp_override=cp)
  cs.lfa = {"DampingGain": 43}
  cs.out.steeringPressed = False
  cs.out.steeringTorque = 0
  cc.actuators.torque = 0.4
  for active, expected in ((True, active_gain), (False, inactive_gain)):
    cc.latActive = active
    _, messages = step(controller, cs, cc)
    data, = [data for addr, data, bus in messages if addr == 0x12A and bus == controller.CAN.ECAN]
    # ccNC's LFA Damping_Gain and carrot's DampingGain both occupy byte 13.
    assert data[13] == expected
    assert bool(data[6] & 0x10) == (active and not angle)
