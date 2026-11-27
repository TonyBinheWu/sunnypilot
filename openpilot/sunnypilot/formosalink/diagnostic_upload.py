"""Parked, opt-in uploads. This process does not load pairing keys or contact other services."""
import json
import os
import re
import secrets
import sqlite3
import time
from contextlib import closing
from pathlib import Path

from openpilot.sunnypilot.formosalink.identity import default_directory

CONSENT = "FormosaLinkDiagnosticConsent"
RECEIPT = "FormosaLinkDiagnosticReceipt"
DAY = 86400
MAX_PENDING = 32


def valid_consent(value):
  return isinstance(value, str) and re.fullmatch(r"[1-9][0-9]{17,19}", value) is not None


def queue_path(directory, consent):
  if not valid_consent(consent):
    raise ValueError("invalid consent")
  return Path(directory) / "diagnostics" / (consent + ".sqlite3")


def set_consent(params, enabled, directory=None):
  old = params.get(CONSENT)
  if enabled:
    if not valid_consent(old):
      params.remove(RECEIPT)
      params.put(CONSENT, str(time.time_ns()), block=True)
  else:
    params.remove(CONSENT)
    params.remove(RECEIPT)
    if valid_consent(old):
      path = queue_path(directory or default_directory(), old)
      # The parked worker holds the database open. SQLite serializes erasure with queue writes.
      if path.exists():
        with closing(sqlite3.connect(path)) as db, db:
          db.execute("PRAGMA secure_delete=ON")
          db.execute("DROP TABLE IF EXISTS segments")
          db.execute("DROP TABLE IF EXISTS retry")
        path.unlink(missing_ok=True)


class Queue:
  def __init__(self, directory, consent):
    self.consent = consent
    path = queue_path(directory, consent)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    self.db = sqlite3.connect(path)
    with self.db:
      self.db.execute("""CREATE TABLE IF NOT EXISTS segments (
        source TEXT PRIMARY KEY, stamp INTEGER NOT NULL, route TEXT NOT NULL, reasons TEXT NOT NULL,
        receipt TEXT, payload BLOB)""")
      self.db.execute("CREATE INDEX IF NOT EXISTS route_reasons ON segments(route,reasons)")
      self.db.execute("CREATE TABLE IF NOT EXISTS retry (id INTEGER PRIMARY KEY, attempts INTEGER, after INTEGER)")
      self.db.execute("INSERT OR IGNORE INTO retry VALUES(1,0,0)")

  def close(self):
    self.db.close()

  def scan(self, root, schema, active, now, batch=8):
    from openpilot.sunnypilot.formosalink.diagnostic_rlog import extract
    import capnp
    import zstandard as zstd

    cutoff = max(int(self.consent) - DAY * 10**9, int(now - 7 * DAY) * 10**9)
    with self.db:
      self.db.execute("DELETE FROM segments WHERE stamp<?", (cutoff,))
    pending = self.db.execute("SELECT count(*) FROM segments WHERE payload IS NOT NULL").fetchone()[0]
    seen = {source: (stamp, queued) for source, stamp, queued in self.db.execute("SELECT source,stamp,payload IS NOT NULL FROM segments")}
    candidates = []
    if pending >= MAX_PENDING or not root.is_dir():
      return
    for folder in root.iterdir():
      if not re.fullmatch(r"[a-zA-Z0-9_-]+--[0-9]+", folder.name) or folder.is_symlink():
        continue
      path = folder / "rlog.zst"
      try:
        stamp = path.stat().st_mtime_ns
        previous_stamp, queued = seen.get(folder.name, (0, False))
        if not queued and stamp >= cutoff and stamp != previous_stamp and not path.is_symlink() and not (folder / "rlog.lock").exists():
          candidates.append((stamp, path))
      except OSError:
        continue
    for stamp, path in sorted(candidates, reverse=True)[:batch]:
      if not active() or pending >= MAX_PENDING:
        return
      try:
        result = extract(path, schema)
        if path.stat().st_mtime_ns != stamp or (path.parent / "rlog.lock").exists():
          continue
      except OSError:
        continue
      except (ValueError, RuntimeError, capnp.KjException, zstd.ZstdError):
        result = None
      if not active():
        return
      name = path.parent.name
      route = name.rsplit("--", 1)[0]
      payload, reason_list = result if result else (None, [])
      reasons = ",".join(reason_list)
      with self.db:
        if payload:
          duplicate = self.db.execute("SELECT source FROM segments WHERE route=? AND reasons=? AND receipt IS NOT NULL LIMIT 1",
                                      (route, reasons)).fetchone()
          if duplicate and duplicate[0] == name:
            self.db.execute("UPDATE segments SET stamp=? WHERE source=?", (stamp, name))
            continue
          if duplicate:
            payload = None
        code = secrets.token_hex(16) if payload else None
        self.db.execute("INSERT OR REPLACE INTO segments VALUES(?,?,?,?,?,?)", (name, stamp, route, reasons, code, payload))
        pending += int(payload is not None)

  def deliver(self, send, allowed, now):
    attempts, after = self.db.execute("SELECT attempts,after FROM retry WHERE id=1").fetchone()
    if now < after or not allowed():
      return None
    row = self.db.execute("SELECT receipt,payload FROM segments WHERE payload IS NOT NULL ORDER BY stamp DESC LIMIT 1").fetchone()
    if row is None or not allowed():
      return None
    code, payload = row
    outcome = send(code, payload)
    if not allowed():
      return None
    with self.db:
      if outcome == "retry":
        delay = min(21600, 60 * 2 ** min(attempts, 9))
        self.db.execute("UPDATE retry SET attempts=?,after=? WHERE id=1", (attempts + 1, int(now + delay)))
        return None
      self.db.execute("UPDATE retry SET attempts=0,after=0 WHERE id=1")
      self.db.execute("UPDATE segments SET payload=NULL WHERE receipt=?", (code,))
    return code if outcome == "accepted" else None


def post(code, payload):
  import requests
  from openpilot.sunnypilot.formosalink.diagnostic_rlog import UPLOAD_PATH
  from openpilot.sunnypilot.formosalink.pairing import DEFAULT_ORIGIN

  # Each attempt gets a fresh HTTPS session without cookies, device credentials, netrc or redirects.
  try:
    with requests.Session() as session:
      session.trust_env = False
      with session.post(DEFAULT_ORIGIN + UPLOAD_PATH, data=payload, stream=True, timeout=(5, 12), allow_redirects=False,
                        headers={"Content-Type": "application/zstd", "X-Report-Id": code}) as response:
        if response.status_code in (400, 409, 413, 415, 422):
          return "rejected"
        if response.status_code == 200:
          reply = bytearray()
          for chunk in response.iter_content(256):
            reply.extend(chunk)
            if len(reply) > 1024:
              return "retry"
          if json.loads(reply) == {"receipt": code}:
            return "accepted"
  except (OSError, ValueError, requests.RequestException):
    pass
  return "retry"


def eligible_network(sm):
  sm.update(0)
  state = sm["deviceState"]
  return (sm.alive["deviceState"] and sm.valid["deviceState"] and not state.started and not state.networkMetered
          and str(state.networkType) in ("wifi", "ethernet"))


def main():
  from openpilot.cereal import log, messaging
  from openpilot.common.hardware.hw import Paths
  from openpilot.common.params import Params
  from openpilot.common.swaglog import cloudlog

  os.nice(10)
  params = Params()
  consent = params.get(CONSENT)
  if not valid_consent(consent):
    return
  sm = messaging.SubMaster(["deviceState"])

  def active():
    return params.get_bool("IsOffroad") and params.get(CONSENT) == consent

  def allowed():
    return active() and eligible_network(sm)

  with closing(Queue(default_directory(), consent)) as queue:
    while active():
      try:
        now = time.time_ns() // 10**9
        queue.scan(Path(Paths.log_root()), log, active, now)
        if active() and (code := queue.deliver(post, allowed, now)) and active():
          params.put(RECEIPT, {"code": code[:12], "consent": consent}, block=True)
      except (OSError, sqlite3.Error) as exc:
        if active():
          cloudlog.warning(f"FormosaLink diagnostic storage unavailable ({type(exc).__name__})")
      time.sleep(10)


if __name__ == "__main__":
  main()
