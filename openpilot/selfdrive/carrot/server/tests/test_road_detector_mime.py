import asyncio

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from openpilot.selfdrive.carrot.server.services.static_assets import create_static_cache_middleware


def test_ort_modules_and_wasm_have_browser_compatible_mime_even_with_bad_os_mapping(tmp_path):
  async def check():
    app = web.Application(middlewares=[create_static_cache_middleware(str(tmp_path))])

    async def wrong_type(_request):
      return web.Response(body=b"export default 1", content_type="text/plain")

    app.router.add_get('/vendor/road-detector/ort/{name}', wrong_type)
    app.router.add_get('/unrelated.mjs', wrong_type)
    async with TestClient(TestServer(app)) as client:
      for filename, expected in [('runtime.mjs', 'text/javascript'), ('runtime.wasm', 'application/wasm')]:
        response = await client.get('/vendor/road-detector/ort/' + filename)
        assert response.content_type == expected
      response = await client.get('/unrelated.mjs')
      assert response.content_type == 'text/plain'

  asyncio.run(check())
