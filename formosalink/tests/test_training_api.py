import base64
import hashlib
import json
from pathlib import Path
import uuid

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

from formosalink.server.app import create_app
from formosalink.server.config import initialize
from formosalink.tests.test_platform import ORIGIN,PASSWORD,pair
from openpilot.sunnypilot.formosalink.protocol import public_key_text,sign
from openpilot.sunnypilot.formosalink.training_protocol import CHUNK_BYTES,POLICY


def test_owner_consent_signed_upload_and_registered_training_worker(tmp_path):
  initialize(tmp_path,ORIGIN,PASSWORD)
  with TestClient(create_app(tmp_path),base_url=ORIGIN) as client:
    device,private,_=pair(client)
    path=f'/api/v1/devices/{device}/training'
    assert not client.get(path).json()['consent']['enabled']
    assert client.post(path,json={'policy':POLICY,'enabled':True,'expected_revision':0}).status_code==403
    assert client.post(path,json={'policy':POLICY,'enabled':True,'expected_revision':0},headers={'Origin':ORIGIN}).status_code==200
    def agent(operation,**fields):
      return client.post('/api/v1/agent/training',json=sign(private,device,'training',{'operation':operation,**fields}))
    for name in ('rlog.zst','fcamera.hevc','ecamera.hevc'):
      raw=b'fixture-real-bytes-'+name.encode()
      checksum=hashlib.sha256(raw).hexdigest()
      response=agent('begin',file={'segment':'a'*64,'filename':name,'sha256':checksum,'size':len(raw),'consent_revision':1})
      assert response.status_code==200,response.text
      upload=response.json()['upload_id']
      envelope=sign(private,device,'training',{'operation':'chunk','chunk':{'upload_id':upload,'offset':0,
        'data':base64.b64encode(raw).decode(),'sha256':checksum,'consent_revision':1}})
      assert client.post('/api/v1/agent/training',json=envelope).json()['complete']
      assert client.post('/api/v1/agent/training',json=envelope).status_code==403
    assert agent('finalize',segment={'segment':'a'*64,'route_group':'b'*64,'consent_revision':1}).status_code==200
    worker_private=Ed25519PrivateKey.generate()
    worker_id=str(uuid.uuid4())
    def worker(operation,**fields):
      return client.post('/api/v1/training-worker',json=sign(worker_private,worker_id,'training-worker',{'operation':operation,**fields}))
    assert worker('index',cursor=0).status_code==403
    (tmp_path/'training-workers.json').write_text(json.dumps({worker_id:public_key_text(worker_private)}))
    index=worker('index',cursor=0)
    assert index.status_code==200,index.text
    item=index.json()['datasets'][0]
    response=worker('file',dataset=item['id'],filename='fcamera.hevc',offset=0)
    assert response.status_code==200
    assert response.content==b'fixture-real-bytes-fcamera.hevc'
    assert worker('file',dataset=item['id'],filename='dcamera.hevc',offset=0).status_code==403
    assert worker('index',cursor=item['seq']).json()['datasets']==[]
    client.cookies.clear()
    assert client.get(path).status_code in (401,404)


def test_chunk_envelope_fits_existing_iis_request_limit():
  raw=b'x'*CHUNK_BYTES
  private=Ed25519PrivateKey.generate()
  value=sign(private,str(uuid.uuid4()),'training',{'operation':'chunk','chunk':{'upload_id':'a'*64,
    'offset':0,'data':base64.b64encode(raw).decode(),'sha256':hashlib.sha256(raw).hexdigest(),'consent_revision':1}})
  assert len(json.dumps(value).encode())<512*1024
