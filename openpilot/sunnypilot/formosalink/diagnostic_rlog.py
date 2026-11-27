"""Build and verify the small, identity-free subset of cereal used in error reports."""
import io
import json
import re
import struct
from functools import cache
from pathlib import Path

import capnp
import zstandard as zstd

ROOT = Path(__file__).resolve().parents[3]
UPLOAD_PATH = "/api/v1/diagnostics/rlog"
MAX_WIRE = 64 * 1024
MAX_CLEAR = 512 * 1024
MAX_SOURCE = 512 * 1024 * 1024
SECOND = 1_000_000_000
MAX_SECONDS = 180
FAULT_EVENTS = frozenset("""
  canError canBusMissing steerUnavailable steerTempUnavailable accFaulted radarFault radarTempUnavailable
  controlsMismatch cruiseMismatch relayMalfunction vehicleSensorsInvalid sensorDataInvalid commIssue commIssueAvgFreq
  processNotRunning cameraMalfunction cameraFrameRate modeldLagging selfdrivedLagging bigModelFailed
  carUnrecognized startupNoCar startupNoControl startupNoSecOcKey dashcamMode invalidLkasSetting
  excessiveActuation actuatorsApiUnavailable overheat lowMemory outOfSpace fanMalfunction
  calibrationInvalid locationdTemporaryError locationdPermanentError paramsdTemporaryError paramsdPermanentError
""".split())
EVENT_FLAGS = ("noEntry", "warning", "softDisable", "immediateDisable", "permanent")
CAR_FAULTS = ("accFaulted", "canTimeout", "steerFaultTemporary", "steerFaultPermanent", "vehicleSensorsInvalid", "carFaultedNonCritical")
PROCESSES = frozenset("card pandad controlsd selfdrived modeld plannerd radard camerad calibrationd locationd paramsd lagd torqued".split())
CHESTNUT_ALERTS = frozenset("Offroad_Chestnut" + suffix for suffix in
                            ("Branch", "NotDetected", "Overheated", "PcieUnavailable", "Uncompiled", "UpdateFailed", "UsbSlow"))


@cache
def platforms():
  catalog = ROOT / "opendbc_repo/opendbc/sunnypilot/car/car_list.json"
  return frozenset(row["platform"] for row in json.loads(catalog.read_text("utf-8")).values())


@cache
def server_schema():
  # The private IIS package and Docker image carry the exact same pinned schemas as the device.
  cereal = ROOT / "openpilot/cereal"
  return capnp.SchemaParser().load((cereal / "log.capnp").as_posix(),
                                   imports=[cereal.as_posix(), (ROOT / "opendbc_repo/opendbc/car").as_posix()])


def messages(stream, total_limit, message_limit):
  """Read standard (unpacked) Cap'n Proto frames without materializing the entire source rlog."""
  used = 0
  while head := stream.read(4):
    if len(head) != 4:
      raise ValueError("truncated segment count")
    segments = struct.unpack("<I", head)[0] + 1
    if segments > 64:
      raise ValueError("too many segments")
    table_size = (segments + (segments % 2 == 0)) * 4
    table = stream.read(table_size)
    if len(table) != table_size:
      raise ValueError("truncated segment table")
    size = sum(struct.unpack_from(f"<{segments}I", table)) * 8
    used += 4 + table_size + size
    if size == 0 or size > message_limit or used > total_limit:
      raise ValueError("invalid message size")
    data = stream.read(size)
    if len(data) != size:
      raise ValueError("truncated message")
    yield head + table + data


def project(event):
  """Copy only named fields into plain values. No raw pointer, free text or extension survives."""
  kind = event.which()
  faults = set()
  if kind == "initData":
    src = event.initData
    if src.gitBranch != "ccnc-port":
      raise ValueError("different release")
    data = {"gitBranch": "ccnc-port"}
    if re.fullmatch(r"[0-9a-f]{40}", src.gitCommit):
      data["gitCommit"] = src.gitCommit
    if len(src.params.entries) > 4096:
      raise ValueError("too many parameters")
    faults = {entry.key for entry in src.params.entries if entry.key in CHESTNUT_ALERTS and entry.value}
    if faults:
      data["params"] = {"entries": [{"key": key, "value": b"1"} for key in sorted(faults)]}
  elif kind == "carParams":
    car = event.carParams
    data = {key: getattr(car, key) for key in ("pcmCruise", "openpilotLongitudinalControl", "dashcamOnly")}
    if car.carFingerprint in platforms():
      data["carFingerprint"] = car.carFingerprint
  elif kind == "carState":
    car = event.carState
    data = {key: getattr(car, key) for key in (*CAR_FAULTS, "canValid", "stockAeb", "stockFcw")}
    data["cruiseState"] = {"enabled": car.cruiseState.enabled, "available": car.cruiseState.available}
    faults = {key for key in CAR_FAULTS if data[key]}
  elif kind in ("onroadEvents", "onroadEventsSP"):
    events = event.onroadEvents if kind == "onroadEvents" else event.onroadEventsSP.events
    if len(events) > 128:
      raise ValueError("too many events")
    allowed = FAULT_EVENTS if kind == "onroadEvents" else {"controlsMismatchLateral"}
    rows = []
    for entry in events:
      name = str(entry.name)
      if name in allowed:
        faults.add(name)
        rows.append({"name": name, **{key: getattr(entry, key) for key in EVENT_FLAGS}})
    if not rows:
      return None
    data = rows if kind == "onroadEvents" else {"events": rows}
  elif kind == "pandaStates":
    if len(event.pandaStates) > 4:
      raise ValueError("too many pandas")
    data = []
    for panda in event.pandaStates:
      status = str(panda.faultStatus)
      if len(panda.faults) > 32:
        raise ValueError("too many panda faults")
      codes = [str(code) for code in panda.faults]
      if status != "none":
        faults.add(status)
      faults.update(codes)
      data.append({"faultStatus": status, "faults": codes, "safetyRxChecksInvalid": panda.safetyRxChecksInvalid,
                   "controlsAllowed": panda.controlsAllowed, "safetyModel": str(panda.safetyModel)})
  elif kind == "managerState":
    if len(event.managerState.processes) > 256:
      raise ValueError("too many processes")
    rows = []
    for proc in event.managerState.processes:
      if proc.name in PROCESSES and proc.shouldBeRunning and not proc.running and proc.exitCode:
        rows.append({"name": proc.name, "shouldBeRunning": True, "exitCode": max(-255, min(255, proc.exitCode))})
        faults.add(proc.name)
    if not rows:
      return None
    data = {"processes": rows}
  else:
    return None
  return data, faults


def encode(schema, kind, timestamp, valid, values):
  return schema.Event.new_message(logMonoTime=timestamp, valid=valid, **{kind: values}).to_bytes()


def extract(path, schema):
  """Return one sanitized rlog for a closed fault segment, or None for a healthy segment."""
  start = header = None
  samples = {}
  reasons = set()
  ended = False
  if path.stat().st_size > 96 * 1024 * 1024:
    raise ValueError("oversized source")
  with path.open("rb") as source, zstd.ZstdDecompressor(max_window_size=128 * 1024).stream_reader(source) as reader:
    with io.BufferedReader(reader) as stream:
      for frame in messages(stream, MAX_SOURCE, 32 * 1024 * 1024):
        with schema.Event.from_bytes(frame) as event:
          kind = event.which()
          if kind == "initData":
            if header is not None:
              raise ValueError("duplicate release")
            values, header_faults = project(event)
            reasons.update(header_faults)
            header = encode(schema, kind, 0, event.valid, values)
          elif kind == "sentinel":
            marker = str(event.sentinel.type)
            if marker in ("startOfRoute", "startOfSegment"):
              start = event.logMonoTime
            ended = marker in ("endOfRoute", "endOfSegment")
          elif start is not None:
            tick = max(0, event.logMonoTime - start) // SECOND
            if tick > MAX_SECONDS or kind not in ("carState", "carParams", "onroadEvents", "onroadEventsSP", "pandaStates", "managerState"):
              continue
            key = (tick, kind)
            # carState is logged at 100 Hz. Keep the first state and any new fault in this second.
            if kind == "carState" and key in samples:
              car = event.carState
              if not any(getattr(car, flag) and flag not in samples[key][1] for flag in CAR_FAULTS):
                continue
            projected = project(event)
            if projected is not None:
              values, faults = projected
              if key not in samples or faults - samples[key][1]:
                samples[key] = (encode(schema, kind, tick * SECOND, event.valid, values), faults)
  if not ended or header is None or start is None:
    raise ValueError("incomplete segment")
  for _, faults in samples.values():
    reasons.update(faults)
  if not reasons:
    return None
  raw = header + b"".join(samples[key][0] for key in sorted(samples))
  if len(raw) > MAX_CLEAR:
    raise ValueError("oversized diagnostic extract")
  payload = zstd.ZstdCompressor(level=3).compress(raw)
  if len(payload) > MAX_WIRE:
    raise ValueError("oversized compressed extract")
  return payload, sorted(reasons)


def verify_report(payload):
  """Only accept our canonical cereal subset. Store a fresh compression of verified bytes."""
  if not 0 < len(payload) <= MAX_WIRE:
    raise ValueError("invalid report size")
  size = zstd.frame_content_size(payload)
  if not 0 < size <= MAX_CLEAR or zstd.get_frame_parameters(payload).window_size > MAX_CLEAR:
    raise ValueError("invalid frame size")
  raw = zstd.ZstdDecompressor().decompress(payload, max_output_size=MAX_CLEAR, allow_extra_data=False)
  schema = server_schema()
  reasons = set()
  previous = None
  revision = platform = ""
  for frame in messages(io.BytesIO(raw), MAX_CLEAR, 16 * 1024):
    with schema.Event.from_bytes(frame, traversal_limit_in_words=8192, nesting_limit=16) as event:
      kind, timestamp = event.which(), event.logMonoTime
      if (previous is None) != (kind == "initData") or timestamp > MAX_SECONDS * SECOND or timestamp % SECOND:
        raise ValueError("invalid report timeline")
      if kind == "initData":
        if timestamp:
          raise ValueError("invalid header time")
      elif previous is not None and (timestamp, kind) <= previous:
        raise ValueError("duplicate or unordered sample")
      projected = project(event)
      if projected is None:
        raise ValueError("unexpected sample")
      values, faults = projected
      if encode(schema, kind, timestamp, event.valid, values) != frame:
        raise ValueError("unexpected data")
      if kind == "initData":
        revision = values.get("gitCommit", "")
      if kind == "carParams":
        platform = values.get("carFingerprint", "")
      reasons.update(faults)
      previous = (timestamp, "" if kind == "initData" else kind)
  if not reasons:
    raise ValueError("missing fault")
  return zstd.ZstdCompressor(level=3).compress(raw), sorted(reasons), revision, platform
