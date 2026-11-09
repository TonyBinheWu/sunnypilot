import ast
import copy
import json
import time
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from formosalink.server.app import create_app
from formosalink.server.config import initialize
from openpilot.sunnypilot.formosalink.agent import send_snapshot
from openpilot.sunnypilot.formosalink.identity import create, read
from openpilot.sunnypilot.formosalink.protocol import fingerprint, public_key_text, sign, validate_origin, validate_snapshot, verify
from openpilot.sunnypilot.formosalink.telemetry import DemoSampler, collect

ROOT = Path(__file__).resolve().parents[2]
ORIGIN = "https://formosapilot.dinglu-t.com"
PASSWORD = "test-owner-password-for-suite"
WS_URL = ORIGIN.replace("https://", "wss://") + "/api/v1/agent/ws"


@pytest.fixture
def client(tmp_path):
  initialize(tmp_path, ORIGIN, PASSWORD)
  with TestClient(create_app(tmp_path), base_url=ORIGIN) as value:
    yield value


def login(client):
  response = client.post("/api/v1/login", json={"password": PASSWORD}, headers={"Origin": ORIGIN})
  assert response.status_code == 200
  return response


def enroll(client):
  private = Ed25519PrivateKey.generate()
  device_id = str(uuid.uuid4())
  public = public_key_text(private)
  envelope = sign(private, device_id, "enroll", {"public_key": public})
  response = client.post("/api/v1/agent/enroll", json=envelope)
  assert response.status_code == 200
  return device_id, private, response.json(), envelope


def pair(client):
  login(client)
  device_id, private, result, _ = enroll(client)
  body = {"code": result["pair_code"], "fingerprint": result["fingerprint"], "name": "台灣・FormosaPilot"}
  assert client.post("/api/v1/pair", json=body, headers={"Origin": ORIGIN}).status_code == 200
  return device_id, private, body


def test_auth_csrf_host_and_cookie(client):
  assert client.get("/api/v1/devices").status_code == 401
  assert client.post("/api/v1/login", json={"password": PASSWORD}).status_code == 403
  assert client.get("/api/v1/health", headers={"Host": "attacker.example"}).status_code == 400
  response = login(client)
  cookie = response.headers["set-cookie"].lower()
  assert "httponly" in cookie and "secure" in cookie and "samesite=strict" in cookie
  assert "password" not in cookie
  assert client.get("/api/v1/devices").status_code == 200
  assert client.post("/api/v1/logout", json={}, headers={"Origin": ORIGIN}).status_code == 200
  assert client.get("/api/v1/devices").status_code == 401


def test_password_login_limit(client):
  for _ in range(8):
    assert client.post("/api/v1/login", json={"password": "wrong"}, headers={"Origin": ORIGIN}).status_code == 401
  assert client.post("/api/v1/login", json={"password": PASSWORD}, headers={"Origin": ORIGIN}).status_code == 429


def test_pair_single_use_fingerprint_and_expiration(client):
  login(client)
  device_id, private, result, envelope = enroll(client)
  assert client.post("/api/v1/agent/enroll", json=envelope).status_code == 400
  body = {"code": result["pair_code"], "fingerprint": "0"*24, "name": "Test"}
  assert client.post("/api/v1/pair", json=body, headers={"Origin": ORIGIN}).status_code == 400
  body["fingerprint"] = result["fingerprint"]
  assert client.post("/api/v1/pair", json=body, headers={"Origin": ORIGIN}).status_code == 200
  assert client.post("/api/v1/pair", json=body, headers={"Origin": ORIGIN}).status_code == 400
  assert client.app.state.store.get(device_id)["pair_hash"] is None
  device_id, _, result, _ = enroll(client)
  with client.app.state.store.connection() as db:
    db.execute("UPDATE devices SET pair_expires=0 WHERE id=?", (device_id,))
  body.update(code=result["pair_code"], fingerprint=result["fingerprint"])
  assert client.post("/api/v1/pair", json=body, headers={"Origin": ORIGIN}).status_code == 400


def test_websocket_snapshot_disconnect_and_revoke(client):
  device_id, private, _ = pair(client)
  with client.websocket_connect(WS_URL) as ws:
    ws.send_json(sign(private, device_id, "connect"))
    assert ws.receive_json()["type"] == "ready"
    ws.send_json(DemoSampler().sample(0))
    assert ws.receive_json() == {"type": "ack", "sequence": 0}
    row = client.get("/api/v1/devices").json()["devices"][0]
    assert row["online"] and not row["stale"]
    assert "public_key" not in row and "pair_hash" not in row
    assert client.post(f"/api/v1/devices/{device_id}/revoke", json={}, headers={"Origin": ORIGIN}).status_code == 200
    with pytest.raises(WebSocketDisconnect):
      ws.receive_json()
  row = client.get("/api/v1/devices").json()["devices"][0]
  assert not row["online"] and row["snapshot"] is None
  public = public_key_text(private)
  assert client.post("/api/v1/agent/enroll", json=sign(private, device_id, "enroll", {"public_key": public})).status_code == 400


def test_offline_and_stale_never_look_online(client):
  device_id, private, _ = pair(client)
  with client.websocket_connect(WS_URL) as ws:
    ws.send_json(sign(private, device_id, "connect")); ws.receive_json()
    data = DemoSampler().sample(0)
    data["sampled_at"] -= 30
    ws.send_json(data); ws.receive_json()
    row = client.get("/api/v1/devices").json()["devices"][0]
    assert row["online"] and row["stale"]
  row = client.get("/api/v1/devices").json()["devices"][0]
  assert not row["online"] and row["stale"]


def test_pending_device_cannot_send_telemetry(client):
  device_id, private, _, _ = enroll(client)
  with client.websocket_connect(WS_URL) as ws:
    ws.send_json(sign(private, device_id, "connect"))
    with pytest.raises(WebSocketDisconnect):
      ws.receive_json()


def test_websocket_replay_and_unknown_fields(client):
  device_id, private, _ = pair(client)
  auth = sign(private, device_id, "connect")
  with client.websocket_connect(WS_URL) as ws:
    ws.send_json(auth); ws.receive_json()
    data = DemoSampler().sample(0)
    data["metrics"]["remote_command"] = "reboot"
    ws.send_json(data)
    with pytest.raises(WebSocketDisconnect):
      ws.receive_json()
  with client.websocket_connect(WS_URL) as ws:
    ws.send_json(auth)
    with pytest.raises(WebSocketDisconnect):
      ws.receive_json()


def test_browser_cannot_open_agent_socket(client):
  with pytest.raises(WebSocketDisconnect):
    with client.websocket_connect(WS_URL, headers={"Origin": ORIGIN}):
      pass


def test_identity_is_independent_and_never_overwritten(tmp_path):
  value, key, public = create(tmp_path, ORIGIN)
  assert fingerprint(public) == fingerprint(read(tmp_path)[2])
  assert "DongleId" not in value and "SunnylinkDongleId" not in value
  assert key.sign(b"test") == read(tmp_path)[1].sign(b"test")
  with pytest.raises(FileExistsError):
    create(tmp_path, ORIGIN)


def test_signature_tamper_wrong_key_purpose_and_expiration():
  key = Ed25519PrivateKey.generate()
  public = public_key_text(key)
  envelope = sign(key, str(uuid.uuid4()), "connect", timestamp=1000)
  assert verify(envelope, public, "connect", now=1000)
  for changed in ("purpose", "timestamp", "payload"):
    modified = copy.deepcopy(envelope)
    modified[changed] = {"purpose":"enroll", "timestamp":1001, "payload":{"x":1}}[changed]
    with pytest.raises((ValueError, InvalidSignature)):
      verify(modified, public, "connect", now=1000)
  with pytest.raises(ValueError):
    verify(envelope, public, "connect", now=1200)
  with pytest.raises(InvalidSignature):
    verify(envelope, public_key_text(Ed25519PrivateKey.generate()), "connect", now=1000)


@pytest.mark.parametrize("url", ["http://192.168.20.145", "https://example.com/path", "https://user:secret@example.com", "file:///etc/passwd"])
def test_transport_policy(url):
  with pytest.raises(ValueError):
    validate_origin(url)


def test_metric_allowlist_and_nonfinite():
  snapshot = DemoSampler().sample(0)
  for key, value in [("gps", "secret"), ("cpu_temp_c", float("nan")), ("memory_percent", 101), ("started", "true")]:
    data = copy.deepcopy(snapshot)
    data["metrics"][key] = value
    with pytest.raises(ValueError):
      validate_snapshot(data)


def test_agent_refuses_commands():
  class Socket:
    def send(self, _):
      pass
    def recv(self):
      return json.dumps({"type":"command", "action":"reboot"})
  with pytest.raises(ValueError):
    send_snapshot(Socket(), DemoSampler().sample(0))


def test_sampler_marks_stale_sources_and_car_speed():
  class SM:
    seen = {"deviceState":True,"carState":True}
    valid = {"deviceState":False,"carState":False}
    logMonoTime = {"deviceState":int(time.monotonic()*1e9),"carState":int(time.monotonic()*1e9)}
    def update(self, _):
      pass
    def __getitem__(self, service):
      if service == "carState":
        return SimpleNamespace(vEgo=10)
      return SimpleNamespace(started=True,cpuTempC=[40,50],gpuTempC=[45],memoryUsagePercent=20,freeSpacePercent=60,thermalStatus="green",deviceType="tizi")
  sm = SM()
  snapshot = collect(sm, {}, 0)
  assert not snapshot["metrics"]["sample_valid"]
  assert snapshot["metrics"]["started"] is None and snapshot["metrics"]["speed_kph"] is None
  sm.valid = {"deviceState":True,"carState":True}
  assert collect(sm, {}, 1)["metrics"]["speed_kph"] == 36
  sm.logMonoTime["carState"] = int((time.monotonic()-10)*1e9)
  assert collect(sm, {}, 2)["metrics"]["speed_kph"] is None
  sm.logMonoTime["deviceState"] = int((time.monotonic()-10)*1e9)
  assert not collect(sm, {}, 3)["metrics"]["sample_valid"]


def test_disabled_by_default_and_readonly_integration():
  params = (ROOT / "openpilot/common/params_keys.h").read_text(encoding="utf-8")
  assert '{"FormosaLinkEnabled", {PERSISTENT, BOOL, "0"}}' in params
  code = ast.parse((ROOT / "openpilot/system/manager/process_config.py").read_text(encoding="utf-8"))
  predicate = next(n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=="formosalink_enabled")
  namespace = {"Params":object,"car":SimpleNamespace(CarParams=object)}
  exec(compile(ast.Module(body=[predicate],type_ignores=[]),"predicate","exec"),namespace)
  assert not namespace["formosalink_enabled"](False,SimpleNamespace(get_bool=lambda k:False),None)
  assert namespace["formosalink_enabled"](True,SimpleNamespace(get_bool=lambda k:k=="FormosaLinkEnabled"),None)
  telemetry = (ROOT / "openpilot/sunnypilot/formosalink/telemetry.py").read_text(encoding="utf-8")
  assert "PubMaster" not in telemetry and "put_bool" not in telemetry and "sendcan" not in telemetry


def test_no_remote_control_routes_and_request_limit(client):
  login(client)
  assert client.post("/api/v1/commands", json={"action":"reboot"}, headers={"Origin":ORIGIN}).status_code in (404,405)
  assert client.post("/api/v1/agent/enroll", content=b"x"*17000).status_code == 413


def test_server_restart_preserves_pairing_and_sessions(tmp_path):
  initialize(tmp_path, ORIGIN, PASSWORD)
  with TestClient(create_app(tmp_path),base_url=ORIGIN) as first:
    device_id, _, _ = pair(first)
    cookies = dict(first.cookies)
  with TestClient(create_app(tmp_path),base_url=ORIGIN) as second:
    second.cookies.update(cookies)
    row = second.get("/api/v1/devices").json()["devices"][0]
    assert row["id"] == device_id and not row["online"]


def test_static_assets_and_iis_protection(client):
  assert client.get("/").status_code == 200
  assert client.get("/app.js").status_code == 200
  logo = client.get("/assets/formosapilot-logo.png")
  assert logo.status_code == 200 and logo.content.startswith(b"\x89PNG\r\n\x1a\n")
  assert client.get("/api/v1/devices").headers["cache-control"] == "no-store"
  config = (ROOT / "formosalink/deploy/web.config").read_text(encoding="utf-8")
  assert 'segment="App_Data"' in config and 'fileExtension=".py" allowed="false"' in config


def test_owner_password_initialization_not_overwritten(tmp_path):
  with pytest.raises(ValueError):
    initialize(tmp_path, ORIGIN, "short")
  initialize(tmp_path, ORIGIN, PASSWORD)
  with pytest.raises(FileExistsError):
    initialize(tmp_path, ORIGIN, PASSWORD)


def test_cli_translation_parity():
  from openpilot.sunnypilot.formosalink.i18n import MESSAGES
  for locale in ("zh-TW", "en", "ja"):
    assert set(MESSAGES[locale]) == set(MESSAGES["zh-TW"])
    assert all(MESSAGES[locale].values())


def test_future_database_schema_is_not_silently_opened(tmp_path):
  import sqlite3
  from formosalink.server.store import Store
  database = tmp_path / "future.sqlite3"
  with sqlite3.connect(database) as db:
    db.execute("PRAGMA user_version=2")
  with pytest.raises(ValueError):
    Store(database)


def test_iis_setup_is_windows_powershell_compatible_utf8():
  script = ROOT / "formosalink/deploy/setup-server.ps1"
  assert script.read_bytes().startswith(b"\xef\xbb\xbf")
  source = script.read_text(encoding="utf-8-sig")
  assert "-Password" not in source
  assert "S-1-5-19" in source and "-AtStartup" in source
  assert "--log-file" in source
