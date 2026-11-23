import asyncio
import json
from types import SimpleNamespace

import pytest
from aiohttp import web

from openpilot.selfdrive.carrot.server import parked_indicator as api
from openpilot.selfdrive.car.parked_indicator import ParkedIndicator


@pytest.mark.parametrize("accepted", [True, False])
def test_browser_waits_for_car_controller_receipt(tmp_path, monkeypatch, accepted):
  monkeypatch.setattr(api, "ROOT", tmp_path)
  reader = ParkedIndicator(tmp_path)
  request = SimpleNamespace(host="car:7000", scheme="http", headers={"Origin": "http://car:7000"},
                            content_type="application/json", match_info={"side": "left"})

  async def exchange():
    task = asyncio.create_task(api.parked_indicator(request))
    await asyncio.sleep(0)
    when, side = reader.take(api.time.monotonic())
    assert side == "left"
    reader.reply(when, accepted)
    response = await task
    assert json.loads(response.text)["ok"] is accepted
    assert response.status == (200 if accepted else 409)
    assert (await api.parked_indicator(request)).status == 409
    assert reader.take(api.time.monotonic()) is None

  asyncio.run(exchange())


def test_cross_origin_request_leaves_no_command(tmp_path, monkeypatch):
  monkeypatch.setattr(api, "ROOT", tmp_path)
  request = SimpleNamespace(host="car:7000", scheme="http", headers={"Origin": "http://other"})
  with pytest.raises(web.HTTPForbidden):
    asyncio.run(api.parked_indicator(request))
  assert not list(tmp_path.iterdir())
