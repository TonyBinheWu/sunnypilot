import hashlib
import os
import subprocess

import pytest

from tools.layout_studio import device_apply
from tools.layout_studio.server import BranchPublisher


@pytest.mark.skipif(os.name != "posix", reason="device uses a POSIX shell")
def test_apply_transfers_exported_commit_before_push(tmp_path, monkeypatch):
  def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()

  work, dev, remote = [tmp_path / name for name in ("work", "device", "upstream")]
  work.mkdir()
  git(work, "init", "-b", "carrot-wip")
  git(work, "config", "user.name", "Layout test")
  git(work, "config", "user.email", "layout@test")
  profile = work / "profile.json"
  profile.write_text("{}")
  git(work, "add", ".")
  git(work, "commit", "-m", "base")
  git(tmp_path, "init", "--bare", "-b", "carrot-wip", str(remote))
  git(work, "remote", "add", "origin", str(remote))
  git(work, "push", "-u", "origin", "carrot-wip")
  git(tmp_path, "clone", str(remote), str(dev))
  git(work, "switch", "-c", "codex/c4-layout-studio")
  (work / "ui").write_text("example")
  git(work, "add", ".")
  git(work, "commit", "-m", "ui")
  profile.write_text('{"mode":1}')
  revision = hashlib.sha256(profile.read_bytes()).hexdigest()
  publisher = BranchPublisher(work, profile)
  offroad, model = tmp_path / "offroad", tmp_path / "model"
  offroad.write_text("1")
  model.write_bytes(b"comma mici\0")
  for name in ("CHECK", "INSTALL"):
    script = getattr(device_apply, name)
    monkeypatch.setattr(
      device_apply,
      name,
      script.replace("/data/openpilot", str(dev))
      .replace("/data/params/d/IsOffroad", str(offroad))
      .replace("/sys/firmware/devicetree/base/model", str(model)),
    )
  ssh = tmp_path / "ssh"
  ssh.write_text('#!/bin/sh\nfor last do :; done\nexec sh -c "$last"\n')
  ssh.chmod(0o755)
  monkeypatch.setenv("PATH", str(tmp_path) + ":" + os.environ["PATH"])
  before = git(dev, "rev-parse", "HEAD")
  after = device_apply.install(publisher, "local-test", None, "c4", revision)
  assert git(dev, "rev-parse", "HEAD") == after != before
  assert git(remote, "rev-parse", "HEAD") == before
  assert device_apply.install(publisher, "local-test", None, "c4", revision) == after
  offroad.write_text("0")
  with pytest.raises(ValueError, match="offroad"):
    device_apply.install(publisher, "local-test", None, "c4", revision)
  assert publisher.publish(revision) == after
