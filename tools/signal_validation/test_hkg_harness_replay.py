"""Run against local, authorized PLATFORM.segment.rlog files (zstd or bzip2).
HKG_ACTIVE_PROBE=recorded checks donor commands. Use generated to replay
carControl through the target controller. HKG_PREROLL=1 includes an adjacent
PLATFORM.previous-segment.pre. Both probes run entirely in memory.
"""
import bz2
from collections import Counter
import os
from pathlib import Path

import pytest
import zstandard

from openpilot.cereal import log
from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.fw_versions import match_fw_to_car
from opendbc.car.hyundai import carcontroller, carstate, interface
from opendbc.car.hyundai.tests.test_experimental_longitudinal import configure_params
from opendbc.car.hyundai.values import CAR, CCNC_PORT_CAR, DBC, HyundaiFlags, HyundaiSafetyFlags
from opendbc.safety.tests.libsafety import libsafety_py


def harness_logs():
  directory = os.environ.get("HKG_REPLAY_DIR")
  if directory is None:
    return [pytest.param(None, marks=pytest.mark.skip(reason="set HKG_REPLAY_DIR for recorded replay"))]
  files = sorted(Path(directory).glob("*.*.rlog"))
  if os.environ.get("HKG_PREROLL") == "1":
    files = [p for p in files if previous_segment(p).is_file()]
  if not files:
    raise ValueError(f"No PLATFORM.segment.rlog files in {directory}")
  return files


def previous_segment(path):
  model, segment, _ = path.name.split(".")
  return path.with_name(f"{model}.{int(segment)-1}.pre")


def read_events(path):
  with path.open("rb") as f:
    raw = bz2.decompress(f.read()) if f.peek(3)[:3] == b"BZh" else zstandard.ZstdDecompressor().stream_reader(f).read()
  return sorted((e for e in log.Event.read_multiple_bytes(raw)
                 if e.which() in ("carParams", "carState", "carControl", "modelV2", "can", "sendcan")), key=lambda e: e.logMonoTime)


def candidate_active_hooks(cp, recorded):
  # Donor and target numeric safety bits have different meanings. These
  # public fixtures use the classic or non-HDA2 front camera harness only.
  mode = structs.CarParams.SafetyModel.hyundai
  flags = 0
  if cp.flags & HyundaiFlags.CANFD:
    assert cp.flags & HyundaiFlags.CANFD_CAMERA_SCC and not cp.flags & HyundaiFlags.CANFD_HDA2
    mode = structs.CarParams.SafetyModel.hyundaiCanfd
    flags |= HyundaiSafetyFlags.CAMERA_SCC
  if cp.flags & HyundaiFlags.HYBRID:
    flags |= HyundaiSafetyFlags.HYBRID_GAS
  if cp.flags & HyundaiFlags.EV:
    flags |= HyundaiSafetyFlags.EV_GAS
  if cp.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
    flags |= HyundaiSafetyFlags.CANFD_ALT_BUTTONS
  if recorded.openpilotLongitudinalControl:
    flags |= HyundaiSafetyFlags.LONG
  return mode, int(flags)


@pytest.mark.parametrize("path", harness_logs(), ids=lambda p: p.name if p else "no-recording")
def test_recorded_harness(monkeypatch, path):
  model = CAR(path.name.split(".")[0])
  events = read_events(path)
  recorded = next(e.carParams for e in events if e.which() == "carParams")
  assert recorded.carFingerprint == model
  fp = gen_empty_fingerprint()
  for e in events:
    if e.which() == "can":
      for m in e.can:
        if m.src in fp:
          fp[m.src][m.address] = len(m.dat)
  configure_params(monkeypatch, {"ControlsReady": True, "HDPuse": "0", "FingerPrints": repr(fp)})
  monkeypatch.setattr(carstate, "Params", interface.Params)
  assert match_fw_to_car(recorded.carFw, recorded.carVin, log=False) == (True, {model})
  cp = interface.CarInterface.get_params(model, fp, recorded.carFw, False, False, False)
  probe = os.environ.get("HKG_ACTIVE_PROBE", "")
  assert probe in ("", "recorded", "generated")
  controller = None
  if probe == "generated":
    # Test the unapproved active configuration only inside this offline process.
    cp.openpilotLongitudinalControl = recorded.openpilotLongitudinalControl
    cp.pcmCruise = not cp.openpilotLongitudinalControl
    monkeypatch.setattr(carcontroller, "Params", interface.Params)
    monkeypatch.setattr(interface.Params, "get_float", lambda self, key: 0.0, raising=False)
    controller = carcontroller.CarController(DBC[model], cp)
  state = carstate.CarState(cp)
  state.modelV2 = None
  state.radarState = None
  parsers = state.get_can_parsers(cp)

  cfg = cp.safetyConfigs[-1]
  mode, flags = candidate_active_hooks(cp, recorded) if probe else (cfg.safetyModel.raw, cfg.safetyParam)
  if not probe:
    assert cp.dashcamOnly and mode == structs.CarParams.SafetyModel.noOutput
  panda = libsafety_py.libsafety
  assert panda.set_safety_hooks(mode, flags) == 0

  start = next(e.logMonoTime for e in events if e.which() == "can")
  batches = [events]
  if os.environ.get("HKG_PREROLL") == "1":
    prior = read_events(previous_segment(path))
    assert next(e.carParams for e in prior if e.which() == "carParams").carFingerprint == model
    prior_end = next(e.logMonoTime for e in reversed(prior) if e.which() == "can")
    assert 0 <= start - prior_end < 500_000_000, "segments must be contiguous on the same vehicle clock"
    batches.insert(0, prior)
  has_car_state = False
  for batch in batches:
    batch_start = next(e.logMonoTime for e in batch if e.which() == "can")
    counts = Counter()
    blocked = Counter()
    blocked_while_allowed = Counter()
    for e in batch:
      typ, t = e.which(), e.logMonoTime
      panda.set_timer((t // 1000) % 2**32)
      if typ in ("can", "sendcan"):
        rows = []
        for m in getattr(e, typ):
          if m.src >= 128:
            continue
          assert m.src < 4, "multi-Panda recordings need explicit bus mapping"
          data = bytes(m.dat)
          pkt = libsafety_py.make_CANPacket(m.address, m.src, data)
          if typ == "can":
            counts["rx"] += 1
            counts["invalid_rx"] += not panda.safety_rx_hook(pkt)
            rows.append((m.address, data, m.src))
          else:
            counts["tx"] += 1
            if controller is not None:
              continue
            accepted = panda.safety_tx_hook(pkt)
            counts["accepted_tx"] += bool(accepted)
            if probe and not accepted:
              blocked[m.address] += 1
              if panda.get_controls_allowed():
                blocked_while_allowed[m.address] += 1
        if typ == "can":
          for parser in parsers.values():
            parser.update([(t, rows)])
      elif typ == "modelV2":
        state.modelV2 = e.modelV2
      elif typ == "carControl" and controller is not None and has_car_state:
        _, outgoing = controller.update(e.carControl, state, t)
        for addr, data, bus in outgoing:
          if model in CCNC_PORT_CAR:
            assert addr not in (0xea, 0x175, 0x2af), "original MDPS, TCS and hands-on feedback belong to the vehicle"
          counts["generated"] += 1
          if not panda.safety_tx_hook(libsafety_py.make_CANPacket(addr, bus, data)):
            blocked[addr] += 1
            if panda.get_controls_allowed():
              blocked_while_allowed[addr] += 1
      elif typ == "carState":
        has_car_state = True
        counts["car_states"] += 1
        current = state.update(parsers)
        current.canValid = all(p.can_valid for p in parsers.values())
        state.out = current.as_reader()
        if t - batch_start <= 3_000_000_000:
          continue
        counts["states"] += 1
        counts["engaged"] += current.cruiseState.enabled
        counts["cruise_diff"] += current.cruiseState.enabled != e.carState.cruiseState.enabled
        counts["gear_diff"] += current.gearShifter != e.carState.gearShifter
        counts["brake_diff"] += current.brakePressed != e.carState.brakePressed
        counts["invalid_can"] += not current.canValid
        if probe:
          panda.safety_tick_current_safety_config()
          counts["invalid_tick"] += not panda.safety_config_valid()

  print(path.name, dict(counts), "blocked", dict(blocked), "while allowed", dict(blocked_while_allowed))
  assert counts["rx"] > 0 and counts["tx"] > 0 and counts["states"] > 100
  assert counts["invalid_can"] == counts["invalid_rx"] == 0
  # Independent publishers can straddle a pedal/SET edge by one host tick.
  for field in ("cruise_diff", "gear_diff", "brake_diff"):
    assert counts[field] / counts["states"] < 0.005, (field, counts)
  if controller is not None:
    assert counts["generated"] > 0
  if probe:
    assert not blocked and not counts["invalid_tick"], (blocked, counts)
  else:
    assert counts["accepted_tx"] == 0, counts
