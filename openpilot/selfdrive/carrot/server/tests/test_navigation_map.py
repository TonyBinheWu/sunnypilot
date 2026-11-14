import asyncio
import json
from contextlib import asynccontextmanager
from types import SimpleNamespace as NS

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from openpilot.selfdrive.carrot.server.features import navigation


@pytest.fixture(autouse=True)
def temporary_params(monkeypatch):
  values = {}
  def params(path):
    assert path == '/dev/shm/params'
    return NS(get=values.get, put=values.__setitem__, remove=lambda key: values.pop(key, None))
  monkeypatch.setattr(navigation, 'Params', params)
  return values


def test_destination_lifecycle_and_validation(monkeypatch, temporary_params):
  values = {}
  monkeypatch.setattr(navigation, 'get_param_value', lambda key, default: values.get(key, default))
  monkeypatch.setattr(navigation, 'set_param_value', lambda key, value: values.__setitem__(key, value))

  async def run():
    app = web.Application()
    navigation.register(app)
    async with TestClient(TestServer(app)) as client:
      response = await client.post('/api/navigation/destination', json={'latitude': 37., 'longitude': 127., 'place_name': '<script>name</script>'})
      assert response.status == 200
      assert json.loads(temporary_params['NavDestinationTemporary'])['place_name'] == '<script>name</script>'
      assert 'NavDestinationTemporary' not in values
      assert response.headers['Cache-Control'] == 'no-store'
      assert values['NavDestination'] == ''
      response = await client.get('/api/navigation/destination')
      assert response.headers['Cache-Control'] == 'no-store'
      assert (await response.json())['destination']['latitude'] == 37.
      for payload in ([], {}, {'latitude': 91, 'longitude': 127}, {'latitude': None, 'longitude': 0}):
        assert (await client.post('/api/navigation/destination', json=payload)).status == 400
      assert (await client.get('/api/navigation/search?q=Seoul')).status == 409
      assert (await client.delete('/api/navigation/destination')).status == 200
      assert values['NavDestination'] == ''
      assert not temporary_params
  asyncio.run(run())


def test_navigation_page_is_served():
  async def run():
    app = web.Application()
    navigation.register(app)
    async with TestClient(TestServer(app)) as client:
      response = await client.get('/navigation')
      assert response.status == 200
      assert response.headers['Cache-Control'] == 'no-store'
      assert 'navigation_map.js?v=' in await response.text()
  asyncio.run(run())


def test_favorite_limit_and_stale_id_do_not_overwrite_other_favorites(monkeypatch, tmp_path):
  path = tmp_path / 'favorites.json'
  monkeypatch.setattr(navigation, 'CARROT_NAVIGATION_FAVORITES_PATH', str(path))
  existing = [dict(id=f'{i:032x}', name=f'最愛{i}', place_name='地址', latitude=25., longitude=121.) for i in range(100)]
  path.write_text(json.dumps(existing, ensure_ascii=False), encoding='utf-8')
  async def run():
    app = web.Application(); navigation.register(app)
    async with TestClient(TestServer(app)) as client:
      new = dict(name='新最愛', place_name='地址', latitude=25., longitude=121., permanent=True)
      assert (await client.post('/api/navigation/favorites', json=new)).status == 409
      assert json.loads(path.read_text(encoding='utf-8')) == existing
      assert (await client.put('/api/navigation/favorites/missing', json=new)).status == 404
      assert (await client.delete('/api/navigation/favorites/missing')).status == 404
      assert (await client.put('/api/navigation/favorites/' + existing[0]['id'], json=new)).status == 200
      saved = json.loads(path.read_text(encoding='utf-8'))
      assert len(saved) == 100 and saved[0]['name'] == '新最愛' and saved[1:] == existing[1:]
  asyncio.run(run())


@pytest.mark.parametrize('fresh,reason,ready', [
  (True, 'route', False), (True, 'position', False), (True, 'ready', True), (False, 'ready', False),
])
def test_destination_requires_usable_preview(monkeypatch, fresh, reason, ready):
  monkeypatch.setattr(navigation, 'get_param_value', lambda key, default: default)
  monkeypatch.setattr(navigation, 'preview_fresh', lambda: fresh)
  monkeypatch.setattr(navigation, 'preview_reason', lambda: reason)
  response = asyncio.run(navigation.get_destination(None))
  assert json.loads(response.text)['map_ready'] is ready


@pytest.mark.parametrize('onroad,reason', [(False, 'offroad'), (True, 'waiting')])
def test_missing_preview_explains_service_state(monkeypatch, tmp_path, onroad, reason):
  demand = tmp_path / 'demand'
  monkeypatch.setattr(navigation, 'WEB_DEMAND_PATH', demand)
  monkeypatch.setattr(navigation, 'preview_fresh', lambda: False)
  monkeypatch.setattr(navigation, 'get_param_value', lambda key, default: onroad if key == 'IsOnroad' else default)
  response = asyncio.run(navigation.preview(None))
  assert response.status == 204
  assert response.headers['X-Nav-Map-Status'] == reason
  assert response.headers['Cache-Control'] == 'no-store'
  assert demand.exists()


@pytest.mark.parametrize('permanent', [False, True])
def test_search_reads_fragmented_response_and_keeps_token_server_side(monkeypatch, permanent):
  monkeypatch.setattr(navigation, 'get_param_value', lambda key, default: 'pk.private-test')
  payload = json.dumps({'features': [{'geometry': {'coordinates': [127., 37.]},
                                     'properties': {'full_address': 'Test destination'}}]}).encode()
  async def chunks(_):
    for i in range(0, len(payload), 7):
      yield payload[i:i + 7]
  @asynccontextmanager
  async def get(url, **kwargs):
    assert url == 'https://api.mapbox.com/search/geocode/v6/forward'
    assert kwargs['params']['access_token'] == 'pk.private-test'
    assert kwargs['params']['permanent'] == str(permanent).lower()
    yield NS(status=200, content=NS(iter_chunked=chunks))
  async def run():
    app = web.Application()
    app['http'] = NS(get=get)
    navigation.register(app)
    async with TestClient(TestServer(app)) as client:
      response = await client.get('/api/navigation/search?q=Seoul' + ('&permanent=true' if permanent else ''))
      body = await response.text()
      assert response.status == 200 and 'pk.private-test' not in body
      assert response.headers['Cache-Control'] == 'no-store'
      assert json.loads(body)['results'][0]['latitude'] == 37.
      assert json.loads(body)['results'][0]['permanent'] is permanent
      assert (await client.get('/api/navigation/search?q=Seoul')).status == 429
  asyncio.run(run())


def test_favorites_crud_persistence_and_navigation(monkeypatch, tmp_path, temporary_params):
  path = tmp_path / 'favorites.json'
  monkeypatch.setattr(navigation, 'CARROT_NAVIGATION_FAVORITES_PATH', str(path))
  monkeypatch.setattr(navigation, 'set_param_value', lambda *args: None)
  async def run():
    app = web.Application(); navigation.register(app)
    async with TestClient(TestServer(app)) as client:
      assert (await (await client.get('/api/navigation/favorites')).json()) == {'favorites': []}
      place = {'name': '家 🏠', 'place_name': '臺北市測試路', 'latitude': 25., 'longitude': 121., 'permanent': True}
      response = await client.post('/api/navigation/favorites', json=place)
      assert response.status == 200 and response.headers['Cache-Control'] == 'no-store'
      identifier = (await response.json())['favorites'][0]['id']
      assert not temporary_params  # Saving does not start navigation.
      renamed = dict(place, name='公司', permanent=False)
      assert (await client.put('/api/navigation/favorites/' + identifier, json=renamed)).status == 200
      changed = dict(place, name='公司', latitude=24., place_name='新竹市新地址')
      assert (await client.put('/api/navigation/favorites/' + identifier, json=changed)).status == 200
      assert not temporary_params
    # A new application instance reads the same persisted favorite.
    app = web.Application(); navigation.register(app)
    async with TestClient(TestServer(app)) as client:
      saved = (await (await client.get('/api/navigation/favorites')).json())['favorites']
      assert len(saved) == 1 and saved[0]['name'] == '公司' and saved[0]['latitude'] == 24.
      assert (await client.post('/api/navigation/favorites/' + identifier + '/destination')).status == 200
      active = json.loads(temporary_params['NavDestinationTemporary'])
      assert active['latitude'] == 24. and active['place_name'] == '新竹市新地址'
      assert (await client.delete('/api/navigation/favorites/' + identifier)).status == 200
      assert json.loads(temporary_params['NavDestinationTemporary']) == active  # Deleting a favorite does not end a drive.
      assert (await client.post('/api/navigation/favorites/' + identifier + '/destination')).status == 404
      assert (await client.delete('/api/navigation/destination')).status == 200
      assert not temporary_params
      assert (await (await client.get('/api/navigation/favorites')).json()) == {'favorites': []}
  asyncio.run(run())


def test_favorites_reject_bad_input_and_preserve_file_on_failure(monkeypatch, tmp_path):
  path = tmp_path / 'favorites.json'
  monkeypatch.setattr(navigation, 'CARROT_NAVIGATION_FAVORITES_PATH', str(path))
  async def run():
    app = web.Application(); navigation.register(app)
    async with TestClient(TestServer(app)) as client:
      valid = {'name': '家', 'place_name': '測試地址', 'latitude': 25., 'longitude': 121., 'permanent': True}
      for updates in ({'name': ''}, {'name': 'x' * 81}, {'latitude': True}, {'longitude': 181},
                      {'latitude': None}, {'place_name': ''}, {'permanent': False}):
        assert (await client.post('/api/navigation/favorites', json=dict(valid, **updates))).status == 400
      assert (await client.post('/api/navigation/favorites', data='{', headers={'Content-Type':'application/json'})).status == 400
      assert not path.exists()
      assert (await client.post('/api/navigation/favorites', json=valid)).status == 200
      original = path.read_bytes()
      monkeypatch.setattr('openpilot.selfdrive.carrot.server.services.navigation_favorites.os.replace',
                          lambda *_: (_ for _ in ()).throw(OSError('disk error')))
      assert (await client.post('/api/navigation/favorites', json=valid)).status == 503
      assert path.read_bytes() == original
      assert list(tmp_path.iterdir()) == [path]
      path.write_text('broken', encoding='utf-8')
      assert (await client.get('/api/navigation/favorites')).status == 503
      assert (await client.post('/api/navigation/favorites', json=valid)).status == 503
      assert path.read_text(encoding='utf-8') == 'broken'
  asyncio.run(run())
