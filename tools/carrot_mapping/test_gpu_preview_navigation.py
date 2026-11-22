import asyncio
from html.parser import HTMLParser
from shutil import copyfile
from types import SimpleNamespace

from aiohttp.test_utils import TestClient, TestServer

from tools.carrot_mapping import gpu_preview


class CockpitPage(HTMLParser):
  navigation = None

  def handle_starttag(self, tag, attrs):
    attrs = dict(attrs)
    if tag == 'iframe' and attrs.get('id') == 'navigation':
      self.navigation = attrs['src']


def test_replay_serves_the_cockpits_navigation_frame(tmp_path, monkeypatch):
  # Route registration needs the two Three.js directories, not an installed GPU or renderer.
  for folder in ('node_modules/three/build', 'node_modules/three/examples/jsm', 'js/generated'):
    (tmp_path / folder).mkdir(parents=True)
  for asset in ('cockpit.html', 'js/generated/cockpit.js'):
    copyfile(gpu_preview.ASSETS / asset, tmp_path / asset)
  monkeypatch.setattr(gpu_preview, 'ASSETS', tmp_path)

  async def run():
    options = SimpleNamespace(parking=False, listen=None, viewer=None, port=7000)
    async with TestClient(TestServer(gpu_preview.make_app(options, None)), headers={'Host': '127.0.0.1:7000'}) as client:
      shell = await (await client.get('/cockpit')).text()
      assert '/js/generated/cockpit.js?v=' in shell
      parser = CockpitPage()
      parser.feed(shell)
      response = await client.get(parser.navigation)
      assert response.status == 200 and response.content_type == 'text/html'
      document = await response.text()
      assert '<html data-navigation-replay ' in document and '/js/pages/navigation_map.js?v=' in document
      for resource, key in (('config', 'osm_tile_url'), ('route_view', 'position'), ('parking', 'areas'),
                            ('destination', 'destination'), ('favorites', 'favorites'), ('offline', 'installed')):
        result = await client.get('/api/navigation/' + resource)
        assert result.status == 200 and key in await result.json()
      fallback = await client.get('/api/navigation/map.png')
      assert fallback.status == 204 and fallback.headers['X-Nav-Map-Status'] == 'offroad'
      assert (await client.post('/api/navigation/destination', json={})).status == 405

  asyncio.run(run())
