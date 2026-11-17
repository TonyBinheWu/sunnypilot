import asyncio
import json
import time
from types import SimpleNamespace as NS

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
import pytest

from openpilot.selfdrive.carrot.server.features import navigation
from openpilot.selfdrive.carrot.server.services import web_settings
from openpilot.selfdrive.navigation.preview import write_navigation_view


def test_old_google_settings_migrate_to_native_map_and_do_not_expose_browser_keys():
  value = web_settings.sanitize_web_settings({})
  assert value['navigation_map_provider'] == 'mapbox' and 'navigation_google_key' not in value
  value = web_settings.sanitize_web_settings({'navigation_map_provider': 'google', 'navigation_google_key': 'old-browser-key-0000000000'})
  assert value['navigation_map_provider'] == 'mapbox' and 'navigation_google_key' not in value
  assert 'MapboxPublicKey' not in value
  config = json.loads(asyncio.run(navigation.map_config(None)).text)
  assert config == {'provider': 'mapbox', 'basemaps': ['mapbox', 'openstreetmap'], 'search': 'mapbox', 'routing': 'mapbox', 'model': 'mapsd'}
  assert all(field['key'] != 'navigation_google_key' for field in web_settings.web_settings_client_spec())


def test_exact_route_ui_copy_freshness_and_no_model_file_write(monkeypatch, tmp_path):
  path = tmp_path / 'view.json'
  monkeypatch.setattr(navigation, 'VIEW_PATH', path)
  monkeypatch.setattr(navigation, 'WEB_DEMAND_PATH', tmp_path / 'demand')
  route = [[121. + i / 1e5, 25. + i / 1e5] for i in range(4096)]
  gps = NS(latitude=25., longitude=121.)
  write_navigation_view(route, gps, 123, path=path)
  result = json.loads(asyncio.run(navigation.route_view(None)).text)
  assert result['coordinates'] == route and result['route_id'] == 123
  assert result['position'] == {'lat': 25., 'lng': 121.}
  assert sorted(p.name for p in tmp_path.iterdir()) == ['demand', 'view.json']
  write_navigation_view(route, gps, 123, path=path, now=time.time() - 4)
  assert json.loads(asyncio.run(navigation.route_view(None)).text)['coordinates'] == []
  write_navigation_view(route, None, 0, path=path)
  assert json.loads(asyncio.run(navigation.route_view(None)).text)['position'] is None
  assert json.loads(path.read_text())['coordinates'] == []


def test_legacy_google_favorites_can_be_renamed_or_explicitly_migrated_without_new_google_references(monkeypatch, tmp_path):
  path = tmp_path / 'favorites.json'
  monkeypatch.setattr(navigation, 'CARROT_NAVIGATION_FAVORITES_PATH', str(path))
  old = dict(id='a' * 32, name='舊最愛', place_name='原地址', latitude=25., longitude=121.)
  identifier = 'b' * 32
  legacy = dict(id=identifier, provider='google', google_place_id='ChIJ_test', name='我的家')
  path.write_text(json.dumps([old, legacy]), encoding='utf-8')
  async def run():
    app = web.Application(); navigation.register(app)
    async with TestClient(TestServer(app)) as client:
      body = {'provider': 'google', 'google_place_id': 'ChIJ_test', 'name': '我的家', 'latitude': 25., 'longitude': 121., 'place_name': '不得保存'}
      response = await client.post('/api/navigation/favorites', json=body)
      assert response.status == 400
      saved = (await (await client.get('/api/navigation/favorites')).json())['favorites']
      assert saved == [old, legacy]
      assert (await client.post(f'/api/navigation/favorites/{identifier}/destination')).status == 409
      body['name'] = '新名稱'
      assert (await client.put(f'/api/navigation/favorites/{identifier}', json=body)).status == 200
      body['google_place_id'] = '../bad'
      assert (await client.put(f'/api/navigation/favorites/{identifier}', json=body)).status == 400
      replacement = dict(provider='query', name='新名稱', query='使用者輸入的地址')
      assert (await client.put(f'/api/navigation/favorites/{identifier}', json=replacement)).status == 200
      converted = (await (await client.get('/api/navigation/favorites')).json())['favorites']
      assert converted == [old, dict(replacement, id=identifier)]
      assert (await client.delete(f'/api/navigation/favorites/{identifier}')).status == 200
      assert (await (await client.get('/api/navigation/favorites')).json())['favorites'] == [old]
  asyncio.run(run())


@pytest.mark.parametrize('body', [{}, [], {'generated_at': 'bad'}, {'generated_at': float('inf')}])
def test_malformed_route_copy_is_not_shown(monkeypatch, tmp_path, body):
  path = tmp_path / 'view.json'; path.write_text(json.dumps(body))
  monkeypatch.setattr(navigation, 'VIEW_PATH', path)
  monkeypatch.setattr(navigation, 'WEB_DEMAND_PATH', tmp_path / 'demand')
  assert json.loads(asyncio.run(navigation.route_view(None)).text)['coordinates'] == []
