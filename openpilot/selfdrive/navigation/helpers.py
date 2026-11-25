import math
import time
from dataclasses import dataclass
from typing import Any

import numpy as np

# convert mapbox steps to valhalla enums the model was trained on
VALHALLA_COMMAND_COUNT = 46
VALHALLA_SIDED_TYPES = {  # (straight, right, left)
  'depart': (1, 2, 3), 'arrive': (4, 5, 6),
  'on ramp': (17, 18, 19), 'off ramp': (20, 20, 21), 'fork': (22, 23, 24),
  'roundabout': (26, 26, 26), 'rotary': (26, 26, 26), 'roundabout turn': (26, 26, 26),
  'exit roundabout': (27, 27, 27), 'exit rotary': (27, 27, 27), 'notification': (28, 28, 28),
}
VALHALLA_TURN_TYPES = {'straight': 8, 'slight right': 9, 'right': 10, 'sharp right': 11, 'uturn': 13,
                       'sharp left': 14, 'left': 15, 'slight left': 16}  # turn, continue, new name, end of road


def valhalla_type(maneuver_type: str, modifier: str) -> int | None:
  if maneuver_type not in {*VALHALLA_SIDED_TYPES, 'turn', 'continue', 'new name', 'end of road', 'merge'}:
    return None
  if maneuver_type == 'merge':
    return None  # Valhalla gives no maneuver at a merge, so the model never saw one
  if maneuver_type in VALHALLA_SIDED_TYPES:
    straight, right, left = VALHALLA_SIDED_TYPES[maneuver_type]
    return right if 'right' in modifier else left if 'left' in modifier else straight
  return VALHALLA_TURN_TYPES.get(modifier, 8)


def navigation_input(maneuvers: Any, traveled: float) -> np.ndarray:
  navigation = np.zeros(VALHALLA_COMMAND_COUNT + 1, dtype=np.float32)
  for maneuver in maneuvers:
    command, distance = valhalla_type(maneuver.type, maneuver.modifier), maneuver.distance - traveled
    if command is not None and command > 6 and math.isfinite(distance) and distance >= 0:
      navigation[command], navigation[-1] = 1, distance / 100
      break
  return navigation


def route_instruction(sm, now_ns, speed, *, require_geometry=False):
  """Return a causal instruction. TBT-only sources can operate without route geometry."""
  tbt_time = sm.logMonoTime['navInstructionCarrot']
  if not sm.valid['navInstructionCarrot'] or not tbt_time or not 0 <= now_ns - tbt_time < 2_000_000_000:
    return None
  route_time = sm.logMonoTime['navRoute']
  route = sm['navRoute']
  if route_time and (not sm.valid['navRoute'] or tbt_time < route.carrotRouteId or route_time > now_ns):
    return None
  instruction = sm['navInstructionCarrot']
  if not route_time or not len(route.coordinates):
    return None if require_geometry else instruction
  report = sm['mapRenderState']
  if (route.carrotRouteId and len(route.coordinates) >= 2 and now_ns - route_time < 5_000_000_000
      and sm.valid['mapRenderState'] and report.carrotRouteId == route.carrotRouteId and report.routeMatch == 'matched'
      and 0 <= now_ns - sm.logMonoTime['mapRenderState'] < 1_500_000_000
      and report.locationMonoTime and 0 <= now_ns - report.locationMonoTime < 2_000_000_000):
    # Do not pair a new turn with the previous step's approval between mapsd updates.
    approach = approach_maneuver(instruction.allManeuvers, speed, (now_ns - tbt_time) * 1e-9)
    if (approach[0] if approach else '') == report.approachManeuver:
      return instruction
  return None


def approach_maneuver(maneuvers, speed, age):
  """Use the nearest actionable step, at most 3.5 s ahead (12–90 m)."""
  if not math.isfinite(speed) or speed < 0. or not 0 <= age < 2.:
    return None
  horizon = min(90., max(12., 3.5 * speed))
  for turn in maneuvers:
    distance = turn.distance - speed * age
    if not math.isfinite(distance) or distance < 0.:
      continue
    if distance > horizon:
      return None
    if turn.type in ('depart', 'notification', 'new name', 'continue') and turn.modifier in ('', 'straight'):
      continue
    if turn.type in ('roundabout', 'rotary', 'roundabout turn', 'exit roundabout', 'exit rotary'):
      return 'roundabout', distance
    if turn.type in ('turn', 'end of road', 'fork', 'off ramp', 'on ramp', 'merge'):
      if turn.modifier == 'uturn':
        return 'uturn', distance
      side = turn.modifier.split()[-1] if turn.modifier else ''
      if side in ('left', 'right'):
        return ('turn ' if turn.type in ('turn', 'end of road') else 'branch ') + side, distance
    return None
  return None


def nearby_maneuver(sm, now_ns, speed):
  if not sm.logMonoTime.get('mapRenderState'):
    return None
  if route_instruction(sm, now_ns, speed, require_geometry=True) is not None:
    return sm['mapRenderState'].approachManeuver or None
  return None


def latest_gps_source(sm) -> str | None:
  """The service with the freshest usable GPS fix, or None."""
  now = time.monotonic()
  now_ns = int(now * 1e9)
  sources = [s for s in ('gpsLocation', 'gpsLocationExternal')
             if sm.valid[s] and sm[s].hasFix and 0 <= now - sm.recv_time[s] < 2
             and sm.logMonoTime[s] > 0 and 0 <= now_ns - sm.logMonoTime[s] < 2_000_000_000
             and all(math.isfinite(v) for v in (sm[s].latitude, sm[s].longitude, sm[s].bearingDeg, sm[s].speed))
             and abs(sm[s].latitude) <= 85.05112878 and abs(sm[s].longitude) <= 180]
  return max(sources, key=lambda s: sm.logMonoTime[s]) if sources else None


def gps_course(gps):
  if gps.speed >= 3. and 0 < gps.bearingAccuracyDeg <= 25. and 0 <= gps.bearingDeg < 360.:
    return gps.bearingDeg
  return None


@dataclass(frozen=True)
class NavigationPosition:
  latitude: float
  longitude: float
  bearing: float
  speed: float
  time: float
  fix_time: float
  course: float | None = None


def navigation_position(sm) -> NavigationPosition | None:
  """Retain Carrot's phone/navigation fusion, bounded by ORIGINAL fix freshness."""
  now = time.monotonic()
  carrot = sm['carrotMan']
  if (sm.valid['carrotMan'] and 0 <= now - sm.recv_time['carrotMan'] < .5
      and (not getattr(carrot, 'positionSource', '') or carrot.positionHeadingValid)
      and carrot.positionFixMonoTime > 0 and 0 <= now - carrot.positionFixMonoTime / 1e9 < 2
      and 0 <= now - carrot.positionMonoTime / 1e9 < .5
      and all(math.isfinite(v) for v in (carrot.xPosLat, carrot.xPosLon, carrot.xPosAngle, carrot.xPosSpeed))
      and abs(carrot.xPosLat) <= 85.05112878 and abs(carrot.xPosLon) <= 180):
    speed = max(0., carrot.xPosSpeed / 3.6)
    course = (carrot.xPosAngle if speed >= 3. and getattr(carrot, 'positionHeadingValid', False)
              and 0 <= carrot.xPosAngle < 360 else None)
    if course is not None and getattr(carrot, 'positionSource', '') == 'device':
      # Carrot propagates this device fix without its bearing accuracy. Check the original observation.
      source = latest_gps_source(sm)
      measured = gps_course(sm[source]) if source and abs(sm.logMonoTime[source] - carrot.positionFixMonoTime) < 350_000_000 else None
      if measured is None or abs((course - measured + 180.) % 360. - 180.) > 25.:
        course = None
    return NavigationPosition(carrot.xPosLat, carrot.xPosLon, carrot.xPosAngle, speed,
                              carrot.positionMonoTime / 1e9, carrot.positionFixMonoTime / 1e9, course)
  source = latest_gps_source(sm)
  if source is None:
    return None
  gps = sm[source]
  fix_time = sm.logMonoTime[source] * 1e-9
  return NavigationPosition(gps.latitude, gps.longitude, gps.bearingDeg, max(0., gps.speed), fix_time, fix_time, gps_course(gps))


class ParkedPosition:
  """Keep an observed parked position, never revive an old fix at startup.

  The original fix timestamp is retained. Fresh carState must continuously
  confirm Park and zero speed; leaving Park or losing that evidence clears
  the anchor before it can be reused. This is not moving dead reckoning.
  """
  def __init__(self):
    self.anchor = None
    self.parked_since = None
    self.checked = None
    self.held = False

  def update(self, sm, *, max_poll_gap=.5):
    now = time.monotonic()
    car = sm['carState']
    parked = (sm.valid['carState'] and sm.alive['carState']
              and 0 <= now - sm.recv_time['carState'] < .5
              and str(car.gearShifter) == 'park' and car.standstill
              and math.isfinite(car.vEgo) and abs(car.vEgo) < .01)
    continuous = self.checked is not None and 0 <= now - self.checked <= max_poll_gap
    if not parked or not continuous:
      self.anchor = None
      self.parked_since = now if parked else None
    self.checked = now
    position = navigation_position(sm)
    self.held = False
    if position is not None:
      if (parked and self.parked_since is not None and now - self.parked_since >= 1.
          and position.fix_time >= self.parked_since and position.speed < .1):
        self.anchor = NavigationPosition(position.latitude, position.longitude, position.bearing, 0., position.time, position.fix_time)
      else:
        self.anchor = None
      return position
    self.held = parked and self.anchor is not None
    return self.anchor if self.held else None
