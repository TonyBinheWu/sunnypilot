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
from formosalink.tests.test_media import frame
from formosalink.tests.test_platform import PASSWORD
from openpilot.sunnypilot.formosalink.identity import create
from openpilot.sunnypilot.formosalink.protocol import fingerprint, sign


def test_real_network_stream_two_cameras_ack_and_probe(tmp_path):
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
  finally:
    server.should_exit = True
    thread.join(timeout=10)
    listener.close()
  assert not thread.is_alive()
