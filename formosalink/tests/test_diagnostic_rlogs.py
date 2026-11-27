import io
import os
import sqlite3
import time
from contextlib import closing
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

import pytest
import zstandard as zstd
from fastapi.testclient import TestClient

from formosalink.server import diagnostics
from formosalink.server.app import COOKIE, create_app
from formosalink.server.config import initialize
from openpilot.sunnypilot.formosalink import diagnostic_rlog as rlog
from openpilot.sunnypilot.formosalink import diagnostic_upload as upload
from openpilot.sunnypilot.formosalink.settings import LOCAL_ONLY

ORIGIN = "https://formosapilot.dinglu-t.com"
VIN = "SYNTHETIC-PRIVATE-VEHICLE"
PRIVATE = "secret-device-and-route"
BUILD = "a1" * 20
CAR = "KIA_SORENTO_2024"
CODE = "34" * 16
START = 98765 * rlog.SECOND


def segment(folder, fault=True, branch="ccnc-port", complete=True, platform=CAR, chestnut=False):
  schema = rlog.server_schema()
  entries = [{"key": "SensitiveSetting", "value": PRIVATE.encode()}]
  if chestnut:
    entries.append({"key": "Offroad_ChestnutUncompiled", "value": VIN.encode()})
  frames = [
    rlog.encode(schema, "initData", 77, True,
                {"gitBranch": branch, "gitCommit": BUILD, "dongleId": PRIVATE, "wallTimeNanos": 12345678901234,
                 "gitRemote": "https://example.test/" + PRIVATE, "params": {"entries": entries}}),
    rlog.encode(schema, "sentinel", START, True, {"type": "startOfSegment"}),
    rlog.encode(schema, "carParams", START + 10, True, {"carFingerprint": platform, "carVin": VIN, "pcmCruise": True}),
    rlog.encode(schema, "gpsLocationExternal", START + 100, True, {"latitude": 25.123456, "longitude": 121.654321}),
    rlog.encode(schema, "logMessage", START + 120, True, PRIVATE),
    rlog.encode(schema, "can", START + 150, True, [{"address": 17, "dat": VIN.encode()}]),
    rlog.encode(schema, "carState", START + 200, True, {"canValid": True, "vEgo": 19.1234}),
    rlog.encode(schema, "onroadEvents", START + 300, True, [{"name": "seatbeltNotLatched", "noEntry": True}]),
  ]
  if fault:
    frames.extend([
      rlog.encode(schema, "carState", START + 400, False, {"canTimeout": True, "accFaulted": True, "vEgo": 17.89}),
      rlog.encode(schema, "onroadEvents", START + 3*rlog.SECOND, True, [{"name": "radarFault", "noEntry": True}]),
      rlog.encode(schema, "onroadEventsSP", START + 3*rlog.SECOND, True, {"events": [{"name": "controlsMismatchLateral", "immediateDisable": True}]}),
      rlog.encode(schema, "managerState", START + 3*rlog.SECOND, True,
                  {"processes": [{"name": "modeld", "exitCode": 7, "shouldBeRunning": True, "pid": 12345},
                                 {"name": PRIVATE, "exitCode": 7, "shouldBeRunning": True}]}),
      rlog.encode(schema, "pandaStates", START + 4*rlog.SECOND, True, [{"faultStatus": "faultPerm", "faults": ["relayMalfunction"]}]),
    ])
  if complete:
    frames.append(rlog.encode(schema, "sentinel", START + 60*rlog.SECOND, True, {"type": "endOfSegment"}))
  folder.mkdir(parents=True, exist_ok=True)
  dest = folder / "rlog.zst"
  dest.write_bytes(zstd.ZstdCompressor().compress(b"".join(frames)))
  return dest


def test_native_rlog_whitelist_and_relative_time(tmp_path):
  path = segment(tmp_path, chestnut=True)
  original = path.read_bytes()
  body, faults = rlog.extract(path, rlog.server_schema())
  output, reasons, revision, platform = rlog.verify_report(body)
  assert faults == reasons == sorted(["Offroad_ChestnutUncompiled", "accFaulted", "canTimeout", "radarFault", "controlsMismatchLateral",
                                     "faultPerm", "modeld", "relayMalfunction"])
  assert (revision, platform) == (BUILD, CAR)
  raw = zstd.ZstdDecompressor().decompress(output)
  assert PRIVATE.encode() not in raw and VIN.encode() not in raw
  rows = list(rlog.server_schema().Event.read_multiple_bytes(raw))
  assert [m.which() for m in rows] == ["initData", "carParams", "carState", "managerState", "onroadEvents", "onroadEventsSP", "pandaStates"]
  assert [m.logMonoTime // rlog.SECOND for m in rows] == [0, 0, 0, 3, 3, 3, 4]
  assert rows[0].initData.params.entries[0].value == b"1" and rows[0].initData.wallTimeNanos == 0
  assert rows[1].carParams.carVin == "" and rows[2].carState.vEgo == 0 and rows[2].carState.accFaulted
  assert rows[3].managerState.processes[0].pid == 0 and len(rows[3].managerState.processes) == 1
  assert path.read_bytes() == original


def test_healthy_incomplete_foreign_and_unknown_platform(tmp_path):
  schema = rlog.server_schema()
  assert rlog.extract(segment(tmp_path, fault=False), schema) is None
  with pytest.raises(ValueError):
    rlog.extract(segment(tmp_path, branch="carrot-wip"), schema)
  with pytest.raises(ValueError):
    rlog.extract(segment(tmp_path, complete=False), schema)
  body, _ = rlog.extract(segment(tmp_path, platform=VIN, fault=False, chestnut=True), schema)
  assert rlog.verify_report(body)[1:] == (["Offroad_ChestnutUncompiled"], BUILD, "")


def test_inbox_access_retry_validation_and_retention(tmp_path, monkeypatch):
  state = tmp_path / "private"
  initialize(state, ORIGIN, "test-only-admin-password")
  raw = segment(tmp_path / "log")
  body, _ = rlog.extract(raw, rlog.server_schema())
  headers = {"Content-Type": "application/zstd", "X-Report-Id": CODE}
  application = create_app(state)
  with TestClient(application, base_url=ORIGIN) as client:
    assert "anonymous-rlog-v1" in client.get("/api/v1/health").json()["features"]
    def post(payload=body, code=CODE):
      return client.post(rlog.UPLOAD_PATH, content=payload, headers={**headers, "X-Report-Id": code})
    assert post().json() == post().json() == {"receipt": CODE}
    assert post(b"broken").status_code == 422
    assert post(raw.read_bytes()).status_code == 422
    junk = rlog.encode(rlog.server_schema(), "carParams", 0, True, {"carVin": VIN})
    clear = zstd.ZstdDecompressor().decompress(body)
    assert post(zstd.ZstdCompressor().compress(clear + junk)).status_code == 422
    frames = list(rlog.messages(io.BytesIO(clear), rlog.MAX_CLEAR, 16384))
    frames[1] = junk
    assert post(zstd.ZstdCompressor().compress(b"".join(frames))).status_code == 422
    assert post(body + b"hidden trailer").status_code == 422
    assert post(zstd.ZstdCompressor().compress(b"0" * (rlog.MAX_CLEAR + 1))).status_code == 422
    assert post(b"0" * (rlog.MAX_WIRE + 1)).status_code == 413
    assert post(body, "../private").status_code == 400
    other, _ = rlog.extract(segment(tmp_path / "other", chestnut=True), rlog.server_schema())
    assert post(other).status_code == 409
    monkeypatch.setattr(diagnostics, "MAX_REPORTS", 1)
    assert post(other, "ab"*16).status_code == 503
    assert post().status_code == 200
    admin = diagnostics.ADMIN_PATH
    download = f"{admin}/{CODE}/rlog.zst"
    assert client.get(admin).status_code == client.get(download).status_code == 401
    store = application.state.store
    client.cookies.set(COOKIE, store.session(store.github_user("123", "test-user")))
    assert client.get(admin).status_code == client.get(download).status_code == 403
    client.cookies.clear()
    client.cookies.set(COOKIE, store.session())
    page = client.get(admin, params={"q": CODE[:12]})
    assert page.status_code == 200 and "radarFault" in page.text and download in page.text
    result = client.get(download)
    assert result.headers["cache-control"] == "no-store" and rlog.verify_report(result.content)[1:]
    with closing(sqlite3.connect(state / "anonymous-rlogs.sqlite3")) as db, db:
      assert db.execute("SELECT COUNT(*) FROM reports").fetchone()[0] == 1
      db.execute("UPDATE reports SET received=0")
    assert client.get(download).status_code == 404
    assert post(other, "ab"*16).status_code == 200


def test_parked_queue_consent_window_retry_and_revoke(tmp_path):
  class Params(dict):
    def put(self, key, value, block=False):
      self[key] = value
    def remove(self, key):
      self.pop(key, None)
  params = Params()
  assert {upload.CONSENT, upload.RECEIPT} <= LOCAL_ONLY
  assert not upload.valid_consent(params.get(upload.CONSENT))
  upload.set_consent(params, True, tmp_path)
  consent = params[upload.CONSENT]
  root = tmp_path / "realdata"
  live = segment(root / "route--0")
  segment(root / "route--1")
  old = segment(root / "old--0")
  locked = segment(root / "locked--0")
  (locked.parent / "rlog.lock").touch()
  now = time.time_ns() // 10**9
  os.utime(old, (now - 2*upload.DAY,) * 2)
  with closing(upload.Queue(tmp_path, consent)) as queue:
    queue.scan(root, rlog.server_schema(), lambda: True, now)
    assert queue.db.execute("SELECT COUNT(*) FROM segments").fetchone()[0] == 2
    assert queue.db.execute("SELECT COUNT(payload) FROM segments").fetchone()[0] == 1
    queued_name, = queue.db.execute("SELECT source FROM segments WHERE payload IS NOT NULL").fetchone()
    os.utime(root / queued_name / "rlog.zst", ns=(now * 10**9,) * 2)
    queue.scan(root, rlog.server_schema(), lambda: True, now)
    assert queue.db.execute("SELECT COUNT(payload) FROM segments").fetchone()[0] == 1
    send = Mock(return_value="retry")
    assert queue.deliver(send, lambda: False, now) is None
    send.assert_not_called()
    assert queue.deliver(send, lambda: True, now) is None
    code = send.call_args.args[0]
    assert queue.deliver(send, lambda: True, now + 30) is None
    assert send.call_count == 1
  with closing(upload.Queue(tmp_path, consent)) as queue:
    accept = Mock(return_value="accepted")
    assert queue.deliver(accept, lambda: True, now + 61) == code
    assert accept.call_args == send.call_args
    assert queue.deliver(accept, lambda: True, now + 62) is None
  upload.set_consent(params, False, tmp_path)
  assert not params and not upload.queue_path(tmp_path, consent).exists() and live.is_file()


def test_anonymous_http_has_no_pairing_and_checks_exact_receipt():
  session = MagicMock()
  response = session.post.return_value.__enter__.return_value
  response.status_code = 200
  response.iter_content.return_value = [b'{"receipt":"', CODE.encode(), b'"}']
  with patch("requests.Session") as factory:
    factory.return_value.__enter__.return_value = session
    assert upload.post(CODE, b"fixture") == "accepted"
    assert session.trust_env is False
    args, kwargs = session.post.call_args
    assert args == (ORIGIN + rlog.UPLOAD_PATH,) and kwargs["allow_redirects"] is False
    assert kwargs["headers"] == {"Content-Type": "application/zstd", "X-Report-Id": CODE}
    response.iter_content.return_value = [b'{"receipt":"wrong"}']
    assert upload.post(CODE, b"fixture") == "retry"
    for status in (302, 403, 404, 429, 503):
      response.status_code = status
      assert upload.post(CODE, b"fixture") == "retry"


@pytest.mark.parametrize("network,metered,started,alive,valid,allowed", [
  ("wifi", False, False, True, True, True), ("ethernet", False, False, True, True, True),
  ("wifi", True, False, True, True, False), ("cell4G", False, False, True, True, False),
  ("wifi", False, True, True, True, False), ("wifi", False, False, False, True, False),
  ("wifi", False, False, True, False, False)])
def test_transport_conditions(network, metered, started, alive, valid, allowed):
  class State(dict):
    def update(self, timeout):
      assert timeout == 0
  state = State(deviceState=SimpleNamespace(networkType=network, networkMetered=metered, started=started))
  state.alive = {"deviceState": alive}
  state.valid = {"deviceState": valid}
  assert upload.eligible_network(state) is allowed
