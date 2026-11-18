"""Ephemeral handoff from the viewing device's detector to the opted-in agent."""

import json
import math
import time

from aiohttp import web
from openpilot.sunnypilot.formosalink.road_scene import check_camera
from openpilot.sunnypilot.formosalink.scene_agent import SHARED, active_lease, publish, read_small


async def status(request):
  lease = active_lease()
  return web.json_response({"revision": lease["revision"] if lease else None}, headers={"Cache-Control": "no-store"})


def clip_view(start, end):
  """Clip even segments whose original endpoints both fall outside the view."""
  first, last = 0.0, 1.0
  for a, b, low, high in zip(start, end, (0, -32), (100, 32)):
    delta = b - a
    if not delta:
      if not low <= a <= high:
        return None
      continue
    entry, exit_at = sorted(((low - a) / delta, (high - a) / delta))
    first, last = max(first, entry), min(last, exit_at)
    if first >= last:
      return None
  return [[round(a + t * (b - a), 2) for a, b in zip(start, end)] for t in (first, last)]


def map_lines(revision, position, cache, now):
  if not position or not cache or position.get("revision") != revision or cache.get("revision") != revision:
    return []
  fix = position.get("fix")
  if not fix or fix["heading"] is None or not 0 <= now - position["eof"] / 1e9 < 1 or now >= cache["expires"]:
    return []
  lat, lon = fix["lat"], fix["lon"]
  scale = 111320 * math.cos(math.radians(lat))
  angle = math.radians(fix["heading"])
  c, s = math.cos(angle), math.sin(angle)
  lat0, lon0 = cache["map"]["center"]
  if math.hypot((lat - lat0) * 111320, (lon - lon0) * scale) > 70:
    return []
  segments = []
  for way in cache["map"]["ways"][:24]:
    previous = None
    for x, y in way[:13]:
      e, n = (x - lon) * scale, (y - lat) * 111320
      point = [round(n * c + e * s, 2), round(e * c - n * s, 2)]
      if previous is not None:
        segment = clip_view(previous, point)
        if segment:
          segments.append(segment)
      previous = point
  return segments


async def context(request):
  lease = active_lease()
  lines = (
    map_lines(lease["revision"], read_small(SHARED / "position", 512), read_small(SHARED / "map", 32768), time.monotonic())
    if lease
    else []
  )
  return web.json_response({"enabled": bool(lease), "lines": lines}, headers={"Cache-Control": "no-store"})


async def observation(request):
  if request.content_type != "application/json":
    raise web.HTTPUnsupportedMediaType()
  data = bytearray()
  async for chunk in request.content.iter_chunked(2048):
    data.extend(chunk)
    if len(data) > 8192:
      raise web.HTTPRequestEntityTooLarge(max_size=8192, actual_size=len(data))
  try:
    body = json.loads(data)
    packet = body["packet"]
    check_camera(packet)
    if abs(time.monotonic_ns() - packet["eof"]) > 2_000_000_000:
      raise ValueError("expired")
    lease = active_lease()
    if not lease or body["revision"] != lease["revision"]:
      raise web.HTTPForbidden()
    publish(SHARED / packet["detector"], {"packet": packet, "revision": lease["revision"]})
  except (KeyError, ValueError, TypeError):
    raise web.HTTPBadRequest() from None
  return web.json_response({"ok": True})


def register(app):
  app.router.add_get("/api/research/road-scenes", status)
  app.router.add_get("/api/research/road-scenes/context", context)
  app.router.add_post("/api/research/road-scenes", observation)
