"""Durable queue and immutable, hash-verified dataset snapshots."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import time
import uuid

from openpilot.sunnypilot.formosalink.training_protocol import FILES, POLICY, digest_file, valid_hash

STAGES = ("prepare", "teacher", "train", "evaluate", "compile")
BASE = {
  "name": "N16 Nav", "repository": "commaai/openpilot_driving_models",
  "revision": "eed9e515dccd5aa9be969a2d6c57eb469174a97d",
  "path": "96244b1f-6c4e-4adc-848d-eccd0b44b182/12800/big_driving_supercombo.onnx",
  "sha256": "01effc679eb46d6036ce0302673a87fe2dcfcc95a679daeeb929679e53c3647a", "size": 814591107,
}


def write_json(path, value):
  path = Path(path)
  path.parent.mkdir(parents=True, exist_ok=True)
  fd, temporary = tempfile.mkstemp(prefix=".studio-", dir=path.parent)
  try:
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
      json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
      stream.flush()
      os.fsync(stream.fileno())
    for attempt in range(8):
      try:
        os.replace(temporary, path)
        break
      except PermissionError:
        if os.name!='nt' or attempt==7: raise
        time.sleep(.01*(attempt+1))  # Windows readers can briefly deny rename sharing.
  finally:
    if os.path.exists(temporary):
      os.unlink(temporary)


def read_json(path, default=None):
  for attempt in range(8):
    try:
      return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
      return default
    except PermissionError:
      if os.name!='nt' or attempt==7: raise
      time.sleep(.01*(attempt+1))


def split_for(group):
  # Whole routes stay together, independent of discovery order or future rounds.
  bucket = int(hashlib.sha256(group.encode()).hexdigest()[:8], 16) % 10
  return "test" if bucket == 0 else "validation" if bucket == 1 else "train"


def teacher_runs(root):
  records={path.parent.name:path for name in ('interrupted.json','result.json')
    for path in (Path(root)/'teacher-cycles').glob('cycle-*/'+name) if path.parent.name.split('-')[-1].isdigit()}
  paths=list(records.values())
  paths=sorted(paths,key=lambda path:int(path.parent.name.split('-')[-1]),reverse=True)
  rows=[]
  for path in paths[:20]:
    result=read_json(path,{})
    rows.append({'id':path.parent.name,'cycle':int(path.parent.name.split('-')[-1]),'history':result.get('history',[]),
      'best_epoch':result.get('best_epoch'),'adapter_saved':result.get('adapter_saved',False),'completed':path.name=='result.json'})
  return rows


class Store:
  def __init__(self, root):
    self.root = Path(root).resolve()
    self.root.mkdir(parents=True, exist_ok=True)
    with self.db() as db:
      db.executescript("""
        CREATE TABLE IF NOT EXISTS control(id INTEGER PRIMARY KEY CHECK(id=1), enabled INTEGER NOT NULL);
        INSERT OR IGNORE INTO control VALUES(1,0);
        CREATE TABLE IF NOT EXISTS datasets(id TEXT PRIMARY KEY, route_group TEXT NOT NULL, split TEXT NOT NULL,
          path TEXT NOT NULL, bytes INTEGER NOT NULL, created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, state TEXT NOT NULL, stage TEXT NOT NULL,
          created REAL NOT NULL, updated REAL NOT NULL, snapshot TEXT NOT NULL, error TEXT, parent TEXT);
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, time REAL, job TEXT, message TEXT);
      """)

  @contextmanager
  def db(self):
    db = sqlite3.connect(self.root / "studio.sqlite3", timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    try:
      with db:
        yield db
    finally:
      db.close()

  def config(self):
    return read_json(self.root / "config.json", {})

  def event(self, message, job=None):
    with self.db() as db:
      db.execute("INSERT INTO events(time,job,message) VALUES(?,?,?)", (time.time(), job, str(message)[:4000]))
      db.execute("DELETE FROM events WHERE id < (SELECT COALESCE(MAX(id),0)-5000 FROM events)")

  def enabled(self, value=None):
    with self.db() as db:
      if value is not None:
        if type(value) is not bool:
          raise ValueError("invalid continuous mode")
        db.execute("UPDATE control SET enabled=? WHERE id=1", (value,))
      return bool(db.execute("SELECT enabled FROM control WHERE id=1").fetchone()[0])

  def discover(self):
    imported = 0
    for location in self.config().get("inboxes", []):
      root = Path(location).resolve()
      if not root.is_dir():
        continue
      for manifest_path in sorted(root.rglob("complete.json")):
        try:
          manifest = read_json(manifest_path)
          if manifest.get("policy") != POLICY or not valid_hash(manifest.get("route_group")):
            raise ValueError("missing contribution policy or route grouping")
          entries = manifest["files"]
          names = {entry["filename"] for entry in entries}
          if not {"fcamera.hevc", "ecamera.hevc"} <= names or not names & {"rlog", "rlog.zst", "rlog.bz2"}:
            raise ValueError("incomplete front-camera segment")
          if len(names) != len(entries) or not names <= FILES:
            raise ValueError("unsupported or duplicate input file")
          identity = hashlib.sha256(json.dumps({"group": manifest["route_group"], "files": sorted(entries, key=lambda r:r["filename"])}, sort_keys=True).encode()).hexdigest()
          with self.db() as db:
            if db.execute("SELECT 1 FROM datasets WHERE id=?", (identity,)).fetchone():
              continue
          destination = self.root / "datasets" / identity
          if destination.exists():
            shutil.rmtree(destination)  # owned incomplete import only, under the dataset root
          destination.mkdir(parents=True)
          size = 0
          for entry in entries:
            path = (manifest_path.parent / entry["filename"]).resolve()
            if not path.is_relative_to(root) or not valid_hash(entry["sha256"]) or path.stat().st_size != entry["size"]:
              raise ValueError("input path or size mismatch")
            target = destination / entry["filename"]
            shutil.copyfile(path, target)
            if digest_file(target) != entry["sha256"]:
              raise ValueError("input digest mismatch")
            size += entry["size"]
          write_json(destination / "complete.json", manifest)
          with self.db() as db:
            db.execute("INSERT INTO datasets VALUES(?,?,?,?,?,?)", (identity, manifest["route_group"], split_for(manifest["route_group"]), str(destination), size, time.time()))
          imported += 1
          self.event("已驗證並匯入行車片段 " + identity[:12])
        except (ValueError, OSError, KeyError, TypeError) as exc:
          self.event("資料拒收：" + str(exc))
    return imported

  def enqueue(self, force=False):
    with self.db() as db:
      db.execute("BEGIN IMMEDIATE")
      if db.execute("SELECT 1 FROM jobs WHERE state IN ('queued','running')").fetchone():
        return None
      datasets = [dict(row) for row in db.execute("SELECT * FROM datasets ORDER BY id")]
      counts = {name: sum(row["split"] == name for row in datasets) for name in ("train", "validation", "test")}
      if not all(counts.values()):
        return None
      snapshot = hashlib.sha256(json.dumps([row["id"] for row in datasets]).encode()).hexdigest()
      if not force and db.execute("SELECT 1 FROM jobs WHERE snapshot=?", (snapshot,)).fetchone():
        return None
      parent = db.execute("SELECT id FROM jobs WHERE state='completed' ORDER BY created DESC LIMIT 1").fetchone()
      identity = "n16-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex[:6]
      path = self.root / "runs" / identity
      config = self.config()
      write_json(path / "plan.json", {"id": identity, "snapshot": snapshot, "datasets": datasets, "counts": counts,
        "base": BASE, "parent": parent[0] if parent else None, "config": config, "training_scope": "action_residual_and_3d_trajectory_heads; visual_backbone_frozen"})
      now = time.time()
      db.execute("INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?)", (identity, "queued", "prepare", now, now, snapshot, None, parent[0] if parent else None))
    self.event("已建立不可變資料快照／訓練版本", identity)
    return identity

  def update(self, identity, state, stage, error=None):
    with self.db() as db:
      db.execute("UPDATE jobs SET state=?,stage=?,updated=?,error=? WHERE id=?", (state, stage, time.time(), error, identity))

  def state(self):
    with self.db() as db:
      datasets = [dict(row) for row in db.execute("SELECT split,COUNT(*) segments,SUM(bytes) bytes FROM datasets GROUP BY split")]
      jobs = [dict(row) for row in db.execute("SELECT * FROM jobs ORDER BY created DESC LIMIT 100")]
      events = [dict(row) for row in db.execute("SELECT * FROM events ORDER BY id DESC LIMIT 50")]
      route_counts={row['split']:row['count'] for row in db.execute('SELECT split,COUNT(DISTINCT route_group) count FROM datasets GROUP BY split')}
    missing=[name for name in ('train','validation','test') if not route_counts.get(name)]
    config=self.config()
    from tools.training_studio.teacher_control import training_ready,adaptation_progress
    qualified=training_ready(self)
    teacher_health=read_json(self.root/'teacher-health.json',{})
    teacher_progress=read_json(self.root/'teacher-qualification-progress.json',{})
    blockers=[]
    if missing:
      blockers.append('缺少獨立行程資料組：'+', '.join(missing)+'；同一行程的片段不會拆到不同資料組。')
    if not qualified:
      if teacher_progress.get('state')=='failed':
        blockers.append('教師資格未通過：'+teacher_progress.get('scenario','')+' / '+', '.join(teacher_progress.get('failures',[])))
      elif teacher_progress.get('state')=='running':
        blockers.append('教師資格驗證中：'+teacher_progress.get('scenario','')+'；通過全部關卡後才能自動蒸餾。')
      else:
        blockers.append('尚未取得與線上教師權重一致的完整資格報告；教師標註與蒸餾尚未開始。')
    for job in jobs:
      folder = self.root / "runs" / job["id"]
      job["progress"] = read_json(folder / "progress.json", {})
      job["evaluation"] = read_json(folder / "evaluation.json", {})
      job["release"] = read_json(folder / "release.json", {})
      job["training"] = read_json(folder / "training.json", {})
      job["compile"] = read_json(folder / "compile.json", {})
    return {"time": time.time(), "enabled": self.enabled(), "datasets": datasets, "jobs": jobs, "events": events,
      "config": {key: value for key, value in self.config().items() if key not in ("commands",)},
      "base": read_json(self.root / "models" / "base.json", {**BASE, "verified": False}),
      "collection":read_json(self.root/"collection.json",{}),
      "collection_progress":read_json(self.root/'collector-progress.json',{}),
      "pipeline":{"missing_splits":missing,"route_counts":route_counts,"blockers":blockers},
      "teacher":{**teacher_health,'qualification':teacher_progress},
      "teacher_training":adaptation_progress(self),
      "teacher_runs":teacher_runs(self.root),
      "readiness":{"collector_configured":bool(self.config().get("collector")),
        "teacher_qualified":qualified,
        "dgx":read_json(self.root/"worker-readiness.json",{}),"compiler_configured":bool(self.config().get("compiler_command"))},
      "worker": read_json(self.root / "worker.json", {})}


@contextmanager
def exclusive_worker(root):
  path = Path(root) / "worker.lock"
  with path.open("a+b") as stream:
    if os.name == "nt":
      import msvcrt
      stream.write(b"0")
      stream.flush()
      stream.seek(0)
      msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
      import fcntl
      fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    yield
