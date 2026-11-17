"""Owner-scoped consent and signed resumable uploads, stored outside the web root."""
import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import threading
import time

from cryptography.exceptions import InvalidSignature
from fastapi import HTTPException, Request, Response

from openpilot.sunnypilot.formosalink.protocol import verify
from openpilot.sunnypilot.formosalink.training_protocol import CHUNK_BYTES, NOTICE, POLICY, digest_file, valid_hash, validate_file


class Contributions:
  def __init__(self, root):
    self.root = Path(root)
    self.root.mkdir(parents=True, exist_ok=True)
    self.lock = threading.RLock()
    with self.db() as db:
      db.executescript("""
        CREATE TABLE IF NOT EXISTS consent(device TEXT PRIMARY KEY, enabled INTEGER NOT NULL, revision INTEGER NOT NULL,
          granted REAL NOT NULL, updated REAL NOT NULL, source TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS operations(device TEXT, id TEXT, PRIMARY KEY(device,id));
        CREATE TABLE IF NOT EXISTS uploads(id TEXT PRIMARY KEY, device TEXT NOT NULL, segment TEXT NOT NULL,
          filename TEXT NOT NULL, sha256 TEXT NOT NULL, size INTEGER NOT NULL, offset INTEGER NOT NULL,
          revision INTEGER NOT NULL, complete INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS datasets(seq INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT UNIQUE NOT NULL,
          folder TEXT NOT NULL,manifest TEXT NOT NULL);
      """)

  @contextmanager
  def db(self):
    db = sqlite3.connect(self.root / "contributions.sqlite3", timeout=30)
    db.row_factory = sqlite3.Row
    try:
      with db:
        yield db
    finally:
      db.close()

  def consent(self, device, db=None):
    if db is None:
      with self.db() as connection:
        return self.consent(device, connection)
    row = db.execute("SELECT * FROM consent WHERE device=?", (device,)).fetchone()
    return dict(row) if row else {"device": device, "enabled": False, "revision": 0, "granted": 0, "updated": 0, "source": "none"}

  def set_consent(self, device, enabled, expected, source, operation=None, granted_at=None):
    if type(enabled) is not bool or type(expected) is not int:
      raise ValueError("invalid consent")
    with self.lock, self.db() as db:
      db.execute("BEGIN IMMEDIATE")
      previous = self.consent(device, db)
      if operation and db.execute("SELECT 1 FROM operations WHERE device=? AND id=?", (device, operation)).fetchone():
        return previous
      if previous["revision"] != expected:
        raise ValueError("consent changed; refresh before choosing again")
      now = time.time()
      if granted_at is not None:
        import math
        if type(granted_at) not in (int,float) or not math.isfinite(granted_at) or not 0<granted_at<=now+90:
          raise ValueError("local authorization clock outside supported interval")
      granted = previous["granted"] if enabled and previous["enabled"] else (min(now,granted_at) if granted_at is not None else now) if enabled else 0
      db.execute("INSERT OR REPLACE INTO consent VALUES(?,?,?,?,?,?)",
                 (device, enabled, expected + 1, granted, now, source))
      if operation:
        db.execute("INSERT INTO operations VALUES(?,?)", (device, operation))
      return self.consent(device, db)

  def require_consent(self, db, device, revision):
    consent = self.consent(device, db)
    if not consent["enabled"] or consent["revision"] != revision:
      raise ValueError("training contribution disabled or revision expired")
    return consent

  def begin(self, device, declaration):
    value = validate_file(declaration)
    identity = hashlib.sha256((device + value["segment"] + value["filename"] + value["sha256"]).encode()).hexdigest()
    with self.lock, self.db() as db:
      db.execute("BEGIN IMMEDIATE")
      self.require_consent(db, device, value["consent_revision"])
      other = db.execute("SELECT sha256 FROM uploads WHERE device=? AND segment=? AND filename=? AND sha256!=?",
        (device,value["segment"],value["filename"],value["sha256"])).fetchone()
      if other:
        raise ValueError("segment filename is immutable; use a new segment identity")
      existing = db.execute("SELECT * FROM uploads WHERE id=?", (identity,)).fetchone()
      if not existing:
        reserved = db.execute("SELECT COALESCE(SUM(size),0) FROM uploads WHERE device=?", (device,)).fetchone()[0]
        quota = int(os.getenv("FORMOSA_TRAINING_DEVICE_QUOTA_GIB", "20")) * 1024**3
        if reserved + value["size"] > quota or shutil.disk_usage(self.root).free < value["size"] + 2 * 1024**3:
          raise ValueError("training storage quota reached")
        db.execute("INSERT INTO uploads VALUES(?,?,?,?,?,?,0,?,0)",
                   (identity, device, value["segment"], value["filename"], value["sha256"], value["size"], value["consent_revision"]))
      elif not existing["complete"]:
        db.execute("UPDATE uploads SET revision=? WHERE id=?", (value["consent_revision"], identity))
        final_path = self.root/"segments"/hashlib.sha256(device.encode()).hexdigest()/value["segment"]/value["filename"]
        if final_path.is_file() and final_path.stat().st_size == value["size"] and digest_file(final_path) == value["sha256"]:
          # Recover a crash between atomic file rename and the SQLite commit.
          db.execute("UPDATE uploads SET offset=size,complete=1 WHERE id=?", (identity,))
      row = db.execute("SELECT * FROM uploads WHERE id=?", (identity,)).fetchone()
      return {"upload_id": identity, "offset": row["offset"], "complete": bool(row["complete"])}

  def chunk(self, device, value):
    if not isinstance(value, dict) or set(value) != {"upload_id", "offset", "data", "sha256", "consent_revision"}:
      raise ValueError("invalid chunk")
    if not valid_hash(value["upload_id"]) or not valid_hash(value["sha256"]) or type(value["offset"]) is not int:
      raise ValueError("invalid chunk identity")
    raw = base64.b64decode(value["data"], validate=True)
    if not 0 < len(raw) <= CHUNK_BYTES or hashlib.sha256(raw).hexdigest() != value["sha256"]:
      raise ValueError("invalid chunk bytes")
    with self.lock, self.db() as db:
      db.execute("BEGIN IMMEDIATE")
      self.require_consent(db, device, value["consent_revision"])
      row = db.execute("SELECT * FROM uploads WHERE id=? AND device=?", (value["upload_id"], device)).fetchone()
      if not row or row["revision"] != value["consent_revision"] or row["complete"]:
        raise ValueError("unknown or completed upload")
      if row["offset"] != value["offset"]:
        return {"offset": row["offset"], "complete": False}
      end = row["offset"] + len(raw)
      if end > row["size"]:
        raise ValueError("chunk exceeds declared size")
      folder = self.root / "segments" / hashlib.sha256(device.encode()).hexdigest() / row["segment"]
      folder.mkdir(parents=True, exist_ok=True)
      path = folder / (row["filename"] + ".part")
      if not path.exists() and row["offset"]:
        raise ValueError("partial upload missing")
      with path.open("r+b" if path.exists() else "w+b") as stream:
        stream.truncate(row["offset"])
        stream.seek(row["offset"])
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
      complete = end == row["size"]
      if complete:
        if digest_file(path) != row["sha256"]:
          path.unlink()
          db.execute("UPDATE uploads SET offset=0 WHERE id=?", (row["id"],))
          # Commit reset before reporting the failed file hash.
          db.commit()
          raise ValueError("file digest mismatch; upload reset")
        os.replace(path, folder / row["filename"])
      db.execute("UPDATE uploads SET offset=?,complete=? WHERE id=?", (end, complete, row["id"]))
      return {"offset": end, "complete": complete}

  def finalize(self, device, value):
    if not isinstance(value, dict) or not valid_hash(value.get("segment")):
      raise ValueError("invalid segment")
    with self.lock, self.db() as db:
      db.execute("BEGIN IMMEDIATE")
      consent = self.require_consent(db, device, value.get("consent_revision"))
      rows = db.execute("SELECT * FROM uploads WHERE device=? AND segment=? AND complete=1", (device, value["segment"])).fetchall()
      names = {row["filename"] for row in rows}
      if not {"fcamera.hevc", "ecamera.hevc"} <= names or not names & {"rlog", "rlog.zst", "rlog.bz2"}:
        raise ValueError("a complete rlog and both front camera videos are required")
      folder = self.root / "segments" / hashlib.sha256(device.encode()).hexdigest() / value["segment"]
      manifest = {"version": 1, "policy": POLICY, "consent_revision": consent["revision"], "received_at": time.time(),
                  "segment": value["segment"], "route_group": value.get("route_group"),
                  "files": [{key: row[key] for key in ("filename", "size", "sha256")} for row in rows]}
      if not valid_hash(manifest["route_group"]):
        raise ValueError("route group required for leakage-free splits")
      path = folder / "complete.json"
      if not path.exists():
        temp = folder / "complete.tmp"
        temp.write_text(json.dumps(manifest), encoding="utf-8")
        os.replace(temp, path)
      dataset_id=hashlib.sha256((hashlib.sha256(device.encode()).hexdigest()+value["segment"]).encode()).hexdigest()
      db.execute("INSERT OR IGNORE INTO datasets(id,folder,manifest) VALUES(?,?,?)",(dataset_id,str(folder),path.read_text()))
      return {"complete": True}


def attach(app, directory, store, owner, rate):
  contributions = Contributions(Path(directory) / "training-contributions")
  app.state.contributions = contributions

  @app.post("/api/v1/training-worker")
  async def worker(request: Request):
    rate(request,"training-worker",7200)
    try:
      envelope=await request.json()
      keys_path=Path(directory)/"training-workers.json"
      workers=json.loads(keys_path.read_text(encoding="utf-8-sig")) if keys_path.is_file() else {}
      public=workers.get(envelope["device_id"])
      if not public:
        raise ValueError("training worker is not registered")
      signed=verify(envelope,public,"training-worker")
      store.consume_nonce(signed["device_id"],signed["nonce"])
      data=signed["payload"]
      if data.get("operation")=="index":
        cursor=data.get("cursor",0)
        if type(cursor) is not int or cursor<0:
          raise ValueError("invalid dataset cursor")
        with contributions.db() as db:
          rows=db.execute("SELECT seq,id,manifest FROM datasets WHERE seq>? ORDER BY seq LIMIT 20",(cursor,)).fetchall()
          summary=dict(db.execute("SELECT COUNT(*) files,COALESCE(SUM(offset),0) uploaded_bytes,COALESCE(SUM(complete=0),0) pending_files FROM uploads").fetchone())
          summary["authorized_devices"]=db.execute("SELECT COUNT(*) FROM consent WHERE enabled=1").fetchone()[0]
          summary["completed_segments"]=db.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
        return {"datasets":[{"seq":row["seq"],"id":row["id"],"manifest":json.loads(row["manifest"])} for row in rows],"summary":summary}
      if data.get("operation")=="file":
        if not valid_hash(data.get("dataset")) or data.get("filename") not in {"rlog","rlog.zst","rlog.bz2","fcamera.hevc","ecamera.hevc"}:
          raise ValueError("unsupported dataset file")
        offset=data.get("offset")
        if type(offset) is not int or offset<0:
          raise ValueError("invalid download offset")
        with contributions.db() as db:
          row=db.execute("SELECT * FROM datasets WHERE id=?",(data["dataset"],)).fetchone()
        if not row:
          raise ValueError("dataset unavailable")
        manifest=json.loads(row["manifest"])
        entry=next(value for value in manifest["files"] if value["filename"]==data["filename"])
        path=(Path(row["folder"])/data["filename"]).resolve()
        if not path.is_relative_to(contributions.root.resolve()) or path.stat().st_size!=entry["size"] or offset>=entry["size"]:
          raise ValueError("dataset file changed or range invalid")
        with path.open("rb") as stream:
          stream.seek(offset)
          body=stream.read(1024*1024)
        return Response(body,media_type="application/octet-stream",headers={"X-File-SHA256":entry["sha256"],"X-Chunk-Offset":str(offset)})
      raise ValueError("unsupported worker operation")
    except (OSError,ValueError,KeyError,TypeError,StopIteration,InvalidSignature) as exc:
      raise HTTPException(403,"invalid training worker request") from exc

  def own(device, request):
    row = store.get(device)
    if not row or row["state"] != "paired" or row["owner_id"] != owner(request)["id"]:
      raise HTTPException(404, "device not found")

  @app.get("/api/v1/devices/{device}/training")
  def status(device: str, request: Request):
    own(device, request)
    with contributions.db() as db:
      totals = dict(db.execute("SELECT COUNT(*) files,COALESCE(SUM(offset),0) bytes FROM uploads WHERE device=?", (device,)).fetchone())
    return {"policy": POLICY, "notice": NOTICE, "consent": contributions.consent(device), "uploads": totals}

  @app.post("/api/v1/devices/{device}/training")
  async def choose(device: str, request: Request):
    own(device, request)
    rate(request, "training-consent", 30)
    try:
      data = await request.json()
      if data.get("policy") != POLICY:
        raise ValueError("review the current contribution notice")
      return contributions.set_consent(device, data["enabled"], data["expected_revision"], "owner-web")
    except (ValueError, KeyError, TypeError) as exc:
      raise HTTPException(409, str(exc)) from exc

  @app.post("/api/v1/agent/training")
  async def agent(request: Request):
    rate(request, "training-agent", 7200)
    try:
      envelope = await request.json()
      row = store.get(envelope["device_id"])
      if not row or row["state"] != "paired":
        raise ValueError("device unavailable")
      signed = verify(envelope, row["public_key"], "training")
      store.consume_nonce(row["id"], signed["nonce"])
      data = signed["payload"]
      operation = data["operation"]
      if operation == "sync":
        pending = data.get("choice")
        conflict = False
        if pending:
          if pending.get("policy") != POLICY or not valid_hash(pending.get("id")):
            raise ValueError("invalid local choice")
          try:
            contributions.set_consent(row["id"], pending["enabled"], pending["expected_revision"], "device", pending["id"],pending.get("granted_at"))
          except ValueError:
            conflict = True
        return {"consent": contributions.consent(row["id"]), "choice_conflict": conflict, "policy": POLICY}
      if operation == "begin":
        return contributions.begin(row["id"], data["file"])
      if operation == "chunk":
        return contributions.chunk(row["id"], data["chunk"])
      if operation == "finalize":
        return contributions.finalize(row["id"], data["segment"])
      raise ValueError("unsupported training operation")
    except (ValueError, KeyError, TypeError, AttributeError, InvalidSignature) as exc:
      raise HTTPException(403, str(exc)) from exc
