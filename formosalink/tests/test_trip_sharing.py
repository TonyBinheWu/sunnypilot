import json
import time
from types import SimpleNamespace

from formosalink.tests.test_settings import Params
from openpilot.sunnypilot.formosalink.trips import CONSENT, JOURNAL, MAX_POINTS, TripRecorder, append_point, clear_sharing, shared_trips


class Sources(dict):
  def __init__(self):
    gps = SimpleNamespace(hasFix=True, latitude=25., longitude=121., horizontalAccuracy=6.)
    super().__init__(gpsLocation=gps, gpsLocationExternal=gps, carState=SimpleNamespace(canValid=True, vEgo=10.),
                     deviceState=SimpleNamespace(started=True))
    self.seen = self.valid = dict.fromkeys(self, True)
    self.logMonoTime = dict.fromkeys(self, time.monotonic_ns())


def test_offline_trip_recording_permission_and_identity():
  params, sm = Params(), Sources()
  recorder = TripRecorder(params)
  params.put("CurrentRoute", "route-one")
  recorder.sample(sm, 10, 1000)
  assert params.get(JOURNAL) is None and shared_trips(params, "owner", sm) == {"trip_sharing": False}
  params.put(CONSENT, "owner/grant")
  for i in range(6):
    sm["gpsLocation"].longitude += .0005
    recorder.sample(sm, 11+i, 1001+i)
  sm["deviceState"].started = False
  recorder.sample(sm, 17, 1007)
  info = shared_trips(params, "owner", sm)
  trip = json.loads(info["trip_history"][0])
  assert trip["route"] == "route-one" and trip["m"] == 50 and len(trip["points"]) == 6
  assert info["trip_fix"][2] == 6
  assert trip["last_fix"][:2] == trip["points"][-1] and trip["last_fix"][3] == 1006
  assert shared_trips(params, "new-owner", sm) == {"trip_sharing": False}
  sm["gpsLocation"].hasFix = False
  assert shared_trips(params, "owner", sm)["trip_fix"] is None
  clear_sharing(params)
  assert params.get(JOURNAL) is None
  params.put(CONSENT, "owner/new-grant")
  recorder.sample(sm, 18, 1008)
  assert shared_trips(params, "owner", sm)["trip_history"] == []


def test_track_limit_keeps_endpoints():
  points = []
  for i in range(800):
    append_point(points, [25+i/1000, 121+i/1000, 5])
  assert len(points) == MAX_POINTS and points[0] == [25, 121] and points[-1] == [25.799, 121.799]


def test_dashcam_trip_uses_gps_and_ignores_jitter():
  params, sm = Params(), Sources()
  params.put(CONSENT, "owner/grant")
  params.put("CurrentRoute", "dashcam")
  recorder = TripRecorder(params)
  sm["carState"].canValid = False
  recorder.sample(sm, 10, 1000)
  sm["gpsLocation"].latitude += .00001
  recorder.sample(sm, 11, 1001)
  assert recorder.routes[0]["m"] == 0
  sm["gpsLocation"].latitude += .00019
  recorder.sample(sm, 12, 1002)
  assert 22 < recorder.routes[0]["m"] < 23 and recorder.routes[0]["distance_known"]
