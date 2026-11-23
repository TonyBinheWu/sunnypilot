"""Install a reviewed, fast-forward UI commit on a named offroad device over SSH."""

import re
import shlex
import subprocess
import tempfile
from pathlib import Path

CHECK = """set -eu
cd /data/openpilot
test "$(cat /data/params/d/IsOffroad)" = 1 || { echo "車機尚未進入 offroad" >&2; exit 1; }
case "$(tr -d '\\000' </sys/firmware/devicetree/base/model)" in
  *"comma $1") ;; *) echo "車機型號不符" >&2; exit 1 ;;
esac
test "$(git branch --show-current)" = carrot-wip || { echo "車機目前分支不是 carrot-wip" >&2; exit 1; }
test -z "$(git status --porcelain --untracked-files=normal)" || { echo "車機有本機變更" >&2; exit 1; }
"""
INSTALL = """
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
cat >"$tmp"
git bundle verify "$tmp" >&2
git fetch --no-tags "$tmp" HEAD >&2
test "$(git rev-parse FETCH_HEAD)" = "$2"
test "$(git rev-parse HEAD)" = "$3"
test "$(cat /data/params/d/IsOffroad)" = 1
git merge --ff-only "$2" >&2
git rev-parse HEAD
"""


def install(publisher, target, key, device, revision):
  if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.@-]*", target):
    raise ValueError("SSH 位址格式有誤")
  hw = {"c3x": "tizi", "c4": "mici"}[device]
  ssh = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=5"]
  if key:
    ssh.extend(["-o", "IdentitiesOnly=yes", "-i", str(key)])

  def remote(script, args, stream=None):
    cmd = shlex.join(["sh", "-c", CHECK + script, "layout", hw, *args])
    result = subprocess.run([*ssh, target, cmd], stdin=stream or subprocess.DEVNULL, capture_output=True, timeout=90)
    if result.returncode:
      raise ValueError(result.stderr.decode(errors="replace").strip()[-400:] or "車機套用失敗")
    return result.stdout.decode().strip()

  before = remote("git rev-parse HEAD", [])
  if not re.fullmatch(r"[a-f0-9]{40}", before):
    raise ValueError("無法確認車機版本")
  publisher.prepare(revision)
  if before == publisher.head:
    return before
  base = publisher.git("rev-parse", "refs/remotes/origin/carrot-wip")
  publisher.git("merge-base", "--is-ancestor", base, before)
  publisher.git("merge-base", "--is-ancestor", before, publisher.head)
  with tempfile.TemporaryDirectory() as directory:
    bundle = Path(directory) / "layout.bundle"
    publisher.git("bundle", "create", str(bundle), "HEAD", "^" + before)
    with bundle.open("rb") as stream:
      after = remote(INSTALL, [publisher.head, before], stream)
  if after != publisher.head:
    raise ValueError("無法確認車機提交版本")
  return after
