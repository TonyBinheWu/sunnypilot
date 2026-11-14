import asyncio
import json
import importlib.util
from pathlib import Path

from aiohttp import web
# Load this route without importing the unrelated hardware-backed feature registry.
spec = importlib.util.spec_from_file_location(
  'openpilot.selfdrive.carrot.server.features.steering_learning',
  Path(__file__).parents[1] / 'features' / 'steering_learning.py')
feature = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feature)


def test_status_is_read_only_and_not_cached(monkeypatch):
  class Service:
    def snapshot(self):
      return {'ok': True, 'delay': {'source': 'live', 'progress': 80}, 'torque': {'source': 'cached', 'progress': 56}}
  monkeypatch.setattr(feature, 'service', Service())
  response = asyncio.run(feature.status(None))
  assert json.loads(response.body)['torque']['source'] == 'cached'
  assert response.headers['Cache-Control'] == 'no-store'
  app = web.Application()
  feature.register(app)
  assert {route.method for route in app.router.routes()} == {'GET', 'HEAD'}
