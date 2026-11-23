import copy
from types import SimpleNamespace

import pytest

from opendbc.can import CANDefine, CANPacker
from opendbc.can.parser import get_raw_value
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


@pytest.mark.parametrize("age,visible", [(0, True), (150_000_000, True), (150_000_001, False), (-1, False)])
def test_ev6_non_camera_scc_hidden_corner_packet(age, visible):
  name = "ADRV_0x1ea"
  source = {}
  for side, kind, distance in [("LF", 4, 12.3), ("RF", 2, 5.2), ("LR", 0, 7), ("RR", 4, 0)]:
    source.update({f"{side}_DETECT": kind, f"{side}_DETECT_DISTANCE": distance, f"{side}_DETECT_LATERAL": 1.2})
  parser = SimpleNamespace(ts_nanos={name: {"COUNTER": 100}}, _last_update_nanos=100+age,
                           dat={0x1EA: bytes(32)}, vl={name: source})
  cp = SimpleNamespace(flags=HyundaiFlags.CANFD_HDA2, carFingerprint=hyundaicanfd.CAR.KIA_EV6)
  def packet(cam):
    packer = CANPacker("hyundai_canfd_generated")
    msgs = hyundaicanfd.create_adrv_messages(cp, packer, SimpleNamespace(ECAN=1), 5, cam)
    assert len(msgs) == 2
    addr, data, bus = msgs[0]
    assert (addr, bus) == (0x1EA, 1)
    return {k: get_raw_value(data, sig) * sig.factor + sig.offset for k, sig in packer.dbc.name_to_msg[name].sigs.items()}
  expected = packet(None)
  if visible:
    expected.update(LF_DETECT=1, RF_DETECT=2, LF_DETECT_DISTANCE=12.3, RF_DETECT_DISTANCE=5.2,
                    LF_DETECT_LATERAL=1.2, RF_DETECT_LATERAL=1.2)
  actual = packet(parser)
  del actual["CHECKSUM"], expected["CHECKSUM"]
  assert actual == pytest.approx(expected)



def test_ev6_adas_display_uses_physical_ecan_rx():
  from opendbc.can.parser import CANParser
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

@pytest.mark.parametrize("age,fault,expected", [(100_000_000, False, 1), (250_000_001, False, 0), (0, True, 0)])
def test_ev6_adas_neighbor_fallback(age, fault, expected):
  packer = CANPacker("hyundai_canfd_generated")
  stamp = 1_000_000_000
  source = {"HDA_MODE2": 5, "AUTOLANECHANGE_MSG": 8}
  for side in ("LF", "RF", "LR", "RR"):
    source.update({f"{side}_DETECT": 2 if side == "LF" else 0,
                   f"{side}_DETECT_DISTANCE": 9, f"{side}_DETECT_LATERAL": 2})
  parser = SimpleNamespace(ts_nanos={"ADRV_0x1ea": {"COUNTER": stamp}}, _last_update_nanos=stamp,
                           dat={0x1EA: bytes(32)}, vl={"ADRV_0x1ea": source})
  def lead(d, y):
    return SimpleNamespace(status=True, radar=True, dRel=d, yRel=y)
  radar = SimpleNamespace(mdMonoTime=stamp, leadsLeft=[lead(3, 3)], leadsRight=[lead(1, 3), lead(24, -3), lead(7, -2)],
                          radarErrors=SimpleNamespace(canError=fault, radarFault=False, wrongConfig=False, radarUnavailableTemporary=False))
  cp = SimpleNamespace(flags=HyundaiFlags.CANFD_HDA2, carFingerprint=hyundaicanfd.CAR.KIA_EV6)
  msg = hyundaicanfd.create_adrv_messages(cp, packer, SimpleNamespace(ECAN=1), 5, parser, radar=radar, now_nanos=stamp+age)[0]
  values = {k: get_raw_value(msg[1], sig) * sig.factor + sig.offset for k, sig in packer.dbc.name_to_msg["ADRV_0x1ea"].sigs.items()}
  assert (values["HDA_MODE2"], values["AUTOLANECHANGE_MSG"]) == (5, 8)
  assert (values["LF_DETECT"], values["LF_DETECT_DISTANCE"]) == (2, 9)
  assert (values["RF_DETECT"], values["RF_DETECT_DISTANCE"], values["RF_DETECT_LATERAL"]) == (expected, 7*expected, 2*expected)
  assert values["LR_DETECT"] == values["RR_DETECT"] == 0
