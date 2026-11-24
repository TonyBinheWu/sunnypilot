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
  monkeypatch.setattr(api, "unavailable_reason", lambda _: None)
  reader = ParkedIndicator(tmp_path)
  request = SimpleNamespace(host="car:7000", scheme="http", headers={"Origin": "http://car:7000"},
                            content_type="application/json", match_info={"side": "left"}, app={})

  async def exchange():
    task = asyncio.create_task(api.parked_indicator(request))
    await asyncio.sleep(0)
    when, side = reader.take(api.time.monotonic())
    assert side == "left"
    reader.reply(when, accepted, None if accepted else "stalk_data_not_ready", setting=0, gear="park")
    if accepted:
      reader.finish(when - 1, True, None)
      await asyncio.sleep(.12)
      assert not task.done()
      reader.finish(when, True, None)
    response = await task
    assert json.loads(response.text)["ok"] is accepted
    if not accepted:
      assert json.loads(response.text) == {"ok": False, "reason": "stalk_data_not_ready", "testSetting": 0, "gear": "park"}
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


@pytest.mark.parametrize("offroad,reason", [(True, "offroad"), (False, "controller_state_unavailable")])
def test_unavailable_request_writes_no_command(tmp_path, monkeypatch, offroad, reason):
  monkeypatch.setattr(api, "ROOT", tmp_path)
  params = SimpleNamespace(get_bool=lambda _: offroad, get=lambda _: None)
  request = SimpleNamespace(host="car", scheme="http", headers={"Origin": "http://car"},
                            content_type="application/json", match_info={"side": "right"}, app={"params": params})
  response = asyncio.run(api.parked_indicator(request))
  assert response.status == 409
  assert json.loads(response.text)["reason"] == reason
  assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("flag,setting,passive,reason", [
  (None, False, False, "spas_setting_off"),
  (None, True, False, "spas_not_active"),
  ("ENABLE_BLINKERS", True, False, "spas_test_unavailable"),
  ("CANFD_SPAS_BLINKERS", True, True, "passive"),
  ("CANFD_SPAS_BLINKERS", True, False, None),
])
def test_current_controller_configuration(flag, setting, passive, reason):
  from openpilot.cereal import car
  from opendbc.car.hyundai.values import HyundaiFlags
  data = car.CarParams.new_message(brand="hyundai", flags=int(HyundaiFlags[flag]) if flag else 0, passive=passive).to_bytes()
  params = SimpleNamespace(get_bool=lambda key: key == "CanfdBlinkerControl" and setting, get=lambda _: data)
  assert api.unavailable_reason(params) == reason
