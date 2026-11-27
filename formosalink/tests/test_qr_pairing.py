import time
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from formosalink.tests.test_platform import client, enroll, login, ORIGIN
from formosalink.server.config import initialize
from formosalink.server.app import create_app
from openpilot.sunnypilot.formosalink.pairing import pairing_url, request_pairing, pairing_status
from openpilot.sunnypilot.formosalink.protocol import sign


def test_status_is_signed_private_replay_protected_and_does_not_rotate_qr(client):
  device_id, key, pending, _ = enroll(client)
  for malformed in (None, [], {"device_id": []}, {"device_id": {}}):
    assert client.post('/api/v1/agent/status',json=malformed).status_code==403
  before = client.app.state.store.get(device_id)["pair_hash"]
  envelope = sign(key, device_id, "status")
  assert client.post('/api/v1/agent/status',json=envelope).json()=={"state":"pending"}
  assert client.post('/api/v1/agent/status',json=envelope).status_code==403
  assert client.app.state.store.get(device_id)["pair_hash"]==before
  assert client.post('/api/v1/agent/status',json=sign(Ed25519PrivateKey.generate(),device_id,'status')).status_code==403
  assert client.post('/api/v1/agent/status',json=sign(key,device_id,'connect')).status_code==403
  assert client.post('/api/v1/agent/status',json=sign(key,device_id,'status',{'owner_id':'local-admin'})).status_code==403
  login(client)
  assert client.post('/api/v1/pair',json={"code":pending["pair_code"],"fingerprint":pending["fingerprint"],"name":"QR device"},headers={'Origin':ORIGIN}).status_code==200
  assert client.post('/api/v1/agent/status',json=sign(key,device_id,'status')).json()=={"state":"paired"}
  client.post(f'/api/v1/devices/{device_id}/revoke',json={},headers={'Origin':ORIGIN})
  assert client.post('/api/v1/agent/status',json=sign(key,device_id,'status')).json()=={"state":"revoked"}


def test_pairing_url_keeps_credentials_out_of_queries_and_rejects_bad_data():
  result={"pair_code":"A1B2C3D4E5F6","fingerprint":"a"*24,"expires_at":time.time()+600}
  url=pairing_url(ORIGIN,result)
  parsed=urlparse(url)
  assert parsed.query=='' and parsed.path=='/'
  assert parse_qs(parsed.fragment)['pair']==[result['pair_code']]
  for patch in ({'pair_code':'<script>'},{'fingerprint':'bad'},{'expires_at':float('nan')},{'expires_at':time.time()-1},{'expires_at':time.time()+86400}):
    with pytest.raises(ValueError):pairing_url(ORIGIN,{**result,**patch})
  with pytest.raises(ValueError):pairing_url('http://unsafe.example',result)


def test_device_pairing_helper_preserves_independent_identity(client,tmp_path,monkeypatch):
  import openpilot.sunnypilot.formosalink.pairing as pairing
  monkeypatch.setattr(pairing.requests,'post',lambda url,**kwargs: client.post(url,json=kwargs['json']))
  directory=tmp_path/'device'
  first=request_pairing(directory,ORIGIN)
  assert first['state']=='pending' and first['url'].startswith(ORIGIN+'/#pair=')
  assert pairing_status(directory)=={'state':'pending'}
  login(client)
  assert client.post('/api/v1/pair',json={'code':first['pair_code'],'fingerprint':first['fingerprint'],'name':'QR'},headers={'Origin':ORIGIN}).status_code==200
  assert pairing_status(directory)=={'state':'paired'}
  assert request_pairing(directory)['url'] is None
  with pytest.raises(ValueError):request_pairing(directory,'https://different.example')


def test_existing_custom_self_hosted_origin_is_used_without_switching_servers(tmp_path,monkeypatch):
  import openpilot.sunnypilot.formosalink.pairing as pairing
  origin='https://custom-formosalink.example'
  initialize(tmp_path/'server',origin,'custom-test-password-2026')
  with TestClient(create_app(tmp_path/'server'),base_url=origin) as custom:
    monkeypatch.setattr(pairing.requests,'post',lambda url,**kwargs: custom.post(url,json=kwargs['json']))
    request_pairing(tmp_path/'device',origin)
    result=request_pairing(tmp_path/'device')
    assert result['url'].startswith(origin+'/#pair=')
