"""Read-only, opt-in publication of offline lane candidates; no log upload."""
import asyncio
import hashlib
import json
import math
import re
from pathlib import Path

from aiohttp import web

MAX_BYTES = 8 * 1024 * 1024
ROOT = web.AppKey('lane_mapping_root', Path)
IDENTIFIER = re.compile(r'^[A-Za-z0-9_.-]{1,80}$')


def read_project(root, name):
  if not IDENTIFIER.fullmatch(name) or name in ('.', '..'):
    raise ValueError('invalid_project_id')
  path = root / (name+'.json')
  if any(part.is_symlink() for part in (path, root, *root.parents)) or not path.is_file():
    raise ValueError('project_unavailable')
  # Read at most the budget even if a concurrent writer enlarged the file.
  with path.open('rb') as stream:
    raw = stream.read(MAX_BYTES+1)
  if len(raw) > MAX_BYTES:
    raise ValueError('project_too_large')
  value = json.loads(raw)
  if not isinstance(value, dict) or value.get('schema') != 'carrot-lane-map/v1' or value.get('ground_truth') is not False or value.get('control_eligible') is not False:
    raise ValueError('unsupported_project')
  revision = value.get('revision')
  content = {k: v for k, v in value.items() if k != 'revision'}
  actual = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
  if revision != actual:
    raise ValueError('revision_mismatch')
  cells = value.get('cells')
  if not isinstance(cells, list) or len(cells) > 25_000:
    raise ValueError('cell_limit')
  for cell in cells:
    xyz = cell.get('xyz')
    if not isinstance(xyz, list) or len(xyz) != 3 or any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or abs(x) > 100_000 for x in xyz):
      raise ValueError('invalid_coordinates')
  return value


async def page(_request):
  from ..config import WEB_DIR
  from ..services.static_assets import fingerprint_static_asset
  html = await asyncio.to_thread(Path(WEB_DIR, 'lane-mapping.html').read_text, encoding='utf-8')
  for asset in ('/js/generated/lane-mapping.js', '/js/generated/display-preferences.js'):
    fingerprint = fingerprint_static_asset(WEB_DIR, asset)
    if fingerprint:
      html = html.replace(f'src="{asset}"', f'src="{asset}?v={fingerprint}"')
  return web.Response(text=html, content_type='text/html', headers={'Cache-Control': 'no-store'})


def catalog(root):
  if not root.is_dir() or any(part.is_symlink() for part in (root, *root.parents)):
    return []
  result = []
  # Do not parse all point clouds just to list names; opening validates the revision.
  for i, path in enumerate(root.iterdir()):
    if i >= 256 or len(result) >= 32:
      break
    if path.suffix == '.json' and IDENTIFIER.fullmatch(path.stem) and not path.is_symlink() and path.is_file():
      result.append(path.stem)
  return sorted(result)


async def listing(request):
  try:
    names = await asyncio.to_thread(catalog, request.app[ROOT])
    return web.json_response({'projects': names, 'limit': 32}, headers={'Cache-Control': 'no-store'})
  except OSError:
    return web.json_response({'projects': [], 'error': 'catalog_unavailable'}, status=503)


async def project(request):
  try:
    value = await asyncio.to_thread(read_project, request.app[ROOT], request.match_info['name'])
    return web.json_response(value, headers={'Cache-Control': 'no-store'})
  except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError):
    return web.json_response({'error': 'project_unavailable_or_invalid'}, status=404, headers={'Cache-Control': 'no-store'})


def register(app, root=None):
  if root is None:
    from ..config import CARROT_DATA_DIR
    root = Path(CARROT_DATA_DIR, 'mapping')
  app[ROOT] = Path(root).absolute()
  app.router.add_get('/lane-mapping', page)
  app.router.add_get('/api/lane-mapping/projects', listing)
  app.router.add_get('/api/lane-mapping/projects/{name}', project)
