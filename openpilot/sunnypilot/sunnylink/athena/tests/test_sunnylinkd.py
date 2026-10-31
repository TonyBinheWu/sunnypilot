"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64
from pathlib import Path
from types import SimpleNamespace

import tempfile

from openpilot.sunnypilot.sunnylink.athena import sunnylinkd
from openpilot.common.test import OpenpilotTestCase


class TestSunnylinkdMethods(OpenpilotTestCase):
  def setup_method(self):
    self.saved_params = []

    self.original_save = sunnylinkd.save_param_from_base64_encoded_string

    def mock_save_param(key, value, compression=False):
      self.saved_params.append((key, value, compression))

    sunnylinkd.save_param_from_base64_encoded_string = mock_save_param  # ty: ignore[invalid-assignment]

  def teardown_method(self):
    sunnylinkd.save_param_from_base64_encoded_string = self.original_save  # ty: ignore[invalid-assignment]

  def test_saveParams_blocked(self):
    blocked_params = {
      "GithubUsername": "attacker",
      "GithubSshKeys": "ssh-rsa attacker_key",
    }

    sunnylinkd.saveParams(blocked_params)

    assert len(self.saved_params) == 0

  def test_saveParams_allowed(self):
    allowed_params = {
      "SpeedLimitOffset": "5",
      "MyCustomParam": "123"
    }

    sunnylinkd.saveParams(allowed_params)

    # verify content
    assert len(self.saved_params) == 2
    keys_saved = [p[0] for p in self.saved_params]
    assert "SpeedLimitOffset" in keys_saved
    assert "MyCustomParam" in keys_saved

  def test_saveParams_mixed(self):
    mixed_params = {
      "GithubUsername": "attacker",
      "SpeedLimitOffset": "10"
    }

    sunnylinkd.saveParams(mixed_params)

    # should save allowed one
    assert len(self.saved_params) == 1
    assert self.saved_params[0][0] == "SpeedLimitOffset"
    assert self.saved_params[0][1] == "10"


class RemoteParams:
  def __init__(self):
    self.bools = {"IsOffroad": True, "DisableUpdates": False, "UpdateAvailable": True}
    self.values = {"GitBranch": "hkg-enhanced", "UpdaterTargetBranch": "hkg-enhanced", "UpdaterState": "idle"}
    self.writes = []

  def get(self, key):
    return self.values.get(key)

  def get_bool(self, key):
    return self.bools.get(key, False)

  def put(self, key, value, block=False):
    self.values[key] = value
    self.writes.append((key, value))

  def put_bool(self, key, value, block=False):
    self.bools[key] = value
    self.writes.append((key, value))


def _encoded(value: str) -> str:
  return base64.b64encode(value.encode("utf-8")).decode("ascii")


class TestRemoteUpdateRequests(OpenpilotTestCase):
  def test_remote_update_requires_offroad(self, monkeypatch):
    fake = RemoteParams()
    fake.bools["IsOffroad"] = False
    monkeypatch.setattr(sunnylinkd, "params", fake)
    monkeypatch.setattr(sunnylinkd, "sunnylink_ready", lambda _: True)
    monkeypatch.setattr(sunnylinkd.subprocess, "run", lambda *args, **kwargs: self.fail("updater was signaled while onroad"))

    with self.assertRaisesRegex(RuntimeError, "offroad"):
      sunnylinkd._remote_update_request("SunnylinkUpdateNow", _encoded("true"), False)
    assert fake.bools["SunnylinkUpdateNow"] is False
    assert fake.values["SunnylinkUpdateRequestStatus"].startswith("failed:")


  def test_remote_update_wakes_existing_updater(self, monkeypatch):
    fake = RemoteParams()
    commands = []
    monkeypatch.setattr(sunnylinkd, "params", fake)
    monkeypatch.setattr(sunnylinkd, "sunnylink_ready", lambda _: True)

    def run(cmd, **kwargs):
      commands.append(cmd)
      return SimpleNamespace(returncode=0)

    monkeypatch.setattr(sunnylinkd.subprocess, "run", run)
    sunnylinkd._remote_update_request("SunnylinkUpdateNow", _encoded("1"), False)
    assert commands == [["pkill", "-SIGHUP", "-f", "openpilot.system.updated.updated"]]
    assert fake.bools["SunnylinkUpdateNow"] is False
    assert fake.values["SunnylinkUpdateRequestStatus"] == "download requested"


  def test_remote_install_requires_ready_update_and_ignition_off(self, monkeypatch):
    tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))
    fake = RemoteParams()
    monkeypatch.setattr(sunnylinkd, "params", fake)
    monkeypatch.setattr(sunnylinkd, "sunnylink_ready", lambda _: True)
    monkeypatch.setenv("UPDATER_STAGING_ROOT", str(tmp_path))
    monkeypatch.setattr(sunnylinkd, "BASEDIR", str(tmp_path / "installed"))

    class DeviceState:
      started = False

    class PandaState:
      ignitionLine = True
      ignitionCan = False

    class FakeSubMaster:
      def __init__(self, *args, **kwargs):
        pass

      def update(self, timeout):
        pass

      def all_checks(self, services):
        return True

      def __getitem__(self, service):
        return DeviceState() if service == "deviceState" else [PandaState()]

    monkeypatch.setattr(sunnylinkd.messaging, "SubMaster", FakeSubMaster)
    with self.assertRaisesRegex(RuntimeError, "vehicle must be off"):
      sunnylinkd._remote_update_request("SunnylinkInstallUpdate", _encoded("1"), False)
    assert ("DoReboot", True) not in fake.writes

    PandaState.ignitionLine = False
    with self.assertRaisesRegex(RuntimeError, "incomplete"):
      sunnylinkd._remote_update_request("SunnylinkInstallUpdate", _encoded("1"), False)
    assert ("DoReboot", True) not in fake.writes

    finalized = tmp_path / "finalized"
    finalized.mkdir()
    (finalized / ".overlay_consistent").touch()

    def run(cmd, **kwargs):
      assert cmd[:2] == ["git", "-C"]
      if cmd[-2:] == ["--abbrev-ref", "HEAD"]:
        return SimpleNamespace(stdout="hkg-enhanced\n")
      return SimpleNamespace(stdout="new\n" if Path(cmd[2]) == finalized else "old\n")

    monkeypatch.setattr(sunnylinkd.subprocess, "run", run)
    sunnylinkd._remote_update_request("SunnylinkInstallUpdate", _encoded("1"), False)
    assert ("DoReboot", True) not in fake.writes
    assert fake.values["SunnylinkUpdateRequestStatus"].startswith("armed:")
    sunnylinkd._remote_update_request("SunnylinkInstallUpdate", _encoded("1"), False)
    assert ("DoReboot", True) in fake.writes
