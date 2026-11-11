import asyncio
import socket
import threading

import aiohttp
from aiohttp import web
from fastapi.testclient import TestClient
import pytest
import uvicorn

from formosalink.server.app import COOKIE, create_app
from formosalink.server.config import initialize
from formosalink.server.remote_web import rewrite_document
from openpilot.sunnypilot.formosalink.identity import create
from openpilot.sunnypilot.formosalink.protocol import fingerprint, sign
from openpilot.sunnypilot.formosalink import remote_web
from openpilot.sunnypilot.formosalink.remote_web_protocol import SERVICE, target_path


@pytest.mark.parametrize("path", ["http://example.com/", "//127.0.0.1:22/", "/../etc/passwd", "/%2e%2e/etc", "/%252e%252e/etc",
                                 "/%2fexample.com/", "/%5cfoo", "/x\r\nHeader:y", "ssh://localhost", "/#fragment"])
def test_only_fixed_loopback_paths(path):
  with pytest.raises(ValueError):
    target_path(path)


def test_html_and_css_routing_preserves_external_urls():
  prefix = "/api/v1/devices/device/carrot/"
  html = rewrite_document(b'<html><head><link href="/css/a.css"></head><img src="/icon.png"><a href="https://example.com/">x</a>', "text/html", prefix)
  assert html.index(b"__formosa_bridge.js") < html.index(b"a.css")
  assert (prefix + "css/a.css").encode() in html
  assert b'href="https://example.com/"' in html
  assert rewrite_document(b'<!doctype html><html lang="zh-Hant"><main>guide</main></html>', "text/html", prefix).startswith(b"<!doctype html><script")
  assert rewrite_document(b"a{background:url('/icon.png')}", "text/css", prefix) == f"a{{background:url('{prefix}icon.png')}}".encode()


def test_owner_only_status_and_agent_replay(tmp_path):
  origin = "https://formosapilot.dinglu-t.com"
  initialize(tmp_path, origin, "test-owner-password-123456")
  app = create_app(tmp_path)
  identity, private, public = create(tmp_path / "device", origin)
  device = identity["device_id"]
  enrolled = app.state.store.enroll(device, public, fingerprint(public))
  app.state.store.pair(enrolled["pair_code"], enrolled["fingerprint"], "Carrot")
  route = f"/api/v1/devices/{device}/carrot-status"
  with TestClient(app, base_url=origin) as client:
    assert client.get(route).status_code == 401
    client.cookies.set(COOKIE, app.state.store.session())
    assert client.get(route).json() == {"available": False, "service": SERVICE}
    auth = sign(private, device, "remote-web", {"service": SERVICE})
    with client.websocket_connect(origin.replace("https:", "wss:") + "/api/v1/agent/carrot/ws") as device_ws:
      device_ws.send_json(auth)
      assert device_ws.receive_json() == {"type": "ready", "service": SERVICE}
      assert client.get(route).json()["available"]
      other = app.state.store.github_user("999999", "different-owner")
      client.cookies.set(COOKIE, app.state.store.session(other))
      assert client.get(route).status_code == 404
      assert client.get(f"/api/v1/devices/{device}/carrot/").status_code == 404
    with client.websocket_connect(origin.replace("https:", "wss:") + "/api/v1/agent/carrot/ws") as replay:
      replay.send_json(auth)
      assert replay.receive()["type"] == "websocket.close"


@pytest.mark.asyncio
async def test_real_device_relay_http_websocket_chunks_and_permission_revocation(tmp_path, monkeypatch):
  """Real TCP, real native agent and cloud gateway; local target is a test Carrot server."""
  local = web.Application()
  writes = []
  payload = bytes(range(256)) * 4096

  async def index(request):
    assert COOKIE not in request.cookies
    return web.Response(text='<html><head></head><a href="/guide.zh-TW.html">繁中</a></html>', content_type="text/html",
                        headers={"Set-Cookie": "must-not-reach-browser=secret"})

  async def settings(request):
    assert request.headers.get("Authorization") == "Bearer native-carrot-grant"
    value = await request.json()
    writes.append(value)
    return web.json_response({"saved": value})

  async def download(request):
    assert request.headers.get("Range") == "bytes=0-1048575"
    return web.Response(body=payload, status=206, headers={"Content-Range": "bytes 0-1048575/1048576"})

  async def echo(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for frame in ws:
      if frame.type == aiohttp.WSMsgType.TEXT:
        await ws.send_str(frame.data)
      elif frame.type == aiohttp.WSMsgType.BINARY:
        await ws.send_bytes(frame.data)
    return ws

  local.router.add_get("/", index)
  local.router.add_post("/api/settings", settings)
  local.router.add_get("/download", download)
  local.router.add_get("/ws/echo", echo)
  runner = web.AppRunner(local)
  await runner.setup()
  site = web.TCPSite(runner, "127.0.0.1", 0)
  await site.start()
  local_port = site._server.sockets[0].getsockname()[1]
  monkeypatch.setattr(remote_web, "LOOPBACK", f"http://127.0.0.1:{local_port}")
  listener = socket.socket()
  listener.bind(("127.0.0.1", 0))
  port = listener.getsockname()[1]
  origin = f"http://127.0.0.1:{port}"
  initialize(tmp_path, origin, "test-owner-password-123456")
  app = create_app(tmp_path)
  identity, private, public = create(tmp_path / "device", origin)
  device = identity["device_id"]
  enrolled = app.state.store.enroll(device, public, fingerprint(public))
  app.state.store.pair(enrolled["pair_code"], enrolled["fingerprint"], "Carrot")
  server = uvicorn.Server(uvicorn.Config(app, log_level="error", ws_max_size=12 * 1024 * 1024, ws_per_message_deflate=False))
  thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
  thread.start()
  allowed = [True]
  stop = threading.Event()
  task = None
  try:
    for _ in range(100):
      if server.started:
        break
      await asyncio.sleep(.05)
    assert server.started
    task = asyncio.create_task(remote_web.serve(identity, private, lambda: allowed[0], stop))
    for _ in range(100):
      if device in app.state.carrot_agents:
        break
      if task.done():
        task.result()
      await asyncio.sleep(.05)
    assert device in app.state.carrot_agents
    jar = aiohttp.CookieJar(unsafe=True)
    async with aiohttp.ClientSession(cookie_jar=jar, timeout=aiohttp.ClientTimeout(total=20)) as browser:
      login = await browser.post(origin + "/api/v1/login", json={"password": "test-owner-password-123456"}, headers={"Origin": origin})
      assert login.status == 200
      prefix = origin + f"/api/v1/devices/{device}/carrot/"
      async with browser.get(prefix) as response:
        assert response.status == 200
        text = await response.text()
        assert "__formosa_bridge.js" in text and f"/devices/{device}/carrot/guide.zh-TW.html" in text
        assert "Set-Cookie" not in response.headers
      # CSRF is checked before forwarding; a rejected request never reaches the local server.
      rejected = await browser.post(prefix + "api/settings", json={"value": 4})
      assert rejected.status == 403 and writes == []
      async with browser.post(prefix + "api/settings", json={"value": 42}, headers={"Origin": origin, "Authorization": "Bearer native-carrot-grant"}) as response:
        assert response.status == 200
        assert await response.json() == {"saved": {"value": 42}}
      assert writes == [{"value": 42}]
      async with browser.get(prefix + "download", headers={"Range": "bytes=0-1048575"}) as response:
        assert response.status == 206
        assert response.headers["Content-Range"] == "bytes 0-1048575/1048576"
        assert await response.read() == payload
      async with browser.ws_connect(prefix.replace("http:", "ws:") + "ws/echo", origin=origin) as websocket:
        await websocket.send_str("繁體中文設定")
        assert (await websocket.receive(timeout=5)).data == "繁體中文設定"
        await websocket.send_bytes(b"binary terminal test")
        assert (await websocket.receive(timeout=5)).data == b"binary terminal test"
        allowed[0] = False
        closed = await websocket.receive(timeout=5)
        assert closed.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED)
      await asyncio.wait_for(task, 5)
      task = None
      async with browser.get(prefix) as response:
        assert response.status == 503
  finally:
    stop.set()
    if task:
      task.cancel()
      await asyncio.gather(task, return_exceptions=True)
    server.should_exit = True
    await asyncio.to_thread(thread.join, 5)
    listener.close()
    await runner.cleanup()
