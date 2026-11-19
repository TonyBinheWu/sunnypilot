import asyncio
import hashlib
from pathlib import Path
from unittest.mock import patch

from aiohttp import ClientSession, web
from aiohttp.test_utils import TestClient, TestServer

from openpilot.selfdrive.carrot.server.features import environment_model as model


def test_worker_and_car_server_pin_the_same_public_asset():
  root = Path(__file__).resolve().parents[2]
  worker = (root / "web/src/features/drive/contents/vision/occupancy_model.js").read_text(encoding="utf-8")
  assert f"MODEL_BYTES={model.SIZE};" in worker
  assert f"MODEL_HASH='{model.SHA256}';" in worker
  assert model.URL.endswith("/" + model.NAME)


def test_model_cache_opt_in_integrity_retry_and_concurrent_readers(tmp_path):
  async def run():
    data = b"small test model"
    enabled, broken, calls = False, False, 0
    path = tmp_path / "models" / model.NAME

    async def serve_fake(request):
      nonlocal calls
      calls += 1
      return web.Response(body=bytes(len(data)) if broken else data)

    remote = web.Application()
    remote.router.add_get("/model", serve_fake)
    async with TestServer(remote) as upstream, ClientSession() as session:
      app = web.Application()
      app["http"] = session
      model.register(app)
      with (
        patch.object(model, "MODEL", path),
        patch.object(model, "URL", str(upstream.make_url("/model"))),
        patch.object(model, "SIZE", len(data)),
        patch.object(model, "SHA256", hashlib.sha256(data).hexdigest()),
        patch.object(model, "read_web_settings", lambda: {"vision_environment_occupancy": enabled}),
      ):
        async with TestClient(TestServer(app)) as client:
          url = "/api/vision/occupancy/model"
          assert (await client.get(url)).status == 403 and calls == 0
          enabled = True
          a, b = await asyncio.gather(client.get(url), client.get(url))
          assert a.status == b.status == 200 and await a.read() == await b.read() == data and calls == 1
          path.unlink()
          broken = True
          assert (await client.get(url)).status == 503 and not path.exists()
          assert (await client.get(url)).status == 503 and calls == 2 and not list(path.parent.iterdir())

  asyncio.run(run())
