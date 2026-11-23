"""Local editor for the native C3X and C4 layouts. Run this file with Python 3."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from openpilot.selfdrive.ui.layout_profile import LIMITS, PROFILE_PATH, defaults, validate

ASSETS = ROOT / "openpilot/selfdrive/assets"
STATIC = {"/": (HERE / "index.html", "text/html; charset=utf-8"),
          "/studio.css": (HERE / "studio.css", "text/css; charset=utf-8"),
          "/scene.js": (HERE / "scene.js", "text/javascript; charset=utf-8"),
          "/studio.js": (HERE / "studio.js", "text/javascript; charset=utf-8"),
          "/assets/display.ttf": (ASSETS / "fonts/KaiGenGothicKR-Bold.ttf", "font/ttf")}
for name, path in {
  "speed": "images/speed_bg.png", "button": "icons_mici/buttons/button_rectangle.png",
  "toggles": "icons_mici/settings.png", "network": "icons_mici/settings/network/wifi_strength_full.png",
  "device": "icons_mici/settings/device_icon.png", "developer": "icons_mici/settings/developer_icon.png",
  "pair": "icons_mici/settings/comma_icon.png", "firehose": "icons_mici/settings/firehose.png",
}.items():
  STATIC[f"/assets/{name}.png"] = (ASSETS / path, "image/png")


class PublishConflict(Exception):
  pass


class BranchPublisher:
  def __init__(self, root, profile_path):
    self.root = root
    self.path = profile_path.relative_to(root).as_posix()
    self.branch = self.git("branch", "--show-current")
    if self.branch not in {"codex/c4-layout-studio", "carrot-wip"}:
      raise PublishConflict("目前工作分支不支援推送至 carrot-wip")
    self.head = self.git("rev-parse", "HEAD")
    self.remote = self.git("remote", "get-url", "--push", "origin")

  def git(self, *args):
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never"}
    result = subprocess.run(["git", "-C", str(self.root), *args], env=env,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=45)
    if result.returncode:
      raise PublishConflict("Git 未完成操作，請檢查分支權限、網路與遠端版本後重試")
    return result.stdout.strip()

  def publish(self, expected_revision):
    if (self.git("branch", "--show-current") != self.branch or self.git("rev-parse", "HEAD") != self.head
        or self.git("remote", "get-url", "--push", "origin") != self.remote):
      raise PublishConflict("工作分支或遠端已變動，請重新檢查分支")
    status = self.git("status", "--porcelain", "--untracked-files=all", "--", ".", f":(exclude){self.path}")
    if status:
      raise PublishConflict("工作目錄還有其他修改，請先檢查再推送")
    raw = (self.root / self.path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_revision:
      raise PublishConflict("版面已變動，請重新輸出")
    remote_ref = self.git("ls-remote", "--exit-code", "origin", "refs/heads/carrot-wip")
    self.git("merge-base", "--is-ancestor", remote_ref.split()[0], self.head)
    if self.git("status", "--porcelain", "--", self.path):
      self.git("commit", "--only", "-m", "Apply exported C3X and C4 native layouts", "--", self.path)
      new_head = self.git("rev-parse", "HEAD")
      if self.git("rev-parse", new_head + "^") != self.head or self.git("diff", "--name-only", self.head, new_head) != self.path:
        raise PublishConflict("提交期間分支已有其他修改，請重新核對")
      self.head = new_head
    if json.loads(self.git("show", self.head + ":" + self.path)) != json.loads(raw):
      raise PublishConflict("提交內容與已輸出版面不同，請重新檢查")
    # Push this reviewed object even if another process subsequently switches HEAD.
    self.git("push", "origin", self.head + ":refs/heads/carrot-wip")
    remote_ref = self.git("ls-remote", "--exit-code", "origin", "refs/heads/carrot-wip")
    if remote_ref.split()[0] != self.head:
      raise PublishConflict("遠端版本已改變，請重新核對")
    return self.head


class Studio(ThreadingHTTPServer):
  def __init__(self, port, profile_path=PROFILE_PATH, publisher=None):
    super().__init__(("127.0.0.1", port), Handler)
    self.profile_path = profile_path
    self.write_lock = threading.Lock()
    self.publisher = publisher
    self.exported_revision = None
    self.published_commit = None

  def snapshot(self):
    raw = self.profile_path.read_bytes()
    return {"profile": validate(json.loads(raw)), "revision": hashlib.sha256(raw).hexdigest()}

  def export(self, profile):
    contents = json.dumps(profile, indent=2, ensure_ascii=False) + "\n"
    fd, temp = tempfile.mkstemp(dir=self.profile_path.parent)
    try:
      with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(contents)
      os.chmod(temp, self.profile_path.stat().st_mode & 0o777)
      os.replace(temp, self.profile_path)
    finally:
      Path(temp).unlink(missing_ok=True)


class Handler(BaseHTTPRequestHandler):
  def send_body(self, status, data, mime="application/json; charset=utf-8"):
    if isinstance(data, dict):
      data = json.dumps(data, ensure_ascii=False).encode()
    self.send_response(status)
    self.send_header("Content-Type", mime)
    self.send_header("Content-Length", str(len(data)))
    self.send_header("Cache-Control", "no-store")
    self.send_header("X-Content-Type-Options", "nosniff")
    self.end_headers()
    self.wfile.write(data)

  def do_GET(self):
    if self.path == "/api/layout":
      self.send_body(200, {**self.server.snapshot(), "defaults": defaults(), "limits": LIMITS,
                           "canPublish": self.server.publisher is not None, "exported": self.server.exported_revision,
                           "published": self.server.published_commit})
    elif self.path in STATIC:
      path, mime = STATIC[self.path]
      self.send_body(200, path.read_bytes(), mime)
    else:
      self.send_body(404, {"error": "找不到頁面"})

  def do_POST(self):
    host = self.headers.get("Host", "")
    if self.path not in {"/api/export", "/api/publish"}:
      return self.send_body(404, {"error": "找不到頁面"})
    if host not in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"} or self.headers.get("Origin") != f"http://{host}":
      return self.send_body(403, {"error": "請從本機編輯器輸出"})
    try:
      size = int(self.headers.get("Content-Length", 0))
      if not 0 < size <= 16384 or self.headers.get_content_type() != "application/json":
        raise ValueError
      payload = json.loads(self.rfile.read(size))
      if not isinstance(payload, dict):
        raise ValueError
      revision = payload["revision"]
      if self.path == "/api/export":
        profile = validate(payload["profile"])
    except (ValueError, KeyError, TypeError):
      return self.send_body(400, {"error": "版面資料格式或數值有誤"})
    with self.server.write_lock:
      current = self.server.snapshot()
      if current["revision"] != revision:
        return self.send_body(409, {"error": "分支檔案已更新。請先載入已輸出版面，再套用調整。"})
      if self.path == "/api/publish":
        if not self.server.publisher or revision != self.server.exported_revision:
          return self.send_body(409, {"error": "請先從此編輯器輸出版面"})
        try:
          self.server.published_commit = self.server.publisher.publish(revision)
        except (PublishConflict, OSError, subprocess.TimeoutExpired) as exc:
          return self.send_body(409, {"error": str(exc) if isinstance(exc, PublishConflict) else "推送未能確認，請重試"})
        return self.send_body(200, {"commit": self.server.published_commit})
      if profile != current["profile"]:
        self.server.published_commit = None
        self.server.export(profile)
      saved = self.server.snapshot()
      self.server.exported_revision = saved["revision"]
      self.send_body(200, saved)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--port", type=int, default=49837)
  parser.add_argument("--publish", action="store_true", help="enable the explicit push to origin/carrot-wip")
  args = parser.parse_args()
  publisher = BranchPublisher(ROOT, PROFILE_PATH) if args.publish else None
  with Studio(args.port, publisher=publisher) as server:
    print(f"http://127.0.0.1:{server.server_port}/", flush=True)
    server.serve_forever()
