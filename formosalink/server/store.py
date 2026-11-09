import hashlib
import json
import secrets
import sqlite3
import time
from contextlib import contextmanager


def digest(value):
  return hashlib.sha256(value.encode()).hexdigest()


class Store:
  def __init__(self, path):
    self.path = str(path)
    with self.connection() as db:
      version = db.execute("PRAGMA user_version").fetchone()[0]
      if version not in (0, 1):
        raise ValueError("unsupported FormosaLink database version; explicit migration required")
      db.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
          id TEXT PRIMARY KEY, public_key TEXT NOT NULL, fingerprint TEXT NOT NULL,
          name TEXT NOT NULL, state TEXT NOT NULL, pair_hash TEXT UNIQUE, pair_expires REAL,
          created_at REAL NOT NULL, last_seen REAL, snapshot TEXT);
        CREATE TABLE IF NOT EXISTS nonces (nonce TEXT PRIMARY KEY, expires REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, expires REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, at REAL NOT NULL, action TEXT NOT NULL, device_id TEXT);
        PRAGMA user_version=1;
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

  def pair(self, code, fingerprint, name):
    with self.connection() as db:
      db.execute("BEGIN IMMEDIATE")
      row = db.execute("SELECT * FROM devices WHERE pair_hash=? AND state='pending' AND pair_expires>?",
                       (digest(code.replace("-", "").replace(" ", "").upper()), time.time())).fetchone()
      if not row or not secrets.compare_digest(row["fingerprint"], fingerprint.lower()):
        raise ValueError("invalid/expired code or fingerprint mismatch")
      db.execute("UPDATE devices SET state='paired',name=?,pair_hash=NULL,pair_expires=NULL WHERE id=?", (name, row["id"]))
      self.audit(db, "device_paired", row["id"])
      return row["id"]

  def revoke(self, device_id):
    with self.connection() as db:
      result = db.execute("UPDATE devices SET state='revoked',snapshot=NULL,pair_hash=NULL WHERE id=? AND state='paired'", (device_id,))
      if not result.rowcount:
        raise ValueError("device not found")
      self.audit(db, "device_revoked", device_id)

  def snapshot(self, device_id, snapshot):
    with self.connection() as db:
      result = db.execute("UPDATE devices SET snapshot=?,last_seen=? WHERE id=? AND state='paired'",
                          (json.dumps(snapshot, allow_nan=False), time.time(), device_id))
      return bool(result.rowcount)

  def devices(self):
    with self.connection() as db:
      rows = db.execute("SELECT id,name,fingerprint,state,last_seen,snapshot FROM devices WHERE state!='pending' ORDER BY created_at").fetchall()
      return [{**dict(row), "snapshot": json.loads(row["snapshot"]) if row["snapshot"] else None} for row in rows]

  def session(self):
    token = secrets.token_urlsafe(32)
    with self.connection() as db:
      db.execute("DELETE FROM sessions WHERE expires < ?", (time.time(),))
      db.execute("INSERT INTO sessions VALUES(?,?)", (digest(token), time.time() + 43200))
      self.audit(db, "owner_login")
    return token

  def authenticated(self, token):
    if not token or len(token) > 128:
      return False
    with self.connection() as db:
      return db.execute("SELECT 1 FROM sessions WHERE token_hash=? AND expires>?", (digest(token), time.time())).fetchone() is not None

  def logout(self, token):
    with self.connection() as db:
      db.execute("DELETE FROM sessions WHERE token_hash=?", (digest(token or ""),))
      self.audit(db, "owner_logout")
