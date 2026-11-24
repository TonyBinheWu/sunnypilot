"""Geofabrik Shortbread road tiles for installed country packages."""
from contextlib import closing
from functools import lru_cache
import gzip
import io
import json
import os
from pathlib import Path
import sqlite3

COUNTRIES = {'taiwan': 'asia', 'south-korea': 'asia', 'andorra': 'europe', 'luxembourg': 'europe'}


def active_country(directory):
  try:
    key = json.loads((directory / 'active.json').read_bytes())['country']
    if isinstance(key, str) and key in COUNTRIES:
      return key
  except (OSError, ValueError, KeyError, TypeError):
    pass
  return 'taiwan'


def database(path):
  db = sqlite3.connect(path.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
  db.execute('PRAGMA trusted_schema=OFF')
  return closing(db)


def read_tile(path, z, x, y):
  with database(path) as db:
    row = db.execute('SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?',
                     (z, x, (1 << z) - 1 - y)).fetchone()
  return row[0] if row else None


@lru_cache(maxsize=4)
def metadata(path, stamp):
  with database(path) as db:
    meta = dict(db.execute('SELECT name, value FROM metadata'))
  return [float(n) for n in meta['bounds'].split(',')], int(meta['minzoom']), int(meta['maxzoom'])


def local_source(gps):
  if gps is None:
    return None
  directory = Path(os.getenv('CARROT_DATA_DIR', '/data/carrot')) / 'maps'
  path = directory / (active_country(directory) + '.mbtiles')
  try:
    stamp = path.stat().st_mtime_ns
    (west, south, east, north), low, high = metadata(path, stamp)
    if west <= gps.longitude <= east and south <= gps.latitude <= north and 0 <= low <= high <= 20:
      return path, stamp, low, high
  except (OSError, ValueError, KeyError, sqlite3.Error):
    pass
  return None


class ShortbreadTiles:
  def __init__(self, path, stamp, low, high):
    self.path, self.min_zoom, self.max_zoom = path, low, high

  def get(self, z, x, y):
    try:
      blob = read_tile(self.path, z, x, y)
      if blob is None:
        return None
      with gzip.GzipFile(fileobj=io.BytesIO(blob)) as gz:
        data = gz.read(4 * 1024 * 1024 + 1)
      if len(data) > 4 * 1024 * 1024:
        raise ValueError('Oversized road tile')
      return data
    except (EOFError, sqlite3.Error) as exc:
      raise OSError('Unreadable road tile') from exc

  def close(self):
    pass
