"""Outbound authenticated HTTP/WebSocket relay; no inbound device port is opened."""
import asyncio
import base64
import json
import logging
import threading

from openpilot.sunnypilot.formosalink.identity import read
from openpilot.sunnypilot.formosalink.protocol import canonical, sign
from openpilot.sunnypilot.formosalink.remote_web_protocol import (
  CHUNK_SIZE, MAX_BODY, MAX_CHANNELS, MAX_MESSAGE, REQUEST_HEADERS, RESPONSE_HEADERS, SERVICE, decode_body, headers, target_path,
)

LOOPBACK = "http://127.0.0.1:7000"


class NativePermission:
  def __init__(self):
    from openpilot.cereal import messaging
    from openpilot.common.params import Params
    self.params = Params()
    self.sm = messaging.SubMaster(["deviceState", "pandaStates"])

  def __call__(self):
    from openpilot.sunnypilot.formosalink.telemetry import source_valid
    self.sm.update(0)
    return bool(self.params.get_bool("FormosaLinkEnabled") and self.params.get_bool("FormosaLinkRemoteWeb")
                and self.params.get_bool("IsOffroad") and source_valid(self.sm, "deviceState", 2)
                and source_valid(self.sm, "pandaStates", 2) and not self.sm["deviceState"].started
                and not any(p.ignitionLine or p.ignitionCan for p in self.sm["pandaStates"]))


async def serve(identity, private, allowed, stop, *, connector=None):
  import aiohttp
  from openpilot.sunnypilot.formosalink.service_policy import self_hosted_origin
  origin = self_hosted_origin(identity["origin"])
  tasks, sockets, gates = {}, {}, {}
  url = origin.replace("https://", "wss://", 1).replace("http://", "ws://", 1)
  timeout = aiohttp.ClientTimeout(total=None, connect=5, sock_read=30)
  async with aiohttp.ClientSession(timeout=timeout, connector=connector, cookie_jar=aiohttp.DummyCookieJar(), trust_env=False) as session:
    async with session.ws_connect(url + "/api/v1/agent/carrot/ws", heartbeat=10, max_msg_size=MAX_MESSAGE) as cloud:
      await cloud.send_str(canonical(sign(private, identity["device_id"], "remote-web", {"service": SERVICE})).decode())
      ready = await cloud.receive_json(timeout=5)
      if ready != {"type": "ready", "service": SERVICE}:
        raise ValueError("unsupported tunnel")

      async def send(message):
        await asyncio.wait_for(cloud.send_json(message), 10)

      async def emit(message):
        gate = gates[message["id"]]
        gate.clear()
        await send(message)
        await asyncio.wait_for(gate.wait(), 15)

      async def request(message):
        channel = message["id"]
        try:
          if not allowed():
            raise PermissionError("remote access disabled")
          path = target_path(message["path"])
          if message["type"] == "ws-open":
            async with session.ws_connect(LOOPBACK + path, origin=LOOPBACK, heartbeat=10, max_msg_size=MAX_BODY) as local:
              sockets[channel] = local
              await send({"type": "ws-ready", "id": channel})
              async for frame in local:
                if not allowed():
                  raise PermissionError("remote access disabled")
                if frame.type == aiohttp.WSMsgType.TEXT:
                  await emit({"type": "ws-data", "id": channel, "text": frame.data})
                elif frame.type == aiohttp.WSMsgType.BINARY:
                  await emit({"type": "ws-data", "id": channel, "binary": base64.b64encode(frame.data).decode()})
                elif frame.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSE):
                  break
          else:
            if message["method"] not in ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"):
              raise ValueError("unsupported method")
            body = decode_body(message.get("body", ""))
            forwarded = headers(message.get("headers", {}), REQUEST_HEADERS)
            forwarded["Origin"] = LOOPBACK
            forwarded["Accept-Encoding"] = "identity"
            async with session.request(message["method"], LOOPBACK + path, headers=forwarded, data=body, allow_redirects=False) as response:
              await send({"type": "head", "id": channel, "status": response.status,
                          "headers": headers(dict(response.headers), RESPONSE_HEADERS)})
              async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                if not allowed():
                  raise PermissionError("remote access disabled")
                await emit({"type": "data", "id": channel, "body": base64.b64encode(chunk).decode()})
          await send({"type": "end", "id": channel})
        except asyncio.CancelledError:
          raise
        except Exception:
          await send({"type": "error", "id": channel})
        finally:
          sockets.pop(channel, None)
          gates.pop(channel, None)
          tasks.pop(channel, None)

      try:
        while not stop.is_set() and allowed():
          try:
            frame = await cloud.receive(timeout=1)
          except asyncio.TimeoutError:
            continue
          if frame.type != aiohttp.WSMsgType.TEXT:
            break
          message = json.loads(frame.data)
          if not isinstance(message, dict):
            raise ValueError("invalid tunnel frame")
          channel = message.get("id")
          if not isinstance(channel, str) or len(channel) != 32:
            raise ValueError("invalid channel")
          kind = message.get("type")
          if kind in ("request", "ws-open"):
            if channel in tasks or len(tasks) >= MAX_CHANNELS:
              await send({"type": "error", "id": channel})
              continue
            gates[channel] = asyncio.Event()
            tasks[channel] = asyncio.create_task(request(message))
          elif kind == "ack" and channel in gates:
            gates[channel].set()
          elif kind == "cancel":
            task = tasks.get(channel)
            if task:
              task.cancel()
          elif kind == "ws-data" and channel in sockets:
            if not allowed():
              break
            if "text" in message and isinstance(message["text"], str) and len(message["text"].encode()) <= MAX_BODY:
              await sockets[channel].send_str(message["text"])
            else:
              await sockets[channel].send_bytes(decode_body(message.get("binary")))
          else:
            raise ValueError("unsupported tunnel frame")
      finally:
        pending = list(tasks.values())
        for task in pending:
          task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)


def run(directory, stop):
  permission = NativePermission()
  while not stop.is_set():
    try:
      if permission():
        identity, private, _ = read(directory)
        asyncio.run(serve(identity, private, permission, stop))
    except Exception as exc:
      logging.getLogger("formosalink-web").info("Remote web unavailable (%s)", type(exc).__name__)
    stop.wait(2)


def start(directory, stop):
  thread = threading.Thread(target=run, args=(directory, stop), name="formosalink-web", daemon=True)
  thread.start()
  return thread
