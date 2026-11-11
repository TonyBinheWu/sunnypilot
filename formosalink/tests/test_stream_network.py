"""Real loopback sockets, not TestClient: validate Uvicorn limits and stream flow."""
import json
import socket
import threading
import time

import httpx
import uvicorn
from websockets.sync.client import connect

from formosalink.server.app import create_app, COOKIE
from formosalink.server.config import initialize
from formosalink.tests.test_media import frame, JPEG
from formosalink.tests.test_platform import PASSWORD
from openpilot.sunnypilot.formosalink.identity import create
from openpilot.sunnypilot.formosalink.protocol import fingerprint, sign


def test_real_network_stream_two_cameras_ack_and_probe(tmp_path, monkeypatch):
  listener = socket.socket()
  listener.bind(('127.0.0.1', 0))
  port = listener.getsockname()[1]
  origin = f'http://127.0.0.1:{port}'
  initialize(tmp_path, origin, PASSWORD)
  app = create_app(tmp_path)
  identity, private, public = create(tmp_path/'device', origin)
  enrolled = app.state.store.enroll(identity['device_id'], public, fingerprint(public))
  app.state.store.pair(enrolled['pair_code'], enrolled['fingerprint'], 'Loopback stream test')
  config = uvicorn.Config(app, host='127.0.0.1', port=port, log_level='error', ws_max_size=262144,
                          ws_max_queue=1, ws_per_message_deflate=False, proxy_headers=False)
  server = uvicorn.Server(config)
  thread = threading.Thread(target=server.run, kwargs={'sockets':[listener]}, daemon=True)
  thread.start()
  try:
    deadline = time.monotonic()+5
    while not server.started and thread.is_alive() and time.monotonic() < deadline:time.sleep(.01)
    assert server.started
    with httpx.Client(base_url=origin) as client:
      assert client.post('/api/v1/login', json={'password':PASSWORD}, headers={'Origin':origin}).status_code == 200
      cookie = COOKIE+'='+client.cookies[COOKIE]
    base = origin.replace('http://', 'ws://')
    with connect(base+'/api/v1/media/probe', compression=None) as probe:
      assert json.loads(probe.recv())['transport'] == 'wss-mjpeg-v1'
    for camera in ('wide-road', 'driver'):
      path = f'/api/v1/devices/{identity["device_id"]}/media/stream?camera={camera}'
      with connect(base+path, origin=origin, additional_headers={'Cookie':cookie}, compression=None) as viewer:
        with connect(base+'/api/v1/agent/media/stream', compression=None) as agent:
          agent.send(json.dumps(sign(private, identity['device_id'], 'media-stream', {'camera':camera})))
          assert json.loads(agent.recv())['type'] == 'ready'
          value = frame();value['source'] = camera
          # Larger than the old telemetry WS limit; the real server must accept it.
          assert len(json.dumps(value)) > 16384
          for sequence in range(8):
            started = time.monotonic()
            value.update(sequence=sequence, sampled_at=time.time())
            agent.send(json.dumps(value))
            assert json.loads(agent.recv()) == {'type':'ack', 'sequence':sequence}
            result = json.loads(viewer.recv())
            assert result['type'] == 'frame' and result['frame']['sequence'] == sequence
            assert result['frame']['source'] == camera
            viewer.send(json.dumps({'type':'ack'}))
            time.sleep(max(0, .125-(time.monotonic()-started)))
    # Exercise the device's real websocket-client caller, not only a separate
    # websockets-based protocol client. The camera bytes are an explicit fixture.
    from openpilot.sunnypilot.formosalink import cameras
    sources = []
    class CameraFixture:
      def __init__(self, camera, **kwargs):
        self.closed = False
        sources.append(self)
      def __call__(self):
        return JPEG, time.time(), {'speed_kph':None, 'engaged':None}
      def close(self):
        self.closed = True
    monkeypatch.setattr(cameras, 'NativeCamera', CameraFixture)
    for camera in ('wide-road', 'driver'):
      path = f'/api/v1/devices/{identity["device_id"]}/media/stream?camera={camera}'
      stop = threading.Event()
      publisher = threading.Thread(target=cameras.stream_camera, args=(identity, private, camera, stop), daemon=True)
      with connect(base+path, origin=origin, additional_headers={'Cookie':cookie}, compression=None) as viewer:
        publisher.start()
        try:
          sequence, deadline = 0, time.monotonic()+8
          while sequence < 3:
            remaining = deadline-time.monotonic()
            assert remaining > 0, 'native publisher did not deliver three frames'
            result = json.loads(viewer.recv(timeout=remaining))
            if result['type'] == 'waiting':
              viewer.send(json.dumps({'type':'ack'}))
              continue
            assert result['type'] == 'frame', result
            assert result['frame']['source'] == camera
            assert result['frame']['sequence'] == sequence
            if sequence == 2:
              stop.set()
            viewer.send(json.dumps({'type':'ack'}))
            sequence += 1
        finally:
          stop.set()
          publisher.join(timeout=5)
      assert not publisher.is_alive()
      assert sources[-1].closed
  finally:
    server.should_exit = True
    thread.join(timeout=10)
    listener.close()
  assert not thread.is_alive()
