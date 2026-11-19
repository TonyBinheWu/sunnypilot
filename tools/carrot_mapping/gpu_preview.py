"""Read-only PC GPU replay for the production Carrot Web / Cockpit viewer."""
import argparse
import asyncio
import ipaddress
import json
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

from aiohttp import web

from openpilot.selfdrive.carrot.realtime.compact_state import encode_carrot_state_batch, encode_carrot_state_frame
from .gpu_scene_relay import GpuSceneRelay
from .gpu_workstation import WorkstationOccupancy

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "openpilot/selfdrive/carrot/web"
MODEL_HASH = "d477bac0f82ace6c8663b222d2c0c00987906a6939f545a5fdf60ef81138b787"
BASE = "/api/vision/gpu-scene"
SETTINGS = {"web_language": "zh-tw", "vision_environment_occupancy": True, "start_page": "carrot"}
PRIVATE = tuple(ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))


def private(value):
  ip = ipaddress.ip_address(value)
  if not any(ip in network for network in PRIVATE):
    raise argparse.ArgumentTypeError("expected a private LAN IPv4 address")
  return str(ip)


async def parked_state(request):
  ws = web.WebSocketResponse()
  await ws.prepare(request)
  await ws.send_json({"mode": "carrot-state-v1"})
  services = request.query.get("services", "").split(",")
  samples = {"carState": SimpleNamespace(vEgo=0., vEgoCluster=0., yawRate=0., gearShifter="park"),
             "carControl": SimpleNamespace(latActive=False, longActive=False), "selfdriveState": SimpleNamespace(enabled=False)}
  async def heartbeat():
    async for msg in ws:
      if msg.type == web.WSMsgType.TEXT and msg.data == '{"type":"ping"}':
        await ws.send_str('{"type":"pong"}')
  reader = asyncio.create_task(heartbeat())
  try:
    n = 0
    while not reader.done():
      await ws.send_bytes(encode_carrot_state_batch([encode_carrot_state_frame(k, v, n) for k, v in samples.items() if k in services]))
      n += 1
      await asyncio.sleep(.2)
  except ConnectionError:
    pass
  finally:
    reader.cancel()
    await asyncio.gather(reader, return_exceptions=True)
  return ws


def make_app(args, inference):
  relay = GpuSceneRelay()
  busy = asyncio.Lock()
  default_view = {"w": 960, "h": 540, "night": True, "yaw": 0., "pitch": 25., "distance": 9., "bottomFraction": 0.}
  view = dict(default_view)
  def local(request):
    if request.remote != "127.0.0.1":
      raise web.HTTPForbidden()

  @web.middleware
  async def access(request, handler):
    if request.remote not in ("127.0.0.1", args.viewer):
      raise web.HTTPForbidden()
    allowed_hosts = {f"{addr}:{args.port}" for addr in ("127.0.0.1", args.listen)}
    if request.host not in allowed_hosts or request.headers.get("Origin", "http://" + request.host) != "http://" + request.host:
      raise web.HTTPForbidden()
    return await handler(request)

  async def host(request):
    local(request)
    imports = {"imports":{"three":"/three/build/three.module.js","three/addons/":"/three/examples/jsm/"}}
    body = ('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>FORMOSA 工作站影片回放</title>'
            '<style>body{background:#141820;color:white;font:18px system-ui}canvas{max-width:90vw;max-height:70vh}</style>'
            '<p>工作站 GPU 回放 · 模擬停車</p><video controls muted playsinline width="320" src="/replay/clip"></video>'
            '<p id="status" role="status"></p><script type="importmap">'+json.dumps(imports)+'</script>'
            '<script type="module" src="/replay/render.js"></script></html>')
    return web.Response(text=body, content_type="text/html")

  async def replay_file(request):
    local(request)
    if request.path.endswith("config"):
      return web.json_response({"fx": args.fx, "fy": args.fy, "cx": args.cx, "cy": args.cy, "heightM": args.height_m,
                                "rpy": args.rpy, "view": view})
    return web.FileResponse(args.video if request.path.endswith("clip") else Path(__file__).with_name("gpu_replay.js"))

  async def infer(request):
    local(request)
    if busy.locked():
      raise web.HTTPTooManyRequests()
    if request.content_length != 224 * 126 * 4:
      raise web.HTTPBadRequest()
    async with busy:
      a, b, _ = await asyncio.to_thread(inference.infer_rgba, await request.read())
    return web.Response(body=a.astype("<f4", copy=False).tobytes()+b.astype("<f4", copy=False).tobytes())

  async def publish(request):
    local(request)
    received = time.monotonic()
    image = await request.read()
    try:
      age = float(request.headers["X-Age"]) + (time.monotonic()-received)*1000
      accepted = relay.publish(image, age, int(request.headers["X-Cells"]), int(request.headers["X-Raised"]))
    except (KeyError, ValueError):
      raise web.HTTPBadRequest()
    return web.Response(status=204 if accepted else 409)

  async def view_update(request):
    limits = {"w": (64, 4096), "h": (64, 4096), "yaw": (-360, 360), "pitch": (18, 82), "distance": (5, 26), "bottomFraction": (0, .45)}
    try:
      values = await request.json()
      if not isinstance(values, dict) or type(values.get("night")) is not bool or any(
          type(values.get(k)) not in (int, float) or not lo <= values[k] <= hi for k, (lo, hi) in limits.items()):
        raise ValueError
    except (ValueError, TypeError):
      raise web.HTTPBadRequest()
    view.update({k: values[k] for k in default_view})
    return web.Response(status=204)

  async def page(request):
    html = (ASSETS / ("index.html" if request.path == "/" else "cockpit.html")).read_text(encoding="utf-8")
    if request.path == "/":
      manifest = (ASSETS/"generated/asset-manifest.json").read_text(encoding="utf-8")
      html = html.replace('<script id="carrotAssetManifest" type="application/json"></script>',
                          '<script id="carrotAssetManifest" type="application/json">'+manifest+'</script>')
      boot = {"visionGpuScene": True, "webSettings": SETTINGS, "deviceLanguage": "zh-CHT", "intro": {"shouldShow": False}}
      html = html.replace("<head>", "<head><script>window.__CARROT_BOOTSTRAP__="+json.dumps(boot)+";</script>", 1)
    else:
      html = html.replace("</body>", '<script>const label=document.querySelector("header strong");if(label)label.textContent="GPU 影片回放";</script></body>')
    return web.Response(text=html, content_type="text/html", headers={"Cache-Control":"no-store"})

  async def info(request):
    answers = {"carrot_navi/capabilities":{"ok":True,"feature":"carrotNavi"}, "web_settings":{"settings":SETTINGS},
               "params_bulk":{"ok":True,"values":{}}, "settings/snapshot":{"ok":True,"settings":{},"values":{}},
               "navigation/destination":{"ok":True,"destination":None}}
    value = answers.get(request.match_info["name"])
    if value is None:
      raise web.HTTPNotFound()
    return web.json_response(value)

  app = web.Application(middlewares=[access], client_max_size=1048577)
  app.router.add_get("/render", host)
  app.router.add_get("/replay/{file:config|clip|render.js}", replay_file)
  app.router.add_post(BASE+"/infer", infer)
  app.router.add_post(BASE+"/publish", publish)
  app.router.add_post(BASE+"/view", view_update)
  app.router.add_get(BASE+"/frame", relay.read)
  app.router.add_get("/api/{name:.*}", info)
  app.router.add_get("/ws/compact_state", parked_state)
  app.router.add_get("/", page)
  app.router.add_get("/cockpit", page)
  for folder in ("build", "examples/jsm"):
    app.router.add_static("/three/"+folder, ASSETS/"node_modules/three"/folder)
  for folder in ("src", "css", "js", "assets", "generated", "vendor"):
    if (ASSETS/folder).is_dir():
      app.router.add_static("/"+folder, ASSETS/folder)
  return app


def main():
  p = argparse.ArgumentParser(description=__doc__)
  p.add_argument("model", type=Path)
  p.add_argument("video", type=Path, help="rectified front-camera recording")
  p.add_argument("--fx", type=float, required=True)
  p.add_argument("--fy", type=float, required=True)
  p.add_argument("--cx", type=float, required=True)
  p.add_argument("--cy", type=float, required=True)
  p.add_argument("--height-m", type=float, required=True)
  p.add_argument("--rpy", type=float, nargs=3, required=True, help="installation roll pitch yaw, radians")
  p.add_argument("--listen", type=private)
  p.add_argument("--viewer", type=private, help="allow this handset along with loopback")
  p.add_argument("--port", type=int, default=7000)
  p.add_argument("--adapter", type=int, default=0)
  args = p.parse_args()
  if bool(args.listen) != bool(args.viewer) or (args.viewer and args.listen == args.viewer):
    p.error("supply distinct --listen and --viewer LAN addresses together")
  if not args.video.is_file() or not all(0 < value < 20000 for value in (args.fx, args.fy, args.cx, args.cy)) or not .3 <= args.height_m <= 4:
    p.error("check the recording and calibration in video pixel units")
  with tempfile.TemporaryDirectory() as profile:
    inference = WorkstationOccupancy(args.model, MODEL_HASH, Path(profile)/"occupancy", args.adapter)
    try:
      web.run_app(make_app(args, inference), host=[v for v in ("127.0.0.1", args.listen) if v], port=args.port, access_log=None)
    finally:
      if inference.latencies:
        print("Executed kernels:", inference.verify_profile())


if __name__ == "__main__":
  main()
