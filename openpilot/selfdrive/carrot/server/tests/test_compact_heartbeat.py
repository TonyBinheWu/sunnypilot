import asyncio

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from openpilot.selfdrive.carrot.server.features.ws import ws_compact_state


def test_parked_compact_channel_answers_fixed_heartbeat_without_dispatching_commands():
  class Hub:
    def __init__(self):
      self.clients = set()

    def is_compact_service(self, service):
      return service == 'carState'

    async def register_compact_many(self, services, ws):
      assert services == ['carState']
      self.clients.add(ws)

    async def unregister_client(self, ws):
      self.clients.remove(ws)

  async def check():
    hub = Hub()
    app = web.Application()
    app['realtime_raw_hub'] = hub
    app.router.add_get('/ws/compact_state', ws_compact_state)
    async with TestClient(TestServer(app)) as client:
      invalid = await client.get('/ws/compact_state?services=not-a-service')
      assert invalid.status == 404
      ws = await client.ws_connect('/ws/compact_state?services=carState')
      assert (await ws.receive_json())['mode'] == 'carrot-state-v1'
      # No publisher, no camera and no driving command dispatcher exists here.
      await ws.send_str('{"type":"param_set","name":"MyDrivingMode","value":4}')
      for _ in range(3):
        await ws.send_str('{"type":"ping"}')
        assert await ws.receive_json(timeout=1) == {'type': 'pong'}
      assert len(hub.clients) == 1
      await ws.close()
      await asyncio.sleep(0)
    assert not hub.clients

  asyncio.run(check())
