"""Mapbox search/destination UI and the shared nav-model preview."""
import asyncio
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
import time

import aiohttp
from aiohttp import web

from openpilot.common.params import Params
from ..config import WEB_DIR, CARROT_NAVIGATION_FAVORITES_PATH
from ..services.navigation_favorites import FavoritesFull, NavigationFavorites
from ..services.static_assets import fingerprint_static_asset
from ..services.params import get_param_value, set_param_value
from openpilot.selfdrive.navigation.preview import PREVIEW_PATH, WEB_DEMAND_PATH, preview_fresh, preview_reason

MAX_RESPONSE = 1024 * 1024


@dataclass
class SearchState:
  lock: asyncio.Lock = field(default_factory=asyncio.Lock)
  next_request: float = 0.


SEARCH_STATE = web.AppKey('navigation_search', SearchState)
FAVORITES = web.AppKey('navigation_favorites', NavigationFavorites)


def destination(value):
  if not isinstance(value, dict):
    raise ValueError('invalid destination')
  lat, lon = float(value['latitude']), float(value['longitude'])
  if not math.isfinite(lat) or not math.isfinite(lon) or abs(lat) > 85.05112878 or abs(lon) > 180:
    raise ValueError('invalid coordinates')
  return {'latitude': lat, 'longitude': lon, 'place_name': str(value.get('place_name', 'Destination'))[:256]}


async def page(request):
  html = Path(WEB_DIR, 'navigation.html').read_text(encoding='utf-8')
  for asset in ('/js/pages/navigation_zh_tw.js', '/js/pages/navigation_map.js'):
    fingerprint = fingerprint_static_asset(WEB_DIR, asset)
    if fingerprint:
      html = html.replace(f'src="{asset}"', f'src="{asset}?v={fingerprint}"')
  return web.Response(text=html, content_type='text/html', headers={'Cache-Control': 'no-store'})


async def search(request):
  query = request.query.get('q', '').strip()
  if not 2 <= len(query) <= 200:
    return web.json_response({'error': 'Enter 2–200 characters.'}, status=400)
  token = str(get_param_value('MapboxPublicKey', '') or '').strip()
  if not token:
    return web.json_response({'error': 'Set the Mapbox Public key in Settings → Network.'}, status=409)
  state = request.app[SEARCH_STATE]
  if state.lock.locked() or time.monotonic() < state.next_request:
    return web.json_response({'error': 'Please wait before searching again.'}, status=429)
  async with state.lock:
    state.next_request = time.monotonic() + 1.
    try:
      permanent = request.query.get('permanent') == 'true'
      params = {'q': query, 'access_token': token, 'limit': '5', 'autocomplete': 'false', 'permanent': str(permanent).lower()}
      async with request.app['http'].get('https://api.mapbox.com/search/geocode/v6/forward', params=params,
                                         timeout=aiohttp.ClientTimeout(total=8)) as response:
        if response.status != 200:
          return web.json_response({'error': f'Mapbox search failed (HTTP {response.status}).'}, status=502)
        body = bytearray()
        async for chunk in response.content.iter_chunked(65536):
          body.extend(chunk)
          if len(body) > MAX_RESPONSE:
            raise ValueError('oversized response')
        results = []
        for feature in json.loads(body).get('features', [])[:5]:
          lon, lat = feature['geometry']['coordinates'][:2]
          properties = feature.get('properties', {})
          results.append(dict(destination({'latitude': lat, 'longitude': lon,
                                           'place_name': properties.get('full_address') or properties.get('name') or query}), permanent=permanent))
        return web.json_response({'results': results}, headers={'Cache-Control': 'no-store'})
    except (aiohttp.ClientError, TimeoutError, ValueError, KeyError, TypeError, IndexError, AttributeError):
      return web.json_response({'error': 'Mapbox search is unavailable.'}, status=502)


async def get_destination(request):
  try:
    value = Params('/dev/shm/params').get('NavDestinationTemporary') or get_param_value('NavDestination', '')
    current = destination(json.loads(value)) if value else None
  except (ValueError, KeyError, TypeError, OverflowError):
    current = None
  return web.json_response({'destination': current, 'map_ready': preview_fresh() and preview_reason() == 'ready',
                            'key_configured': bool(get_param_value('MapboxPublicKey', ''))},
                           headers={'Cache-Control': 'no-store'})


async def set_destination(request):
  try:
    value = destination(await request.json())
  except (ValueError, KeyError, TypeError, OverflowError):
    return web.json_response({'error': 'Invalid destination.'}, status=400)
  activate_destination(value)
  return web.json_response({'destination': value}, headers={'Cache-Control': 'no-store'})


def activate_destination(value):
  # Keep the active destination in RAM. Manager clears it when the drive ends.
  set_param_value('NavDestination', '')
  set_param_value('NavDestinationWaypoints', '')
  Params('/dev/shm/params').put('NavDestinationTemporary', json.dumps(value, ensure_ascii=False))


async def favorites(request):
  store = request.app[FAVORITES]
  identifier = request.match_info.get('identifier')
  value = None
  if request.method in ('POST', 'PUT') and not request.path.endswith('/destination'):
    try:
      body = await request.json()
      value = destination(body)
      name = body.get('name')
      if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
        raise ValueError('invalid name')
      if not isinstance(body.get('place_name'), str) or not 1 <= len(body['place_name'].strip()) <= 256:
        raise ValueError('invalid address')
      if any(type(body.get(key)) not in (int, float) for key in ('latitude', 'longitude')):
        raise ValueError('invalid coordinates')
      value.update(name=name.strip(), place_name=body['place_name'].strip())
    except (ValueError, KeyError, TypeError, OverflowError):
      return web.json_response({'error': 'Invalid favorite.'}, status=400)
  try:
    # Existing saved coordinates may be renamed without another geocode.
    if value is not None and body.get('permanent') is not True:
      previous = next((item for item in store.read() if item['id'] == identifier), None) if identifier else None
      if previous is None or any(value[key] != previous[key] for key in ('latitude', 'longitude', 'place_name')):
        return web.json_response({'error': 'Invalid favorite.'}, status=400)
    if request.path.endswith('/destination'):
      saved = next((item for item in store.read() if item['id'] == identifier), None)
      if saved is None:
        raise KeyError(identifier)
      target = destination(saved)
      activate_destination(target)
      result = {'destination': target}
    elif request.method == 'GET':
      result = {'favorites': store.read()}
    elif request.method == 'DELETE':
      result = {'favorites': store.delete(identifier)}
    else:
      result = {'favorites': store.save(value, identifier)}
    return web.json_response(result, headers={'Cache-Control': 'no-store'})
  except KeyError:
    return web.json_response({'error': 'Favorite not found.'}, status=404)
  except FavoritesFull:
    return web.json_response({'error': 'You can save up to 100 favorites.'}, status=409)
  except (OSError, ValueError, TypeError, OverflowError):
    return web.json_response({'error': 'Favorites are unavailable. Please try again.'}, status=503)


async def clear_destination(request):
  set_param_value('NavDestination', '')
  Params('/dev/shm/params').remove('NavDestinationTemporary')
  set_param_value('NavDestinationWaypoints', '')
  return web.json_response({'destination': None})


async def preview(request):
  try:
    WEB_DEMAND_PATH.touch()
  except OSError:
    pass
  if not preview_fresh():
    reason = 'waiting' if get_param_value('IsOnroad', False) else 'offroad'
    return web.Response(status=204, headers={'Cache-Control': 'no-store', 'X-Nav-Map-Status': reason})
  return web.FileResponse(PREVIEW_PATH, headers={'Cache-Control': 'no-store', 'X-Nav-Map-Status': preview_reason()})


def register(app):
  app[SEARCH_STATE] = SearchState()
  app[FAVORITES] = NavigationFavorites(CARROT_NAVIGATION_FAVORITES_PATH)
  app.router.add_get('/navigation', page)
  app.router.add_get('/api/navigation/search', search)
  app.router.add_get('/api/navigation/destination', get_destination)
  app.router.add_post('/api/navigation/destination', set_destination)
  app.router.add_delete('/api/navigation/destination', clear_destination)
  app.router.add_get('/api/navigation/favorites', favorites)
  app.router.add_post('/api/navigation/favorites', favorites)
  app.router.add_put('/api/navigation/favorites/{identifier}', favorites)
  app.router.add_delete('/api/navigation/favorites/{identifier}', favorites)
  app.router.add_post('/api/navigation/favorites/{identifier}/destination', favorites)
  app.router.add_get('/api/navigation/map.png', preview)
