import hashlib
import json
import subprocess
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from openpilot.selfdrive.ui import layout_profile
from tools.layout_studio.server import BranchPublisher, PublishConflict, STATIC, Studio


@pytest.fixture
def studio(tmp_path, monkeypatch):
  path = tmp_path / "layout.json"
  path.write_bytes(layout_profile.PROFILE_PATH.read_bytes())
  monkeypatch.setattr(layout_profile, "PROFILE_PATH", path)
  layout_profile._load.cache_clear()
  with Studio(0, path) as server:
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
      yield f"http://127.0.0.1:{server.server_port}"
    finally:
      server.shutdown()
      thread.join()
      layout_profile._load.cache_clear()


def get(url):
  with urlopen(url, timeout=3) as response:
    return json.load(response)


def post(url, data, origin=None, endpoint="/api/export"):
  request = Request(url + endpoint, data=json.dumps(data).encode(),
                    headers={"Content-Type": "application/json", "Origin": origin or url})
  try:
    with urlopen(request, timeout=3) as response:
      return response.status, json.load(response)
  except HTTPError as e:
    return e.code, json.load(e)


def test_both_native_profiles_round_trip_and_conflicting_export(studio):
  initial = get(studio + "/api/layout")
  data = initial["profile"]
  c4, c3 = data["devices"]["c4"], data["devices"]["c3x"]
  c4["order"].reverse()
  c4["menu_font"] = 51
  c3["hud_x"] = 94
  c3["speed_font"] = 102
  payload = {"profile": data, "revision": initial["revision"]}
  code, saved = post(studio, payload)
  assert code == 200 and saved["revision"] != initial["revision"]
  assert saved["profile"] == data
  assert layout_profile.device_layout("c4") == c4
  assert layout_profile.device_layout("c3x") == c3
  assert post(studio, payload)[0] == 409
  assert post(studio, {**payload, "revision": saved["revision"]}) == (200, saved)


def test_invalid_profiles_and_cross_origin_cannot_overwrite(studio):
  before = get(studio + "/api/layout")
  payload = {"profile": before["profile"], "revision": before["revision"]}
  assert post(studio, payload, "http://other.invalid")[0] == 403
  c4 = payload["profile"]["devices"]["c4"]
  for k, value in [("order", ["device"] * 9), ("hud_x", 500), ("speed_font", True), ("extra", "x")]:
    old = c4.copy()
    c4[k] = value
    assert post(studio, payload)[0] == 400
    c4.clear()
    c4.update(old)
  assert get(studio + "/api/layout") == before


def test_all_preview_assets_servable(studio):
  for route in STATIC:
    with urlopen(studio + route) as response:
      assert response.status == 200
      data = response.read()
      assert data.startswith(b"\x89PNG") if route.endswith(".png") else bool(data)
  assert layout_profile.validate(layout_profile.defaults()) == layout_profile.defaults()


def test_invalid_native_profile_uses_stock(tmp_path, monkeypatch):
  path = Path(tmp_path, "layout.json")
  path.write_text("{}", encoding="utf-8")
  monkeypatch.setattr(layout_profile, "PROFILE_PATH", path)
  layout_profile._load.cache_clear()
  try:
    assert layout_profile.device_layout("c4") == layout_profile.defaults()["devices"]["c4"]
  finally:
    layout_profile._load.cache_clear()


def test_publisher_only_pushes_exported_profile_and_refuses_divergence(tmp_path):
  remote, repo = tmp_path / "remote.git", tmp_path / "work"
  def git(*args, cwd=tmp_path):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()
  git("init", "--bare", "-b", "carrot-wip", str(remote))
  git("init", "-b", "carrot-wip", str(repo))
  git("config", "user.name", "Layout Test", cwd=repo)
  git("config", "user.email", "test@localhost", cwd=repo)
  path = repo / "layout.json"
  data = layout_profile.defaults()
  path.write_text(json.dumps(data), encoding="utf-8")
  git("add", path.name, cwd=repo)
  git("commit", "-m", "base", cwd=repo)
  git("remote", "add", "origin", str(remote), cwd=repo)
  git("push", "origin", "carrot-wip", cwd=repo)
  git("switch", "-c", "codex/c4-layout-studio", cwd=repo)
  publisher = BranchPublisher(repo, path)
  data["devices"]["c3x"]["speed_font"] = 95
  path.write_text(json.dumps(data), encoding="utf-8")
  revision = hashlib.sha256(path.read_bytes()).hexdigest()
  with pytest.raises(PublishConflict):
    publisher.publish("stale")
  extra = repo / "unrelated"
  extra.touch()
  with pytest.raises(PublishConflict):
    publisher.publish(revision)
  extra.unlink()
  head = publisher.publish(revision)
  assert git("rev-parse", "carrot-wip", cwd=remote) == head
  assert json.loads(git("show", "carrot-wip:layout.json", cwd=remote)) == data
  assert publisher.publish(revision) == head

  # Simulate an independent remote update; publishing must keep it intact.
  git("switch", "carrot-wip", cwd=repo)
  git("commit", "--allow-empty", "-m", "other update", cwd=repo)
  newer = git("rev-parse", "HEAD", cwd=repo)
  git("update-ref", "refs/heads/test-other", newer, cwd=repo)
  git("push", "origin", "test-other", cwd=repo)
  git("update-ref", "refs/heads/carrot-wip", newer, cwd=remote)
  git("switch", "codex/c4-layout-studio", cwd=repo)
  with pytest.raises(PublishConflict):
    publisher.publish(revision)
  assert git("rev-parse", "carrot-wip", cwd=remote) == newer

def test_publish_endpoint_requires_explicit_export(tmp_path):
  path = tmp_path / "layout.json"
  path.write_bytes(layout_profile.PROFILE_PATH.read_bytes())
  calls = []
  class Publisher:
    def publish(self, revision):
      calls.append(revision)
      return "test-commit"

  with Studio(0, path, Publisher()) as server:
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
      url = f"http://127.0.0.1:{server.server_port}"
      initial = get(url + "/api/layout")
      request = {"revision": initial["revision"]}
      assert initial["canPublish"]
      assert post(url, request, endpoint="/api/publish")[0] == 409
      assert post(url, {**request, "profile": initial["profile"]})[0] == 200
      assert calls == []
      assert post(url, request, origin="http://other.invalid", endpoint="/api/publish")[0] == 403
      assert post(url, request, endpoint="/api/publish") == (200, {"commit": "test-commit"})
      assert calls == [request["revision"]]
      assert get(url + "/api/layout")["published"] == "test-commit"
    finally:
      server.shutdown()
      thread.join()
