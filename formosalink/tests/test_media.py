import base64
import copy
import time
import uuid
from pathlib import Path

import pytest

from formosalink.tests.test_platform import client, pair, ORIGIN
from formosalink.server.media import MediaRelay
from openpilot.sunnypilot.formosalink.media_protocol import validate_frame, jpeg_size, MAX_MEDIA_BYTES
from openpilot.sunnypilot.formosalink.protocol import sign
from openpilot.sunnypilot.formosalink.media_agent import PreviewPublisher

JPEG = (Path(__file__).parent/'fixtures/media-demo.jpg').read_bytes()


def frame():
  return {'version':1,'stream':str(uuid.uuid4()),'sequence':0,'sampled_at':time.time(),'source':'demo',
    'width':640,'height':360,'jpeg':base64.b64encode(JPEG).decode(),'hud':{'speed_kph':0,'engaged':False}}


def test_signed_preview_owner_nonce_and_csrf(client):
  device,private,_=pair(client)
  body=sign(private,device,'media',frame())
  path='/api/v1/devices/'+device+'/media'
  assert client.post('/api/v1/agent/media',json=body).status_code==200
  value=client.get(path).json();assert value['available'] and value['frame']['hud']['speed_kph']==0
  assert client.get(path,params={'after':value['cursor']}).json()['frame'] is None
  assert client.post('/api/v1/agent/media',json=body).status_code==403
  assert client.get('/api/v1/devices/'+str(uuid.uuid4())+'/media').status_code==404
  client.cookies.clear();assert client.get(path).status_code==401


def test_other_owner_and_revoked_device_cannot_view(client):
  device,private,_=pair(client)
  assert client.post('/api/v1/agent/media',json=sign(private,device,'media',frame())).status_code==200
  store=client.app.state.store
  with store.connection() as db:
    db.execute("UPDATE devices SET owner_id='someone-else' WHERE id=?",(device,))
  assert client.get('/api/v1/devices/'+device+'/media').status_code==404
  with store.connection() as db:
    db.execute("UPDATE devices SET owner_id='local-admin',state='revoked' WHERE id=?",(device,))
  assert client.get('/api/v1/devices/'+device+'/media').status_code==404
  assert client.post('/api/v1/agent/media',json=sign(private,device,'media',frame())).status_code==403


@pytest.mark.parametrize('change',[{'sampled_at':0},{'width':1281},{'width':639},{'jpeg':'not base64'},{'hud':{'speed_kph':True,'engaged':False}},{'source':'unknown-camera'},{'sequence':True},{'hud':{'speed_kph':1,'engaged':False,'latitude':25}}])
def test_invalid_stale_oversized_or_private_media_is_rejected(change):
  data=frame();data.update(change)
  with pytest.raises((ValueError,TypeError)):validate_frame(data)


def test_relay_expiry_capacity_sequence_and_no_history():
  clock=[0];relay=MediaRelay(capacity=1,clock=lambda:clock[0]);f=frame();relay.put('d',f)
  with pytest.raises(ValueError):relay.put('d',f)
  with pytest.raises(ValueError):relay.put('other',frame())
  newer=copy.deepcopy(f);newer['sequence']=1;relay.put('d',newer)
  assert len(relay.frames)==1 and relay.get('d','')['frame']['sequence']==1
  clock[0]=4;assert relay.get('d','')['frame'] is None;assert not relay.frames


def test_body_limits_and_signature_purpose(client):
  device,private,_=pair(client)
  wrong=sign(private,device,'telemetry',frame())
  assert client.post('/api/v1/agent/media',json=wrong).status_code==403
  assert client.post('/api/v1/agent/media',content=b'x'*(MAX_MEDIA_BYTES+1)).status_code==413
  assert client.post('/api/v1/login',content=b'x'*17000,headers={'Origin':ORIGIN}).status_code==413


def test_real_publisher_uses_existing_identity_and_signed_http(client):
  device,private,_=pair(client)
  source=lambda:(JPEG,time.time(),{'speed_kph':None,'engaged':None})
  publisher=PreviewPublisher({'device_id':device,'origin':ORIGIN},private,source,demo=True)
  publisher.once(client)
  data=client.get('/api/v1/devices/'+device+'/media').json()
  assert data['frame']['source']=='demo' and jpeg_size(JPEG)==(640,360)


def test_native_cameras_require_owner_watch_and_are_separate(client):
  device, private, _ = pair(client)
  root = '/api/v1/devices/'+device+'/media'
  for camera in ('wide-road','driver'):
    data = frame();data['source'] = camera
    assert client.post('/api/v1/agent/media',json=sign(private,device,'media',data)).status_code == 403
    assert client.post(root+'/watch',json={'camera':camera}).status_code == 403
    assert client.post(root+'/watch',json={'camera':camera},headers={'Origin':ORIGIN}).status_code == 200
    assert client.post('/api/v1/agent/media',json=sign(private,device,'media',data)).status_code == 200
    assert client.get(root,params={'camera':camera}).json()['frame']['source'] == camera
  request = sign(private,device,'media-watch')
  assert client.post('/api/v1/agent/media/watch',json=request).json()['cameras'] == ['driver','wide-road']
  assert client.post('/api/v1/agent/media/watch',json=request).status_code == 403
  with client.app.state.store.connection() as db:
    db.execute("UPDATE devices SET owner_id='different-owner' WHERE id=?", (device,))
  assert client.post(root+'/watch',json={'camera':'driver'},headers={'Origin':ORIGIN}).status_code == 404
  assert client.get(root,params={'camera':'driver'}).status_code == 404


def test_camera_watch_expires_without_history():
  now=[100];relay=MediaRelay(clock=lambda:now[0])
  relay.watch('device','driver')
  assert relay.requested('device') == ['driver']
  assert relay.remaining('device') == 15
  now[0]=114
  assert relay.remaining('device') == 1
  now[0]=116
  assert relay.requested('device') == []
  assert relay.remaining('device') == 0
