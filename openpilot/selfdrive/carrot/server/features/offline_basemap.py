"""Install a complete, redistributable Taiwan OSM map for the web viewer."""
import asyncio
import contextlib
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sqlite3

import aiohttp
from aiohttp import web

from ..config import CARROT_DATA_DIR


SOURCE = "https://download.geofabrik.de/asia/taiwan-shortbread-1.0.mbtiles"
LIMIT = 1024**3
RESERVE = 512 * 1024**2


def database(path):
  db = sqlite3.connect(path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
  db.execute("PRAGMA trusted_schema=OFF")
  return contextlib.closing(db)


def inspect_package(path):
  with database(path) as db:
    if db.execute("PRAGMA quick_check").fetchone() != ("ok",):
      raise ValueError("damaged map")
    meta = dict(db.execute("SELECT name, value FROM metadata"))
    if meta.get("format") != "pbf" or meta.get("name") != "Shortbread":
      raise ValueError("unexpected map format")
    bounds = [float(x) for x in meta["bounds"].split(",")]
    min_zoom, max_zoom = int(meta['minzoom']), int(meta['maxzoom'])
    if len(bounds) != 4 or not (-180 <= bounds[0] < bounds[2] <= 180 and -85.1 <= bounds[1] < bounds[3] <= 85.1 and 0 <= min_zoom <= max_zoom <= 20):
      raise ValueError("invalid map limits")
    sample = db.execute("SELECT tile_data FROM tiles LIMIT 1").fetchone()
    if not sample or sample[0][:2] != b"\x1f\x8b":
      raise ValueError("missing vector tiles")
    return {'bounds': bounds, 'minZoom': min_zoom, 'maxZoom': max_zoom}


def read_tile(path, z, x, y):
  with database(path) as db:
    row = db.execute("SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
                     (z, x, (1 << z) - 1 - y)).fetchone()
    return row[0] if row else None


class OfflineMap:
  def __init__(self, directory):
    self.path = Path(directory) / 'taiwan.mbtiles'
    self.partial = self.path.with_suffix('.download')
    self.task = None
    self.received = self.total = 0
    self.stage = 'idle'
    self.installed = None
    self.lock = asyncio.Lock()

  async def metadata(self):
    async with self.lock:
      if self.installed is None and self.path.is_file():
        try:
          self.installed = await asyncio.to_thread(installed_info, self.path)
        except (OSError, ValueError, KeyError, sqlite3.Error):
          self.stage = 'invalid'
      return self.installed

  def status(self):
    return {'stage': self.stage, 'installed': self.installed, 'received': self.received, 'total': self.total}

  def start(self, session):
    if self.task is None or self.task.done():
      self.received = self.total = 0
      self.stage = 'downloading'
      self.task = asyncio.create_task(self.download(session))

  async def download(self, session):
    try:
      self.path.parent.mkdir(parents=True, exist_ok=True)
      self.partial.unlink(missing_ok=True)
      async with session.get(SOURCE, timeout=aiohttp.ClientTimeout(total=1800, sock_read=45)) as response:
        response.raise_for_status()
        self.total = response.content_length or 0
        if self.total < 0 or self.total > LIMIT:
          raise ValueError("invalid package size")
        if shutil.disk_usage(self.path.parent).free < self.total + RESERVE:
          self.stage = 'space'
          return
        next_space_check = 0
        with self.partial.open('wb') as out:
          async for chunk in response.content.iter_chunked(256 * 1024):
            size = self.received + len(chunk)
            if size > (self.total or LIMIT):
              raise ValueError("package too large")
            if size >= next_space_check:
              if shutil.disk_usage(self.path.parent).free < RESERVE + len(chunk):
                self.stage = 'space'
                return
              next_space_check = size + 1024**2
            out.write(chunk)
            self.received = size
        if not self.received or (self.total and self.received != self.total):
          raise ValueError("incomplete package")
      self.stage = 'verifying'
      info = await asyncio.to_thread(installed_info, self.partial)
      async with self.lock:
        self.partial.replace(self.path)
        self.installed = info
        self.stage = 'idle'
    except (OSError, ValueError, KeyError, sqlite3.Error, TimeoutError, aiohttp.ClientError):
      self.stage = 'failed'
    finally:
      self.partial.unlink(missing_ok=True)


def installed_info(path):
  info = inspect_package(path)
  stat = path.stat()
  return dict(info, bytes=stat.st_size, version=str(stat.st_mtime_ns),
              installedAt=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat())


def register(app, directory=None):
  store = OfflineMap(directory if directory is not None else Path(CARROT_DATA_DIR) / 'maps')

  async def status(_):
    await store.metadata()
    return web.json_response(store.status(), headers={'Cache-Control': 'no-store'})

  async def install(request):
    if request.content_type != 'application/json' or request.headers.get('Sec-Fetch-Site') == 'cross-site':
      raise web.HTTPBadRequest()
    await store.metadata()
    store.start(request.app['http'])
    return web.json_response(store.status(), status=202, headers={'Cache-Control': 'no-store'})

  async def tile(request):
    try:
      z, x, y = (int(request.match_info[k]) for k in ('z', 'x', 'y'))
      if not 0 <= z <= 20 or not (0 <= x < 1 << z and 0 <= y < 1 << z) or not store.path.is_file():
        raise web.HTTPNotFound()
      data = await asyncio.to_thread(read_tile, store.path, z, x, y)
    except (ValueError, OverflowError, sqlite3.Error):
      raise web.HTTPBadRequest() from None
    headers = {'Cache-Control': 'private, max-age=86400'}
    if data is None:
      return web.Response(status=204, headers=headers)
    return web.Response(body=data, content_type='application/vnd.mapbox-vector-tile', headers={**headers, 'Content-Encoding': 'gzip'})

  async def stop(_):
    if store.task and not store.task.done():
      store.task.cancel()
      with contextlib.suppress(asyncio.CancelledError):
        await store.task

  app.on_cleanup.append(stop)
  app.router.add_get('/api/navigation/offline', status)
  app.router.add_post('/api/navigation/offline', install)
  app.router.add_get('/api/navigation/offline/tiles/{z:\\d+}/{x:\\d+}/{y:\\d+}.pbf', tile)
