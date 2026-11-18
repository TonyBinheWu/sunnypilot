"""Low-rate research subscriber. Consent is independent from logs and raw video."""

from collections import OrderedDict, deque
import json
import os
from pathlib import Path
import tempfile
import threading
import time

from .identity import read
from .protocol import sign
from .road_scene import SCHEMA, model_scene
from .service_policy import self_hosted_origin

SHARED = Path("/dev/shm/formosa-road-scenes")
SERVICES = ["modelV2", "carState", "radarState", "liveCalibration", "gpsLocation", "gpsLocationExternal"]


def publish(path, data):
  path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
  with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as out:
    name = out.name
    try:
      json.dump(data, out, allow_nan=False)
    except BaseException:
      out.close()
      os.unlink(name)
      raise
  try:
    os.replace(name, path)
  finally:
    Path(name).unlink(missing_ok=True)


def read_small(path, limit):
  try:
    with path.open("rb") as stream:
      raw = stream.read(limit + 1)
    return json.loads(raw) if len(raw) <= limit else None
  except (OSError, ValueError):
    return None


def active_lease(root=SHARED):
  value = read_small(root / "lease", 512)
  if isinstance(value, dict) and 0 < value.get("until", 0) - time.monotonic() <= 46:
    return value
  return None


class Snapshot(dict):
  """Immutable service readers and their receive clocks at one model tick."""


class SceneBuffer:
  """Hold native snapshots briefly so delayed image inference can match its actual frame."""

  def __init__(self):
    self.frames = OrderedDict()
    self.chosen = set()
    self.next_sample = 0

  def add(self, sm, now_ns):
    model = sm["modelV2"]
    if not sm.updated["modelV2"] or not sm.valid["modelV2"] or not 0 <= now_ns - model.timestampEof < 500_000_000:
      return
    key = (model.frameId, model.timestampEof)
    if key in self.frames:
      return

    data = Snapshot((name, sm[name]) for name in SERVICES)
    data.updated = {"modelV2": True}
    data.logMonoTime = dict(sm.logMonoTime)
    data.valid = dict(sm.valid)
    self.frames[key] = (data, now_ns, [])
    if now_ns >= self.next_sample:
      self.chosen.add(key)
      self.next_sample = now_ns + 1_000_000_000

  def camera(self, packet):
    key = packet["frame"], packet["eof"]
    row = self.frames.get(key)
    if row is not None:
      packets = row[2]
      if not any(p["detector"] == packet["detector"] for p in packets):
        packets.append(packet)
      self.chosen.add(key)

  def ready(self, now_ns):
    while self.frames:
      key = next(iter(self.frames))
      data, captured, packets = self.frames[key]
      if now_ns - captured < 2_100_000_000 and len(self.frames) <= 64:
        break
      del self.frames[key]
      if key in self.chosen:
        self.chosen.remove(key)
        scene = model_scene(data, captured)
        if scene is not None:
          scene["camera"] = packets
          yield scene


def sample(stop, lock, queue, grant, root):
  from openpilot.cereal import messaging

  buffer = sm = current = None
  while not stop.is_set():
    with lock:
      revision, until = grant
    if not revision or time.monotonic() >= until:
      buffer = sm = current = None
      stop.wait(0.5)
      continue
    if current != revision:
      buffer = SceneBuffer()
      sm = messaging.SubMaster(SERVICES, poll="modelV2")
      current = revision
      started_ns = time.monotonic_ns()
      fix_at = 0
    sm.update(100)
    now_ns = time.monotonic_ns()
    if not sm.updated["modelV2"] or sm["modelV2"].timestampEof < started_ns:
      continue
    buffer.add(sm, now_ns)
    if now_ns >= fix_at:
      fix_at = now_ns + 500_000_000
      current_scene = model_scene(sm, now_ns)
      fix = current_scene["fix"] if current_scene and current_scene["calibrated"] else None
      publish(root / "position", {"eof": sm["modelV2"].timestampEof, "fix": fix, "revision": revision})
    for detector in ("efficientdet", "road"):
      obs = read_small(root / detector, 8192)
      if isinstance(obs, dict) and obs.get("revision") == revision:
        buffer.camera(obs["packet"])
    for entry in buffer.ready(now_ns):
      with lock:
        if grant[0] == revision and time.monotonic() < grant[1]:
          queue.append(entry)


def run(directory, stop):
  import requests

  identity, private, _ = read(directory)
  origin = self_hosted_origin(identity["origin"])
  boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
  with requests.Session() as http:
    http.trust_env = False

    def call(payload):
      response = http.post(
        origin + "/api/v1/agent/road-scenes",
        json=sign(private, identity["device_id"], "road-scenes", payload),
        timeout=(3, 4),
        allow_redirects=False,
      )
      try:
        response.raise_for_status()
        result = response.json()
        if result["schema"] != SCHEMA or type(result["enabled"]) is not bool or type(result["revision"]) is not int:
          raise ValueError("unsupported scene grant")
        return result
      finally:
        response.close()

    pending = deque(maxlen=90)
    lock = threading.Lock()
    grant_state = [None, 0.0]
    end = threading.Event()
    collector = threading.Thread(target=sample, args=(end, lock, pending, grant_state, SHARED), daemon=True)
    collector.start()
    try:
      sync_loop(stop, call, pending, lock, grant_state, boot, collector)
    finally:
      end.set()
      collector.join(2)


def sync_loop(stop, call, pending, lock, grant_state, boot, collector):
  import requests

  revision = None
  until = sync_at = send_at = 0.0
  while not stop.is_set():
    if not collector.is_alive():
      raise RuntimeError("scene subscriber stopped")
    now = time.monotonic()
    if now >= sync_at:
      sync_at = now + 30
      try:
        grant = call({"operation": "status"})
        new = grant["revision"] if grant["enabled"] else None
        with lock:
          if revision != new:
            pending.clear()
          revision = new
          until = now + 45 if new is not None else 0
          grant_state[:] = [revision, until]
        if revision is not None:
          publish(SHARED / "lease", {"revision": revision, "until": until})
      except (OSError, ValueError, KeyError, requests.RequestException):
        sync_at = now + 10
    if not revision or now >= until:
      with lock:
        grant_state[:] = [None, 0.0]
        pending.clear()
      (SHARED / "lease").unlink(missing_ok=True)
      for detector in ("efficientdet", "road", "position", "map"):
        (SHARED / detector).unlink(missing_ok=True)
      stop.wait(2)
      continue
    with lock:
      batch = list(pending)[:8]
    if batch and now >= send_at:
      send_at = now + 2
      try:
        ack = call(dict(revision=revision, boot=boot, samples=batch))
        if ack["revision"] != revision or not ack["enabled"]:
          raise ValueError("grant changed")
        if ack.get("map"):
          publish(SHARED / "map", {"map": ack["map"], "revision": revision, "expires": time.monotonic() + 20})
        with lock:
          while pending and pending[0]["eof"] <= batch[-1]["eof"]:
            pending.popleft()
      except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code in (403, 404):
          with lock:
            pending.clear()
            grant_state[:] = [None, 0.0]
          until = 0
          sync_at = 0
      except (OSError, ValueError, KeyError, requests.RequestException):
        pass
    stop.wait(1)


def start(directory, stop):
  def supervise():
    while not stop.is_set():
      try:
        run(directory, stop)
      except Exception:
        # Identity and cereal services can appear after agent startup.
        stop.wait(30)
      finally:
        (SHARED / "lease").unlink(missing_ok=True)

  threading.Thread(target=supervise, name="formosa-road-scenes", daemon=True).start()
