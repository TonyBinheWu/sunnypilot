"""Optional display-only OSM parking polygons, never navigation/control input."""
import asyncio
import json
import math
import time
from dataclasses import dataclass, field

import aiohttp
from aiohttp import web

from openpilot.selfdrive.navigation.preview import VIEW_PATH, WEB_DEMAND_PATH
from ..services.web_settings import read_web_settings


@dataclass
class ParkingCache:
  lock: asyncio.Lock = field(default_factory=asyncio.Lock)
  attempted: float = -math.inf
  generated: float = -math.inf
  center: tuple | None = None
  areas: list = field(default_factory=list)


KEY = web.AppKey('parking_display_cache', ParkingCache)


def parse_areas(data, lat, lon):
  areas = []
  for item in data.get('elements', [])[:500]:
    tags = item.get('tags', {})
    if item.get('type') != 'way' or tags.get('amenity') not in ('parking', 'parking_space'):
      continue
    geometry = item.get('geometry', [])
    if not 4 <= len(geometry) <= 300:
      continue
    points = [[p.get('lat'), p.get('lon')] for p in geometry]
    if any(not isinstance(n, (float, int)) or not math.isfinite(n) for p in points for n in p):
      continue
    if points[0] != points[-1] or any(abs(p[0]-lat) > .005 or abs(p[1]-lon) > .006 for p in points):
      continue
    areas.append({'id': str(item.get('id', ''))[:32], 'kind': tags['amenity'],
                  'name': str(tags.get('name', ''))[:100], 'points': points, 'occupancy': 'unknown'})
  return areas[:80]


async def context(request):
  headers = {'Cache-Control': 'no-store'}
  # A separate explicit location-sharing preference; no requests while off.
  if not read_web_settings().get('vision_parking_map'):
    return web.json_response({'status': 'off', 'areas': []}, headers=headers)
  WEB_DEMAND_PATH.touch()
  try:
    if VIEW_PATH.stat().st_size > 512*1024:
      raise ValueError()
    view = json.loads(VIEW_PATH.read_text(encoding='utf-8'))
    lat, lon = float(view['position']['lat']), float(view['position']['lng'])
    if not all(math.isfinite(n) for n in (lat, lon)) or abs(lat) > 85 or abs(lon) > 180 or not 0 <= time.time()-float(view['generated_at']) < 3:
      raise ValueError()
  except (OSError, KeyError, TypeError, ValueError):
    return web.json_response({'status': 'no_position', 'areas': []}, headers=headers)
  cache = request.app[KEY]
  now = time.monotonic()
  near = cache.center and abs(lat-cache.center[0]) < .0007 and abs(lon-cache.center[1]) < .0008
  if now-cache.generated < 600 and near:
    return web.json_response({'status': 'ready', 'position': [lat, lon], 'areas': cache.areas}, headers=headers)
  if cache.lock.locked() or now-cache.attempted < 60:
    return web.json_response({'status': 'waiting', 'areas': []}, headers=headers)
  async with cache.lock:
    cache.attempted = now
    query = f'[out:json][timeout:5];way["amenity"~"^(parking|parking_space)$"](around:180,{lat:.5f},{lon:.5f});out geom;'
    try:
      async with request.app['http'].post('https://overpass-api.de/api/interpreter', data={'data': query},
                                          timeout=aiohttp.ClientTimeout(total=8)) as response:
        if response.status != 200:
          raise ValueError()
        body = bytearray()
        async for chunk in response.content.iter_chunked(65536):
          body.extend(chunk)
          if len(body) > 1024*1024:
            raise ValueError()
        areas = parse_areas(json.loads(body), lat, lon)
      cache.areas, cache.center, cache.generated = areas, (lat, lon), time.monotonic()
      return web.json_response({'status': 'ready', 'position': [lat, lon], 'areas': areas}, headers=headers)
    except (aiohttp.ClientError, TimeoutError, ValueError, TypeError, AttributeError):
      return web.json_response({'status': 'unavailable', 'areas': []}, headers=headers)


def register(app):
  app[KEY] = ParkingCache()
  app.router.add_get('/api/navigation/parking', context)
