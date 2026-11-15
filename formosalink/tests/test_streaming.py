import asyncio
import time

import pytest
from starlette.websockets import WebSocketDisconnect

from formosalink.server.streaming import StreamHub
from formosalink.tests.test_platform import client, pair, ORIGIN
from formosalink.tests.test_media import frame
from openpilot.sunnypilot.formosalink.protocol import sign

AGENT = ORIGIN.replace('https://', 'wss://')+'/api/v1/agent/media/stream'


def view_path(device, camera='driver'):
  return ORIGIN.replace('https://', 'wss://')+'/api/v1/devices/'+device+'/media/stream?camera='+camera


def start_agent(client, socket, device, private, camera='driver'):
  socket.send_json(sign(private, device, 'media-stream', {'camera':camera}))
  assert socket.receive_json() == {'type':'ready', 'fps':8, 'transport':'wss-mjpeg-v1'}


@pytest.mark.parametrize('camera', ['driver', 'wide-road'])
def test_persistent_stream_many_frames_and_owner_ack(client, camera):
  device, private, _ = pair(client)
  with client.websocket_connect(view_path(device, camera), headers={'origin':ORIGIN}) as viewer:
    with client.websocket_connect(AGENT) as agent:
      start_agent(client, agent, device, private, camera)
      value = frame();value['source'] = camera
      for sequence in range(4):
        value.update(sequence=sequence, sampled_at=time.time())
        agent.send_json(value)
        assert agent.receive_json() == {'type':'ack', 'sequence':sequence}
        received = viewer.receive_json()
        assert received['type'] == 'frame' and received['frame'] == value
        viewer.send_json({'type':'ack'})
        time.sleep(.125)
  assert not client.app.state.streams.publishers
  assert not client.app.state.streams.viewers


@pytest.mark.parametrize('headers', [{}, {'origin':'https://attacker.example'}, {'origin':ORIGIN, 'host':'attacker.example'}])
def test_viewer_rejects_cross_origin_and_wrong_host(client, headers):
  device, _, _ = pair(client)
  with pytest.raises(WebSocketDisconnect):
    with client.websocket_connect(view_path(device), headers=headers):
      pass


def test_viewer_requires_login_and_owner(client):
  device, _, _ = pair(client)
  with client.app.state.store.connection() as db:
    db.execute("UPDATE devices SET owner_id='other-owner' WHERE id=?", (device,))
  with pytest.raises(WebSocketDisconnect):
    with client.websocket_connect(view_path(device), headers={'origin':ORIGIN}):pass
  client.cookies.clear()
  with pytest.raises(WebSocketDisconnect):
    with client.websocket_connect(view_path(device), headers={'origin':ORIGIN}):pass


def test_revoke_during_stream_closes_both_channels(client):
  device, private, _ = pair(client)
  with client.websocket_connect(view_path(device), headers={'origin':ORIGIN}) as viewer:
    with client.websocket_connect(AGENT) as agent:
      start_agent(client, agent, device, private)
      with client.app.state.store.connection() as db:
        db.execute("UPDATE devices SET state='revoked' WHERE id=?", (device,))
      value = frame();value['source'] = 'driver'
      agent.send_json(value)
      with pytest.raises(WebSocketDisconnect):agent.receive_json()
      with pytest.raises(WebSocketDisconnect):viewer.receive_json()


def test_publisher_requires_viewer_signature_and_fresh_nonce(client):
  device, private, _ = pair(client)
  envelope = sign(private, device, 'media-stream', {'camera':'driver'})
  with client.websocket_connect(AGENT) as agent:
    agent.send_json(envelope)
    with pytest.raises(WebSocketDisconnect):agent.receive_json()
  with client.websocket_connect(view_path(device), headers={'origin':ORIGIN}):
    with client.websocket_connect(AGENT) as agent:
      agent.send_json(envelope)
      assert agent.receive_json()['type'] == 'ready'
    with client.websocket_connect(AGENT) as agent:
      agent.send_json(envelope)
      with pytest.raises(WebSocketDisconnect):agent.receive_json()


@pytest.mark.parametrize('change', [{'source':'wide-road'}, {'sampled_at':0}, {'jpeg':'bad'}, {'sequence':-1}])
def test_invalid_stream_frame_rejected(client, change):
  device, private, _ = pair(client)
  with client.websocket_connect(view_path(device), headers={'origin':ORIGIN}):
    with client.websocket_connect(AGENT) as agent:
      start_agent(client, agent, device, private)
      value = frame();value['source'] = 'driver';value.update(change)
      agent.send_json(value)
      with pytest.raises(WebSocketDisconnect):agent.receive_json()


def test_latest_only_backpressure_and_camera_isolation():
  hub = StreamHub()
  driver, wide = asyncio.Queue(maxsize=1), asyncio.Queue(maxsize=1)
  hub.viewers[('device','driver')] = {driver}
  hub.viewers[('device','wide-road')] = {wide}
  for index in range(100):hub.push(('device','driver'), {'sequence':index})
  assert driver.qsize() == 1 and driver.get_nowait()[1] == {'sequence':99}
  assert wide.empty()


def test_no_origin_allowed_for_device_stream(client):
  pair(client)
  with pytest.raises(WebSocketDisconnect):
    with client.websocket_connect(AGENT, headers={'origin':ORIGIN}):pass


def test_stream_feature_is_advertised(client):
  assert 'live-camera-stream-v1' in client.get('/api/v1/health').json()['features']
  with client.websocket_connect(ORIGIN.replace('https://','wss://')+'/api/v1/media/probe') as socket:
    assert socket.receive_json() == {'service':'FormosaLink', 'transport':'wss-mjpeg-v1', 'fps':8}
