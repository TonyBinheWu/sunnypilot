"""Parked Hyundai/Kia indicator test requested by the local settings page."""
import asyncio
import time
from urllib.parse import urlsplit

from aiohttp import web

from openpilot.selfdrive.car.parked_indicator import ACCEPT_WINDOW, DURATION, ROOT
from openpilot.selfdrive.carrot.bluetooth.model import atomic_json, read_json


def unavailable_reason(params):
  if params is None:
    return "controller_state_unavailable"
  if params.get_bool("IsOffroad") or params.get_bool("ForceOffroadObserver"):
    return "offroad"
  data = params.get("CarParams")
  if not data:
    return "controller_state_unavailable"
  from openpilot.cereal import car
  from opendbc.car.hyundai.values import HyundaiFlags
  with car.CarParams.from_bytes(data) as cp:
    if cp.passive or cp.dashcamOnly:
      return "passive"
    if cp.brand != "hyundai" or cp.flags & HyundaiFlags.ENABLE_BLINKERS:
      return "spas_test_unavailable"
    if not cp.flags & HyundaiFlags.CANFD_SPAS_BLINKERS:
      return "spas_setting_off" if not params.get_bool("CanfdBlinkerControl") else "spas_not_active"
  return None


async def parked_indicator(request):
  origin = urlsplit(request.headers.get("Origin", ""))
  if origin.netloc != request.host or origin.scheme != request.scheme or request.headers.get("Sec-Fetch-Site") == "cross-site":
    raise web.HTTPForbidden()
  if request.content_type != "application/json":
    raise web.HTTPUnsupportedMediaType()
  side = request.match_info["side"]
  reason = unavailable_reason(request.app.get("params"))
  if reason:
    return web.json_response({"ok": False, "reason": reason}, status=409)
  stamp = time.monotonic()
  previous = read_json(ROOT / "request.json", {})
  if isinstance(previous, dict) and stamp - previous.get("stamp", 0) < 1:
    return web.json_response({"ok": False, "reason": "busy"}, status=409)
  atomic_json(ROOT / "request.json", {"stamp": stamp, "side": side})
  for _ in range(round(ACCEPT_WINDOW / .05) + 2):
    await asyncio.sleep(.05)
    receipt = read_json(ROOT / "reply.json", {})
    if isinstance(receipt, dict) and receipt.get("stamp") == stamp:
      if receipt.get("accepted") is True:
        while time.monotonic() < stamp + DURATION + .5:
          lamp = read_json(ROOT / "lamp.json", {})
          if isinstance(lamp, dict) and lamp.get("stamp") == stamp:
            if lamp.get("observed") is True:
              return web.json_response({"ok": True, "lampObserved": True})
            return web.json_response({"ok": False, "reason": lamp.get("reason") or "lamp_feedback_missing"}, status=409)
          await asyncio.sleep(.1)
        return web.json_response({"ok": False, "reason": "lamp_feedback_missing"}, status=504)
      details = {key: receipt[key] for key in ("testSetting", "gear") if key in receipt}
      return web.json_response({"ok": False, "reason": receipt.get("reason") or "controller_rejected", **details}, status=409)
  return web.json_response({"ok": False, "reason": "unconfirmed"}, status=503)
