"""Exercise the real HTTP/WebSocket client, not just ASGI in-memory transport."""
import socket
import threading
import time
import subprocess
import sys
from pathlib import Path

import requests
import uvicorn

from formosalink.server.app import create_app
from formosalink.server.config import initialize
from openpilot.sunnypilot.formosalink.agent import connect_once
from openpilot.sunnypilot.formosalink.identity import create
from openpilot.sunnypilot.formosalink.protocol import sign
from openpilot.sunnypilot.formosalink.telemetry import DemoSampler


def test_real_agent_http_and_websocket(tmp_path):
  listener = socket.socket()
  listener.bind(("127.0.0.1", 0))
  origin = f"http://127.0.0.1:{listener.getsockname()[1]}"
  password = "test-only-live-transport-password"
  initialize(tmp_path, origin, password)
  server = uvicorn.Server(uvicorn.Config(create_app(tmp_path), log_level="error", ws_max_size=16384))
  thread = threading.Thread(target=server.run, kwargs={"sockets":[listener]}, daemon=True)
  thread.start()
  try:
    for _ in range(100):
      if server.started:
        break
      time.sleep(.05)
    assert server.started
    identity, private, public = create(tmp_path / "device", origin)
    enrollment = requests.post(origin+"/api/v1/agent/enroll", json=sign(private,identity["device_id"],"enroll",{"public_key":public}),timeout=5)
    assert enrollment.status_code == 200
    result = enrollment.json()
    with requests.Session() as owner:
      headers = {"Origin":origin}
      assert owner.post(origin+"/api/v1/login",json={"password":password},headers=headers,timeout=5).status_code == 200
      assert owner.post(origin+"/api/v1/pair",json={"code":result["pair_code"],"fingerprint":result["fingerprint"],"name":"Live transport test"},headers=headers,timeout=5).status_code == 200
      stop = threading.Event()
      class Once:
        def sample(self, sequence):
          stop.set()
          return DemoSampler().sample(sequence)
      connect_once(identity, private, Once(), stop)
      rows = owner.get(origin+"/api/v1/devices",timeout=5).json()["devices"]
      assert rows[0]["snapshot"]["metrics"]["software_version"] == "FormosaPilot demo"
      assert rows[0]["snapshot"]["sequence"] == 0
  finally:
    server.should_exit = True
    thread.join(timeout=10)
    listener.close()
    assert not thread.is_alive()


def test_service_entrypoint_rotating_log(tmp_path):
  listener = socket.socket()
  listener.bind(("127.0.0.1", 0))
  port = listener.getsockname()[1]
  listener.close()
  origin = f"http://127.0.0.1:{port}"
  initialize(tmp_path, origin, "test-only-service-entrypoint-password")
  log_file = tmp_path / "server.log"
  process = subprocess.Popen([sys.executable,"-m","formosalink.server","--data-dir",str(tmp_path),"--port",str(port),
                              "--log-file",str(log_file)], cwd=Path(__file__).resolve().parents[2],
                             stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  try:
    ready = False
    for _ in range(100):
      if process.poll() is not None:
        raise AssertionError(process.communicate()[1].decode(errors="replace"))
      try:
        ready = requests.get(origin+"/api/v1/health",timeout=.3).json()["service"] == "FormosaLink"
      except (requests.RequestException,ValueError):
        pass
      if ready:
        break
      time.sleep(.05)
    assert ready
    assert "Application startup complete" in log_file.read_text(encoding="utf-8")
    assert "test-only-service-entrypoint-password" not in log_file.read_text(encoding="utf-8")
  finally:
    process.terminate()
    process.communicate(timeout=10)
