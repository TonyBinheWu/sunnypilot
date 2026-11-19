"""Read-only world observations. Distances refer to the front bumper, y positive right."""
from bisect import bisect_left
from itertools import islice
import math

TTL_NS = 300_000_000
TTL = TTL_NS / 1_000_000_000
RADAR_SOURCES = {"frontRadar", "corner180", "corner235"}
ERROR_FLAGS = ("canError", "radarFault", "wrongConfig", "radarUnavailableTemporary")


def lifetime(stamp_ns, now):
  age_ns = round(now * 1_000_000_000) - stamp_ns
  return (TTL_NS - age_ns) // 1_000_000 if stamp_ns > 0 and 0 <= age_ns < TTL_NS else 0


def path_beyond_edge(model):
  # Compare the predicted centre trajectory with the observed road edge at the
  # same longitudinal distance. Never extend an edge past its observed endpoint.
  path = model.position
  for i, (edge, std) in enumerate(islice(zip(model.roadEdges, model.roadEdgeStds), 2)):
    if not 0 <= std <= .45 or len(edge.x) != len(edge.y) or not 2 <= len(edge.x) <= 64:
      continue
    xs, ys = list(edge.x), list(edge.y)
    if not all(map(math.isfinite, xs + ys)) or any(b <= a for a, b in zip(xs, xs[1:])):
      continue
    hits = 0
    for x, y, t in islice(zip(path.x, path.y, path.t), 64):
      if not (.1 <= t <= 2 and 1 <= x <= 35 and math.isfinite(y) and xs[0] < x <= xs[-1]):
        hits = 0
        continue
      j = bisect_left(xs, x)
      limit = ys[j - 1] + (ys[j] - ys[j - 1]) * (x - xs[j - 1]) / (xs[j] - xs[j - 1])
      beyond = limit - y if i == 0 else y - limit
      hits = hits + 1 if beyond > max(.25, 2 * std) else 0
      if hits >= 2:
        return "left" if i == 0 else "right"
  return None


class ContactHistory:
  """Confirm distinct native measurements, even when a radar repeats a held slot."""
  def __init__(self):
    self.last = {}

  def confirm(self, contacts, now):
    current = {}
    confirmed = []
    for p in contacts:
      key = p["source"], p["nativeId"]
      stamp = p.pop("measurementNs")
      prior = self.last.get(key)
      ok = False
      if prior is not None:
        last_stamp, x, y, speed, was_confirmed = prior
        dt = (stamp - last_stamp) * 1e-9
        if dt == 0:
          ok = was_confirmed and (p["x"], p["y"], p["vRel"]) == (x, y, speed)
        elif 0 < dt < TTL:
          ok = abs(p["x"] - x - speed * dt) < 1.5 + 2 * dt and abs(p["y"] - y) < .8 + 6 * dt
      if lifetime(stamp, now):
        current[key] = stamp, p["x"], p["y"], p["vRel"], ok
        if ok:
          confirmed.append(p)
    self.last = current
    return confirmed


def world_observations(sm, now, sensor_now, history):
  # Python service envelopes use MONOTONIC. pandad CAN events and camerad EOF
  # use BOOTTIME, which includes suspend time on the vehicle.
  def remaining(key):
    return lifetime(sm.logMonoTime[key], now) if sm.seen[key] and sm.valid[key] else 0

  result = {"contacts": [], "signals": {}}
  radar = sm["liveTracks"]
  radar_ttl = remaining("liveTracks")
  if radar_ttl and not any(getattr(radar.errors, name) for name in ERROR_FLAGS):
    contacts = {}
    duplicates = set()
    for p in radar.points:
      source = str(p.radarSource)
      ttl = min(radar_ttl, lifetime(getattr(p, "measurementMonoTime", 0), sensor_now))
      if not (ttl and p.measured and source in RADAR_SOURCES):
        continue
      x, y, speed = p.dRel, -p.yRel, p.vRel
      if not all(map(math.isfinite, (x, y, speed))) or abs(y) > 20 or not .2 < x <= 75:
        continue
      key = (source, p.trackId)
      if key in contacts:
        duplicates.add(key)
      contacts[key] = {"source": source, "nativeId": str(p.trackId), "x": x, "y": y, "vRel": speed, "ttlMs": ttl,
                       "measurementNs": p.measurementMonoTime}
    result["contacts"] = sorted((v for k, v in contacts.items() if k not in duplicates),
                                key=lambda p: math.hypot(p["x"], p["y"]))[:48]

  result["contacts"] = history.confirm(result["contacts"], sensor_now)
  car = sm["carState"]
  car_ttl = remaining("carState")
  if car_ttl and car.canValid:
    for field in ("leftBlindspot", "rightBlindspot"):
      if getattr(car, field):
        result["signals"][field] = car_ttl

  # A radar-only indication of decreasing longitudinal separation. This makes
  # no assumption about the target's class, heading or future crossing point.
  closing = [p for p in result["contacts"] if p["source"] == "frontRadar" and abs(p["y"]) <= .75
             and p["vRel"] <= -2 and p["x"] <= -2 * p["vRel"]]
  if closing and car_ttl and car.canValid and str(car.gearShifter) == "drive" and car.vEgo >= 1:
    p = min(closing, key=lambda pt: pt["x"] / -pt["vRel"])
    result["closing"] = {**p, "ttlMs": min(car_ttl, p["ttlMs"])}

  model = sm["modelV2"]
  model_ttl = min(remaining("modelV2"), lifetime(model.timestampEof, sensor_now))
  lenses = {"road": ["road"], "wide": ["wide"], "roadWide": ["road", "wide"]}.get(str(model.visionCameraInputs))
  if model_ttl and str(model.visionCompute) == "usbGpu" and lenses:
    result["model"] = {"backend": "drivingModelUsbGpu", "cameras": lenses, "frame": model.frameId, "ttlMs": model_ttl}
    side = path_beyond_edge(model)
    if side:
      result["signals"]["pathBeyondLeftEdge" if side == "left" else "pathBeyondRightEdge"] = model_ttl

  plan = sm["longitudinalPlan"]
  plan_ttl = remaining("longitudinalPlan")
  if plan_ttl and plan.fcw:
    result["signals"]["plannerFcw"] = plan_ttl

  source = str(plan.longitudinalPlanSource)
  ttl = min(plan_ttl, remaining("radarState"), remaining("carControl"), car_ttl)
  if (ttl and car.canValid and sm["carControl"].longActive and plan.hasLead and source in ("lead0", "lead1")
      and not any(getattr(sm["radarState"].radarErrors, name) for name in ERROR_FLAGS)):
    lead = sm["radarState"].leadOne if source == "lead0" else sm["radarState"].leadTwo
    if lead.status and lead.radar and lead.radarTrackId >= 0:
      matches = [p for p in result["contacts"] if p["nativeId"] == str(lead.radarTrackId)
                 and abs(lead.dRel - p["x"]) < 2 and abs(lead.yRel + p["y"]) < .65]
      if len(matches) == 1:
        p = matches[0]
        result["following"] = {**p, "ttlMs": min(ttl, p["ttlMs"])}
  return result
