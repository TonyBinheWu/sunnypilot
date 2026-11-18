"""Loopback Training Studio UI and operator actions. No training data is publicly served."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

from tools.training_studio.store import BASE, Store, read_json, write_json

WEB = Path(__file__).with_name("web")


def initialize(root, inboxes=()):
  store = Store(root)
  if not (store.root/"config.json").is_file():
    write_json(store.root/"config.json",{"version":1,"inboxes":list(inboxes),"teacher_url":"http://127.0.0.1:18766",
      "teacher_qualification":"","training_device":"cuda","feature_provider":"CPUExecutionProvider",
      "epochs":20,"batch_size":128,"learning_rate":.00001,"seed":7,"sample_interval_s":1.,"max_speed_mps":15.,
      "action_speed_floor_mps":2.5,
      "compiler_command":[],"release_repository":"TonyBinheWu/sunnypilot","release_branch":"carrot-wip",
      "base":BASE,"navigation_training":"no_route_only"})
  (store.root/"inbox").mkdir(exist_ok=True)
  return store


def handler_for(store, port):
  class Handler(BaseHTTPRequestHandler):
    def send_json(self, value, status=200):
      body = json.dumps(value,ensure_ascii=False,allow_nan=False).encode()
      self.send_response(status)
      self.send_header("Content-Type","application/json; charset=utf-8")
      self.send_header("Content-Length",str(len(body)))
      self.send_header("Cache-Control","no-store")
      self.send_header("X-Content-Type-Options","nosniff")
      self.end_headers()
      self.wfile.write(body)

    def valid_host(self):
      return self.headers.get("Host") in (f"127.0.0.1:{port}",f"localhost:{port}")

    def do_GET(self):
      if not self.valid_host():
        self.send_error(403)
        return
      if self.path == "/api/state":
        state = store.state()
        state["worker"]["fresh"] = time.time()-state["worker"].get("updated",0)<15
        self.send_json(state)
        return
      if self.path.startswith("/api/log/"):
        parts = self.path.split("/")
        if len(parts)!=5 or parts[4] not in ("prepare","teacher","train","evaluate","compile"):
          self.send_error(404)
          return
        folder = (store.root/"runs"/parts[3]).resolve()
        if not folder.is_relative_to(store.root/"runs"):
          self.send_error(403)
          return
        path = folder/(parts[4]+".log")
        text = ""
        if path.is_file():
          with path.open("rb") as stream:
            stream.seek(max(0,path.stat().st_size-20000))
            text = stream.read().decode("utf-8",errors="replace")
        self.send_json({"text":text})
        return
      files = {"/":"index.html","/studio.js":"studio.js","/studio.css":"studio.css","/status.mjs":"status.mjs"}
      if self.path not in files:
        self.send_error(404)
        return
      file = WEB/files[self.path]
      body = file.read_bytes()
      self.send_response(200)
      self.send_header("Content-Type",{".html":"text/html; charset=utf-8",".js":"text/javascript; charset=utf-8",".mjs":"text/javascript; charset=utf-8",".css":"text/css; charset=utf-8"}[file.suffix])
      self.send_header("Content-Length",str(len(body)))
      self.send_header("Cache-Control","no-store")
      self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'")
      self.end_headers()
      self.wfile.write(body)

    def do_POST(self):
      if not self.valid_host() or self.headers.get("Origin") not in (f"http://127.0.0.1:{port}",f"http://localhost:{port}"):
        self.send_error(403)
        return
      if self.headers.get("Content-Type") != "application/json":
        self.send_error(415)
        return
      try:
        length = int(self.headers.get("Content-Length","0"))
        if not 0<length<=4096:
          raise ValueError("invalid action size")
        data = json.loads(self.rfile.read(length))
        if self.path == "/api/control":
          action = data["action"]
          if action == "start":
            store.enabled(True)
          elif action == "pause":
            store.enabled(False)
          elif action == "scan":
            # Scan is performed by the worker, so large copies do not block HTTP threads.
            write_json(store.root/"scan-request.json",{"requested":time.time()})
          elif action == "retry":
            if not store.enqueue(force=True):
              raise ValueError("已有工作執行中，或尚缺 train／validation／test 行程")
          else:
            raise ValueError("unknown control")
          store.event("操作："+action)
          self.send_json({"ok":True})
        elif self.path == "/api/publish":
          from tools.training_studio.release import request_publish
          self.send_json(request_publish(store,data["version"]))
        else:
          self.send_error(404)
      except (ValueError,KeyError,TypeError,OSError) as exc:
        self.send_json({"error":str(exc)},409)

    def log_message(self,*unused):
      pass
  return Handler


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--root",default="build/training-studio")
  parser.add_argument("--port",type=int,default=8890)
  parser.add_argument("--inbox",action="append",default=[])
  parser.add_argument("--no-worker",action="store_true")
  args = parser.parse_args()
  store = initialize(args.root,args.inbox)
  child = None
  if not args.no_worker:
    log = (store.root/"worker.log").open("a",encoding="utf-8")
    child = subprocess.Popen([sys.executable,"-m","tools.training_studio.engine","worker","--root",str(store.root)],
      stdout=log,stderr=subprocess.STDOUT,start_new_session=os.name!="nt")
  server = ThreadingHTTPServer(("127.0.0.1",args.port),handler_for(store,args.port))
  stop = threading.Event()
  for signum in (signal.SIGINT,signal.SIGTERM):
    signal.signal(signum,lambda *_:stop.set())
  thread = threading.Thread(target=server.serve_forever,daemon=True)
  thread.start()
  write_json(store.root/"server.json",{"pid":os.getpid(),"port":args.port,"started":time.time()})
  print(f"Training Studio ready: http://127.0.0.1:{args.port}",flush=True)
  try:
    while not stop.wait(1):
      if child and child.poll() is not None:
        store.event("工作程序已退出；請查看 worker.log")
        child = None
  finally:
    server.shutdown()
    server.server_close()
    if child:
      child.terminate()
      try:
        child.wait(timeout=15)
      except subprocess.TimeoutExpired:
        child.kill()
        child.wait()


if __name__ == "__main__":
  main()
