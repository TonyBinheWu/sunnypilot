"""Parked Hyundai/Kia indicator test requested by the local settings page."""
import asyncio
import time
from urllib.parse import urlsplit

from aiohttp import web

from openpilot.selfdrive.car.parked_indicator import ACCEPT_WINDOW, ROOT
from openpilot.selfdrive.carrot.bluetooth.model import atomic_json, read_json


async def parked_indicator(request):
  origin = urlsplit(request.headers.get("Origin", ""))
  if origin.netloc != request.host or origin.scheme != request.scheme or request.headers.get("Sec-Fetch-Site") == "cross-site":
    raise web.HTTPForbidden()
  if request.content_type != "application/json":
    raise web.HTTPUnsupportedMediaType()
  side = request.match_info["side"]
  stamp = time.monotonic()
  previous = read_json(ROOT / "request.json", {})
  if isinstance(previous, dict) and stamp - previous.get("stamp", 0) < 1:
    return web.json_response({"ok": False, "reason": "busy"}, status=409)
  atomic_json(ROOT / "request.json", {"stamp": stamp, "side": side})
  for _ in range(round(ACCEPT_WINDOW / .05) + 2):
    await asyncio.sleep(.05)
    receipt = read_json(ROOT / "reply.json", {})
    if isinstance(receipt, dict) and receipt.get("stamp") == stamp:
      return web.json_response({"ok": receipt.get("accepted") is True}, status=200 if receipt.get("accepted") is True else 409)
  return web.json_response({"ok": False, "reason": "unconfirmed"}, status=503)
