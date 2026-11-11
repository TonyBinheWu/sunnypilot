"""Owner-authenticated, per-device Carrot web gateway over an outbound device WSS."""
import asyncio
import base64
import json
from pathlib import Path
import re
import uuid
from urllib.parse import urlsplit

from cryptography.exceptions import InvalidSignature
from fastapi import HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse

from openpilot.sunnypilot.formosalink.protocol import MAX_FRAME_BYTES, verify
from openpilot.sunnypilot.formosalink.remote_web_protocol import (
  CHUNK_SIZE, MAX_BODY, MAX_CHANNELS, MAX_MESSAGE, REQUEST_HEADERS, RESPONSE_HEADERS, SERVICE, decode_body, headers, target_path,
)

ASSET_URL = re.compile(r'''((?:src|href|action|poster)\s*=\s*["'])/(?!/)|url\(\s*(["']?)/(?!/)''', re.I)
BRIDGE = Path(__file__).resolve().parents[1] / "web" / "carrot-bridge.js"


def rewrite_document(body, content_type, prefix):
  text = body.decode("utf-8")
  text = ASSET_URL.sub(lambda m: (m[1] or "url(" + m[2]) + prefix, text)
  if "text/html" in content_type:
    script = f'<script src="{prefix}__formosa_bridge.js"></script>'
    if re.search(r"<head(?:\s[^>]*)?>", text, re.I):
      text = re.sub(r"(<head(?:\s[^>]*)?>)", lambda m: m[0] + script, text, count=1, flags=re.I)
    else:
      doctype = re.match(r"\s*<!doctype[^>]*>", text, re.I)
      index = doctype.end() if doctype else 0
      text = text[:index] + script + text[index:]
  return text.encode("utf-8")


class Agent:
  def __init__(self, socket, row):
    self.socket, self.device, self.owner = socket, row["id"], row["owner_id"]
    self.channels = {}
    self.lock = asyncio.Lock()

  async def send(self, frame):
    async with self.lock:
      await asyncio.wait_for(self.socket.send_json(frame), timeout=10)

  async def begin(self, frame):
    if len(self.channels) >= MAX_CHANNELS:
      raise HTTPException(429, "remote request capacity reached")
    channel = uuid.uuid4().hex
    queue = self.channels[channel] = asyncio.Queue(maxsize=4)
    try:
      await self.send({**frame, "id": channel})
    except BaseException:
      self.channels.pop(channel, None)
      raise
    return channel, queue

  async def close(self, channel):
    self.channels.pop(channel, None)
    try:
      await self.send({"type": "cancel", "id": channel})
    except (OSError, RuntimeError, asyncio.TimeoutError, WebSocketDisconnect):
      pass


def register(app, store, owner, rate, origin):
  agents = app.state.carrot_agents = {}
  authority = urlsplit(origin).netloc.lower()

  def owned(request, device, user_id=None):
    if request.headers.get("host", "").lower() != authority:
      raise HTTPException(400, "invalid host")
    user = owner(request)
    row = store.get(device)
    if not row or row["state"] != "paired" or row["owner_id"] != user["id"] or user_id and user["id"] != user_id:
      raise HTTPException(404, "device not found")
    return user["id"]

  def connected(request, device):
    user = owned(request, device)
    agent = agents.get(device)
    if not agent or agent.owner != user:
      raise HTTPException(503, "車機尚未開啟遠端 Carrot 網頁。請確認配對、網路、本機授權，並停車熄火。")
    return agent, user

  async def receive(queue, request, device, user):
    # Session revocation/ownership changes also cancel an idle or slow transfer.
    for _ in range(30):
      owned(request, device, user)
      try:
        frame = await asyncio.wait_for(queue.get(), 1)
        owned(request, device, user)
        if frame["type"] == "error":
          raise HTTPException(502, "車機網頁連線中斷，請確認車輛仍停妥且授權有效。")
        return frame
      except asyncio.TimeoutError:
        continue
    raise HTTPException(504, "車機網頁回應逾時。")

  @app.websocket("/api/v1/agent/carrot/ws")
  async def device_socket(socket: WebSocket):
    agent = None
    try:
      if socket.headers.get("host", "").lower() != authority or socket.headers.get("origin"):
        raise ValueError("invalid device origin")
      rate(socket, "carrot-agent-auth", 120)
      if len(agents) >= 64:
        raise ValueError("agent capacity reached")
      await socket.accept()
      raw = await asyncio.wait_for(socket.receive_text(), 5)
      if len(raw.encode()) > MAX_FRAME_BYTES:
        raise ValueError("oversized authentication")
      envelope = json.loads(raw)
      row = store.get(envelope["device_id"])
      if not row or row["state"] != "paired":
        raise ValueError("device unavailable")
      value = verify(envelope, row["public_key"], "remote-web")
      if value["payload"] != {"service": SERVICE}:
        raise ValueError("unsupported service")
      store.consume_nonce(row["id"], value["nonce"])
      if row["id"] in agents:
        raise ValueError("device already connected")
      agent = agents[row["id"]] = Agent(socket, row)
      await agent.send({"type": "ready", "service": SERVICE})
      while True:
        current = store.get(agent.device)
        if not current or current["state"] != "paired" or current["owner_id"] != agent.owner:
          raise ValueError("device revoked")
        try:
          raw = await asyncio.wait_for(socket.receive_text(), 1)
        except asyncio.TimeoutError:
          continue
        if len(raw.encode()) > MAX_MESSAGE:
          raise ValueError("oversized frame")
        frame = json.loads(raw)
        if not isinstance(frame, dict):
          raise ValueError("invalid frame")
        if frame.get("type") not in ("head", "data", "end", "error", "ws-ready", "ws-data"):
          raise ValueError("invalid frame")
        queue = agent.channels.get(frame.get("id"))
        if queue is not None:
          await asyncio.wait_for(queue.put(frame), 10)
    except (ValueError, KeyError, TypeError, InvalidSignature, HTTPException, asyncio.TimeoutError):
      try:
        await socket.close(code=1008)
      except (RuntimeError, WebSocketDisconnect):
        pass
    except (WebSocketDisconnect, OSError):
      pass
    finally:
      if agent and agents.get(agent.device) is agent:
        agents.pop(agent.device, None)
        for channel, queue in agent.channels.items():
          while not queue.empty():
            queue.get_nowait()
          queue.put_nowait({"type": "error", "id": channel})

  @app.get("/api/v1/devices/{device_id}/carrot-status")
  async def status(request: Request, device_id: str):
    user = owned(request, device_id)
    agent = agents.get(device_id)
    return {"available": bool(agent and agent.owner == user), "service": SERVICE}

  @app.api_route("/api/v1/devices/{device_id}/carrot/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
  async def proxy(request: Request, device_id: str, path: str):
    prefix = f"/api/v1/devices/{device_id}/carrot/"
    owned(request, device_id)
    if path == "__formosa_bridge.js":
      return Response(BRIDGE.read_bytes(), media_type="text/javascript")
    try:
      agent, user = connected(request, device_id)
      suffix = "?" + request.url.query if request.url.query else ""
      target = target_path("/" + path + suffix)
      body = await request.body()
      if len(body) > MAX_BODY:
        raise HTTPException(413, "檔案超過遠端通道 8 MiB 上傳限制。")
      rate(request, "carrot-http:" + device_id, 3000)
      channel, queue = await agent.begin({"type": "request", "method": request.method, "path": target,
                                          "headers": headers(dict(request.headers), REQUEST_HEADERS), "body": base64.b64encode(body).decode()})
    except HTTPException as exc:
      if "text/html" in request.headers.get("accept", ""):
        # Fixed messages only; never reflect an upstream response or submitted path.
        return HTMLResponse('<html lang="zh-Hant"><meta charset="utf-8"><title>FormosaLink 遠端網頁</title>'
                            '<h1>遠端 Carrot 網頁尚未連線</h1><p>請在車機開啟 FormosaLink，配對並允許「遠端 Carrot 網頁」，確認停車熄火與網路後重新整理。</p>',
                            status_code=exc.status_code)
      raise
    except ValueError as exc:
      raise HTTPException(400, "invalid remote request") from exc
    try:
      first = await receive(queue, request, device_id, user)
      if first["type"] != "head" or type(first.get("status")) is not int or not 200 <= first["status"] <= 599:
        raise HTTPException(502, "invalid remote response")
      response_headers = headers(first.get("headers", {}), RESPONSE_HEADERS)
      location = response_headers.get("location")
      if location:
        parsed = urlsplit(location)
        if not parsed.scheme and not parsed.netloc:
          response_headers["location"] = prefix + location.lstrip("/")
        elif parsed.netloc in ("127.0.0.1:7000", "localhost:7000"):
          response_headers["location"] = prefix + parsed.path.lstrip("/") + ("?" + parsed.query if parsed.query else "")
        else:
          response_headers.pop("location", None)

      async def chunks():
        try:
          while True:
            frame = await receive(queue, request, device_id, user)
            if frame["type"] == "end":
              return
            if frame["type"] != "data":
              raise HTTPException(502, "invalid remote body")
            yield decode_body(frame.get("body"), CHUNK_SIZE)
            await agent.send({"type": "ack", "id": channel})
        finally:
          await agent.close(channel)

      content_type = response_headers.get("content-type", "application/octet-stream")
      if request.method != "HEAD" and any(kind in content_type for kind in ("text/html", "text/css")):
        body = bytearray()
        async for chunk in chunks():
          body.extend(chunk)
          if len(body) > 4 * 1024 * 1024:
            raise HTTPException(502, "remote document too large")
        response_headers.pop("content-disposition", None)
        return Response(rewrite_document(body, content_type, prefix), status_code=first["status"], headers=response_headers)
      return StreamingResponse(chunks(), status_code=first["status"], headers=response_headers)
    except BaseException:
      await agent.close(channel)
      raise

  @app.websocket("/api/v1/devices/{device_id}/carrot/{path:path}")
  async def browser_socket(socket: WebSocket, device_id: str, path: str):
    agent = channel = None
    try:
      if socket.headers.get("origin") != origin:
        raise HTTPException(403, "invalid viewer origin")
      agent, user = connected(socket, device_id)
      target = target_path("/" + path + ("?" + socket.url.query if socket.url.query else ""))
      rate(socket, "carrot-websocket:" + device_id, 120)
      channel, queue = await agent.begin({"type": "ws-open", "path": target})
      ready = await receive(queue, socket, device_id, user)
      if ready["type"] != "ws-ready":
        raise ValueError("websocket unavailable")
      await socket.accept()

      async def outgoing():
        while True:
          owned(socket, device_id, user)
          message = await socket.receive()
          if message["type"] == "websocket.disconnect":
            return
          owned(socket, device_id, user)
          if message.get("text") is not None:
            if len(message["text"].encode()) > MAX_BODY:
              raise ValueError("oversized message")
            frame = {"text": message["text"]}
          else:
            data = message.get("bytes", b"")
            if len(data) > MAX_BODY:
              raise ValueError("oversized message")
            frame = {"binary": base64.b64encode(data).decode()}
          await agent.send({"type": "ws-data", "id": channel, **frame})

      async def incoming():
        while True:
          frame = await receive(queue, socket, device_id, user)
          if frame["type"] == "end":
            return
          if frame["type"] != "ws-data":
            raise ValueError("invalid websocket frame")
          if isinstance(frame.get("text"), str) and len(frame["text"].encode()) <= MAX_BODY:
            await asyncio.wait_for(socket.send_text(frame["text"]), 10)
          else:
            await asyncio.wait_for(socket.send_bytes(decode_body(frame.get("binary"))), 10)
          await agent.send({"type": "ack", "id": channel})

      pending = [asyncio.create_task(outgoing()), asyncio.create_task(incoming())]
      try:
        done, _ = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
          task.result()
      finally:
        for task in pending:
          task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
    except (HTTPException, ValueError, OSError, WebSocketDisconnect, asyncio.TimeoutError):
      pass
    finally:
      if agent and channel:
        await agent.close(channel)
      try:
        await socket.close(code=1000)
      except (RuntimeError, WebSocketDisconnect):
        pass
