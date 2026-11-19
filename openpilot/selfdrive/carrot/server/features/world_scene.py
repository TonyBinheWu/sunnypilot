"""One bounded on-demand read shared by cockpit viewers. Never opens a GPU device."""
import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from aiohttp import web

from ..services.world_scene import ContactHistory, world_observations
from openpilot.sunnypilot.formosalink.cameras import camera_clock


def register(app):
  sm = pending = cached = None
  history = ContactHistory()
  pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="world-display")

  def sample():
    nonlocal sm
    from openpilot.cereal import messaging
    if sm is None:
      sm = messaging.SubMaster(["liveTracks", "radarState", "carState", "carControl", "longitudinalPlan", "modelV2"])
    sm.update(0)
    at = time.monotonic()
    return at, world_observations(sm, at, camera_clock(), history)

  async def snapshot(_request):
    nonlocal pending, cached
    if cached is None or time.monotonic() - cached[0] >= .09:
      if pending is None:
        pending = asyncio.get_running_loop().run_in_executor(pool, sample)
      work = pending
      try:
        cached = await asyncio.shield(work)
      except Exception:
        logging.getLogger(__name__).debug("World observations unavailable", exc_info=True)
        cached = time.monotonic(), {"contacts": [], "signals": {}}
      finally:
        if work.done() and pending is work:
          pending = None
    at, body = cached
    return web.json_response({**body, "ageMs": max(0, (time.monotonic() - at) * 1000)}, headers={"Cache-Control": "no-store"})

  async def close(_app):
    await asyncio.to_thread(pool.shutdown, wait=True, cancel_futures=True)

  app.on_cleanup.append(close)
  app.router.add_get("/api/vision/world-scene", snapshot)
