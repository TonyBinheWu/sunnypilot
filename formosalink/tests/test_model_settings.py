import json
import time
from types import SimpleNamespace

from formosalink.tests.test_platform import ORIGIN, client as client, pair
from formosalink.tests.test_settings import command, provider, sync
from openpilot.sunnypilot.formosalink.management_protocol import validate_snapshot
from openpilot.sunnypilot.formosalink.model_settings import ACTION, QUEUE, ModelSettings

SMALL, BIG = "1" * 40, "2" * 40


def manifest(ref, name, version=21):
  return {"ref": ref, "display_name": name, "minimum_selector_version": version}


def configured():
  source, params, guard = provider()
  source.models = ModelSettings(params, 21, lambda: None)
  params.values["ModelManager_ModelsCache"] = {"bundles": [manifest(SMALL, "Small"), manifest("3"*40, "Old", 20)]}
  params.values["ModelManager_ModelsCache_Chestnut"] = {"bundles": [manifest(BIG, "Big")]}
  return source, params, guard


def test_signed_model_selection_and_configured_readback(client):
  device, private, _ = pair(client)
  source, params, guard = configured()
  sync(client, device, private, source.capture()).raise_for_status()
  path = "/api/v1/devices/" + device + "/settings"
  def request(key, value):
    state = source.capture()
    return client.post(path, json={"key": key, "value": value, "session": state["session"], "expected_revision": state["revision"]},
                       headers={"Origin": ORIGIN})
  for invalid in (SMALL, "3"*40, "https://example.org/bundle", {"ref": BIG}):
    assert request("DrivingModelBig", invalid).status_code == 409
  assert request("DrivingModelBig", BIG).status_code == 200
  cmd = sync(client, device, private, source.capture()).json()["command"]
  receipt = source.apply(cmd, device, time.monotonic()+4)
  assert receipt["status"] == "applied" and params.get(QUEUE) == BIG
  snap = source.capture()
  snap["receipts"] = [receipt]
  assert sync(client, device, private, snap).json()["acknowledged"] == [cmd["id"]]
  assert snap["values"]["DrivingModelBig"] == ""
  artifact = SimpleNamespace(fileName="bundle", downloadProgress=SimpleNamespace(status="verifying", progress=99))
  progress = SimpleNamespace(ref=BIG, status="downloading", models=[SimpleNamespace(artifact=artifact)])
  source.models.progress = lambda: progress
  info = json.loads(source.capture()["info"]["model_manager"])
  assert (info["status"], info["name"], info["percent"]) == ("verifying", "Big", 99)
  params.put("ModelManager_ActiveBundleChestnut", {"ref": BIG, "displayName": "Big", "minimumSelectorVersion": 21})
  params.put("ModelManager_LastDownload", {"ref": BIG, "status": "downloaded"})
  params.remove(QUEUE)
  source.models.progress = lambda: None
  state = source.capture()
  assert state["values"]["DrivingModelBig"] == BIG
  assert json.loads(state["info"]["model_manager"])["configured"][1] == "Big"
  command_default = command(state, "DrivingModelBig", "", device)
  guard.parked = False
  assert source.apply(command_default, device, time.monotonic()+4)["reason"] == "offroad_required"
  guard.parked = True
  params.values["FormosaLinkRemoteSettings"] = False
  assert source.apply(command_default, device, time.monotonic()+4)["reason"] == "local_disabled"
  params.values["FormosaLinkRemoteSettings"] = True
  command_default = command(source.capture(), "DrivingModelBig", "", device)
  assert source.apply(command_default, device, time.monotonic()+4)["status"] == "applied"
  assert params.get("ModelManager_ActiveBundleChestnut") is None


def test_model_actions_retry_and_growing_catalog():
  source, params, _ = configured()
  def apply(key, value):
    cmd = command(source.capture(), key, value)
    return source.apply(cmd, cmd["device_id"], time.monotonic()+2)["status"]
  def status():
    return json.loads(source.capture()["info"]["model_manager"])["status"]
  assert apply(ACTION, "refresh") == "applied" and status() == "refreshing"
  for suffix in ("", "_Chestnut"):
    params.put("ModelManager_LastSyncTime"+suffix, 100)
  assert status() == "refreshed"
  assert apply(ACTION, "clear") == "applied" and status() == "clearing"
  params.remove("ModelManager_ClearCache")
  assert status() == "cleared"
  assert apply("DrivingModelSmall", SMALL) == "applied"
  assert apply("DrivingModelBig", BIG) == "rejected"
  assert apply(ACTION, "cancel") == "applied" and status() == "cancelled"
  params.put("ModelManager_LastDownload", {"ref": SMALL, "status": "failed"})
  assert status() == "failed"
  assert apply("DrivingModelSmall", SMALL) == "applied"
  params.remove(QUEUE)
  bundles = [manifest(f"{n:040x}", f"Model {n}") for n in range(160)]
  params.put("ModelManager_ModelsCache", {"bundles": bundles})
  snap = validate_snapshot(source.capture())
  choices = [o["value"] for e in snap["catalog"] if e["key"].startswith("DrivingModelSmall") for o in e["options"]]
  assert set(choices) == {"", *(b["ref"] for b in bundles)}
