import math
import time
from dataclasses import dataclass
from openpilot.selfdrive.navigation.commands import (
  VALHALLA_COMMAND_COUNT as VALHALLA_COMMAND_COUNT,
  VALHALLA_SIDED_TYPES as VALHALLA_SIDED_TYPES,
  VALHALLA_TURN_TYPES as VALHALLA_TURN_TYPES,
  navigation_input as navigation_input,
  valhalla_type as valhalla_type,
)


def latest_gps_source(sm) -> str | None:
  """The service with the freshest usable GPS fix, or None."""
  now = time.monotonic()
  sources = [s for s in ('gpsLocation', 'gpsLocationExternal')
             if sm.valid[s] and sm[s].hasFix and 0 <= now - sm.recv_time[s] < 2
             and all(math.isfinite(v) for v in (sm[s].latitude, sm[s].longitude, sm[s].bearingDeg, sm[s].speed))
             and abs(sm[s].latitude) <= 85.05112878 and abs(sm[s].longitude) <= 180]
  return max(sources, key=lambda s: sm.logMonoTime[s]) if sources else None


@dataclass(frozen=True)
class NavigationPosition:
  latitude: float
  longitude: float
  bearing: float
  speed: float
  time: float
  fix_time: float


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
    return NavigationPosition(carrot.xPosLat, carrot.xPosLon, carrot.xPosAngle, max(0., carrot.xPosSpeed / 3.6),
                              carrot.positionMonoTime / 1e9, carrot.positionFixMonoTime / 1e9)
  source = latest_gps_source(sm)
  if source is None:
    return None
  gps = sm[source]
  return NavigationPosition(gps.latitude, gps.longitude, gps.bearingDeg, max(0., gps.speed), sm.recv_time[source], sm.recv_time[source])


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
