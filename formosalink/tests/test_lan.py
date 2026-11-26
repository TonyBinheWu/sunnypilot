import uuid
from unittest.mock import patch

from formosalink.tests.test_model_settings import configured
from openpilot.sunnypilot.formosalink.lan import GRANT, REQUEST, LanDevice, certificate


def test_local_pairing_lifecycle_and_guarded_settings(tmp_path):
  provider, params, guard = configured()
  grant, device_id = str(uuid.uuid4()), str(uuid.uuid4())
  params.put(GRANT, grant)
  client = LanDevice(tmp_path, params, grant, provider, device_id)
  params.put(REQUEST, "on-device-1")
  _, pin = certificate(tmp_path)
  assert certificate(tmp_path)[1] == pin
  client.refresh("192.168.1.20", pin)
  for _ in range(5):
    assert client.pair("bad") is None
  assert client.pair(client.code) is None
  params.put(REQUEST, "on-device-2")
  client.refresh("192.168.1.20", pin)
  with patch("time.monotonic", return_value=client.until + 1):
    assert client.pair(client.code) is None
  guard.parked = False
  assert client.pair(client.code) is None
  guard.parked = True
  code = client.code
  paired = client.pair(code)
  assert client.paired(paired["token"]) and not client.paired("other") and client.pair(code) is None
  assert paired["token"] not in (tmp_path / "phones.json").read_text()
  snapshot = client.state()["snapshot"]
  command = {"session": snapshot["session"], "expected_revision": snapshot["revision"], "key": "QuietMode", "value": True}
  guard.parked = False
  assert client.submit(command)["reason"] == "offroad_required"
  guard.parked = True
  command["expected_revision"] = client.state()["snapshot"]["revision"]
  command["session"] = client.state()["snapshot"]["session"]
  assert client.submit(command)["status"] == "applied" and params.get("QuietMode") is True
  assert client.submit(command)["status"] == "rejected"
  assert client.state()["commands"][1]["status"] == "applied"
  assert LanDevice(tmp_path, params, grant, provider, device_id).paired(paired["token"])
  params.put(GRANT, "new-grant")
  assert not client.paired(paired["token"])
  assert not LanDevice(tmp_path, params, "new-grant", provider, device_id).paired(paired["token"])
