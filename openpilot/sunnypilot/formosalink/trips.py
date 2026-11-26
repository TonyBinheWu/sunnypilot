"""Local, explicitly shared trip summaries. Sample independently of the cloud connection."""
import json
import math
import threading
import time

from openpilot.sunnypilot.formosalink.telemetry import source_valid

CONSENT = "FormosaLinkTripConsent"
JOURNAL = "FormosaLinkTripJournal"
MAX_TRIPS = 12
MAX_POINTS = 64


def fix_at(sm):
  for name in ("gpsLocationExternal", "gpsLocation"):
    if not source_valid(sm, name, 4):
      continue
    gps = sm[name]
    if (gps.hasFix and -90 <= gps.latitude <= 90 and -180 <= gps.longitude <= 180 and 0 < gps.horizontalAccuracy <= 50):
      return [round(gps.latitude, 5), round(gps.longitude, 5), max(1, round(gps.horizontalAccuracy))]
  return None


def saved_routes(params, token):
  journal = params.get(JOURNAL)
  if not isinstance(journal, dict) or journal.get("grant") != token or not isinstance(journal.get("routes"), list):
    return []
  return [r for r in journal["routes"][-MAX_TRIPS:] if isinstance(r, dict) and isinstance(r.get("route"), str) and
          all(type(r.get(k)) in (int, float) and math.isfinite(r[k]) for k in ("start", "last", "m")) and isinstance(r.get("points"), list)]


def shared_trips(params, device_id, sm):
  token = params.get(CONSENT)
  if not device_id or not token or token.partition("/")[0] != device_id or not params.get_bool("FormosaLinkEnabled"):
    return {"trip_sharing": False}
  return {"trip_sharing": True, "trip_fix": fix_at(sm), "trip_history": [
    json.dumps(r, separators=(",", ":")) for r in saved_routes(params, token)]}


def clear_sharing(params):
  params.remove(CONSENT)
  params.remove(JOURNAL)


def append_point(points, fix):
  if not fix:
    return
  point = fix[:2]
  if points and max(abs(points[-1][i] - point[i]) for i in (0, 1)) < .00015:
    return
  points.append(point)
  if len(points) > MAX_POINTS:
    # Discard the least significant interior bend, retaining endpoints and turns.
    def area(i):
      a, b, c = points[i-1:i+2]
      return abs((b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]))
    points.pop(min(range(1, len(points)-1), key=area))


class TripRecorder:
  def __init__(self, params):
    self.params = params
    self.grant = None
    self.routes = []
    self.previous = None
    self.gps_anchor = None
    self.last_save = 0
    self.active = False

  def sample(self, sm, now, wall):
    grant = self.params.get(CONSENT) if self.params.get_bool("FormosaLinkEnabled") else None
    if grant != self.grant:
      self.routes = saved_routes(self.params, grant) if grant else []
      self.grant, self.previous, self.active = grant, None, False
      if not grant:
        self.params.remove(JOURNAL)
      self.gps_anchor = None
    if not grant or not source_valid(sm, "deviceState", 4):
      self.previous = self.gps_anchor = None
      return
    started = sm["deviceState"].started
    route = self.params.get("CurrentRoute") if started else None
    if not route:
      self.previous = self.gps_anchor = None
      if not started and self.active:
        self.active = False
        self.save(now)
      return
    if not self.routes or self.routes[-1]["route"] != route:
      self.routes = self.routes[-(MAX_TRIPS-1):] + [{"route": route[:100], "start": wall, "last": wall, "m": 0, "distance_known": False, "points": []}]
      self.previous = self.gps_anchor = None
      self.last_save = 0
    self.active = True
    trip = self.routes[-1]
    fix = fix_at(sm)
    car = sm["carState"]
    speed = car.vEgo if source_valid(sm, "carState", 2) and car.canValid else None
    delta = None
    if speed is not None and math.isfinite(speed) and 0 <= speed <= 140:
      if self.previous and 0 < now-self.previous[0] <= 4:
        delta = (now-self.previous[0])*(speed+self.previous[1])/2
      self.previous = (now, speed)
    else:
      self.previous = None
    if delta is None and fix and self.gps_anchor and 0 < (dt := now-self.gps_anchor[0]) <= 12:
      # A dashcam-only vehicle can have a valid GPS fix without a CAN speed.
      lat, lon, accuracy = self.gps_anchor[1]
      dlon = (fix[1]-lon+180) % 360 - 180
      meters = 111195 * math.hypot(fix[0]-lat, dlon*math.cos(math.radians((lat+fix[0])/2)))
      if meters <= 140*dt:
        delta = meters if meters > accuracy+fix[2] else 0
    if delta is not None:
      trip["m"] = round(trip["m"]+delta, 2)
      trip["distance_known"] = True
    if self.previous or not self.gps_anchor or not fix or delta != 0:
      self.gps_anchor = (now, fix) if fix else None
    trip["last"] = max(trip["start"], wall)
    if fix:
      append_point(trip["points"], fix)
      trip["last_fix"] = [*fix, wall]
    if not self.last_save or now - self.last_save >= 20:
      self.save(now)

  def save(self, now):
    if self.grant and self.params.get(CONSENT) == self.grant:
      self.params.put(JOURNAL, {"grant": self.grant, "routes": self.routes}, block=True)
      self.last_save = now


def run(stop):
  from openpilot.cereal import messaging
  from openpilot.common.params import Params
  params = Params()
  recorder = TripRecorder(params)
  sm = None
  while not stop.is_set():
    if params.get(CONSENT) and params.get_bool("FormosaLinkEnabled"):
      if sm is None:
        sm = messaging.SubMaster(["deviceState", "carState", "gpsLocation", "gpsLocationExternal"])
      sm.update(0)
      recorder.sample(sm, time.monotonic(), int(time.time()))  # noqa: TID251 - trip calendar time
    elif sm is not None:
      recorder.sample(sm, time.monotonic(), int(time.time()))  # noqa: TID251 - trip calendar time
      sm = None
    stop.wait(1)
  recorder.save(time.monotonic())


def start(stop):
  threading.Thread(target=run, args=(stop,), name="formosalink-trips", daemon=True).start()
