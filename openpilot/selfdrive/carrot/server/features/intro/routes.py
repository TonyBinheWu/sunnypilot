"""Carrot intro HTTP routes.

  GET  /api/intro/state          is the intro due? (also exposed via bootstrap)
  POST /api/intro/complete       record completion
  POST /api/intro/apply_preset   apply one driving-control preset in one shot
  POST /api/intro/reset          clear the flag (debug / "show intro again")
  GET/POST /api/intro/reconfigure read current choices / apply reviewed repeat setup

Everything else the intro needs already exists:
  GET  /api/cars                 features/cars.py
  POST /api/param_set            features/params.py      (car, HDA)
  POST /api/web_settings         features/web_settings.py (language)
  POST /api/params_restore       features/params.py      (backup restore)
  POST /api/reboot               features/system.py
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict

from aiohttp import web

from ...services.params import HAS_PARAMS, clamp_numeric, set_param_value
from ...services.settings import get_settings_cached
from .presets import PRESET_NAMES, get_preset
from . import reconfigure
from .state import (
  REASON_FINISHED,
  intro_bootstrap,
  mark_completed,
  read_intro_state,
)


def _clamped(name: str, value: Any) -> Any:
  """Same clamp features/params.py:api_param_set applies, so a preset can
  never write a value the settings UI would reject."""
  try:
    _, _, by_name, _ = get_settings_cached()
    p = by_name.get(name)
  except Exception:
    p = None
  if p is None:
    return value, None
  try:
    if isinstance(p.get("min"), (int, float)) and isinstance(p.get("max"), (int, float)):
      fv = clamp_numeric(float(value), p)
      if all(isinstance(p.get(k), int) for k in ("min", "max", "default")):
        return int(round(fv)), p
      return fv, p
  except Exception:
    pass
  return value, p


def _apply_preset_sync(name: str) -> Dict[str, Any]:
  """Write every param of the preset. Runs in a thread — Params writes hit
  the filesystem and would otherwise block the event loop."""
  values = get_preset(name)
  if values is None:
    raise ValueError(f"unknown preset: {name}")

  applied: Dict[str, Any] = {}
  failed: Dict[str, str] = {}
  for param, raw in values.items():
    try:
      value, p = _clamped(param, raw)
      set_param_value(param, value, p)
      applied[param] = value
    except Exception as exc:
      failed[param] = str(exc)
  return {"applied": applied, "failed": failed}


async def api_state(_request: web.Request) -> web.Response:
  return web.json_response({"ok": True, **intro_bootstrap(), "state": read_intro_state()})


async def api_complete(request: web.Request) -> web.Response:
  try:
    body = await request.json()
  except Exception:
    body = {}
  reason = str((body or {}).get("reason") or REASON_FINISHED)
  return web.json_response({"ok": True, "state": mark_completed(reason)})


async def api_reset(_request: web.Request) -> web.Response:
  """Legacy/debug flag reset. Tools uses the separate staged reconfigure API."""
  from .state import CARROT_INTRO_STATE_PATH
  import os

  try:
    if os.path.exists(CARROT_INTRO_STATE_PATH):
      os.remove(CARROT_INTRO_STATE_PATH)
  except Exception as exc:
    return web.json_response({"ok": False, "error": str(exc)}, status=500)
  return web.json_response({"ok": True, **intro_bootstrap()})


async def api_apply_preset(request: web.Request) -> web.Response:
  if not HAS_PARAMS:
    return web.json_response({"ok": False, "error": "Params not available"}, status=500)

  try:
    body = await request.json()
  except Exception:
    return web.json_response({"ok": False, "error": "invalid json"}, status=400)

  preset = str((body or {}).get("preset") or "").strip()
  if preset not in PRESET_NAMES:
    return web.json_response(
      {"ok": False, "error": f"unknown preset: {preset}", "known": list(PRESET_NAMES)},
      status=400,
    )

  try:
    result = await asyncio.to_thread(_apply_preset_sync, preset)
  except Exception as exc:
    return web.json_response({"ok": False, "error": str(exc)}, status=500)

  # Report partial failure honestly rather than claiming success — these are
  # vehicle control params and the caller needs to know if one did not land.
  if result["failed"]:
    return web.json_response(
      {"ok": False, "error": "some params failed", "preset": preset, **result},
      status=500,
    )
  return web.json_response({"ok": True, "preset": preset, **result})


def register(app: web.Application) -> None:
  app.router.add_get("/api/intro/reconfigure", api_reconfigure_state)
  app.router.add_post("/api/intro/reconfigure", api_reconfigure_apply)
  app.router.add_get("/api/intro/state", api_state)
  app.router.add_post("/api/intro/complete", api_complete)
  app.router.add_post("/api/intro/reset", api_reset)
  app.router.add_post("/api/intro/apply_preset", api_apply_preset)


def _check_setup_state(p, sm):
  import math
  from openpilot.common.forced_offroad import fresh, toggle_reason
  if sm is None or not fresh(sm, 'deviceState', 1.5, time.monotonic()):
    raise reconfigure.SetupError('vehicle_unavailable')
  now = time.monotonic()
  # A fresh, contradictory vehicle observation always wins over an offroad flag.
  if fresh(sm, 'carState', .5, now) and sm['carState'].canValid:
    car = sm['carState']
    if str(car.gearShifter) != 'park' or not car.standstill or any(not math.isfinite(float(v)) or abs(float(v)) > .05 for v in (car.vEgo, car.vEgoRaw)):
      raise reconfigure.SetupError('park_required')
  if not sm['deviceState'].started and p.get_bool('IsOffroad') and not p.get_bool('IsOnroad'):
    for name, fields in [('selfdriveState', ('enabled',)), ('carControl', ('enabled', 'latActive', 'longActive'))]:
      if fresh(sm, name, .5, now) and any(getattr(sm[name], key) for key in fields):
        raise reconfigure.SetupError('controls_active')
    return
  reason = toggle_reason(sm, now=now)
  if reason:
    raise reconfigure.SetupError(reason)


def _reconfigure_guard(_app):
  from openpilot.common.forced_offroad import get_service
  from ...services import params
  if not params.HAS_PARAMS or params.Params is None:
    raise reconfigure.SetupError('params_unavailable')
  # The compact web broker intentionally excludes carState/deviceState. Reuse
  # the Park interlock's native subscriber, under its lock, and refresh for each
  # write instead of relying on an open Drive page to keep the samples current.
  service = get_service()
  with service.lock:
    service.sm.update(0)
    _check_setup_state(service.params, service.sm)


def _reconfigure_state():
  from ...services import params, web_settings
  if not params.HAS_PARAMS or params.Params is None:
    raise reconfigure.SetupError('params_unavailable')
  with reconfigure.LOCK:
    state = reconfigure.snapshot(params.Params(), web_settings.read_web_settings)
  state.pop('raw')
  _, _, catalog, _ = get_settings_cached()
  state['titles'] = {name: {lang: str((catalog.get(name) or {}).get(field) or name) for lang, field in
    [('en', 'etitle'), ('ko', 'title'), ('zh', 'ctitle'), ('zh-tw', 'ttitle')]} for name in reconfigure.KEYS}
  state['presets'] = {name: get_preset(name) for name in PRESET_NAMES}
  return state


def _setup_error(exc):
  conflict = exc.code in {'settings_changed', 'park_required', 'moving', 'controls_active', 'vehicle_unavailable', 'controls_unavailable'}
  return web.json_response({'ok': False, 'error': exc.code, 'rollbackFailed': exc.rollback_failed},
    status=409 if conflict else 503 if exc.code == 'params_unavailable' else 500 if exc.code in {'write_failed', 'rollback_incomplete'} else 400)


async def api_reconfigure_state(request):
  try:
    await asyncio.to_thread(_reconfigure_guard, request.app)
    state = await asyncio.to_thread(_reconfigure_state)
    return web.json_response({'ok': True, **state})
  except reconfigure.SetupError as exc:
    return _setup_error(exc)
  except Exception:
    return web.json_response({'ok': False, 'error': 'vehicle_unavailable'}, status=503)


async def api_reconfigure_apply(request):
  from urllib.parse import urlsplit
  from ...services import params, web_settings
  from ...services.param_changes import append_param_change
  from ..cars import load_supported_cars
  origin = request.headers.get('Origin')
  if (origin and urlsplit(origin).netloc != request.host) or request.headers.get('Sec-Fetch-Site') == 'cross-site':
    return web.json_response({'ok': False, 'error': 'same_origin_required'}, status=403)
  if request.content_type != 'application/json':
    return web.json_response({'ok': False, 'error': 'invalid_selection'}, status=415)
  raw = bytearray()
  async for chunk in request.content.iter_chunked(4097):
    raw.extend(chunk)
    if len(raw) > 4096:
      return web.json_response({'ok': False, 'error': 'invalid_selection'}, status=413)
  try:
    import json
    body = json.loads(raw)
    if not params.HAS_PARAMS or params.Params is None:
      raise reconfigure.SetupError('params_unavailable')
    await asyncio.to_thread(_reconfigure_guard, request.app)
    _, makers = await asyncio.to_thread(load_supported_cars)
    def write(name, value):
      clamped, meta = _clamped(name, value)
      set_param_value(name, clamped, meta)
    result = await asyncio.to_thread(reconfigure.apply, params.Params(), body,
      read_web=web_settings.read_web_settings, update_web=web_settings.update_web_settings,
      makers=makers, write=write, guard=lambda: _reconfigure_guard(request.app),
      record=lambda name, before, after: append_param_change(name, before, after, source='intro', engaged=False))
    return web.json_response(result)
  except (ValueError, TypeError):
    return web.json_response({'ok': False, 'error': 'invalid_selection'}, status=400)
  except reconfigure.SetupError as exc:
    return _setup_error(exc)
  except Exception:
    return web.json_response({'ok': False, 'error': 'write_failed'}, status=500)
