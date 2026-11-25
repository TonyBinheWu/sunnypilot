import copy
from types import SimpleNamespace

import pytest

from opendbc.can import CANDefine, CANPacker
from opendbc.can.parser import CANParser, get_raw_value
from opendbc.car import structs
from opendbc.car.hyundai import hyundaicanfd
from opendbc.car.hyundai.hyundaicanfd import _select_cluster_background
from opendbc.car.hyundai.values import HyundaiFlags


@pytest.mark.parametrize(
  ("cruise_enabled", "lat_active", "paddle_pressed", "paddle_mode", "expected"),
  (
    (True, True, True, 0, 1),
    (False, True, True, 0, 3),
    (False, False, True, 0, 7),
    (True, True, True, 1, 6),
    (True, True, False, 1, 1),
  ),
)
def test_paddle_background_requires_enabled_paddle_mode(
  cruise_enabled, lat_active, paddle_pressed, paddle_mode, expected,
):
  assert _select_cluster_background(cruise_enabled, lat_active, paddle_pressed, paddle_mode) == expected


@pytest.mark.parametrize('cruise_enabled', (False, True))
@pytest.mark.parametrize('lat_active', (False, True))
def test_model_turn_background_requires_active_steering(cruise_enabled, lat_active):
  normal = 1 if cruise_enabled else 7
  assert _select_cluster_background(cruise_enabled, lat_active, False, 0, turning=True) == (6 if lat_active else normal)


@pytest.mark.parametrize('desire', range(5))
@pytest.mark.parametrize('lat_active', (False, True))
def test_turn_changes_only_background_in_existing_cluster_frame(monkeypatch, desire, lat_active):
  from openpilot.cereal import log
  monkeypatch.setattr(hyundaicanfd, 'Params', lambda: SimpleNamespace(get_int=lambda key: 0, get=lambda key: '0'))
  packer = CANPacker('hyundai_canfd_generated')
  definition = packer.dbc.name_to_msg['ADRV_0x161']
  stock = {key: 0 for key in definition.sigs}
  stock['COUNTER'] = 17
  original = stock.copy()
  model = log.ModelDataV2.new_message()
  model.meta.desire = desire
  state = SimpleNamespace(
    adrv_0x161=stock, out=structs.CarState(), modelV2=model, lfahda_cluster=None,
    cruise_buttons_msg=None, adrv_0x200=None, adrv_0x1ea=None, ccnc_0x162=None,
    is_metric=True, paddle_button_prev=0, softHoldActive=0, trailer_connected=False,
  )
  control = structs.CarControl(latActive=lat_active, enabled=True)

  def messages():
    return hyundaicanfd.create_ccnc_messages(
      SimpleNamespace(flags=HyundaiFlags.CAMERA_SCC), CANPacker('hyundai_canfd_generated'),
      SimpleNamespace(ECAN=0, CAM=2), 5, control, state, control.hudControl, 0, False, False, 0, False, 0, 0)
  actual = messages()
  monkeypatch.setattr(hyundaicanfd, '_select_cluster_background',
                      lambda enabled, lat, paddle, mode, **kwargs: 6 if mode > 0 and paddle else 1 if enabled else 3 if lat else 7)
  baseline = messages()
  assert len(actual) == len(baseline) == 1
  assert (actual[0][0], actual[0][2]) == (baseline[0][0], baseline[0][2]) == (0x161, 0)

  def decode(message):
    return {key: get_raw_value(message[1], sig) for key, sig in definition.sigs.items()}
  values, old = decode(actual[0]), decode(baseline[0])
  assert values['BACKGROUND'] == (6 if lat_active and desire in (1, 2) else 1)
  assert {k: v for k, v in values.items() if k not in ('BACKGROUND', 'CHECKSUM')} == {
    k: v for k, v in old.items() if k not in ('BACKGROUND', 'CHECKSUM')}
  assert values['CHECKSUM'] == hyundaicanfd.hkg_can_fd_checksum(0x161, None, bytearray(actual[0][1]))
  assert stock == original


@pytest.mark.parametrize("distance", (0.0, 1.6, 14.0, 14.1, 20.0, 25.5))
@pytest.mark.parametrize(("message", "detect", "expected_corner", "expected_front"), [
  *(('ADRV_0x1ea', detect, expected, None) for detect, expected in (
    (0, 0), (1, 1), (2, 2), (3, 3), (4, 1), (5, 1), (6, 1), (7, 1),
  )),
  *(('CCNC_0x162', detect, 3, expected) for detect, expected in (
    (1, 3), (2, 4), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
    (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14),
  )),
  # EV5 supplies nonzero corner geometry while 0x162 DETECT stays hidden.
  ('CCNC_0x162', 0, 3, 0),
])
def test_cluster_objects_restore_corner_state_without_blinking_or_distance_clamp(monkeypatch, message, distance, detect,
                                                                               expected_corner, expected_front):
  monkeypatch.setattr(hyundaicanfd, "Params", lambda: SimpleNamespace(get_int=lambda key: 0))
  packer = CANPacker("hyundai_canfd_generated")
  display_types = CANDefine("hyundai_canfd_generated").dv[message]
  definition = packer.dbc.name_to_msg[message]
  source = {key: 0 for key in definition.sigs}
  for side in ("LF", "RF", "LR", "RR"):
    source[f"{side}_DETECT"] = detect
    source[f"{side}_DETECT_DISTANCE"] = distance
    source[f"{side}_DETECT_LATERAL"] = 2.9
  if message == "CCNC_0x162":
    source.update(FF_DETECT=detect, FF_DISTANCE=81.2, FF_LATERAL=1.3,
                  FF_DETECT_ALT=2, FF_DISTANCE_ALT=42.1, FF_LATERAL_ALT=0.7)
  original = copy.deepcopy(source)
  state = SimpleNamespace(
    out=SimpleNamespace(brakeHoldActive=False, parkingBrake=False, steeringAngleDeg=6.0,
                        leftBlinker=False, rightBlinker=False),
    modelV2=None, lfahda_cluster=None, cruise_buttons_msg=None, adrv_0x161=None, adrv_0x200=None,
    adrv_0x1ea=source if message == "ADRV_0x1ea" else None,
    ccnc_0x162=source if message == "CCNC_0x162" else None,
    radarState=SimpleNamespace(leadOne=SimpleNamespace(status=True, dRel=81.2, yRel=-1.3, vRel=-5.0)),
  )
  cp = SimpleNamespace(flags=HyundaiFlags.CAMERA_SCC.value)
  can = SimpleNamespace(ECAN=0, CAM=2)
  control = SimpleNamespace(latActive=True, enabled=True)
  # FF uses radarState directly, independently of the older HUD distance.
  hud = SimpleNamespace(leadDistance=123.4, leadRadar=1, leadRelSpeed=-5.0)

  for frame in (0, 5, 65, 70, 100, 135, 200):
    messages = hyundaicanfd.create_ccnc_messages(cp, packer, can, frame, control, state, hud,
                                                0, False, False, 0, False, 0, 0)
    assert len(messages) == 1
    address, data, bus = messages[0]
    assert (address, bus) == (definition.address, 0)
    decoded = {key: get_raw_value(data, sig) * sig.factor + sig.offset for key, sig in definition.sigs.items()}
    assert decoded["CHECKSUM"] == hyundaicanfd.hkg_can_fd_checksum(address, None, bytearray(data))
    for side in ("LF", "RF", "LR", "RR"):
      assert decoded[f"{side}_DETECT_DISTANCE"] == pytest.approx(distance)
      assert decoded[f"{side}_DETECT_LATERAL"] == pytest.approx(2.9)
      assert decoded[f"{side}_DETECT"] == (expected_corner if distance != 0 else detect)
      if message == "CCNC_0x162" and distance != 0:
        assert display_types[f"{side}_DETECT"][decoded[f"{side}_DETECT"]] == "GRAY_CAR"
    if message == "CCNC_0x162":
      assert decoded["FF_DETECT"] == (expected_front or 4)
      for key in ("FF_DISTANCE", "FF_LATERAL", "FF_DETECT_ALT", "FF_DISTANCE_ALT", "FF_LATERAL_ALT"):
        assert decoded[key] == pytest.approx(original[key])
    else:
      assert decoded["LANELINE_CURVATURE"] == 2
    assert source == original


@pytest.mark.parametrize("age", [0, 150_000_000, 150_000_001, -1])
@pytest.mark.parametrize("kind", [0, 1, 2, 3, 4])
def test_ev6_adas_preserves_raw_corner_and_warning(age, kind):
  name = "ADRV_0x1ea"
  stamp = 1_000_000_000
  packer = CANPacker("hyundai_canfd_generated")
  parser = CANParser("hyundai_canfd_generated", [(name, 20)], 1)
  fields = {"HDA_MODE2": 5, "AUTOLANECHANGE_MSG": 8, "LANE_CHANGING": 2, "LANELINE_LEFT_POSITION": 19,
            "LF_DETECT": kind, "LF_DETECT_DISTANCE": 12.3, "LF_DETECT_LATERAL": 1.2}
  addr, raw, bus = packer.make_can_msg(name, 1, fields)
  data = bytearray(raw)
  data[16] = 0xa6  # Unnamed bits in this DBC.
  data[:2] = hyundaicanfd.hkg_can_fd_checksum(addr, None, data).to_bytes(2, "little")
  assert parser.update([stamp, [(addr, bytes(data), bus)]]) == {addr}
  cp = SimpleNamespace(flags=HyundaiFlags.CANFD_HDA2, carFingerprint=hyundaicanfd.CAR.KIA_EV6)
  out = hyundaicanfd.create_adrv_messages(cp, packer, SimpleNamespace(ECAN=1), 5, parser, now_nanos=stamp+age)
  assert len(out) == 2
  address, payload, dest = out[0]
  assert (address, dest) == (addr, 1)
  if 0 <= age <= 150_000_000:
    assert payload[3:] == data[3:]
  else:
    sigs = packer.dbc.addr_to_msg[addr].sigs
    assert all(get_raw_value(payload, sigs[field]) == 0 for field in ("HDA_MODE2", "LANE_CHANGING", "LF_DETECT"))
  assert int.from_bytes(payload[:2], "little") == hyundaicanfd.hkg_can_fd_checksum(addr, None, payload)


def test_ev6_adas_display_uses_physical_ecan_rx():
  name = "ADRV_0x1ea"
  dbc = "hyundai_canfd_generated"
  parser = CANParser(dbc, [], 1)
  parser._add_message(name, float("nan"), ignore_counter=True)
  packer = CANPacker(dbc)
  addr, data, _ = packer.make_can_msg(name, 1, {"RF_DETECT": 4, "RF_DETECT_DISTANCE": 9.5, "RF_DETECT_LATERAL": 1.2})
  for bus in (129, 193, 2):
    parser.update([100, [(addr, data, bus)]])
    assert not hyundaicanfd.ev6_cluster_corners(parser)
  parser.update([101, [(addr, data, 1)]])
  assert hyundaicanfd.ev6_cluster_corners(parser) == pytest.approx({
    "RF_DETECT": 1, "RF_DETECT_DISTANCE": 9.5, "RF_DETECT_LATERAL": 1.2})
  parser.update([150_000_102, [(addr, data, 129)]])
  assert not hyundaicanfd.ev6_cluster_corners(parser)

@pytest.mark.parametrize("target, offset, age, occupied, expected", [
  (-3.5, 0, 100, False, "LF"), (3.5, 0, 100, False, "RF"),
  (-3.5, -3.5, 100, False, None), (-3.5, 0, 250_000_001, False, None),
  (-3.5, 0, 100, True, None), (-1.8, 0, 100, False, None),
])
def test_ev6_vision_only_neighbor(target, offset, age, occupied, expected):
  stamp = 1_000_000_000
  model = SimpleNamespace(timestampEof=stamp, leadsV3=[SimpleNamespace(prob=.9, x=[20], y=[target], yStd=[.25])],
                          laneLineProbs=[.9]*4, laneLines=[SimpleNamespace(x=[0, 20], y=[y, y+offset]) for y in (-5.25, -1.75, 1.75, 5.25)])
  values = {"LF_DETECT": 2} if occupied else {}
  previous = values.copy()
  hyundaicanfd._add_ev6_vision_neighbor(values, model, stamp+age)
  if expected:
    assert values == pytest.approx({f"{expected}_DETECT": 1, f"{expected}_DETECT_DISTANCE": 18.48,
                                    f"{expected}_DETECT_LATERAL": 3.5})
  else:
    assert values == previous


@pytest.mark.parametrize("age,stock_mode", [(0, 0), (250_000_000, 1), (250_000_001, 1), (0, 3), (0, 5)])
def test_ev6_camera_scc_oem_icons(monkeypatch, age, stock_mode):
  from openpilot.cereal import log
  monkeypatch.setattr(hyundaicanfd, "Params", lambda: SimpleNamespace(get_int=lambda key: 0, get=lambda key: "2"))
  packer = CANPacker("hyundai_canfd_generated")
  def blank(name):
    return dict.fromkeys(packer.dbc.name_to_msg[name].sigs, 0)
  stamp = 1_000_000_000
  model = log.ModelDataV2.new_message(timestampEof=stamp)
  stock, corner = blank("ADRV_0x161"), blank("ADRV_0x1ea")
  stock.update(NAV_ICON=4, LCA_RIGHT_ICON=1, LCA_LEFT_ARROW=1)
  corner["HDA_MODE2"] = stock_mode
  cam = SimpleNamespace(ts_nanos={"ADRV_0x161":{"COUNTER":stamp}}, _last_update_nanos=stamp,
                        dat={0x161: bytes(32)}, vl={"ADRV_0x161":stock})
  state = SimpleNamespace(adrv_0x161=stock, adrv_0x1ea=corner, cp_cam=cam, modelV2=model, out=structs.CarState(leftBlinker=True, canValid=True),
                          lfahda_cluster=None, cruise_buttons_msg=None, adrv_0x200=None, ccnc_0x162=blank("CCNC_0x162"), scc_control=None,
                          is_metric=True, paddle_button_prev=0, softHoldActive=0, trailer_connected=False)
  control = structs.CarControl(latActive=True, enabled=True)
  control.hudControl.leftLaneVisible = control.hudControl.rightLaneVisible = True
  state.out.rightBlindspot = True
  radar = log.RadarState.new_message(mdMonoTime=stamp)
  radar.init("leadsRight", 1)
  lead = radar.leadsRight[0]
  lead.status, lead.radar, lead.dRel, lead.yRel = True, True, 12.0, -3.5
  corner.update(LR_DETECT=2, LR_DETECT_DISTANCE=8, LR_DETECT_LATERAL=3)
  cam.ts_nanos["ADRV_0x1ea"] = {"COUNTER": stamp}
  cam.dat[0x1ea] = packer.make_can_msg("ADRV_0x1ea", 2, corner)[1]
  cam.vl["ADRV_0x1ea"] = corner
  model.init("leadsV3", 1)
  target = model.leadsV3[0]
  target.prob, target.x, target.y, target.yStd = .95, [20], [0], [.2]
  model.laneLineProbs = [.9] * 4
  for line, offset in zip(model.init("laneLines", 4), (-5.25, -1.75, 1.75, 5.25)):
    line.x, line.y = [0, 30], [offset, offset]
  state.radarState = radar
  cp = SimpleNamespace(flags=HyundaiFlags.CAMERA_SCC | HyundaiFlags.CANFD_HDA2, carFingerprint=hyundaicanfd.CAR.KIA_EV6, openpilotLongitudinalControl=True)
  msgs = hyundaicanfd.create_ccnc_messages(cp, packer, SimpleNamespace(ECAN=0, CAM=2), 5, control, state, control.hudControl,
                                          0, False, False, 2, False, 0, 0, now_nanos=stamp+age)
  frames = {addr:data for addr,data,_ in msgs}
  def raw(addr,key):
    return get_raw_value(frames[addr], packer.dbc.addr_to_msg[addr].sigs[key])
  assert [raw(0x161,k) for k in ("NAV_ICON","LCA_RIGHT_ICON","LCA_LEFT_ARROW")] == [4,1,1]
  assert (raw(0x161, "LANELINE_LEFT"), raw(0x161, "LANELINE_RIGHT")) == (6, 4)
  assert (0x1ea in frames) == (age <= 150_000_000)
  if 0x1ea in frames:
    assert raw(0x1ea, "HDA_MODE2") == stock_mode
    assert raw(0x1ea, "RF_DETECT") == 0  # A fused lead supplies no measured corner position.
  assert raw(0x162, "LR_DETECT") == (3 if age <= 150_000_000 else 0)
  assert raw(0x162, "RR_DETECT") == 0
  assert raw(0x162, "RF_DETECT") == (3 if age <= 250_000_000 else 0)
  assert raw(0x162, "FF_DETECT") == (3 if age <= 250_000_000 else 0)

  # Check a factory notification, then its cancellation on the following frame.
  scene = state.ccnc_0x162
  cam.dat[0x162] = bytes(32)
  cam.vl["CCNC_0x162"] = scene
  for active in (1, 0):
    stamp += 50_000_000
    cam._last_update_nanos = stamp
    for name in ("CCNC_0x162", "ADRV_0x161"):
      cam.ts_nanos[name] = {"COUNTER": stamp}
    stock.update(ALERTS_3=21*active, ALERTS_5=11*active, SOUNDS_3=3*active, LANE_HIGHLIGHT=active)
    scene.update(FF_DETECT=7*active, FF_DISTANCE=20*active, FF_DETECT_ALT=3*active, FF_DISTANCE_ALT=35*active,
                 SIGNS=8*active, FAULT_HDA=active)
    msgs = hyundaicanfd.create_ccnc_messages(cp, packer, SimpleNamespace(ECAN=0, CAM=2), 10, control, state,
                                             control.hudControl, 0, False, False, 2, False, 0, 0, now_nanos=stamp)
    frames = {addr: data for addr, data, _ in msgs}
    for key in ("ALERTS_3", "ALERTS_5", "SOUNDS_3", "LANE_HIGHLIGHT"):
      assert raw(0x161, key) == stock[key]
    for key in ("SIGNS", "FF_DETECT_ALT", "FAULT_HDA"):
      assert raw(0x162, key) == scene[key]
    assert raw(0x162, "FF_DETECT") == (7 if active else 3)
    for enabled, elapsed, visible in ((True, 0, True), (False, 0, False), (True, 150_000_001, False)):
      scene.update(SIGNS=9, SPEEDLIMIT=60, SPEEDLIMIT_FLASH=2, SPEEDLIMIT_WEATHER=1)
      msgs = hyundaicanfd.create_ccnc_messages(cp, packer, SimpleNamespace(ECAN=0, CAM=2), 10, control, state,
        control.hudControl, 0, False, False, 2, False, 0, 0, now_nanos=stamp+elapsed, show_stock_signs=enabled)
      frames = {addr: data for addr, data, _ in msgs}
      for key in ("SIGNS", "SPEEDLIMIT", "SPEEDLIMIT_FLASH", "SPEEDLIMIT_WEATHER"):
        assert raw(0x162, key) == (scene[key] if visible else 0)
