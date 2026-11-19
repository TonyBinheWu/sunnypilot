import asyncio
import gzip
import sqlite3
from contextlib import closing

import pytest

from openpilot.selfdrive.carrot.server.features.offline_basemap import OfflineMap, installed_info, read_tile


def sample(path):
  with closing(sqlite3.connect(path)) as db:
    db.execute('CREATE TABLE metadata(name TEXT, value TEXT)')
    db.executemany('INSERT INTO metadata VALUES(?,?)', [('name', 'Shortbread'), ('format', 'pbf'), ('minzoom', '0'),
                                                       ('maxzoom', '14'), ('bounds', '118,20,123,27')])
    db.execute('CREATE TABLE tiles(zoom_level, tile_column, tile_row, tile_data)')
    db.execute('INSERT INTO tiles VALUES(3,5,6,?)', (gzip.compress(b'example'),))
    db.commit()


class Transfer:
  def __init__(self, data, total=None):
    self.data = data
    self.content_length = len(data) if total is None else total
    self.content = self
    self.requests = 0

  def get(self, *_args, **_kwargs):
    self.requests += 1
    return self

  async def __aenter__(self):
    return self

  async def __aexit__(self, *_args):
    pass

  def raise_for_status(self):
    pass

  async def iter_chunked(self, _):
    yield self.data


def test_download_persists_deduplicates_and_preserves_previous_map(tmp_path):
  source = tmp_path / 'source'
  sample(source)
  first = source.read_bytes()
  store = OfflineMap(tmp_path / 'maps')

  async def run():
    transfer = Transfer(first)
    store.start(transfer)
    store.start(transfer)
    await store.task
    assert transfer.requests == 1 and store.installed['bytes'] == len(first)
    original = store.installed.copy()
    for broken in (Transfer(first[:100], len(first)), Transfer(b'not a package')):
      store.start(broken)
      await store.task
      assert store.stage == 'failed' and not store.partial.exists()
      assert store.path.read_bytes() == first and store.installed == original
    assert await OfflineMap(store.path.parent).metadata() == original
    chunked = Transfer(first)
    chunked.content_length = None
    store.start(chunked)
    await store.task
    assert store.stage == 'idle' and store.installed['bytes'] == len(first)
  asyncio.run(run())
  assert gzip.decompress(read_tile(store.path, 3, 5, 1)) == b'example'
  assert read_tile(store.path, 3, 5, 6) is None


def test_reject_invalid_bounds(tmp_path):
  archive = tmp_path / 'map'
  sample(archive)
  with closing(sqlite3.connect(archive)) as db:
    db.execute("UPDATE metadata SET value='0,90,25,180' WHERE name='bounds'")
    db.commit()
  with pytest.raises(ValueError):
    installed_info(archive)
