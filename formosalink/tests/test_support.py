import base64
import hashlib
import io
import os
import time
import uuid

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from formosalink.server.app import create_app
from formosalink.server.config import initialize
from formosalink.server.support import SupportStore, RETENTION
from openpilot.sunnypilot.formosalink.protocol import public_key_text, fingerprint, sign
from openpilot.sunnypilot.formosalink.support import latest_route, sanitize, upload

ORIGIN='https://formosapilot.dinglu-t.com'


@pytest.fixture
def client(tmp_path):
  initialize(tmp_path,ORIGIN,'test-support-password-123')
  with TestClient(create_app(tmp_path),base_url=ORIGIN) as client:
    key=Ed25519PrivateKey.generate();identifier=str(uuid.uuid4());public=public_key_text(key)
    store=client.app.state.store
    record=store.enroll(identifier,public,fingerprint(public))
    store.pair(record['pair_code'],record['fingerprint'],'Test device')
    client.cookies.set('formosalink_session',store.session())
    yield client,identifier,key


def post(client,device,private,payload):
  return client.post('/api/v1/agent/support',json=sign(private,device,'support',payload))


def metadata(data,kind='diagnostic',job=None):
  return {'action':'start','kind':kind,'name':'test.json','size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'job':job}


def test_explicit_consent_signed_upload_replay_download_and_delete(client):
  c,d,k=client;data=b'{"error":"CAN unavailable"}'
  assert post(c,d,k,metadata(data)).status_code==403
  assert c.post('/api/v1/support/'+d+'/consent',json={'diagnostics':True}).status_code==403
  headers={'Origin':ORIGIN}
  assert c.post('/api/v1/support/'+d+'/consent',json={'diagnostics':True},headers=headers).status_code==200
  record=post(c,d,k,metadata(data)).json()
  payload={'action':'chunk','id':record['id'],'offset':0,'data':base64.b64encode(data).decode()}
  envelope=sign(k,d,'support',payload)
  assert c.post('/api/v1/agent/support',json=envelope).json()['complete']
  assert c.post('/api/v1/agent/support',json=envelope).status_code==403
  assert post(c,d,k,payload).json()['complete'] # lost-ack retry with fresh signature
  rows=c.get('/api/v1/admin/support').json()['files'];assert len(rows)==1 and rows[0]['complete']
  assert c.get('/api/v1/support-files/'+record['id']).content==data
  assert c.post('/api/v1/support/'+d+'/delete',json={},headers=headers).status_code==200
  assert c.get('/api/v1/support-files/'+record['id']).status_code==404
  assert not post(c,d,k,{'action':'poll'}).json()['diagnostics']


def test_cross_account_admin_scope_and_route_consent(client):
  c,d,k=client;store=c.app.state.store
  with store.connection() as db:db.execute("INSERT INTO users VALUES('other','Other')")
  c.cookies.set('formosalink_session',store.session('other'))
  assert c.get('/api/v1/admin/support').status_code==403
  assert c.get('/api/v1/support/'+d).status_code==404
  assert c.post('/api/v1/support/'+d+'/route',json={'consent':'latest-completed-rlog-with-location-v1'},headers={'Origin':ORIGIN}).status_code==404
  c.cookies.set('formosalink_session',store.session())
  assert post(c,d,k,metadata(b'raw','rlog')).status_code==403
  assert c.post('/api/v1/support/'+d+'/route',json={},headers={'Origin':ORIGIN}).status_code==400
  job=c.post('/api/v1/support/'+d+'/route',json={'consent':'latest-completed-rlog-with-location-v1'},headers={'Origin':ORIGIN}).json()['id']
  assert post(c,d,k,metadata(b'raw','rlog',job)).status_code==200
  assert post(c,d,k,{'action':'finish','job':job,'outcome':'done'}).status_code==403
  post(c,d,k,{'action':'finish','job':job,'outcome':'upload_failed'})
  assert post(c,d,k,metadata(b'raw','rlog',job)).status_code==403
  assert c.get('/api/v1/support/'+d).json()['latest_job']['state']=='upload_failed'


def test_expiry_partial_digest_and_cancel(client):
  c,d,k=client;support=c.app.state.support
  support.consent(d,'local-admin',True)
  data=b'correct';record=post(c,d,k,metadata(data)).json()
  assert c.get('/api/v1/support-files/'+record['id']).status_code==404
  wrong={'action':'chunk','id':record['id'],'offset':0,'data':base64.b64encode(b'incorrc').decode()}
  assert post(c,d,k,wrong).status_code==403
  assert not (support.root/record['id']).exists()
  record=post(c,d,k,metadata(data)).json()
  support.consent(d,'local-admin',False)
  assert post(c,d,k,{'action':'chunk','id':record['id'],'offset':0,'data':base64.b64encode(data).decode()}).status_code==403
  with support.db() as db:db.execute('UPDATE files SET expires=?',(time.time()-1,))
  support.purge();assert not support.list() and not (support.root/record['id']).exists()
  assert RETENTION==30*86400


def test_path_quota_and_chunk_bounds(client,monkeypatch):
  c,d,k=client;c.app.state.support.consent(d,'local-admin',True)
  bad=metadata(b'x');bad['name']='../secret';assert post(c,d,k,bad).status_code==403
  import formosalink.server.support as module
  monkeypatch.setattr(module,'MAX_DEVICE',2)
  assert post(c,d,k,metadata(b'123')).status_code==403
  assert c.post('/api/v1/agent/support',content=b'x'*65537).status_code==413


def test_local_route_selection_redaction_and_no_driving_upload(tmp_path):
  old=tmp_path/'2026-01-01--route--0';old.mkdir();(old/'rlog.zst').write_bytes(b'old')
  current=tmp_path/'2026-01-02--route--0';current.mkdir();(current/'rlog.zst').write_bytes(b'active')
  os.utime(old/'rlog.zst',(1,1))
  assert latest_route(tmp_path)==[old/'rlog.zst']
  assert 'SECRET' not in sanitize('Authorization: Bearer SECRET\npassword=SECRET\nhttps://secret/SECRET')
  class Stop:
    def is_set(self):return False
  with pytest.raises(ValueError,match='deferred'):
    upload(None,{},None,io.BytesIO(b'x'),'a','rlog','job',lambda:False,Stop())


def test_real_agent_chunk_transport(client):
  c,d,k=client;c.app.state.support.consent(d,'local-admin',True)
  class Session:
    def post(self,url,**kwargs):
      response=c.post('/api/v1/agent/support',json=kwargs['json'])
      response.iter_content=response.iter_bytes
      return response
  class Stop:
    def is_set(self):return False
    def wait(self,_):pass
  data=b'error-context\n'*9000
  upload(Session(),{'origin':ORIGIN,'device_id':d},k,io.BytesIO(data),'report.json','diagnostic',None,lambda:True,Stop())
  rows=c.app.state.support.list(d);assert len(rows)==1 and rows[0]['complete']
  assert c.get('/api/v1/support-files/'+rows[0]['id']).content==data
