"""ACAN lane loss must not disable camera longitudinal control."""
import time
from unittest.mock import Mock

import pytest

from opendbc.can import CANPacker
from opendbc.car import Bus, structs
from opendbc.car.hyundai import carstate, hyundaicanfd
from opendbc.car.hyundai.radar_interface import get_radar_can_parser_scc
from opendbc.car.hyundai.values import CAR, DBC, HyundaiFlags


@pytest.fixture
def make_parsers(monkeypatch):
  params = Mock()
  params.get_int.return_value = 0
  params.get_bool.return_value = False
  params.get.return_value = repr({bus: {} for bus in range(8)})
  monkeypatch.setattr(carstate, 'Params', lambda: params)
  monkeypatch.setattr(hyundaicanfd, 'Params', lambda: params)

  def make(camera_scc=True, longitudinal=True, offset=0):
    flags = HyundaiFlags.CANFD | HyundaiFlags.CANFD_ALT_BUTTONS
    if camera_scc:
      flags |= HyundaiFlags.CAMERA_SCC
    cp = structs.CarParams(carFingerprint=CAR.KIA_CARNIVAL_4TH_GEN, flags=int(flags),
                          openpilotLongitudinalControl=longitudinal, safetyConfigs=[{}] * (2 if offset else 1))
    state = carstate.CarState(cp)
    parsers = state.get_can_parsers(cp)
    for parser in parsers.values():
      parser.controls_ready = True
    state.controls_ready_count = 124
    return state, parsers, CANPacker(DBC[cp.carFingerprint][Bus.pt])

  return make


def register_lanes(state, parsers, packer, names, bus, now):
  packets = [packer.make_can_msg(name, bus, {}) for name in names]
  for parser in parsers.values():
    parser.update([(now, packets)])
  state.monitor_fingerprint(parsers, True)


@pytest.mark.parametrize('names', [('CAM_0x2a4',), ('CAM_0x362',), ('CAM_0x2a4', 'CAM_0x362')])
@pytest.mark.parametrize('offset', [0, 4])
def test_acan_lane_loss_and_recovery_keep_vehicle_and_scc_checks(make_parsers, names, offset):
  state, parsers, packer = make_parsers(offset=offset)
  alt, pt, cam = parsers[Bus.alt], parsers[Bus.pt], parsers[Bus.cam]
  assert alt.bus == 1 + offset
  pt._add_message('TCS', 50)
  pt._add_message('MDPS', 100)
  radar = get_radar_can_parser_scc(state.CP)
  assert radar.bus == cam.bus == 2 + offset
  now = time.monotonic_ns()
  register_lanes(state, parsers, packer, names, alt.bus, now)

  def tick(include_lanes=False, missing=None):
    nonlocal now
    now += 20_000_000
    packets = [packer.make_can_msg(name, bus, {}) for name, bus in
               [('TCS', pt.bus), ('MDPS', pt.bus), ('SCC_CONTROL', cam.bus)] if name != missing]
    if include_lanes:
      packets += [packer.make_can_msg(name, alt.bus, {'LEFT_LANE_TYPE': 1}) for name in names]
    for parser in [*parsers.values(), radar]:
      parser.update([(now, packets)])
      # Match the interface's per-cycle validity evaluation and debounce.
      _ = parser.can_valid

  for _ in range(60):
    tick(include_lanes=True)
  stamp = alt.ts_nanos[names[0]]['LEFT_LANE_TYPE']
  assert getattr(state, names[0].lower())['LEFT_LANE_TYPE'] == 1
  for name in names:
    check = alt.message_states[alt.dbc.name_to_msg[name].address]
    assert check.ignore_alive
    assert not check.ignore_counter and not check.ignore_checksum

  # Exceed even the initial 10-second threshold with no ACAN frames at all.
  for _ in range(600):
    tick()
  assert all(parser.can_valid for parser in [*parsers.values(), radar])
  assert not any(parser.bus_timeout for parser in parsers.values())
  assert alt.ts_nanos[names[0]]['LEFT_LANE_TYPE'] == stamp  # No fabricated freshness.
  tick(include_lanes=True)
  assert alt.ts_nanos[names[0]]['LEFT_LANE_TYPE'] > stamp

  # Necessary body and SCC streams remain mandatory independently of ACAN lanes.
  for missing, parser in [('TCS', pt), ('MDPS', pt), ('SCC_CONTROL', radar)]:
    for _ in range(30):
      tick(missing=missing)
    assert not parser.can_valid, missing
    for _ in range(30):
      tick()
    assert parser.can_valid


@pytest.mark.parametrize('camera_scc,longitudinal,lane_bus,optional', [
  (True, True, Bus.alt, True),
  (True, True, Bus.cam, False),
  (True, False, Bus.alt, False),
  (False, True, Bus.alt, False),
])
@pytest.mark.parametrize('name', ['CAM_0x2a4', 'CAM_0x362'])
def test_lane_timeout_policy_is_scoped(make_parsers, camera_scc, longitudinal, lane_bus, optional, name):
  state, parsers, packer = make_parsers(camera_scc, longitudinal)
  parser = parsers[lane_bus]
  now = time.monotonic_ns()
  register_lanes(state, parsers, packer, [name], parser.bus, now)
  check = parser.message_states[parser.dbc.name_to_msg[name].address]
  assert check.ignore_alive == optional
  for _ in range(6):
    parser.update([(now + 20_000_000_000, [])])
    valid = parser.can_valid
  assert valid == optional
  assert parser.bus_timeout != optional


def test_unseen_acan_lanes_are_not_registered(make_parsers):
  state, parsers, _ = make_parsers()
  state.monitor_fingerprint(parsers, True)
  alt = parsers[Bus.alt]
  assert not alt.message_states
  assert alt.can_valid and not alt.bus_timeout
