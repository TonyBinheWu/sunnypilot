from types import SimpleNamespace as NS

import pytest

from openpilot.cereal import log
from opendbc.can import CANPacker, CANParser
from opendbc.car import structs
from opendbc.car.hyundai.cluster_radar import EV6ClusterCorners
from opendbc.car.hyundai.hyundaicanfd import create_acc_control
from opendbc.car.hyundai import hyundaicanfd
from opendbc.car.hyundai.stopping import CanfdStopping
from opendbc.car.hyundai.tests.test_stopping import make_cs


STAMP = 1_000_000_000


def sample(stamp=STAMP, **overrides):
  event = log.Event.new_message(logMonoTime=stamp, valid=True)
  tracks = event.init("liveTracks")
  p, = tracks.init("points", 1)
  for key, value in dict(trackId=12, radarSource="corner180", dRel=10., yRel=3.5,
                         vLead=8., measured=True).items():
    setattr(p, key, overrides.get(key, value))
  return event


def lanes(stamp=STAMP):
  model = log.ModelDataV2.new_message(timestampEof=stamp)
  model.laneLineProbs = [1.] * 4
  for line, y in zip(model.init("laneLines", 4), (-5.4, -1.8, 1.8, 5.4), strict=True):
    line.x, line.y = [0., 40.], [y, y]
  return model


@pytest.mark.parametrize("y,side", [(3.5, "LF"), (-3.5, "RF")])
def test_confirmed_corner_fills_vacant_front_only(y, side):
  corners, model = EV6ClusterCorners(), lanes()
  for i in (0, 1):
    now = STAMP + i * 50_000_000
    corners.update(sample(now, yRel=y), model, now)
    values = {}
    corners.fill(values, now)
    expected = {f"{side}_DETECT": 1, f"{side}_DETECT_DISTANCE": 10., f"{side}_DETECT_LATERAL": abs(y)}
    assert values == (expected if i else {})
  values = {f"{side}_DETECT": 2, f"{side}_DETECT_DISTANCE": 4.}
  original = values.copy()
  corners.fill(values, now)
  assert values == original
  values = {}
  corners.fill(values, now + 150_000_001)
  assert values == {}


@pytest.mark.parametrize("case", ["duplicate", "future", "stale", "invalid", "fault", "no-lanes", "stale-model",
                                  "new-id", "sideways", "zero-range", "stationary", "wrong-source", "unmeasured", "outside-lane"])
def test_reject_uncertain_corner(case):
  corners, model = EV6ClusterCorners(), lanes()
  corners.update(sample(), model, STAMP)
  stamp = STAMP if case == "duplicate" else STAMP + 50_000_000
  changes = {"new-id": {"trackId": 21}, "sideways": {"yRel": 4.9}, "zero-range": {"dRel": 0.},
             "stationary": {"vLead": 0.}, "wrong-source": {"radarSource": "frontRadar"},
             "unmeasured": {"measured": False}, "outside-lane": {"yRel": 7.}}
  event = sample(stamp, **changes.get(case, {}))
  event.valid = case != "invalid"
  event.liveTracks.errors.radarFault = case == "fault"
  if case == "no-lanes":
    model.laneLineProbs = [0.] * 4
  if case == "stale-model":
    model.timestampEof = stamp - 250_000_001
  now = stamp + {"future": -1, "stale": 150_000_001}.get(case, 0)
  corners.update(event, model, now)
  result = {}
  corners.fill(result, now)
  assert result == {}


@pytest.mark.parametrize("state", [0, 1, 2])
@pytest.mark.parametrize("bus,age,can_valid,copy_stock", [(1, 150_000_000, True, True), (1, 150_000_001, True, False),
                                                       (1, -1, True, False), (129, 0, True, False), (2, 0, True, False),
                                                       (1, 0, False, False)])
def test_adas_scc_only_copies_fresh_physical_object(state, bus, age, can_valid, copy_stock):
  packer = CANPacker("hyundai_canfd_generated")
  parser = CANParser("hyundai_canfd_generated", [("SCC_CONTROL", 50)], 1)
  fields = dict(HUD_LEAD_INFO=state, ACC_ObjDist=28.5, ACC_ObjLatPos=0., ACC_ObjRelSpd=-2., NSCCOper=state, NSCCOnOff=2)
  parser.update([STAMP, [packer.make_can_msg("SCC_CONTROL", bus, dict(fields, StopReq=1, aReqValue=-2.))]])
  cs = NS(cp=parser, out=structs.CarState(canValid=can_valid), softHoldActive=0)
  cs.out.cruiseState.available = True
  def run(ev6):
    msg, accel = create_acc_control(CANPacker("hyundai_canfd_generated"), NS(ECAN=1), True, 0., .2, False, False,
                                    78., NS(leadDistanceBars=2), 1., 2., cs, ev6_display=ev6, now_nanos=STAMP+age)
    assert (msg[0], msg[2]) == (0x1a0, 1)
    decoder = CANParser("hyundai_canfd_generated", [("SCC_CONTROL", 50)], 1)
    assert decoder.update([STAMP, [msg]]) == {0x1a0}
    return dict(decoder.vl["SCC_CONTROL"]), accel
  baseline, accel = run(False)
  actual, updated_accel = run(True)
  assert updated_accel == accel
  del baseline["CHECKSUM"], actual["CHECKSUM"]
  baseline.update(fields if copy_stock else dict(HUD_LEAD_INFO=0, ACC_ObjDist=204.6, ACC_ObjLatPos=0.,
                                                 ACC_ObjRelSpd=239.4, NSCCOper=0, NSCCOnOff=0))
  assert actual == pytest.approx(baseline)


@pytest.mark.parametrize("camera", [False, True])
@pytest.mark.parametrize("mode", range(6))  # off, standby, ready, operating, cancelled, fault
def test_lane_change_and_measured_corner_preserve_oem_payload(camera, mode):
  name = "ADRV_0x1ea"
  packer = CANPacker("hyundai_canfd_generated")
  source, dest = (2, 0) if camera else (1, 1)
  parser = CANParser("hyundai_canfd_generated", [(name, 20)], source)
  fields = dict(HDA_MODE2=mode, LANE_CHANGING=4, AUTOLANECHANGE_MSG=9, LEFT_BLINK_HOLD=1,
                LF_DETECT=4, LF_DETECT_DISTANCE=23, LR_DETECT=2, LR_DETECT_LATERAL=3.2)
  corners = EV6ClusterCorners()
  corners.stamp, corners.expires = STAMP, STAMP + 150_000_000
  corners.neighbors = {"LF": (8., 3.5), "RF": (14.2, 2.9)}
  # A fresh off frame after any state must immediately clear the indicator.
  for i, state in enumerate([mode, 0]):
    now = STAMP + 50_000_000 * i
    fields["HDA_MODE2"] = state
    addr, data, _ = packer.make_can_msg(name, source, fields)
    raw = bytearray(data)
    raw[16] = 0xa7
    raw[:2] = hyundaicanfd.hkg_can_fd_checksum(addr, None, raw).to_bytes(2, "little")
    assert parser.update([now, [(addr, bytes(raw), source)]]) == {addr}
    frame, = hyundaicanfd._ev6_three_lane_message(packer, dest, parser, now, corners, hold=4 if camera else None, camera=camera)
    assert (frame[0], frame[2]) == (addr, dest)
    expected = {**fields, "RF_DETECT": 1, "RF_DETECT_DISTANCE": 14.2, "RF_DETECT_LATERAL": 2.9,
                "LEFT_BLINK_HOLD": 0, "RIGHT_BLINK_HOLD": int(camera), "COUNTER": frame[1][2]}
    gold = bytearray(packer.make_can_msg(name, dest, expected)[1])
    gold[16] = raw[16]
    gold[:2] = hyundaicanfd.hkg_can_fd_checksum(addr, None, gold).to_bytes(2, "little")
    assert frame[1] == gold


@pytest.mark.parametrize("nav", [0, 1, 2, 3])
@pytest.mark.parametrize("age", [0, 150_000_000, 150_000_001])
@pytest.mark.parametrize("stopping", [False, True])
def test_camera_scc_nav_and_front_object_keep_braking_packet(nav, age, stopping):
  name = "SCC_CONTROL"
  packer = CANPacker("hyundai_canfd_generated")
  parser = CANParser("hyundai_canfd_generated", [(name, 50)], 2)
  stock = dict(NSCCOper=nav, NSCCOnOff=2, HUD_LEAD_INFO=1, ACC_ObjDist=25.4, ACC_ObjRelSpd=-3., ACC_ObjLatPos=1.)
  parser.update([STAMP, [packer.make_can_msg(name, 2, stock)]])
  cs = make_cs()
  cs.cp_cam = parser
  cs.scc_control.update(parser.vl[name])
  hud = NS(leadDistanceBars=2, signalStopObject=stopping)
  def build(ev6):
    packet, accel = hyundaicanfd.create_acc_control_scc2(
      CANPacker("hyundai_canfd_generated"), NS(ECAN=0), True, -.5, -.5, stopping, False, 72., hud,
      NS(carrot_cruise=0, jerk_u=1., jerk_l=2.), cs, CanfdStopping(), ev6_display=ev6, now_nanos=STAMP+age)
    decoder = CANParser("hyundai_canfd_generated", [(name, 50)], 0)
    assert decoder.update([STAMP, [packet]]) == {0x1a0}
    return dict(decoder.vl[name]), accel
  baseline, previous = build(False)
  actual, accel = build(True)
  assert accel == previous
  del actual["CHECKSUM"], baseline["CHECKSUM"]
  fresh = age <= 150_000_000
  baseline.update(NSCCOper=nav if fresh else 0, NSCCOnOff=2 if fresh else 0)
  if not stopping:
    baseline.update(stock if fresh else dict(HUD_LEAD_INFO=0, ACC_ObjDist=204.6, ACC_ObjRelSpd=239.4, ACC_ObjLatPos=0.))
  else:
    assert actual["StopReq"] == 1 and actual["ACC_ObjDist"] == 3.
  assert actual == pytest.approx(baseline)
