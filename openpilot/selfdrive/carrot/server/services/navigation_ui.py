"""Navigation UI shared by the vehicle and the read-only GPU replay host."""
from pathlib import Path

from aiohttp import web

from ..config import WEB_DIR
from .static_assets import fingerprint_static_asset


def version_assets(html, web_dir, assets):
  for asset in assets:
    fingerprint = fingerprint_static_asset(web_dir, asset)
    if fingerprint:
      html = html.replace(f'"{asset}"', f'"{asset}?v={fingerprint}"')
  return html


async def page(_request, *, replay=False):
  html = Path(WEB_DIR, 'navigation.html').read_text(encoding='utf-8')
  if replay:
    html = html.replace('<html ', '<html data-navigation-replay ', 1)
  html = version_assets(html, WEB_DIR, ('/css/navigation-guidance.css', '/js/generated/offline-map.js', '/js/pages/navigation_zh_tw.js',
                                        '/js/pages/navigation_osm.js', '/js/pages/navigation_map.js'))
  return web.Response(text=html, content_type='text/html', headers={'Cache-Control': 'no-store'})


async def map_config(_request):
  return web.json_response({'provider': 'openstreetmap', 'basemaps': ['openstreetmap'],
                            'search': 'mapbox', 'routing': 'mapbox', 'model': 'mapsd',
                            'osm_tile_url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'},
                           headers={'Cache-Control': 'no-store'})
