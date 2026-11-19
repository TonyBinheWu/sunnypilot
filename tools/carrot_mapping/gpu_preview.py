"""Read-only PC GPU replay for the production Carrot Web / Cockpit viewer."""
import argparse
import asyncio
import ipaddress
import json
import math
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

from aiohttp import web

from openpilot.selfdrive.carrot.realtime.compact_state import encode_carrot_state_batch, encode_carrot_state_frame
from .gpu_objects import INPUT, WorkstationObjects
from .gpu_scene_relay import GpuSceneRelay
from .gpu_workstation import WorkstationOccupancy

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "openpilot/selfdrive/carrot/web"
MODEL_HASH = "d477bac0f82ace6c8663b222d2c0c00987906a6939f545a5fdf60ef81138b787"
BASE = "/api/vision/gpu-scene"
SETTINGS = {"web_language": "zh-tw", "vision_environment_occupancy": True, "start_page": "carrot"}
PRIVATE = tuple(ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))


def valid_calibration(lens):
  def within(value, lower, upper):
    return type(value) in (float, int) and math.isfinite(value) and lower <= value <= upper
  return (all(within(lens.get(k), 1, 20000) for k in ("fx", "fy")) and
          all(within(lens.get(k), 0, lens.get(dim, 20000)) for k, dim in (("cx", "width"), ("cy", "height"))) and
          within(lens.get("heightM"), .3, 4) and isinstance(lens.get("rpy"), list) and len(lens["rpy"]) == 3 and
          all(within(a, -math.pi, math.pi) for a in lens["rpy"]) and
          all(within(lens.get(k, 0), -5, 5) for k in ("offsetX", "offsetY")))


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


def make_app(args, inference, lens_profiles=None):
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
                                "rpy": args.rpy, "view": view, "objects": isinstance(inference, WorkstationObjects),
                                "lenses": lens_profiles})
    return web.FileResponse(args.video if request.path.endswith("clip") else Path(__file__).with_name("gpu_replay.js"))

  async def infer(request):
    local(request)
    if busy.locked():
      raise web.HTTPTooManyRequests()
    if isinstance(inference, WorkstationObjects):
      if request.content_length != INPUT * INPUT * 4:
        raise web.HTTPBadRequest()
      async with busy:
        detections = await asyncio.to_thread(inference.detect, await request.read())
      return web.json_response(detections)
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
  p.add_argument("--fx", type=float)
  p.add_argument("--fy", type=float)
  p.add_argument("--cx", type=float)
  p.add_argument("--cy", type=float)
  p.add_argument("--height-m", type=float)
  p.add_argument("--rpy", type=float, nargs=3, help="installation roll pitch yaw, radians")
  p.add_argument("--listen", type=private)
  p.add_argument("--viewer", type=private, help="allow this handset along with loopback")
  p.add_argument("--port", type=int, default=7000)
  p.add_argument("--objects", action="store_true", help="use YOLOX-Nano object detection instead of the occupancy network")
  p.add_argument("--paired-profile", type=Path, help="calibration and crops for synchronized rectified road/wide images in one recording")
  p.add_argument("--adapter", type=int, default=0)
  args = p.parse_args()
  if bool(args.listen) != bool(args.viewer) or (args.viewer and args.listen == args.viewer):
    p.error("supply distinct --listen and --viewer LAN addresses together")
  if not args.video.is_file():
    p.error("recording not found")
  profiles = None
  if args.paired_profile:
    if not args.objects:
      p.error("paired replay requires --objects")
    profiles = json.loads(args.paired_profile.read_text(encoding="utf-8"))
    if not isinstance(profiles, dict) or set(profiles) != {"road", "wide"}:
      p.error("supply both road and wide camera profiles")
    for lens in profiles.values():
      if not isinstance(lens, dict) or not all(type(lens.get(key)) is int and lens[key] >= 0 for key in ("left", "top", "width", "height")):
        p.error("invalid calibrated crop")
      if min(lens["width"], lens["height"]) < 2 or not valid_calibration(lens):
        p.error("invalid paired camera calibration")
    r, w = profiles["road"], profiles["wide"]
    if (min(r["left"]+r["width"], w["left"]+w["width"]) > max(r["left"], w["left"]) and
        min(r["top"]+r["height"], w["top"]+w["height"]) > max(r["top"], w["top"])):
      p.error("the two camera crops overlap")
  elif not valid_calibration({"fx":args.fx, "fy":args.fy, "cx":args.cx, "cy":args.cy, "heightM":args.height_m, "rpy":args.rpy}):
    p.error("supply the calibrated focal lengths, principal point, height and roll/pitch/yaw")
  with tempfile.TemporaryDirectory() as profile:
    inference = (WorkstationObjects(args.model, Path(profile)/"objects", args.adapter) if args.objects else
                 WorkstationOccupancy(args.model, MODEL_HASH, Path(profile)/"occupancy", args.adapter))
    try:
      web.run_app(make_app(args, inference, profiles), host=[v for v in ("127.0.0.1", args.listen) if v], port=args.port, access_log=None)
    finally:
      if inference.profile is not None:
        print("Executed kernels:", inference.verify_profile())


if __name__ == "__main__":
  main()
