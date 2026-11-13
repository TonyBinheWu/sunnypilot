from aiohttp import web

from openpilot.common.forced_offroad import get_service


async def status(_request):
  return web.json_response({"ok": True, **get_service().status()})


async def change(request):
  try:
    body = await request.json()
    if not isinstance(body, dict) or set(body) != {"enabled"}:
      raise ValueError("boolean_required")
    value = get_service().request(body["enabled"])
  except PermissionError as exc:
    return web.json_response({"ok": False, "error": str(exc)}, status=409)
  except (ValueError, TypeError):
    return web.json_response({"ok": False, "error": "boolean_required"}, status=400)
  return web.json_response({"ok": True, **value})


def register(app):
  app.router.add_get("/api/device/forced_offroad", status)
  app.router.add_post("/api/device/forced_offroad", change)
