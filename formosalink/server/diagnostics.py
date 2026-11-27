"""Anonymous ccNC error rlogs. This store has no device or account foreign keys."""
import asyncio
import hashlib
import re
import sqlite3
import time
from contextlib import asynccontextmanager, closing, suppress
from datetime import UTC, datetime
from html import escape
from urllib.parse import urlencode

import capnp
import zstandard as zstd
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from starlette.concurrency import run_in_threadpool

from openpilot.sunnypilot.formosalink.diagnostic_rlog import UPLOAD_PATH, platforms, server_schema, verify_report

ADMIN_PATH = "/api/v1/admin/anonymous-rlogs"
RETENTION_DAYS = 30
MAX_REPORTS = 4096


def epoch_seconds():
  # Retention and receipts span process and host restarts.
  return time.time_ns() // 1_000_000_000


class Inbox:
  def __init__(self, path):
    self.path = path
    with closing(self.connect()) as db, db:
      db.execute("""CREATE TABLE IF NOT EXISTS reports (
        seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT UNIQUE NOT NULL, received INTEGER NOT NULL,
        digest BLOB NOT NULL, faults TEXT NOT NULL, revision TEXT NOT NULL, platform TEXT NOT NULL, rlog BLOB NOT NULL)""")
      db.execute("CREATE INDEX IF NOT EXISTS received_time ON reports(received)")

  def connect(self):
    db = sqlite3.connect(self.path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA secure_delete=ON")
    return db

  def purge(self):
    with closing(self.connect()) as db, db:
      db.execute("DELETE FROM reports WHERE received<=?", (epoch_seconds() - RETENTION_DAYS * 86400,))

  def accept(self, code, body):
    try:
      payload, faults, revision, platform = verify_report(body)
    except (ValueError, TypeError, RuntimeError, OverflowError, UnicodeError, capnp.KjException, zstd.ZstdError) as exc:
      raise HTTPException(422, "invalid anonymous rlog") from exc
    # Hash the canonical uncompressed content so retries survive changes in zstd versions.
    digest = hashlib.sha256(zstd.ZstdDecompressor().decompress(payload)).digest()
    now = epoch_seconds()
    with closing(self.connect()) as db, db:
      db.execute("BEGIN IMMEDIATE")
      db.execute("DELETE FROM reports WHERE received<=?", (now - RETENTION_DAYS * 86400,))
      row = db.execute("SELECT digest FROM reports WHERE id=?", (code,)).fetchone()
      if row:
        if row["digest"] != digest:
          raise HTTPException(409, "report code already used")
      else:
        if db.execute("SELECT COUNT(*) FROM reports").fetchone()[0] >= MAX_REPORTS:
          raise HTTPException(503, "inbox full", headers={"Retry-After": "3600"})
        db.execute("INSERT INTO reports(id,received,digest,faults,revision,platform,rlog) VALUES(?,?,?,?,?,?,?)",
                   (code, now, digest, ", ".join(faults), revision, platform, payload))
    return {"receipt": code}

  def page(self, query, before):
    with closing(self.connect()) as db:
      return db.execute("""SELECT seq,id,received,faults,revision,platform FROM reports WHERE received>? AND
        (?=0 OR seq<?) AND instr(lower(id || ' ' || faults || ' ' || platform || ' ' || revision),?)>0
        ORDER BY seq DESC LIMIT 51""", (epoch_seconds() - RETENTION_DAYS * 86400, before, before, query.lower())).fetchall()

  def download(self, code):
    with closing(self.connect()) as db:
      row = db.execute("SELECT rlog FROM reports WHERE id=? AND received>?", (code, epoch_seconds() - RETENTION_DAYS * 86400,)).fetchone()
    if not row:
      raise HTTPException(404, "report unavailable")
    return bytes(row["rlog"])


def register(app, directory, owner, rate):
  inbox = Inbox(directory / "anonymous-rlogs.sqlite3")
  # Verify package dependencies before advertising this capability.
  server_schema()
  platforms()

  async def expire():
    while True:
      await run_in_threadpool(inbox.purge)
      await asyncio.sleep(3600)

  @asynccontextmanager
  async def lifespan(_app):
    cleanup = asyncio.create_task(expire())
    try:
      yield
    finally:
      cleanup.cancel()
      with suppress(asyncio.CancelledError):
        await cleanup

  router = APIRouter(lifespan=lifespan)

  def admin(request):
    if owner(request)["id"] != "local-admin":
      raise HTTPException(403, "administrator required")

  @router.post(UPLOAD_PATH)
  async def report(request: Request):
    rate(request, "anonymous-rlog", 60)
    code = request.headers.get("X-Report-Id", "")
    if not re.fullmatch(r"[0-9a-f]{32}", code):
      raise HTTPException(400, "invalid report code")
    if request.headers.get("content-type") != "application/zstd":
      raise HTTPException(415, "expected application/zstd")
    return await run_in_threadpool(inbox.accept, code, await request.body())

  @router.get(ADMIN_PATH, response_class=HTMLResponse)
  def listing(request: Request, q: str = Query("", max_length=80), before: int = Query(0, ge=0, le=2**63-1)):
    admin(request)
    rows = inbox.page(q, before)
    cards = []
    for row in rows[:50]:
      when = datetime.fromtimestamp(row["received"], UTC).strftime("%Y-%m-%d %H:%M UTC")
      code = row["id"]
      cards.append(f'''<li><strong>{escape(row["faults"])}</strong>
        <p>{when} · {escape(row["platform"] or "未知車型")} · ccnc-port {escape(row["revision"][:10])}</p>
        <code>{code[:12]}</code> <a href="{ADMIN_PATH}/{code}/rlog.zst" download>下載 rlog.zst</a></li>''')
    more = ""
    if len(rows) > 50:
      link = urlencode({"q": q, "before": rows[49]["seq"]})
      more = f'<a href="?{escape(link)}">下一頁</a>'
    results = '<ul>' + "".join(cards) + '</ul>' if cards else '<p>沒有符合的回報。</p>'
    return f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
      <title>匿名錯誤回報 · FormosaLink</title><link rel="stylesheet" href="/diagnostics.css"><main>
      <a href="/">回 FormosaLink</a><h1>匿名錯誤回報</h1><p>回報保留 30 天。可用車主提供的回報碼、車型、版本或錯誤名稱搜尋。</p>
      <form><label>搜尋 <input type="search" name="q" maxlength="80" value="{escape(q, quote=True)}"></label> <button>查詢</button></form>
      {results}{more}</main></html>'''

  @router.get(ADMIN_PATH + "/{code}/rlog.zst")
  def download(code: str, request: Request):
    admin(request)
    return Response(inbox.download(code), media_type="application/zstd",
                    headers={"Content-Disposition": 'attachment; filename="rlog.zst"'})

  app.include_router(router)
