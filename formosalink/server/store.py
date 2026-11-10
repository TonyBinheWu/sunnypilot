import hashlib
import json
import secrets
import sqlite3
import time
import uuid
from pathlib import Path
from contextlib import contextmanager


def digest(value):
  return hashlib.sha256(value.encode()).hexdigest()


class Store:
  def __init__(self, path):
    self.path = str(path)
    with self.connection() as db:
      version = db.execute("PRAGMA user_version").fetchone()[0]
      if version not in (0, 1, 2, 3):
        raise ValueError("unsupported FormosaLink database version; explicit migration required")
      if version == 1:
        backup = Path(self.path + ".before-v2.sqlite3")
        if backup.exists():
          raise ValueError("migration backup already exists; inspect before retrying")
        with sqlite3.connect(backup) as destination:
          db.backup(destination)
      if version == 2:
        backup = Path(self.path + ".before-v3.sqlite3")
        if backup.exists():
          raise ValueError("migration backup already exists; inspect before retrying")
        with sqlite3.connect(backup) as destination:
          db.backup(destination)
      db.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
          id TEXT PRIMARY KEY, public_key TEXT NOT NULL, fingerprint TEXT NOT NULL,
          name TEXT NOT NULL, state TEXT NOT NULL, pair_hash TEXT UNIQUE, pair_expires REAL,
          created_at REAL NOT NULL, last_seen REAL, snapshot TEXT);
        CREATE TABLE IF NOT EXISTS nonces (nonce TEXT PRIMARY KEY, expires REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, expires REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, at REAL NOT NULL, action TEXT NOT NULL, device_id TEXT);
      """)
      if version < 2:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE users (id TEXT PRIMARY KEY, name TEXT NOT NULL)")
        db.execute("INSERT INTO users VALUES('local-admin','FormosaLink administrator')")
        db.execute("ALTER TABLE devices ADD COLUMN owner_id TEXT REFERENCES users(id)")
        db.execute("UPDATE devices SET owner_id='local-admin' WHERE state!='pending'")
        db.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT NOT NULL DEFAULT 'local-admin' REFERENCES users(id)")
        db.execute("CREATE TABLE identities (github_id TEXT PRIMARY KEY, user_id TEXT NOT NULL UNIQUE REFERENCES users(id), login TEXT NOT NULL)")
        db.execute("CREATE TABLE oauth_states (state_hash TEXT PRIMARY KEY, browser_hash TEXT NOT NULL, verifier TEXT NOT NULL, expires REAL NOT NULL, link_session TEXT)")
        db.execute("CREATE INDEX device_owner ON devices(owner_id)")
        db.execute("PRAGMA user_version=2")
      db.executescript("""
        CREATE TABLE IF NOT EXISTS device_management (device_id TEXT PRIMARY KEY REFERENCES devices(id), received_at REAL NOT NULL, snapshot TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS setting_commands (id TEXT PRIMARY KEY, device_id TEXT NOT NULL REFERENCES devices(id), created_at REAL NOT NULL, expires_at REAL NOT NULL, status TEXT NOT NULL, reason TEXT, command TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS setting_device ON setting_commands(device_id,created_at);
        PRAGMA user_version=3;
      """)

  @contextmanager
  def connection(self):
    db = sqlite3.connect(self.path, timeout=10)
    db.row_factory = sqlite3.Row
    try:
      with db:
        yield db
    finally:
      db.close()

  def audit(self, db, action, device_id=None):
    db.execute("INSERT INTO audit(at,action,device_id) VALUES(?,?,?)", (time.time(), action, device_id))
    db.execute("DELETE FROM audit WHERE id <= (SELECT COALESCE(MAX(id),0)-10000 FROM audit)")

  def consume_nonce(self, device_id, nonce):
    with self.connection() as db:
      db.execute("DELETE FROM nonces WHERE expires < ?", (time.time(),))
      try:
        db.execute("INSERT INTO nonces VALUES(?,?)", (device_id + ":" + nonce, time.time() + 180))
      except sqlite3.IntegrityError as exc:
        raise ValueError("replayed authentication") from exc

  def get(self, device_id):
    with self.connection() as db:
      row = db.execute("SELECT * FROM devices WHERE id=?", (device_id,)).fetchone()
      return dict(row) if row else None

  def enroll(self, device_id, public_key, fingerprint):
    code = secrets.token_hex(6).upper()
    now = time.time()
    with self.connection() as db:
      db.execute("BEGIN IMMEDIATE")
      db.execute("DELETE FROM devices WHERE state='pending' AND pair_expires < ?", (now,))
      current = db.execute("SELECT * FROM devices WHERE id=?", (device_id,)).fetchone()
      if current:
        if current["public_key"] != public_key or current["state"] == "revoked":
          raise ValueError("device identity is unavailable; explicitly create a new identity to re-pair")
        if current["state"] == "paired":
          return {"state": "paired", "fingerprint": fingerprint}
      count = db.execute("SELECT COUNT(*) FROM devices WHERE state='pending'").fetchone()[0]
      if count >= 100 and not current:
        raise ValueError("too many pending enrollments")
      db.execute("""INSERT INTO devices(id,public_key,fingerprint,name,state,pair_hash,pair_expires,created_at)
        VALUES(?,?,?,?,'pending',?,?,?) ON CONFLICT(id) DO UPDATE SET pair_hash=excluded.pair_hash,
        pair_expires=excluded.pair_expires""", (device_id, public_key, fingerprint, "FormosaPilot", digest(code), now + 600, now))
      self.audit(db, "enrollment_requested", device_id)
    return {"state": "pending", "pair_code": code, "expires_at": now + 600, "fingerprint": fingerprint}

  def pair(self, code, fingerprint, name, user_id="local-admin"):
    with self.connection() as db:
      db.execute("BEGIN IMMEDIATE")
      row = db.execute("SELECT * FROM devices WHERE pair_hash=? AND state='pending' AND pair_expires>?",
                       (digest(code.replace("-", "").replace(" ", "").upper()), time.time())).fetchone()
      if not row or not secrets.compare_digest(row["fingerprint"], fingerprint.lower()):
        raise ValueError("invalid/expired code or fingerprint mismatch")
      db.execute("UPDATE devices SET state='paired',name=?,owner_id=?,pair_hash=NULL,pair_expires=NULL WHERE id=?", (name, user_id, row["id"]))
      self.audit(db, "device_paired", row["id"])
      return row["id"]

  def revoke(self, device_id, user_id="local-admin"):
    with self.connection() as db:
      result = db.execute("UPDATE devices SET state='revoked',snapshot=NULL,pair_hash=NULL WHERE id=? AND owner_id=? AND state='paired'", (device_id, user_id))
      if not result.rowcount:
        raise ValueError("device not found")
      db.execute("DELETE FROM device_management WHERE device_id=?", (device_id,))
      db.execute("UPDATE setting_commands SET status='cancelled' WHERE device_id=? AND status IN ('queued','delivered')", (device_id,))
      self.audit(db, "device_revoked", device_id)

  def management(self, device_id, user_id):
    with self.connection() as db:
      if not db.execute("SELECT 1 FROM devices WHERE id=? AND owner_id=? AND state='paired'", (device_id,user_id)).fetchone():
        raise LookupError("device not found")
      db.execute("UPDATE setting_commands SET status='expired',reason='expired' WHERE device_id=? AND expires_at<? AND status IN ('queued','delivered')", (device_id,time.time()))
      row = db.execute("SELECT * FROM device_management WHERE device_id=?", (device_id,)).fetchone()
      commands = db.execute("SELECT id,status,reason,created_at FROM setting_commands WHERE device_id=? ORDER BY created_at DESC LIMIT 10", (device_id,)).fetchall()
      return {"snapshot":json.loads(row["snapshot"]) if row else None,"received_at":row["received_at"] if row else None,
              "fresh":bool(row and time.time()-row["received_at"]<=10),"commands":[dict(x) for x in commands]}

  def queue_setting(self, device_id, user_id, key, value, expected_revision, session):
    from openpilot.sunnypilot.formosalink.settings import validate_setting
    with self.connection() as db:
      db.execute("BEGIN IMMEDIATE")
      if not db.execute("SELECT 1 FROM devices WHERE id=? AND owner_id=? AND state='paired'", (device_id,user_id)).fetchone():
        raise LookupError("device not found")
      row = db.execute("SELECT * FROM device_management WHERE device_id=?", (device_id,)).fetchone()
      now = time.time()
      if not row or now-row["received_at"]>10:
        raise ValueError("device_offline")
      snapshot = json.loads(row["snapshot"])
      if not snapshot["offroad"] or not snapshot["remote_enabled"]:
        raise ValueError("offroad_required" if not snapshot["offroad"] else "local_disabled")
      if snapshot["revision"]!=expected_revision or snapshot["session"]!=session:
        raise ValueError("conflict")
      entry = next((x for x in snapshot["catalog"] if x["key"]==key), None)
      if not entry:
        raise ValueError("setting_unavailable")
      value = validate_setting(entry,value)
      db.execute("UPDATE setting_commands SET status='expired',reason='expired' WHERE expires_at<? AND status IN ('queued','delivered')", (now,))
      if db.execute("SELECT 1 FROM setting_commands WHERE device_id=? AND status IN ('queued','delivered')", (device_id,)).fetchone():
        raise ValueError("command_pending")
      command = {"id":str(uuid.uuid4()),"device_id":device_id,"session":session,"expected_revision":expected_revision,
                 "key":key,"value":value,"created_at":now,"expires_at":now+20}
      db.execute("INSERT INTO setting_commands VALUES(?,?,?,?,?,?,?)", (command["id"],device_id,now,now+20,"queued",None,json.dumps(command,allow_nan=False)))
      db.execute("DELETE FROM setting_commands WHERE device_id=? AND id NOT IN (SELECT id FROM setting_commands WHERE device_id=? ORDER BY created_at DESC LIMIT 100)", (device_id,device_id))
      self.audit(db,"setting_queued",device_id)
      return {"id":command["id"],"status":"queued"}

  def sync_settings(self, device_id, snapshot):
    with self.connection() as db:
      db.execute("BEGIN IMMEDIATE")
      if not db.execute("SELECT 1 FROM devices WHERE id=? AND state='paired'", (device_id,)).fetchone():
        raise ValueError("device unavailable")
      snapshot = dict(snapshot)
      if snapshot["catalog"] is None:
        old = db.execute("SELECT snapshot FROM device_management WHERE device_id=?", (device_id,)).fetchone()
        old = json.loads(old["snapshot"]) if old else None
        if not old or old["catalog_revision"]!=snapshot["catalog_revision"]:
          return {"server_time":time.time(),"command":None,"acknowledged":[],"needs_catalog":True}
        snapshot["catalog"] = old["catalog"]
      now, acknowledged = time.time(), []
      for receipt in snapshot["receipts"]:
        result = db.execute("UPDATE setting_commands SET status=?,reason=? WHERE id=? AND device_id=? AND status IN ('delivered','expired')", (receipt["status"],receipt["reason"],receipt["id"],device_id))
        if result.rowcount or db.execute("SELECT 1 FROM setting_commands WHERE id=? AND device_id=? AND status IN ('applied','rejected')", (receipt["id"],device_id)).fetchone():
          acknowledged.append(receipt["id"])
      snapshot["receipts"] = []
      db.execute("INSERT INTO device_management VALUES(?,?,?) ON CONFLICT(device_id) DO UPDATE SET received_at=excluded.received_at,snapshot=excluded.snapshot", (device_id,now,json.dumps(snapshot,allow_nan=False)))
      db.execute("UPDATE setting_commands SET status='expired',reason='expired' WHERE device_id=? AND expires_at<? AND status IN ('queued','delivered')", (device_id,now))
      row = db.execute("SELECT * FROM setting_commands WHERE device_id=? AND status='queued' ORDER BY created_at LIMIT 1", (device_id,)).fetchone()
      command = json.loads(row["command"]) if row else None
      if row:
        # Delivery is at most once. Lost replies expire; they cannot replay later.
        db.execute("UPDATE setting_commands SET status='delivered' WHERE id=?", (row["id"],))
      return {"server_time":now,"command":command,"acknowledged":acknowledged,"needs_catalog":False}

  def snapshot(self, device_id, snapshot):
    with self.connection() as db:
      result = db.execute("UPDATE devices SET snapshot=?,last_seen=? WHERE id=? AND state='paired'",
                          (json.dumps(snapshot, allow_nan=False), time.time(), device_id))
      return bool(result.rowcount)

  def devices(self, user_id="local-admin"):
    with self.connection() as db:
      rows = db.execute("SELECT id,name,fingerprint,state,last_seen,snapshot FROM devices WHERE state!='pending' AND owner_id=? ORDER BY created_at", (user_id,)).fetchall()
      return [{**dict(row), "snapshot": json.loads(row["snapshot"]) if row["snapshot"] else None} for row in rows]

  def session(self, user_id="local-admin"):
    token = secrets.token_urlsafe(32)
    with self.connection() as db:
      db.execute("DELETE FROM sessions WHERE expires < ?", (time.time(),))
      db.execute("INSERT INTO sessions(token_hash,expires,user_id) VALUES(?,?,?)", (digest(token), time.time() + 43200, user_id))
      self.audit(db, "owner_login")
    return token

  def authenticated(self, token):
    return self.principal(token) is not None

  def principal(self, token):
    if not token or len(token) > 128:
      return None
    with self.connection() as db:
      row = db.execute("SELECT u.id,u.name,i.login AS github_login FROM sessions s JOIN users u ON s.user_id=u.id LEFT JOIN identities i ON i.user_id=u.id WHERE s.token_hash=? AND s.expires>?", (digest(token), time.time())).fetchone()
      return dict(row) if row else None

  def oauth_start(self, state, browser, verifier, link_session=None):
    with self.connection() as db:
      db.execute("DELETE FROM oauth_states WHERE expires<?", (time.time(),))
      db.execute("INSERT INTO oauth_states VALUES(?,?,?,?,?)", (digest(state), digest(browser), verifier, time.time()+600, digest(link_session) if link_session else None))

  def oauth_consume(self, state, browser):
    with self.connection() as db:
      db.execute("BEGIN IMMEDIATE")
      row = db.execute("SELECT * FROM oauth_states WHERE state_hash=?", (digest(state),)).fetchone()
      db.execute("DELETE FROM oauth_states WHERE state_hash=?", (digest(state),))
      if not row or row["expires"] < time.time() or not secrets.compare_digest(row["browser_hash"], digest(browser)):
        return None
      return dict(row)

  def github_user(self, github_id, login, link_session=None):
    with self.connection() as db:
      db.execute("BEGIN IMMEDIATE")
      identity = db.execute("SELECT user_id FROM identities WHERE github_id=?", (github_id,)).fetchone()
      if link_session:
        admin = db.execute("SELECT 1 FROM sessions WHERE token_hash=? AND user_id='local-admin' AND expires>?", (link_session, time.time())).fetchone()
        if not admin or (identity and identity["user_id"] != "local-admin"):
          raise ValueError("identity cannot be linked")
        user_id = "local-admin"
        existing = db.execute("SELECT github_id FROM identities WHERE user_id=?", (user_id,)).fetchone()
        if existing and existing["github_id"] != github_id:
          raise ValueError("administrator already linked")
      else:
        user_id = identity["user_id"] if identity else str(uuid.uuid4())
      db.execute("INSERT INTO users VALUES(?,?) ON CONFLICT(id) DO NOTHING", (user_id, login))
      db.execute("INSERT INTO identities VALUES(?,?,?) ON CONFLICT(github_id) DO UPDATE SET login=excluded.login", (github_id, user_id, login))
      self.audit(db, "github_identity_verified")
      return user_id

  def logout(self, token):
    with self.connection() as db:
      db.execute("DELETE FROM sessions WHERE token_hash=?", (digest(token or ""),))
      self.audit(db, "owner_logout")
