import asyncio
import json
from pathlib import Path
from aiohttp import web

from ..services.web_capabilities import resolve_web_capabilities
from ..services.web_settings import read_web_settings, update_web_settings


async def get_web_settings(request: web.Request) -> web.Response:
  settings = read_web_settings()
  return web.json_response({
    "ok": True,
    "settings": settings,
    "capabilities": resolve_web_capabilities(settings),
  })


async def set_web_settings(request: web.Request) -> web.Response:
  try:
    body = await request.json()
  except Exception:
    body = {}
  if not isinstance(body, dict):
    return web.json_response({"ok": False, "error": "bad request"}, status=400)
  settings = update_web_settings(body)
  return web.json_response({
    "ok": True,
    "settings": settings,
    "capabilities": resolve_web_capabilities(settings),
  })


async def get_recording_quota(_request):
  from openpilot.system.loggerd.recording_quota import STATUS
  try:
    body = await asyncio.to_thread(Path(STATUS).read_text)
    data = json.loads(body)
    if not isinstance(data, dict):
      raise ValueError('invalid status')
  except (OSError, ValueError):
    data = {'available': False}
  return web.json_response(data, headers={'Cache-Control': 'no-store'})


def register(app: web.Application) -> None:
  app.router.add_get("/api/recording_quota", get_recording_quota)
  app.router.add_get("/api/web_settings", get_web_settings)
  app.router.add_post("/api/web_settings", set_web_settings)
