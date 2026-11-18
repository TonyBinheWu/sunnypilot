"""Device-frame research observations. x forward, y right, z down, metres."""

import math

SCHEMA = "formosa-road-scene/v1"
CLASSES = frozenset(
  "person bicycle car motorcycle bus truck cat dog horse sheep cow elephant bear zebra giraffe bird".split()
) | {
  "traffic light",
  "stop sign",
  "traffic cone",
  "crosswalk",
}
MAX_CLOCK_GAP_NS = 200_000_000


def number(value, low, high):
  return type(value) in (int, float) and math.isfinite(value) and low <= value <= high


def near(clock, reference, limit=MAX_CLOCK_GAP_NS):
  return type(clock) is int and clock > 0 and abs(clock - reference) <= limit


def paint_code(value):
  return type(value) is int and 10 <= value <= 38 and value % 10 <= 8


def model_scene(sm, now_ns):
  model = sm["modelV2"]
  eof = model.timestampEof

  def fresh(name, limit=MAX_CLOCK_GAP_NS):
    return sm.valid[name] and near(sm.logMonoTime[name], eof, limit)

  if not sm.updated["modelV2"] or not fresh("modelV2") or not 0 <= now_ns - eof <= 500_000_000:
    return None
  car = sm["carState"]
  oem = fresh("carState") and car.canValid and not car.canTimeout and near(car.laneLineInfoMonoTime, eof)
  cal = sm["liveCalibration"]
  calibrated = fresh("liveCalibration", 2_000_000_000) and str(cal.calStatus) == "calibrated"
  lines = []
  for kind, curves, stds in (("lane", model.laneLines, model.laneLineStds), ("edge", model.roadEdges, model.roadEdgeStds)):
    for i, (curve, std) in enumerate(zip(curves, stds)):
      prob = model.laneLineProbs[i] if kind == "lane" and i < len(model.laneLineProbs) else None
      if not number(std, 0, 2) or (kind == "lane" and not number(prob, 0.5, 1)):
        continue
      points = []
      for x, y, z in zip(curve.x, curve.y, curve.z):
        if not (number(x, 0, 100) and number(y, -30, 30) and number(z, -10, 10)):
          break
        point = [round(x, 2), round(y, 2), round(z, 2)]
        if points and point[0] <= points[-1][0]:
          continue
        points.append(point)
      if len(points) < 2:
        continue
      code = (car.leftLaneLine if i == 1 else car.rightLaneLine) if kind == "lane" and i in (1, 2) and oem else None
      lines.append(
        dict(kind=kind, index=i, std=round(std, 3), probability=prob, oem=code if paint_code(code) else None, xyz=points)
      )
  targets = []
  if fresh("radarState"):
    radar = sm["radarState"]
    seen = set()
    for lead in (
      radar.leadOne,
      radar.leadTwo,
      getattr(radar, "leadLeft", None),
      getattr(radar, "leadRight", None),
      getattr(radar, "leadCutInRisk", None),
      *radar.leadsLeft,
      *radar.leadsRight,
      *radar.leadsCenter,
      *radar.leadsLeft2,
      *radar.leadsRight2,
      *radar.leadsCutIn,
    ):
      if lead is None or not lead.status or not number(lead.dRel, 0.1, 120) or not number(lead.yRel, -35, 35):
        continue
      xy = round(lead.dRel, 2), round(-lead.yRel, 2)
      if xy not in seen:
        seen.add(xy)
        targets.append(list(xy))
      if len(targets) == 48:
        break
  fix = None
  for name in ("gpsLocationExternal", "gpsLocation"):
    gps = sm[name]
    if (
      fresh(name)
      and gps.hasFix
      and number(gps.latitude, -85, 85)
      and number(gps.longitude, -180, 180)
      and number(gps.horizontalAccuracy, 0.01, 15)
    ):
      heading = (
        gps.bearingDeg
        if number(gps.speed, 2, 90) and number(gps.bearingAccuracyDeg, 0.01, 15) and number(gps.bearingDeg, 0, 360)
        else None
      )
      fix = dict(
        lat=gps.latitude,
        lon=gps.longitude,
        accuracy=gps.horizontalAccuracy,
        heading=heading,
        heading_std=gps.bearingAccuracyDeg if heading is not None else None,
        dt_ms=round((sm.logMonoTime[name] - eof) / 1e6),
      )
      break
  clocks = {
    name: sm.logMonoTime[name]
    for name in ("modelV2", "carState", "radarState", "liveCalibration", "gpsLocationExternal", "gpsLocation")
    if fresh(name, 2_000_000_000)
  }
  rpy = list(cal.rpyCalib) if calibrated else []
  height = list(cal.height) if calibrated else []
  metadata = dict(
    clocks=clocks,
    rpy=rpy if len(rpy) == 3 and all(number(v, -1, 1) for v in rpy) else None,
    camera_height_m=height[0] if height and number(height[0], 0.5, 3) else None,
    paint_clock=car.laneLineInfoMonoTime if oem else None,
  )
  return dict(
    frame=model.frameId, eof=eof, calibrated=calibrated, lines=lines, targets=targets, fix=fix, camera=[], meta=metadata
  )


def exact(obj, keys):
  return isinstance(obj, dict) and set(obj) == set(keys.split())


def seq(value, maximum):
  return isinstance(value, list) and len(value) <= maximum


def coords(value, bounds):
  return isinstance(value, list) and len(value) == len(bounds) and all(number(v, *b) for v, b in zip(value, bounds))


def check_camera(packet):
  if (
    not exact(packet, "frame eof detector objects")
    or not valid_frame(packet)
    or packet["detector"] not in ("efficientdet", "road")
    or not seq(packet["objects"], 32)
  ):
    raise ValueError("invalid camera observation")
  for o in packet["objects"]:
    if not exact(o, "kind score xy box") or o["kind"] not in CLASSES or not number(o["score"], 0.5, 1):
      raise ValueError("invalid classification")
    xy, box = o["xy"], o["box"]
    if (xy is None) == (box is None):
      raise ValueError("invalid observation space")
    if xy is not None and not coords(xy, [(0, 75), (-25, 25)]):
      raise ValueError("invalid ground point")
    if box is not None and (
      not coords(box, [(0, 1)] * 4) or min(box[2:]) <= 0 or box[0] + box[2] > 1.01 or box[1] + box[3] > 1.01
    ):
      raise ValueError("invalid image box")


def valid_frame(s):
  return type(s["eof"]) is int and 0 < s["eof"] < 2**63 and type(s["frame"]) is int and 0 <= s["frame"] < 2**32
