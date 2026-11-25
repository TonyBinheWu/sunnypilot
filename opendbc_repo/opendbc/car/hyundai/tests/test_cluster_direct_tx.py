import json
from pathlib import Path

import pytest

from opendbc.car import gen_empty_fingerprint
from opendbc.car import interfaces as interfaces_module
from opendbc.car.hyundai import carstate, hyundaicanfd, interface
from opendbc.car.hyundai.values import CAR, CANFD_CAR, HyundaiFlags, HyundaiSafetyFlags


@pytest.fixture
def configuration(monkeypatch):
  fingerprint = gen_empty_fingerprint()
  values = {"FingerPrints": repr(fingerprint)}

  class Params:
    def get_int(self, key):
      return int(values.get(key, 0))

    def get_bool(self, key):
      return bool(values.get(key, False))

    def get_float(self, key):
      return float(values.get(key, 0))

    def get(self, key, return_default=False):
      return values.get(key, "")

    def put_bool(self, key, value):
      pass

  for module in (interface, hyundaicanfd, carstate, interfaces_module):
    monkeypatch.setattr(module, "Params", Params)

  def make(candidate):
    return interface.CarInterface.get_params(candidate, fingerprint, [], False, False, False)

  return values, make


@pytest.mark.parametrize("mode,tracks,longitudinal,bus", [(0, 0, False, 1), (0, 1, True, 1), (1, 0, True, 0),
                                                       (2, 0, True, 0), (3, 1, False, 0)])
@pytest.mark.parametrize("corner_setting", [0, 1, 2])
def test_ev6_cluster_scc_ownership(configuration, monkeypatch, mode, tracks, longitudinal, bus, corner_setting):
  from opendbc.can import CANParser
  from opendbc.can.parser import get_raw_value
  from opendbc.car import Bus, structs
  from opendbc.car.hyundai import carcontroller
  values, make = configuration
  values.update(HyundaiCameraSCC=mode, EnableRadarTracks=tracks, CanfdHDA2=1, EnableCornerRadar=corner_setting)
  cp = make(CAR.KIA_EV6)
  monkeypatch.setattr(carcontroller, "Params", interface.Params)
  controller = carcontroller.CarController({Bus.pt: "hyundai_canfd_generated"}, cp)
  cs = carstate.CarState(cp)
  cs.out = structs.CarState(canValid=True)
  cs.scc_control = dict.fromkeys(controller.packer.dbc.name_to_msg["SCC_CONTROL"].sigs, 0)
  cs.adrv_0x1ea = dict.fromkeys(controller.packer.dbc.name_to_msg["ADRV_0x1ea"].sigs, 0)
  cs.ccnc_0x162 = dict.fromkeys(controller.packer.dbc.name_to_msg["CCNC_0x162"].sigs, 0)
  rx_bus = 2 if mode else bus
  parser = CANParser("hyundai_canfd_generated", [("SCC_CONTROL", 50), ("ADRV_0x1ea", 20)], rx_bus)
  if mode:
    cs.cp_cam = parser
  else:
    cs.cp = parser
  lane_state = {"HDA_MODE2": 3, "AUTOLANECHANGE_MSG": 9, "LANELINE_RIGHT_POSITION": 92, "LR_DETECT": 4}
  scc = {"NSCCOnOff": 2, "NSCCOper": 2, "HUD_LEAD_INFO": 1, "ACC_ObjDist": 17.5}
  inputs = [controller.packer.make_can_msg(name, rx_bus, fields) for name, fields in
            (("ADRV_0x1ea", lane_state), ("SCC_CONTROL", scc))]
  assert parser.update([1_000_000_000, inputs]) == {0x1ea, 0x1a0}
  assert cp.openpilotLongitudinalControl == longitudinal
  assert controller.ev6_mode0_display == (mode == 0 and longitudinal)
  assert controller.CAN.ECAN == bus
  assert (controller.cluster_corners is not None) == longitudinal
  if longitudinal:
    controller.cluster_corners.stamp = 1_000_000_000
    controller.cluster_corners.expires = 1_150_000_000
    controller.cluster_corners.neighbors = {"RF": (16., 3.5)}
  _, packets = controller.update(structs.CarControl().as_reader(), cs, 1_000_000_000)
  cluster = [(addr, net) for addr, _, net in packets if addr in (0x1a0, 0x162, 0x1ea)]
  expected = {(0x1a0, bus), (0x1ea, bus)} if longitudinal else set()
  if mode in (1, 2):
    expected.add((0x162, bus))
  assert set(cluster) == expected
  assert len(cluster) == len(expected)
  for addr, data, _ in packets:
    if addr in (0x1a0, 0x1ea):
      fields = scc if addr == 0x1a0 else lane_state
      sigs = controller.packer.dbc.addr_to_msg[addr].sigs
      for key, expected_value in fields.items():
        assert get_raw_value(data, sigs[key]) * sigs[key].factor + sigs[key].offset == pytest.approx(expected_value)
    if addr in (0x162, 0x1ea):
      sigs = controller.packer.dbc.addr_to_msg[addr].sigs
      kind = 3 if addr == 0x162 else 1
      assert get_raw_value(data, sigs["RF_DETECT"]) == (kind if corner_setting else 0)
      assert get_raw_value(data, sigs["RR_DETECT"]) == 0


@pytest.mark.parametrize("age", [0, 1])
def test_ev6_mode0_apply_display(configuration, monkeypatch, age):
  from opendbc.can import CANParser
  from opendbc.car import Bus
  from opendbc.car.hyundai import carcontroller
  from opendbc.car.hyundai.cluster_indicators import executing_indicators
  from opendbc.car.hyundai.cluster_radar import EV6DisplayCorner180
  from opendbc.car.hyundai.tests.test_ev6_mode0_display import STAMP, driving, scan
  values, make = configuration
  values.update(HyundaiCameraSCC=0, EnableRadarTracks=1, CanfdHDA2=1, EnableCornerRadar=2)
  monkeypatch.setattr(carcontroller, "Params", interface.Params)
  cp = make(CAR.KIA_EV6)
  controller = carcontroller.CarController({Bus.pt: "hyundai_canfd_generated"}, cp)
  cs = carstate.CarState(cp)
  sm, cs.out, cc = driving()
  cs.out.cruiseState.available = True
  cs.cp = CANParser("hyundai_canfd_generated", [("SCC_CONTROL", 50), ("ADRV_0x1ea", 20)], 1)
  reader = EV6DisplayCorner180((0, 1, 2), controller.cluster_corners)
  for t, counter in ((STAMP - 30_000_000, 20), (STAMP, 21)):
    sm["modelV2"].timestampEof = t
    reader.update([(t, scan(1, counter, 12.))], sm["modelV2"], cs.out, t)
  controller.raw_display_corners = reader
  controller.ev6_indicator_tick = (STAMP, *executing_indicators(sm, cs.out, cc, STAMP))
  _, packets = controller.update(cc.as_reader(), cs, STAMP + age)
  decoder = CANParser("hyundai_canfd_generated", [("SCC_CONTROL", 50), ("ADRV_0x1ea", 20)], 1)
  assert decoder.update([STAMP + age, packets]) >= {0x1a0, 0x1ea}
  lanes, scc = decoder.vl["ADRV_0x1ea"], decoder.vl["SCC_CONTROL"]
  assert (lanes["LF_DETECT"], lanes["RF_DETECT"], lanes["LR_DETECT"], lanes["RR_DETECT"]) == (1, 1, 0, 0)
  assert (lanes["LEFT_BLINK_HOLD"], lanes["RIGHT_BLINK_HOLD"]) == (0, 0)
  assert (lanes["HDA_MODE2"], lanes["LANE_CHANGING"], scc["NSCCOper"]) == ((3, 3, 2) if age == 0 else (0, 0, 0))


@pytest.mark.parametrize("candidate", [c for c in CANFD_CAR if c in interfaces_module.get_torque_params()])
@pytest.mark.parametrize("hda2", [0, 1])
def test_configured_canfd_vehicles_default_off_and_manual_on(configuration, candidate, hda2):
  values, make = configuration
  values["HyundaiCameraSCC"] = 1
  values["CanfdHDA2"] = hda2
  default = make(candidate)
  assert not default.flags & HyundaiFlags.CANFD_CLUSTER_DIRECT_TX
  assert not default.safetyConfigs[-1].safetyParam & HyundaiSafetyFlags.CANFD_CLUSTER_DIRECT_TX
  values["HyundaiCanfdClusterDirectTx"] = True
  enabled = make(candidate)
  assert enabled.flags == default.flags | HyundaiFlags.CANFD_CLUSTER_DIRECT_TX
  assert enabled.safetyConfigs[-1].safetyParam == default.safetyConfigs[-1].safetyParam | HyundaiSafetyFlags.CANFD_CLUSTER_DIRECT_TX
  # A saved setting change is applied when CarParams is rebuilt, never live.
  values["HyundaiCanfdClusterDirectTx"] = False
  assert enabled.flags & HyundaiFlags.CANFD_CLUSTER_DIRECT_TX
  assert make(candidate).flags == default.flags


@pytest.mark.parametrize("candidate", [CAR.KIA_EV6, CAR.HYUNDAI_SONATA])
def test_setting_ignored_outside_camera_canfd(configuration, candidate):
  values, make = configuration
  original = make(candidate)
  values["HyundaiCanfdClusterDirectTx"] = True
  enabled = make(candidate)
  assert enabled.flags == original.flags
  assert [c.to_dict() for c in enabled.safetyConfigs] == [c.to_dict() for c in original.safetyConfigs]


def test_direct_tx_setting_defaults_and_safety_bit():
  # No platform, including entries without complete torque configuration, opts in.
  assert all(not c.config.flags & HyundaiFlags.CANFD_CLUSTER_DIRECT_TX for c in CAR)
  root = next(p for p in Path(__file__).resolve().parents if (p / "panda/board").is_dir())
  catalog = json.loads((root / "openpilot/selfdrive/carrot_settings.json").read_text(encoding="utf-8"))
  setting = next(p for p in catalog["params"] if p["name"] == "HyundaiCanfdClusterDirectTx")
  assert setting["default"] == 0 and setting["control"] == "toggle"
  keys = (root / "openpilot/common/params_keys.h").read_text(encoding="utf-8")
  assert '{"HyundaiCanfdClusterDirectTx", {PERSISTENT, BOOL, "0"}}' in keys
  # Bit 1024 belongs to the separately gated parked blinker diagnostic.
  assert HyundaiSafetyFlags.CANFD_CLUSTER_DIRECT_TX == 2048
  header = (root / "opendbc_repo/opendbc/safety/safety/safety_hyundai_canfd.h").read_bytes()
  assert b"HYUNDAI_PARAM_CANFD_CLUSTER_DIRECT_TX = 2048;" in header
