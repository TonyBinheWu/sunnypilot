import asyncio
import json
import secrets
import time
from collections import defaultdict, deque
from pathlib import Path
from urllib.parse import urlparse

from cryptography.exceptions import InvalidSignature
from fastapi import FastAPI, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import httpx
from pydantic import BaseModel, ConfigDict, Field

from openpilot.sunnypilot.formosalink.protocol import MAX_FRAME_BYTES, ONLINE_SECONDS, VERSION, fingerprint, validate_snapshot, verify
from formosalink.server.config import load, password_hash
from formosalink.server.store import Store
from formosalink.server import oauth
from typing import Any
from openpilot.sunnypilot.formosalink.media_protocol import MAX_MEDIA_BYTES
from openpilot.sunnypilot.formosalink.management_protocol import MAX_MANAGEMENT_BYTES, validate_snapshot as validate_management

COOKIE = "formosalink_session"


class Login(BaseModel):
  model_config = ConfigDict(extra="forbid")
  password: str = Field(min_length=1, max_length=256)


class Pair(BaseModel):
  model_config = ConfigDict(extra="forbid")
  code: str = Field(min_length=12, max_length=24)
  fingerprint: str = Field(pattern=r"^[a-fA-F0-9]{24}$")
  name: str = Field(min_length=1, max_length=60)


class Limit:
  def __init__(self):
    self.buckets = defaultdict(deque)

  def check(self, key, maximum, seconds=60):
    now = time.monotonic()
    # All routes also use a global bucket; cap bookkeeping for anonymous clients.
    if len(self.buckets) >= 2048 and key not in self.buckets:
      self.buckets = defaultdict(deque, {k: v for k, v in self.buckets.items() if v and now - v[-1] < seconds})
      if len(self.buckets) >= 2048:
        raise HTTPException(429, "try later")
    bucket = self.buckets[key]
    while bucket and now - bucket[0] >= seconds:
      bucket.popleft()
    if len(bucket) >= maximum:
      raise HTTPException(429, "too many requests; try later")
    bucket.append(now)


class Setting(BaseModel):
  model_config = ConfigDict(extra="forbid")
  key: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9]{0,95}$")
  value: Any
  expected_revision: str = Field(pattern=r"^[a-f0-9]{64}$")
  session: str = Field(min_length=36, max_length=36)


def create_app(data_dir, web_dir=None):
  directory, config = load(data_dir)
  store = Store(directory / "formosalink.sqlite3")
  github = oauth.settings(directory)
  callback = config["origin"] + "/api/v1/auth/github/callback"
  app = FastAPI(title="FormosaLink", version="0.6.0", docs_url=None, redoc_url=None, openapi_url=None)
  app.state.store = store
  limiter = Limit()
  connections = {}
  http_channels = {}
  secure = config["origin"].startswith("https:")

  def owner(request):
    user = store.principal(request.cookies.get(COOKIE))
    if not user:
      raise HTTPException(401, "sign in required")
    return user

  def rate(request, kind, maximum):
    # Do not trust client-supplied forwarding headers. IIS forwards to loopback;
    # this intentionally makes the limit global behind IIS for release 0.1.
    limiter.check(kind + ":global", maximum * 4)
    limiter.check(kind + ":" + request.client.host, maximum)

  @app.middleware("http")
  async def security(request: Request, call_next):
    if request.url.path.startswith("/api/"):
      if request.headers.get("host", "").lower() != urlparse(config["origin"]).netloc.lower():
        return Response(status_code=400)
      if request.method not in ("GET", "HEAD", "OPTIONS") and request.url.path not in ("/api/v1/agent/enroll", "/api/v1/agent/telemetry", "/api/v1/agent/status", "/api/v1/agent/sync", "/api/v1/agent/media"):
        if request.headers.get("origin") != config["origin"]:
          return Response(status_code=403)
      try:
        length = int(request.headers.get("content-length", "0"))
      except ValueError:
        return Response(status_code=400)
      limit = MAX_MEDIA_BYTES if request.url.path == "/api/v1/agent/media" else MAX_MANAGEMENT_BYTES if request.url.path == "/api/v1/agent/sync" else MAX_FRAME_BYTES
      if length > limit:
        return Response(status_code=413)
      # Bound streamed/chunked requests as well as declared Content-Length.
      body = bytearray()
      async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > limit:
          return Response(status_code=413)
      request._body = bytes(body)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; media-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    if secure:
      response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response

  @app.get("/api/v1/health")
  def health():
    return {"service": "FormosaLink", "version": VERSION, "features": ["device-pairing", "signed-https-telemetry", "github-oauth", "device-ownership", "qr-pairing", "offroad-settings", "device-health", "navigation-destination", "media-preview-v1"], "database_version": 3}

  @app.get("/api/v1/auth/me")
  def me(request: Request):
    return {"user": store.principal(request.cookies.get(COOKIE)), "github_enabled": github is not None}

  def begin_oauth(request, link=False):
    rate(request, "oauth", 12)
    if not github:
      raise HTTPException(503, "GitHub OAuth is not configured")
    link_session = None
    if link:
      if owner(request)["id"] != "local-admin":
        raise HTTPException(403, "administrator required")
      link_session = request.cookies.get(COOKIE)
    state, browser, verifier = (secrets.token_urlsafe(32) for _ in range(3))
    store.oauth_start(state, browser, verifier, link_session)
    response = RedirectResponse(oauth.authorize_url(github, callback, state, verifier), status_code=303)
    response.set_cookie("formosalink_oauth", browser, httponly=True, secure=secure, samesite="lax", max_age=600, path="/api/v1/auth/github/callback")
    return response

  @app.get("/api/v1/auth/github/start")
  def github_start(request: Request):
    return begin_oauth(request)

  @app.post("/api/v1/auth/github/link")
  def github_link(request: Request):
    # Return a URL instead of following a cross-origin redirect in fetch.
    response = begin_oauth(request, link=True)
    result = Response(content=json.dumps({"url": response.headers["location"]}), media_type="application/json")
    result.headers["set-cookie"] = response.headers["set-cookie"]
    return result

  @app.get("/api/v1/auth/github/callback")
  async def github_callback(request: Request):
    rate(request, "oauth-callback", 20)
    state = request.query_params.get("state", "")
    browser = request.cookies.get("formosalink_oauth", "")
    flow = store.oauth_consume(state, browser) if len(state) <= 128 and len(browser) <= 128 else None
    response = RedirectResponse("/?auth=failed", status_code=303)
    response.delete_cookie("formosalink_oauth", path="/api/v1/auth/github/callback")
    code = request.query_params.get("code", "")
    if not github or not flow or not code or len(code) > 512 or "error" in request.query_params:
      return response
    try:
      github_id, login_name = await oauth.exchange(github, callback, code, flow["verifier"])
      user_id = store.github_user(github_id, login_name, flow["link_session"])
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
      return response
    # Replace the browser's old session after verified identity, never merge accounts.
    store.logout(request.cookies.get(COOKIE))
    response.headers["location"] = "/"
    response.set_cookie(COOKIE, store.session(user_id), httponly=True, secure=secure, samesite="strict", max_age=43200, path="/api")
    return response

  @app.post("/api/v1/login")
  def login(body: Login, request: Request, response: Response):
    rate(request, "login", 8)
    actual = password_hash(body.password, config["password_salt"])
    if not secrets.compare_digest(actual, config["password_hash"]):
      raise HTTPException(401, "invalid password")
    response.set_cookie(COOKIE, store.session(), httponly=True, secure=secure, samesite="strict", max_age=43200, path="/api")
    return {"ok": True}

  @app.post("/api/v1/logout")
  def logout(request: Request, response: Response):
    owner(request)
    store.logout(request.cookies.get(COOKIE))
    response.delete_cookie(COOKIE, path="/api")
    return {"ok": True}

  @app.get("/api/v1/devices")
  def devices(request: Request):
    user = owner(request)
    rows = store.devices(user["id"])
    now = time.time()
    for row in rows:
      active = row["id"] in connections or now - http_channels.get(row["id"], 0) <= ONLINE_SECONDS
      row["online"] = row["state"] == "paired" and active and now - (row["last_seen"] or 0) <= ONLINE_SECONDS
      row["transport"] = "websocket" if row["id"] in connections else "https" if active else None
      snapshot = row["snapshot"]
      row["stale"] = not row["online"] or not snapshot or not snapshot["metrics"].get("sample_valid", False) or abs(now - snapshot["sampled_at"]) > ONLINE_SECONDS
    return {"devices": rows, "server_time": now, "protocol_version": VERSION}

  @app.post("/api/v1/pair")
  def pair(body: Pair, request: Request):
    user = owner(request)
    rate(request, "pair", 10)
    try:
      device_id = store.pair(body.code, body.fingerprint, body.name.strip() or "FormosaPilot", user["id"])
    except ValueError as exc:
      raise HTTPException(400, str(exc)) from exc
    return {"device_id": device_id}

  @app.post("/api/v1/devices/{device_id}/revoke")
  async def revoke(device_id: str, request: Request):
    user = owner(request)
    try:
      store.revoke(device_id, user["id"])
    except ValueError as exc:
      raise HTTPException(404, str(exc)) from exc
    socket = connections.pop(device_id, None)
    http_channels.pop(device_id, None)
    if socket:
      try:
        await socket.close(code=4003)
      except (RuntimeError, WebSocketDisconnect):
        pass
    return {"ok": True}

  @app.post("/api/v1/agent/enroll")
  async def enroll(request: Request):
    rate(request, "enroll", 10)
    try:
      envelope = await request.json()
      public_key = envelope["payload"]["public_key"]
      verified = verify(envelope, public_key, "enroll")
      if set(verified["payload"]) != {"public_key"}:
        raise ValueError("invalid enrollment")
      store.consume_nonce(verified["device_id"], verified["nonce"])
      return store.enroll(verified["device_id"], public_key, fingerprint(public_key))
    except (ValueError, KeyError, TypeError, InvalidSignature) as exc:
      raise HTTPException(400, "invalid enrollment or unavailable identity") from exc

  @app.get("/api/v1/devices/{device_id}/settings")
  def settings(device_id: str, request: Request):
    try:
      return store.management(device_id, owner(request)["id"])
    except LookupError as exc:
      raise HTTPException(404, "device not found") from exc

  @app.post("/api/v1/devices/{device_id}/settings")
  def setting(device_id: str, body: Setting, request: Request):
    user = owner(request)
    rate(request,"setting",60)
    try:
      return store.queue_setting(device_id,user["id"],body.key,body.value,body.expected_revision,body.session)
    except LookupError as exc:
      raise HTTPException(404,"device not found") from exc
    except (ValueError, KeyError, TypeError) as exc:
      from openpilot.sunnypilot.formosalink.management_protocol import REASONS
      reason = str(exc)
      raise HTTPException(409,reason if reason in REASONS|{"device_offline","command_pending"} else "setting_unavailable") from exc

  @app.post("/api/v1/agent/sync")
  async def sync_settings(request: Request):
    rate(request,"agent-sync",1800)
    try:
      envelope = await request.json()
      row = store.get(envelope["device_id"])
      if not row or row["state"]!="paired":
        raise ValueError("device unavailable")
      verified = verify(envelope,row["public_key"],"sync")
      snapshot = validate_management(verified["payload"])
      limiter.check("device-sync:"+row["id"],30)
      store.consume_nonce(row["id"],verified["nonce"])
      return store.sync_settings(row["id"],snapshot)
    except (ValueError, KeyError, TypeError, AttributeError, OverflowError, InvalidSignature) as exc:
      raise HTTPException(403,"invalid device settings") from exc

  @app.post("/api/v1/agent/telemetry")
  async def http_telemetry(request: Request):
    # Proxy-safe fallback; device signatures and replay protection are mandatory.
    rate(request, "telemetry", 3600)
    try:
      envelope = await request.json()
      row = store.get(envelope["device_id"])
      if not row or row["state"] != "paired":
        raise ValueError("device unavailable")
      verified = verify(envelope, row["public_key"], "telemetry")
      data = validate_snapshot(verified["payload"])
      if abs(time.time() - data["sampled_at"]) > 90:
        raise ValueError("expired sample")
      limiter.check("device-telemetry:" + row["id"], 20)
      store.consume_nonce(row["id"], verified["nonce"])
      if not store.snapshot(row["id"], data):
        raise ValueError("device revoked")
      http_channels[row["id"]] = time.time()
      return {"type": "ack", "sequence": data["sequence"]}
    except (ValueError, KeyError, TypeError, InvalidSignature) as exc:
      raise HTTPException(403, "invalid device telemetry") from exc

  @app.post("/api/v1/agent/status")
  async def agent_status(request: Request):
    # Device-signed state only: polling never rotates the QR credential or reveals ownership.
    rate(request, "agent-status", 1800)
    try:
      envelope = await request.json()
      if not isinstance(envelope, dict) or not isinstance(envelope.get("device_id"), str):
        raise ValueError("invalid device identifier")
      row = store.get(envelope["device_id"])
      if not row:
        raise ValueError("unknown device")
      verified = verify(envelope, row["public_key"], "status")
      if verified["payload"]:
        raise ValueError("unexpected status payload")
      limiter.check("device-status:" + row["id"], 30)
      store.consume_nonce(row["id"], verified["nonce"])
      return {"state": row["state"]}
    except (ValueError, KeyError, TypeError, InvalidSignature) as exc:
      raise HTTPException(403, "invalid device authentication") from exc

  @app.websocket("/api/v1/agent/ws")
  async def agent_socket(socket: WebSocket):
    if socket.headers.get("host", "").lower() != urlparse(config["origin"]).netloc.lower() or socket.headers.get("origin"):
      await socket.close(code=1008)
      return
    try:
      limiter.check("ws:global", 120)
    except HTTPException:
      await socket.close(code=1013)
      return
    await socket.accept()
    device_id = None
    try:
      raw = await asyncio.wait_for(socket.receive_text(), timeout=10)
      if len(raw.encode()) > MAX_FRAME_BYTES:
        raise ValueError("oversized authentication")
      envelope = json.loads(raw)
      row = store.get(envelope["device_id"])
      if not row or row["state"] != "paired":
        await socket.close(code=4003)
        return
      verified = verify(envelope, row["public_key"], "connect")
      if verified["payload"]:
        raise ValueError("unexpected connect payload")
      store.consume_nonce(row["id"], verified["nonce"])
      device_id = row["id"]
      old = connections.get(device_id)
      connections[device_id] = socket
      if old:
        await old.close(code=4009)
      await socket.send_json({"type": "ready", "version": VERSION, "sample_interval": 5})
      previous = -1
      last_received = 0
      while True:
        raw = await asyncio.wait_for(socket.receive_text(), timeout=20)
        if len(raw.encode()) > MAX_FRAME_BYTES or time.monotonic() - last_received < 1:
          raise ValueError("oversized or excessive telemetry")
        data = validate_snapshot(json.loads(raw))
        if data["sequence"] <= previous or abs(time.time() - data["sampled_at"]) > 90:
          raise ValueError("old or invalid snapshot")
        if connections.get(device_id) is not socket or not store.snapshot(device_id, data):
          await socket.close(code=4003)
          return
        previous = data["sequence"]
        last_received = time.monotonic()
        # Acknowledgement only: there is deliberately no command dispatcher.
        await socket.send_json({"type": "ack", "sequence": previous})
    except WebSocketDisconnect:
      pass
    except (ValueError, KeyError, TypeError, InvalidSignature, asyncio.TimeoutError):
      try:
        await socket.close(code=1008)
      except (RuntimeError, WebSocketDisconnect):
        pass
    finally:
      if device_id and connections.get(device_id) is socket:
        connections.pop(device_id, None)

  from formosalink.server.media import register as register_media
  register_media(app, store, owner, rate)
  web = Path(web_dir) if web_dir else Path(__file__).resolve().parents[1] / "web"
  if web.is_dir():
    app.mount("/", StaticFiles(directory=web, html=True), name="web")
  return app
