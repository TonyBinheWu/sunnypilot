from types import SimpleNamespace as NS

import pytest

from openpilot.cereal import log
from opendbc.can import CANPacker, CANParser
from opendbc.car import structs
from opendbc.car.hyundai import hyundaicanfd as fd
from opendbc.car.hyundai.cluster_indicators import executing_indicators
from opendbc.car.hyundai.cluster_radar import EV6ClusterCorners, EV6DisplayCorner180
from opendbc.car.hyundai.tests.test_ev6_cluster_radar import STAMP, lanes


class Messages(dict):
  pass


def driving():
  cs = structs.CarState(canValid=True, gearShifter="drive", vEgo=20.)
  cc = structs.CarControl(enabled=True, latActive=True, longActive=True)
  cc.actuators.longControlState = "pid"
  md = lanes()
  md.meta.laneChangeState, md.meta.laneChangeDirection = "laneChangeStarting", "left"
  plan = log.LongitudinalPlan.new_message(modelMonoTime=STAMP, speedConstraint="mapCurve", longitudinalPlanSource="cruise")
  sm = Messages(carControl=cc, modelV2=md, longitudinalPlan=plan,
                pandaStates=[log.PandaState.new_message(controlsAllowed=True, safetyModel="hyundaiCanfd")])
  sm.valid, sm.alive, sm.logMonoTime = dict.fromkeys(sm, True), dict.fromkeys(sm, True), dict.fromkeys(sm, STAMP)
  return sm, cs, cc


@pytest.mark.parametrize("phase", ["off", "preLaneChange", "laneChangeStarting", "laneChangeFinishing"])
@pytest.mark.parametrize("side,direction", [("left", 3), ("right", 4)])
@pytest.mark.parametrize("source,active", [("cruise", False), ("mapCurve", True), ("speedLimit", True),
                                          ("carrot/route", True), ("lead0", False), ("hkgCurve", False)])
def test_selected_maneuver_and_navigation_only(phase, side, direction, source, active):
  sm, cs, cc = driving()
  sm["modelV2"].meta.laneChangeState, sm["modelV2"].meta.laneChangeDirection = phase, side
  sm["longitudinalPlan"].speedConstraint = source
  assert executing_indicators(sm, cs, cc, STAMP) == (direction if phase in ("laneChangeStarting", "laneChangeFinishing") else 0, active)


@pytest.mark.parametrize("case,expected", [
  ("override", (3, False)), ("gas", (0, False)), ("brake", (0, False)), ("fault", (0, True)), ("takeover", (0, True)),
  ("plan_source", (3, False)), ("stop", (3, False)), ("no_long", (3, False)), ("no_lat", (0, True)), ("blocked", (0, True)),
  ("cancel", (0, False)), ("bad_can", (0, False)), ("no_panda", (0, False)), ("stale_control", (0, False)),
  ("stale_plan", (3, False)), ("stale_model", (0, True)), ("stale_plan_model", (3, False)), ("future_panda", (0, False)),
  ("invalid_panda_rx", (0, False)), ("nonfinite_speed", (0, False)),
])
def test_status_veto(case, expected):
  sm, cs, cc = driving()
  if case == "override": cc.cruiseControl.override = True
  if case == "gas": cs.gasPressed = True
  if case == "brake": cs.brakePressed = True
  if case == "fault": cs.steerFaultTemporary = True
  if case == "takeover": cs.steeringPressed = True
  if case == "plan_source": sm["longitudinalPlan"].longitudinalPlanSource = "e2e"
  if case == "stop": sm["longitudinalPlan"].shouldStop = True
  if case == "no_long": cc.longActive = False
  if case == "no_lat": cc.latActive = False
  if case == "blocked": cs.leftBlindspot = True
  if case == "cancel": cs.cruiseCancelState = True
  if case == "bad_can": cs.canTimeout = True
  if case == "no_panda": sm["pandaStates"][0].controlsAllowed = False
  if case == "stale_control": sm.logMonoTime["carControl"] -= 150_000_001
  if case == "stale_plan": sm.logMonoTime["longitudinalPlan"] -= 250_000_001
  if case == "stale_model": sm["modelV2"].timestampEof -= 250_000_001
  if case == "stale_plan_model": sm["longitudinalPlan"].modelMonoTime -= 250_000_001
  if case == "future_panda": sm.logMonoTime["pandaStates"] += 1
  if case == "invalid_panda_rx": sm["pandaStates"][0].safetyRxChecksInvalid = True
  if case == "nonfinite_speed": cs.vEgo = float("inf")
  assert executing_indicators(sm, cs, cc, STAMP) == expected


def test_only_the_panda_connected_to_the_display_bus_authorizes_feedback():
  sm, cs, cc = driving()
  assert executing_indicators(sm, cs, cc, STAMP, 1) == (0, False)
  sm["pandaStates"].append(log.PandaState.new_message(controlsAllowed=False, safetyModel="hyundaiCanfd"))
  assert executing_indicators(sm, cs, cc, STAMP, 1) == (0, False)
  sm["pandaStates"][1].controlsAllowed = True
  assert executing_indicators(sm, cs, cc, STAMP, 1) == (3, True)


@pytest.mark.parametrize("state,age,blocked", [("never", 0, False), ("off", 0, True), ("off", 999_999_999, True),
                                              ("off", 1_000_000_000, False), ("fault", 2_000_000_000, True)])
def test_packed_fallback_only_after_loss(state, age, blocked):
  dbc = "hyundai_canfd_generated"
  parser = CANParser(dbc, [("ADRV_0x1ea", 20), ("SCC_CONTROL", 50)], 1)
  p = CANPacker(dbc)
  if state != "never":
    parser.update([STAMP, [p.make_can_msg("ADRV_0x1ea", 1, {"HDA_MODE2": 5 if state == "fault" else 0}),
                           p.make_can_msg("SCC_CONTROL", 1, {"NSCCOnOff": 2, "NSCCOper": 3 if state == "fault" else 0})]])
  _, cs, cc = driving()
  cs.cruiseState.available = True
  car = NS(cp=parser, out=cs, softHoldActive=0)

  def packets(active):
    packer = CANPacker(dbc)
    lane, = fd._ev6_three_lane_message(packer, 1, parser, STAMP+age, None, changing=3 if active else 0)
    scc, _ = fd.create_acc_control(packer, NS(ECAN=1), True, 0., .1, False, False, 72., cc.hudControl,
                                   1., 1., car, ev6_display=True, now_nanos=STAMP+age, nav_active=active)
    decoder = CANParser(dbc, [("ADRV_0x1ea", 20), ("SCC_CONTROL", 50)], 1)
    assert decoder.update([STAMP+age, [lane, scc]]) == {0x1ea, 0x1a0}
    return [dict(decoder.vl[name]) for name in ("ADRV_0x1ea", "SCC_CONTROL")]
  baseline = packets(False)
  updated = packets(True)
  if not blocked:
    baseline[0].update(HDA_MODE2=3, LANE_CHANGING=3)
    baseline[1].update(NSCCOper=2, NSCCOnOff=2)
  for old, new in zip(baseline, updated, strict=True):
    del old["CHECKSUM"], new["CHECKSUM"]
    assert new == old


@pytest.mark.parametrize("setting,expected", [(0, 2), (1, 0), (2, 2), (3, 0)])
def test_nav_after_loss_and_immediate_stock_recovery(setting, expected):
  dbc = "hyundai_canfd_generated"
  parser = CANParser(dbc, [("SCC_CONTROL", 50)], 1)
  rx, tx = CANPacker(dbc), CANPacker(dbc)
  _, cs, cc = driving()
  cs.cruiseState.available = True
  car = NS(cp=parser, out=cs, softHoldActive=0)
  now = STAMP + 1_000_000_000

  def status(stopping=False):
    packet, _ = fd.create_acc_control(tx, NS(ECAN=1), True, 0., .1, stopping, False, 72., cc.hudControl, 1., 1.,
                                      car, ev6_display=True, now_nanos=now, nav_active=True)
    decoder = CANParser(dbc, [("SCC_CONTROL", 50)], 1)
    assert decoder.update([now, [packet]]) == {0x1a0}
    return decoder.vl["SCC_CONTROL"]["NSCCOper"]

  assert parser.update([STAMP, [rx.make_can_msg("SCC_CONTROL", 1, {"NSCCOnOff": setting})]]) == {0x1a0}
  assert status() == expected
  assert status(stopping=True) == 0
  assert parser.update([now, [rx.make_can_msg("SCC_CONTROL", 1, {"NSCCOnOff": 2, "NSCCOper": 1})]]) == {0x1a0}
  assert status() == 1


def scan(bus, counter, x):
  packer = CANPacker("hyundai_canfd_corner_radar_180_generated")
  frames = []
  for addr in range(0x180, 0x185):
    fields = {}
    if addr == 0x180:
      for slot, y in ((1, -3.5), (2, 3.5)):
        prefix = f"SLOT{slot}_"
        fields.update({prefix + k: v for k, v in dict(QUAL_LEVEL=35, AGE=16, OBJECT_ID=slot, REL_POS_X=x,
                                                      REL_POS_Y=y, REL_VEL_X=1.).items()})
    _, data, _ = packer.make_can_msg(addr, bus, fields)
    wire = bytearray(data)
    wire[2] = counter
    wire[:2] = fd.hkg_can_fd_checksum(addr, None, wire).to_bytes(2, "little")
    frames.append((addr, bytes(wire), bus))
  return frames


@pytest.mark.parametrize("bus", [0, 1, 2, 129])
@pytest.mark.parametrize("case", ["good", "loss", "crc", "mixed", "repeat", "gap", "clipped", "split_bus"])
def test_two_physical_neighbors_only_on_coherent_scans(bus, case):
  reader = EV6DisplayCorner180((0, 1, 2), EV6ClusterCorners())
  sm, cs, _ = driving()
  for i in range(2):
    frames = scan(bus, [255, 0][i] if case not in ("repeat", "gap") else [4, 4 if case == "repeat" else 6][i],
                  0 if case == "clipped" else 12. + i)
    if case == "loss": frames.pop()
    if case == "crc": frames[-1] = (0x184, b"\x00"*32, bus)
    if case == "mixed": frames[-1] = scan(bus, 14, 12.)[-1]
    if case == "split_bus": frames[-1] = (0x184, frames[-1][1], (bus+1) % 3)
    now = STAMP + i * 30_000_000
    reader.update([(now, frames)], sm["modelV2"], cs, now)
  values = {}
  reader.fill(values, now)
  if case == "good" and bus < 3:
    assert values == pytest.approx({f"{side}_{suffix}": v for side in ("RF", "LF") for suffix, v in
                                    (("DETECT", 1), ("DETECT_DISTANCE", 13.), ("DETECT_LATERAL", 3.5))})
  else:
    assert not values
  expired = {}
  reader.fill(expired, now + 150_000_001)
  assert not expired


def test_bus_change_requires_new_continuity_and_one_physical_source():
  reader = EV6DisplayCorner180((0, 1, 2), EV6ClusterCorners())
  sm, cs, _ = driving()
  for offset_ms, bus, seq, occupied in [(0, 1, 3, False), (30, 1, 4, True), (31, 2, 5, True),
                                        (140, 2, 6, False), (170, 2, 7, True)]:
    t = STAMP + offset_ms * 1_000_000
    sm["modelV2"].timestampEof = t
    reader.update([(t, scan(bus, seq, 10. if bus == 1 else 14.))], sm["modelV2"], cs, t)
    fields = {}
    reader.fill(fields, t)
    assert bool(fields) == occupied
    if occupied:
      assert fields["LF_DETECT_DISTANCE"] == fields["RF_DETECT_DISTANCE"] == (10. if offset_ms < 140 else 14.)
