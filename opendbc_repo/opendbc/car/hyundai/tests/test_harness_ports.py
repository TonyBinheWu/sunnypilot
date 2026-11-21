from types import SimpleNamespace

import pytest

from opendbc.can import CANPacker, CANParser
from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.fw_versions import match_fw_to_car_exact
from opendbc.car.hyundai.factory_cruise import update_ccnc_cruise, update_non_scc_state
from opendbc.car.hyundai.fingerprints import FW_VERSIONS
from opendbc.car.hyundai.hyundaicanfd import create_steering_messages_camera_scc
from opendbc.car.hyundai.interface import CarInterface
from opendbc.car.hyundai.tests.test_experimental_longitudinal import configure_params
from opendbc.car.hyundai.values import CAR, CCNC_PORT_CAR, NON_SCC_CAR, HyundaiFlags
from opendbc.safety.tests.libsafety import libsafety_py


@pytest.mark.parametrize("car", sorted(CCNC_PORT_CAR | NON_SCC_CAR))
@pytest.mark.parametrize("override", [False, True])
def test_pending_harness_has_no_command_authority(monkeypatch, car, override):
  fp = gen_empty_fingerprint()
  fp[2][0x1a0] = 32
  fp[0][0x201] = 6
  configure_params(monkeypatch, {"FingerPrints": repr(fp), "HyundaiCameraSCC": 2 * override,
                                 "EnableRadarTracks": int(override), "CommaPedalEnabled": override,
                                 "AlwaysLateral": int(override), "CanfdHDA2": int(override)})
  cp = CarInterface.get_params(car, fp, [], override, False, False)
  assert cp.dashcamOnly and cp.pcmCruise and not cp.autoResumeSng and cp.radarUnavailable
  assert not cp.openpilotLongitudinalControl and not cp.alphaLongitudinalAvailable
  assert not cp.flags & (HyundaiFlags.PEDAL_INTERCEPTOR | HyundaiFlags.CANFD_HDA2)
  CarInterface.init(cp, None, None)
  assert [(s.safetyModel.raw, s.safetyParam) for s in cp.safetyConfigs] == [(structs.CarParams.SafetyModel.noOutput, 0)]
  panda = libsafety_py.libsafety
  config = cp.safetyConfigs[0]
  assert panda.set_safety_hooks(config.safetyModel.raw, config.safetyParam) == 0
  for addr, size in ((0x1a0, 32), (0x12a, 16), (0x421, 8), (0x200, 6)):
    assert not panda.safety_tx_hook(libsafety_py.make_CANPacket(addr, 0, bytes(size)))


@pytest.mark.parametrize("car,status,main,active,speed,target", [
  (CAR.KIA_FORTE_2019_NON_SCC, "EMS16", "CRUISE_LAMP_M", "CRUISE_LAMP_S", "LVR12", "CF_Lvr_CruiseSet"),
  (CAR.KIA_CEED_PHEV_2022_NON_SCC, "E_CRUISE_CONTROL", "CRUISE_LAMP_M", "CRUISE_LAMP_S", "ELECT_GEAR", "SLC_SET_SPEED"),
  (CAR.HYUNDAI_KONA_EV_NON_SCC, "LABEL11", "CC_React", "CC_ACT", "E_EMS11", "Cruise_Limit_Target"),
])
def test_factory_cruise_lamps_release_and_expiry(car, status, main, active, speed, target):
  dbc = "hyundai_kia_generic"
  cp = structs.CarParams(carFingerprint=str(car), flags=int(car.config.flags))
  pt = CANParser(dbc, [(status, 10), (speed, 10)], 0)
  cam = CANParser(dbc, [], 2)
  packer = CANPacker(dbc)
  for now, lamps in [(1_000_000_000, (1, 1)), (1_100_000_000, (1, 0)), (1_200_000_000, (1, 1)), (2_000_000_000, None)]:
    packets = [] if lamps is None else [packer.make_can_msg(status, 0, {main: lamps[0], active: lamps[1]}),
                                        packer.make_can_msg(speed, 0, {target: 72})]
    pt.update([(now, packets)])
    ret = structs.CarState()
    update_non_scc_state(ret, cp, pt, cam, 1 / 3.6)
    assert ret.cruiseState.nonAdaptive
    assert ret.cruiseState.available == (lamps is not None)
    assert ret.cruiseState.enabled == bool(lamps and lamps[1])
    assert ret.cruiseState.speed == pytest.approx(20 if lamps else 0)


def test_camera_request_and_fresh_brake_controller_feedback():
  dbc = "hyundai_canfd_generated"
  pt = CANParser(dbc, [("TCS", 50)], 0)
  cam = CANParser(dbc, [("SCC_CONTROL", 50)], 2)
  packer = CANPacker(dbc)
  for now, request, feedback in [(1_000_000_000, 1, 0), (1_020_000_000, 0, 1), (2_000_000_000, None, None)]:
    packets = [] if request is None else [packer.make_can_msg("SCC_CONTROL", 2, {"ACCMode": request, "MainMode_ACC": 1}),
                                          packer.make_can_msg("TCS", 0, {"ACC_REQ": feedback})]
    for parser in (pt, cam):
      parser.update([(now, packets)])
    ret = structs.CarState()
    update_ccnc_cruise(ret, pt, cam, 1)
    assert ret.cruiseState.enabled == bool(feedback)
    assert ret.cruiseState.available == (feedback is not None)


def test_new_firmware_entries_never_claim_an_existing_full_fingerprint():
  new_cars = CCNC_PORT_CAR | NON_SCC_CAR
  for model, versions in FW_VERSIONS.items():
    if model in new_cars:
      continue
    ecu_responses = {key[1:]: set(responses) for key, responses in versions.items() if responses}
    matches = match_fw_to_car_exact(ecu_responses, "hyundai", log=False)
    assert not (matches & new_cars), (model, matches & new_cars)


@pytest.mark.parametrize("model,source", [(CAR.KIA_FORTE_2019_NON_SCC, None),
                                          (CAR.KIA_CEED_PHEV_2022_NON_SCC, 2),
                                          (CAR.GENESIS_G70_2021_NON_SCC, 0)])
def test_factory_emergency_braking_uses_observed_bus_and_expires(model, source):
  cp = structs.CarParams(carFingerprint=str(model), flags=int(model.config.flags))
  dbc = "hyundai_kia_generic"
  packer = CANPacker(dbc)
  pt, cam = (CANParser(dbc, [("FCA11", 10)], bus) for bus in (0, 2))
  for step, bus in enumerate([0, 2]):
    now = (step + 1) * 1_000_000_000
    observed = packer.make_can_msg("FCA11", bus, {"CF_VSM_Warn": 1, "FCA_CmdAct": 1})
    for parser in (pt, cam):
      parser.update([(now, [observed])])
    ret = structs.CarState()
    update_non_scc_state(ret, cp, pt, cam, 1)
    assert ret.stockAeb == (source == bus)
    assert not ret.stockFcw


def test_original_ccnc_driver_feedback_is_receive_only():
  state = SimpleNamespace(mdps={}, steer_touch_2af={}, adrv_0x161=None, lfa=None)
  cp = structs.CarParams(carFingerprint=CAR.HYUNDAI_TUCSON_HEV_2025)
  bus = SimpleNamespace(CAM=2, ECAN=0)
  messages = create_steering_messages_camera_scc(0, CANPacker("hyundai_canfd_generated"),
                                                cp, bus, None, False, 0, state, 0, 0, False)
  assert not messages
