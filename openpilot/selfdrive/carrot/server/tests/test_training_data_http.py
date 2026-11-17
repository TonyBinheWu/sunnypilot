import json
import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient,TestServer

from openpilot.selfdrive.carrot.server.tests.test_assistant_settings_http import load_routes
from openpilot.sunnypilot.formosalink.identity import create
from openpilot.sunnypilot.formosalink.training_upload import local_state,save_state


class Params:
  def __init__(self):
    self.offroad=True
  def get_bool(self,key):
    return self.offroad if key=='IsOffroad' else True


@pytest.mark.asyncio
async def test_local_web_requires_explicit_notice_and_parked_enable_but_revoke_works_onroad(tmp_path):
  routes=load_routes('training_data')
  create(tmp_path,'https://formosapilot.dinglu-t.com')
  params=Params()
  app=web.Application()
  app['params']=params
  app['training_data_directory']=tmp_path
  routes.register(app)
  async with TestClient(TestServer(app)) as client:
    path='/api/device/training_data'
    headers={'Host':'192.168.0.178:7000','Origin':'http://192.168.0.178:7000'}
    status=await (await client.get(path)).json()
    assert not status['enabled'] and status['can_enable']
    assert not (tmp_path/'training-consent.json').exists()
    assert 'private_key' not in json.dumps(status)
    body={'policy':status['policy'],'enabled':True,'revision':status['revision']}
    assert (await client.post(path,json=body)).status==403
    assert (await client.post(path,json=body,headers={**headers,'Sec-Fetch-Site':'cross-site'})).status==403
    params.offroad=False
    assert (await client.post(path,json=body,headers=headers)).status==409
    params.offroad=True
    result=await client.post(path,json=body,headers=headers)
    assert result.status==200
    saved=await result.json()
    assert saved['pending_enabled'] is True and not saved['enabled']
    assert local_state(tmp_path)['pending']['enabled'] is True
    assert (await client.post(path,json=body,headers=headers)).status==409
    params.offroad=False
    result=await client.post(path,json={'policy':status['policy'],'enabled':False,'revision':saved['revision']},headers=headers)
    assert result.status==200
    assert (await result.json())['pending_enabled'] is False


@pytest.mark.asyncio
async def test_unpaired_device_cannot_start_upload_and_invalid_payload_does_not_grant(tmp_path):
  routes=load_routes('training_data')
  app=web.Application()
  app['params']=Params()
  app['training_data_directory']=tmp_path
  routes.register(app)
  async with TestClient(TestServer(app)) as client:
    path='/api/device/training_data'
    headers={'Host':'192.168.0.178:7000','Origin':'http://192.168.0.178:7000'}
    status=await (await client.get(path)).json()
    assert not status['configured'] and not status['can_enable']
    body={'policy':status['policy'],'enabled':True,'revision':status['revision']}
    assert (await client.post(path,json=body,headers=headers)).status==409
    for invalid in ({**body,'enabled':'true'},{**body,'policy':'old'},{**body,'extra':True}):
      assert (await client.post(path,json=invalid,headers=headers)).status==409
    assert not (tmp_path/'training-consent.json').exists()
