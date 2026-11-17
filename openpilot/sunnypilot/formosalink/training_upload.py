"""Low-priority, parked-only, consent-gated upload of closed logger segments."""
import base64
import hashlib
import json
import logging
import os
from pathlib import Path
import threading
import time
import uuid

from openpilot.sunnypilot.formosalink.identity import default_directory, read
from openpilot.sunnypilot.formosalink.protocol import sign
from openpilot.sunnypilot.formosalink.service_policy import self_hosted_origin
from openpilot.sunnypilot.formosalink.training_protocol import CHUNK_BYTES, FILES, NOTICE, POLICY, digest_file

_LOCK = threading.RLock()


def local_state(directory=None):
  try:
    return json.loads((Path(directory or default_directory()) / "training-consent.json").read_text())
  except (OSError, ValueError):
    return {"enabled": False, "revision": 0, "granted": 0, "pending": None}


def save_state(directory, value):
  path = Path(directory) / "training-consent.json"
  path.parent.mkdir(parents=True, exist_ok=True)
  temporary = path.with_suffix(".tmp")
  with temporary.open("w", encoding="utf-8") as stream:
    os.chmod(temporary, 0o600)
    json.dump(value, stream)
    stream.flush()
    os.fsync(stream.fileno())
  os.replace(temporary, path)


def consent_revision(state):
  value={key:state.get(key) for key in ('enabled','revision','pending')}
  return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def choose(enabled, directory=None, *, expected_revision=None):
  if type(enabled) is not bool:
    raise ValueError("consent must be an explicit boolean")
  directory = directory or default_directory()
  with _LOCK:
    state = local_state(directory)
    if expected_revision is not None and expected_revision!=consent_revision(state):
      raise ValueError('consent_changed')
    state["pending"] = {"enabled": enabled, "expected_revision": state["revision"], "policy": POLICY,
                        "id": hashlib.sha256(uuid.uuid4().bytes).hexdigest(), "granted_at": time.time()}
    # A local revocation takes effect before the network acknowledges it.
    state["enabled"] = False
    save_state(directory, state)
  return state


def eligible_segments(log_root, granted, now=None):
  now = time.time() if now is None else now
  root = Path(log_root).resolve()
  for folder in sorted(root.iterdir()):
    if not folder.is_dir() or folder.is_symlink() or "--" not in folder.name:
      continue
    # loggerd holds lock files while a segment is being written.
    if list(folder.glob("*.lock")):
      continue
    files = {path.name: path for path in folder.iterdir() if path.name in FILES and path.is_file() and not path.is_symlink()}
    if not {"fcamera.hevc", "ecamera.hevc"} <= files.keys() or not files.keys() & {"rlog", "rlog.zst", "rlog.bz2"}:
      continue
    if any(path.stat().st_mtime > now - 120 or path.stat().st_mtime < granted for path in files.values()):
      continue
    yield folder, files


def segment_started_at(rlog):
  """Map a recorded monotonic timestamp to the logger's measured Unix clock."""
  from openpilot.tools.lib.logreader import LogReader
  anchor=None
  for event in LogReader(str(rlog)):
    kind=event.which()
    if kind=="initData" and event.initData.wallTimeNanos:
      anchor=(event.logMonoTime,event.initData.wallTimeNanos)
    elif anchor and kind in ("carState","narrowRoadCameraState","roadCameraState","wideRoadCameraState"):
      return (anchor[1]+event.logMonoTime-anchor[0])/1e9
  raise ValueError("recording clock anchor missing; cannot establish training authorization time")


class Uploader:
  def __init__(self, directory, log_root, parked, stop, session):
    self.directory, self.log_root, self.parked, self.stop, self.session = Path(directory), Path(log_root), parked, stop, session
    self.identity, self.private, _ = read(directory)
    self_hosted_origin(self.identity["origin"])
    self.journal = self.directory / "training-uploads.json"
    self.segment_times = {}
    try:
      self.completed = json.loads(self.journal.read_text())
    except (OSError, ValueError):
      self.completed = {}

  def call(self, operation, **fields):
    response = self.session.post(self.identity["origin"] + "/api/v1/agent/training",
      json=sign(self.private, self.identity["device_id"], "training", {"operation": operation, **fields}), timeout=(5, 30))
    try:
      response.raise_for_status()
      if len(response.content) > 65536:
        raise ValueError("oversized upload acknowledgement")
      return response.json()
    finally:
      response.close()

  def sync(self):
    with _LOCK:
      before = local_state(self.directory)
      choice = before.get("pending")
    result = self.call("sync", choice=choice)
    if result.get("policy") != POLICY:
      raise ValueError("contribution policy changed")
    with _LOCK:
      current = local_state(self.directory)
      # Do not overwrite a user choice made while this request was in flight.
      if current.get("pending") != choice:
        return current
      state = {**result["consent"], "enabled": bool(result["consent"]["enabled"]), "pending": None,
               "choice_conflict": result.get("choice_conflict", False)}
      save_state(self.directory, state)
      return state

  def allowed(self, revision):
    state = local_state(self.directory)
    return not self.stop.is_set() and self.parked() and state.get("enabled") is True and not state.get("pending") and state["revision"] == revision

  def once(self):
    consent = self.sync()
    revision = consent["revision"]
    if not self.allowed(revision) or not self.log_root.is_dir():
      return
    for folder, files in eligible_segments(self.log_root, consent["granted"]):
      # Bind split grouping to device + complete route, never adjacent segment IDs.
      route = folder.name.rsplit("--", 1)[0]
      group = hashlib.sha256((self.identity["device_id"] + route).encode()).hexdigest()
      segment = hashlib.sha256((self.identity["device_id"] + folder.name).encode()).hexdigest()
      if segment in self.completed:
        continue
      if folder.name not in self.segment_times:
        rlog=next(path for name,path in files.items() if name in ("rlog","rlog.zst","rlog.bz2"))
        self.segment_times[folder.name]=segment_started_at(rlog)
      if self.segment_times[folder.name]<consent["granted"]:
        continue  # exclude pre-authorization frames, including a segment spanning the choice
      for name, path in sorted(files.items()):
        if not self.allowed(revision):
          return
        stamp = (path.stat().st_size, path.stat().st_mtime_ns)
        checksum = digest_file(path)
        declaration = {"segment": segment, "filename": name, "sha256": checksum, "size": stamp[0], "consent_revision": revision}
        result = self.call("begin", file=declaration)
        upload_id = result["upload_id"]
        with path.open("rb") as stream:
          offset = result["offset"]
          while not result["complete"]:
            # Refresh server-side revocations between bounded chunks.
            consent = self.sync()
            if not self.allowed(revision) or consent["revision"] != revision:
              return
            if (path.stat().st_size, path.stat().st_mtime_ns) != stamp:
              raise ValueError("logger segment changed during upload")
            stream.seek(offset)
            raw = stream.read(CHUNK_BYTES)
            if not raw:
              raise ValueError("unexpected end of training file")
            result = self.call("chunk", chunk={"upload_id": upload_id, "offset": offset,
              "data": base64.b64encode(raw).decode(), "sha256": hashlib.sha256(raw).hexdigest(), "consent_revision": revision})
            offset = result["offset"]
            if self.stop.wait(0.2):
              return
        # Completion is acknowledged by the server, not by local file reads.
      if not self.allowed(revision):
        return
      self.call("finalize", segment={"segment": segment, "route_group": group, "consent_revision": revision})
      self.completed[segment] = time.time()
      self.completed = dict(sorted(self.completed.items(), key=lambda item: item[1])[-20000:])
      temporary = self.journal.with_suffix(".tmp")
      temporary.write_text(json.dumps(self.completed))
      os.replace(temporary, self.journal)
      return  # one closed segment per sweep, with backpressure


def run(directory, stop):
  import requests
  from openpilot.common.params import Params
  try:
    from openpilot.common.hardware.hw import Paths
  except ImportError:
    from openpilot.system.hardware.hw import Paths
  params = Params()
  while not stop.is_set():
    try:
      with requests.Session() as session:
        client = Uploader(directory, Paths.log_root(), lambda: params.get_bool("IsOffroad"), stop, session)
        while not stop.is_set():
          client.once()
          stop.wait(30)
    except Exception as exc:
      logging.getLogger("formosalink").info("Training upload waiting (%s)", type(exc).__name__)
      stop.wait(30)


def start(directory, stop):
  thread = threading.Thread(target=run, args=(directory, stop), name="training-upload", daemon=True)
  thread.start()
  return thread
