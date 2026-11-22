import asyncio
import os

from aiohttp import web

from ..config import UNIT_CYCLE
from ..services.device_info import (
  get_device_network_snapshot,
  get_device_setting_group_names,
  get_device_setting_values,
  get_longitudinal_setup_status,
)
from ..services.param_changes import observe_param_values
from ..services.params import HAS_PARAMS, ParamKeyType, Params, get_param_values
from ..services.popular_values import read_popular_values_memory, schedule_popular_value_refresh
from ..services.setting_favorites import read_setting_favorites
from ..services.setting_profiles import read_setting_profiles
from ..services.setting_unit_index import read_setting_unit_index, update_setting_unit_index
from ..services.settings import current_vehicle_settings_context, filter_settings_catalog_for_brand, get_settings_cached, settings_cache
from ..services.ssh_keys import get_ssh_key_status


def _settings_catalog_payload(cache_parts: tuple | None = None, vehicle_brand: str | None = None,
                              ray_pedal_control: bool = False) -> dict:
  path = settings_cache["path"]
  data, groups, _by_name, groups_list = cache_parts or get_settings_cached()
  if vehicle_brand is None:
    vehicle_brand, ray_pedal_control = current_vehicle_settings_context()
  groups, groups_list, categories, _hidden_names = filter_settings_catalog_for_brand(
    groups, groups_list, settings_cache.get("categories"), vehicle_brand, ray_pedal_control=ray_pedal_control,
  )
  return {
    "path": path,
    "apilot": data.get("apilot"),
    "groups": groups_list,
    "items_by_group": dict(groups),
    "categories": categories,
    "unit_cycle": UNIT_CYCLE,
    "has_params": HAS_PARAMS,
    "has_param_type": bool(ParamKeyType is not None and hasattr(Params(), "get_type")) if HAS_PARAMS else False,
  }


def _settings_snapshot_payload() -> dict:
  cache_parts = get_settings_cached()
  _data, _groups, by_name, _groups_list = cache_parts
  vehicle_brand, ray_pedal_control = current_vehicle_settings_context()
  catalog = _settings_catalog_payload(cache_parts, vehicle_brand, ray_pedal_control)
  visible_names = {
    item.get("name")
    for items in catalog["items_by_group"].values()
    for item in items
    if item.get("name")
  }
  values = get_param_values(
    list(visible_names),
    {name: by_name[name].get("default", 0) for name in visible_names},
  )
  # Entering settings is exactly when a value changed elsewhere would confuse
  # the user, so this is the read worth comparing against what we last knew.
  observe_param_values(values)
  ssh_status = get_ssh_key_status()
  favorites = [name for name in read_setting_favorites().get("favorites", []) if name in visible_names]
  return {
    "ok": True,
    "settings": catalog,
    "values": values,
    "device_values": get_device_setting_values(ssh_status),
    "longitudinal_setup": get_longitudinal_setup_status(),
    # The web reads its Device tab parameter names from here rather than
    # restating them, so the two lists cannot drift apart.
    "device_groups": get_device_setting_group_names(),
    "device_network": get_device_network_snapshot(),
    "device_ssh": ssh_status,
    "favorites": favorites,
    "profiles": read_setting_profiles().get("profiles", []),
    "popular": read_popular_values_memory(),
    # Shipped with the snapshot so restoring the step multipliers costs no
    # extra round trip on first entry.
    "unit_index": read_setting_unit_index().get("units", {}),
  }


def _compressed_json_response(payload: dict) -> web.Response:
  response = web.json_response(payload)
  response.headers["Cache-Control"] = "no-store"
  response.enable_compression()
  return response


def _missing_settings_response() -> web.Response | None:
  path = settings_cache["path"]
  if os.path.exists(path):
    return None
  return web.json_response({"ok": False, "error": f"settings file not found: {path}"}, status=404)


async def api_settings(request: web.Request) -> web.Response:
  missing = _missing_settings_response()
  if missing is not None:
    return missing

  try:
    return _compressed_json_response({"ok": True, **_settings_catalog_payload()})
  except Exception as e:
    return web.json_response({"ok": False, "error": str(e)}, status=500)


async def api_settings_snapshot(request: web.Request) -> web.Response:
  """Return all data required for the first settings entry in one request.

  The catalog is process-cached by services.settings. Favorites, profiles and
  popular values remain live per-device data, but are read together so the
  client does not create a four-request render barrier on its first visit.
  """
  missing = _missing_settings_response()
  if missing is not None:
    return missing

  try:
    schedule_popular_value_refresh(request.app)
    return _compressed_json_response(await asyncio.to_thread(_settings_snapshot_payload))
  except Exception as e:
    return web.json_response({"ok": False, "error": str(e)}, status=500)


async def api_setting_unit_index(request: web.Request) -> web.Response:
  units = await asyncio.to_thread(read_setting_unit_index)
  return web.json_response({"ok": True, "units": units.get("units", {})})


async def api_setting_unit_index_update(request: web.Request) -> web.Response:
  try:
    body = await request.json()
  except Exception:
    return web.json_response({"ok": False, "error": "invalid json"}, status=400)

  try:
    saved = await asyncio.to_thread(update_setting_unit_index, body)
    return web.json_response({"ok": True, "units": saved.get("units", {})})
  except Exception as e:
    return web.json_response({"ok": False, "error": str(e)}, status=500)


def _experimental_setup(params, change=None):
  """Expose the same vehicle-scoped request used by the native toggles page."""
  from openpilot.cereal import car
  from opendbc.car.hyundai.values import CANFD_CAR, CANFD_UNSUPPORTED_LONGITUDINAL_CAR
  from opendbc.car.selected_car import get_selected_car_platform
  from .intro.reconfigure import SetupError

  requested = params.get("AutoExperimentalPlatform") or ""
  platform = ""
  raw = params.get("CarParamsPersistent")
  if raw:
    try:
      with car.CarParams.from_bytes(raw) as cp:
        if (cp.brand == "hyundai" and cp.carFingerprint in CANFD_CAR and cp.carFingerprint not in CANFD_UNSUPPORTED_LONGITUDINAL_CAR
            and not cp.passive and not cp.dashcamOnly and params.get_int("HyundaiCameraSCC") == 0):
          platform = cp.carFingerprint
    except Exception:
      pass
  selected = params.get("CarSelected3")
  if params.get_bool("IsReleaseBranch") or (selected and get_selected_car_platform(selected) != platform):
    platform = ""
  if change is not None:
    enabled, expected = change
    if expected != (platform if enabled else requested) or not expected or (enabled and requested and requested != expected):
      raise SetupError("settings_changed")
    if enabled:
      params.put("AutoExperimentalPlatform", expected)
    else:
      params.remove("AutoExperimentalPlatform")
    requested = params.get("AutoExperimentalPlatform") or ""
    if requested != (expected if enabled else ""):
      raise SetupError("write_failed")
  return {"platform": platform, "requested": requested, "owner": get_longitudinal_setup_status(params)}


async def api_experimental_setup(request):
  from urllib.parse import urlsplit
  from .intro import reconfigure
  from .intro.routes import _reconfigure_guard, _setup_error

  if not HAS_PARAMS:
    return web.json_response({"ok": False, "error": "params_unavailable"}, status=503)
  change = None
  if request.method == "POST":
    origin = request.headers.get("Origin")
    if (origin and urlsplit(origin).netloc != request.host) or request.headers.get("Sec-Fetch-Site") == "cross-site":
      return web.json_response({"ok": False, "error": "same_origin_required"}, status=403)
    if request.content_type != "application/json":
      return web.json_response({"ok": False, "error": "invalid_selection"}, status=415)
    try:
      body = await request.json()
      if type(body["enabled"]) is not bool or not isinstance(body["platform"], str):
        raise ValueError
      change = body["enabled"], body["platform"]
    except (ValueError, KeyError, TypeError):
      return web.json_response({"ok": False, "error": "invalid_selection"}, status=400)

  def read_or_update():
    with reconfigure.LOCK:
      params = Params()
      if change is not None:
        _reconfigure_guard(request.app)
        if not params.get_bool("IsOffroad") or params.get_bool("IsOnroad"):
          raise reconfigure.SetupError("park_required")
      return _experimental_setup(params, change)

  try:
    state = await asyncio.to_thread(read_or_update)
    return web.json_response({"ok": True, **state}, headers={"Cache-Control": "no-store"})
  except reconfigure.SetupError as exc:
    return _setup_error(exc)


def register(app: web.Application) -> None:
  app.router.add_get("/api/settings/experimental_setup", api_experimental_setup)
  app.router.add_post("/api/settings/experimental_setup", api_experimental_setup)
  app.router.add_get("/api/settings", api_settings)
  app.router.add_get("/api/settings/snapshot", api_settings_snapshot)
  app.router.add_get("/api/setting_unit_index", api_setting_unit_index)
  app.router.add_post("/api/setting_unit_index", api_setting_unit_index_update)
