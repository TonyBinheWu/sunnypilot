"""Mapbox search/destination UI and the shared nav-model preview."""
import asyncio
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
import time
import unicodedata

import aiohttp
from aiohttp import web

from openpilot.common.params import Params
from ..config import WEB_DIR, CARROT_NAVIGATION_FAVORITES_PATH
from ..services.navigation_favorites import FavoritesFull, NavigationFavorites, google_reference, query_reference
from ..services.static_assets import fingerprint_static_asset
from ..services.params import get_param_value, set_param_value
from openpilot.selfdrive.navigation.preview import PREVIEW_PATH, VIEW_PATH, WEB_DEMAND_PATH, preview_fresh, preview_reason

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
  for asset in ('/js/pages/navigation_zh_tw.js', '/js/pages/navigation_osm.js', '/js/pages/navigation_map.js'):
    fingerprint = fingerprint_static_asset(WEB_DIR, asset)
    if fingerprint:
      html = html.replace(f'src="{asset}"', f'src="{asset}?v={fingerprint}"')
  return web.Response(text=html, content_type='text/html', headers={'Cache-Control': 'no-store'})


async def map_config(_request):
  return web.json_response({'provider': 'openstreetmap', 'basemaps': ['openstreetmap'],
                            'search': 'mapbox', 'routing': 'mapbox', 'model': 'mapsd',
                            'osm_tile_url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'},
                           headers={'Cache-Control': 'no-store'})


async def route_view(_request):
  try:
    WEB_DEMAND_PATH.touch()
    if VIEW_PATH.stat().st_size > 512 * 1024:
      raise ValueError('oversized view')
    value = json.loads(VIEW_PATH.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or not 0 <= time.time() - float(value['generated_at']) < 3.:
      raise ValueError('stale view')
  except (OSError, ValueError, KeyError, TypeError, OverflowError):
    value = {'position': None, 'coordinates': [], 'route_id': 0}
  return web.json_response(value, headers={'Cache-Control': 'no-store'})


async def search(request):
  # Explicitly reject paid permanent requests, including old cached clients.
  if request.query.get('permanent', 'false').lower() not in ('false', '0', ''):
    return web.json_response({'error': 'Permanent geocoding is disabled. Reload navigation.'}, status=400)
  query = unicodedata.normalize('NFKC', request.query.get('q', '')).strip()
  if not 2 <= len(query) <= 200:
    return web.json_response({'error': 'Enter 2–200 characters.'}, status=400)
  country, language = request.query.get('country', ''), request.query.get('language', '')
  if country not in ('', 'tw') or language not in ('', 'en', 'ko', 'zh', 'zh-Hant'):
    return web.json_response({'error': 'Invalid search region or language.'}, status=400)
  token = str(get_param_value('MapboxPublicKey', '') or '').strip()
  if not token:
    return web.json_response({'error': 'Set the Mapbox Public key in Settings → Network.'}, status=409)
  state = request.app[SEARCH_STATE]
  if state.lock.locked() or time.monotonic() < state.next_request:
    return web.json_response({'error': 'Please wait before searching again.'}, status=429)
  async with state.lock:
    state.next_request = time.monotonic() + 1.
    try:
      params = {'q': query, 'access_token': token, 'limit': '5', 'autocomplete': 'false', 'permanent': 'false'}
      if country:
        params['country'] = country
      if language:
        params['language'] = language
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
          metadata = {'feature_type': str(properties.get('feature_type', ''))[:32],
                      'accuracy': str((properties.get('coordinates') or {}).get('accuracy', ''))[:32],
                      'match_confidence': str((properties.get('match_code') or {}).get('confidence', ''))[:32]}
          results.append(dict(destination({'latitude': lat, 'longitude': lon,
                                           'place_name': properties.get('full_address') or properties.get('name') or query}),
                              permanent=False, **metadata))
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
  try:
    if request.path.endswith('/destination'):
      # Cached older pages must not show "destination set" for a query shortcut.
      return web.json_response({'error': 'Select a search result first. Reload navigation.'}, status=409)
    if request.path.endswith('/query'):
      saved = next((item for item in store.read() if item['id'] == identifier), None)
      if saved is None:
        raise KeyError(identifier)
      if saved.get('provider') == 'google':
        return web.json_response({'error': 'Enter an address or search text for this legacy favorite.'}, status=409)
      # A favorite is a query shortcut, never an implicit destination command.
      # Legacy permanent coordinates remain on disk until explicitly edited;
      # their original address is searched again before the user selects a point.
      return web.json_response({'query': saved.get('query') or saved['place_name'], 'requires_selection': True},
                               headers={'Cache-Control': 'no-store'})
    if request.method == 'GET':
      result = {'favorites': store.read()}
    elif request.method == 'DELETE':
      result = {'favorites': store.delete(identifier)}
    else:
      try:
        body = await request.json()
        if not isinstance(body, dict):
          raise ValueError('invalid favorite')
        if body.get('provider') == 'query':
          value = query_reference(body)
        else:
          # Existing records may still be renamed by an older client. Never
          # accept a new coordinate/Google record or an address replacement.
          previous = next((item for item in store.read() if item['id'] == identifier), None) if identifier else None
          if previous is None:
            raise ValueError('query favorites required')
          if body.get('provider') == 'google':
            value = google_reference(body)
            if previous.get('provider') != 'google' or value['google_place_id'] != previous['google_place_id']:
              raise ValueError('invalid legacy reference')
          else:
            value = destination(body)
            if any(value[key] != previous.get(key) for key in ('latitude', 'longitude', 'place_name')):
              raise ValueError('query favorites required')
            name = body.get('name')
            if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
              raise ValueError('invalid name')
            value['name'] = name.strip()
      except (ValueError, KeyError, TypeError, OverflowError):
        return web.json_response({'error': 'Save a name and address text. Coordinate favorites are no longer created.'}, status=400)
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
  app.router.add_get('/api/navigation/config', map_config)
  app.router.add_get('/api/navigation/route_view', route_view)
  app.router.add_get('/api/navigation/search', search)
  app.router.add_get('/api/navigation/destination', get_destination)
  app.router.add_post('/api/navigation/destination', set_destination)
  app.router.add_delete('/api/navigation/destination', clear_destination)
  app.router.add_get('/api/navigation/favorites', favorites)
  app.router.add_post('/api/navigation/favorites', favorites)
  app.router.add_put('/api/navigation/favorites/{identifier}', favorites)
  app.router.add_delete('/api/navigation/favorites/{identifier}', favorites)
  app.router.add_post('/api/navigation/favorites/{identifier}/destination', favorites)
  app.router.add_get('/api/navigation/favorites/{identifier}/query', favorites)
  app.router.add_get('/api/navigation/map.png', preview)
