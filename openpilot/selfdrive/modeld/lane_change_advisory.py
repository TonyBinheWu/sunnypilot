"""Read-only advance notices. No desire, signal request or actuator writes."""
import math

from openpilot.selfdrive.controls.lib.desire_lib.indicator_observer import path_direction


def forecast_direction(md):
  try:
    forecast = md.meta.desirePrediction
    if len(forecast) != 32:
      return 0
    rows = [list(forecast[start:start + 8]) for start in (0, 8)]
    if any(not all(math.isfinite(p) and 0 <= p <= 1 for p in row) or abs(sum(row) - 1) > .05 for row in rows):
      return 0
    for direction, index in ((1, 3), (2, 4)):
      if all(row[index] >= .65 and row[index] == max(row) for row in rows):
        return direction
  except (AttributeError, TypeError, ValueError):
    pass
  return 0


class LaneChangeAdvisory:
  """Confirm a candidate on new model frames; never renew it on duplicates."""
  def __init__(self):
    self.frame = None
    self.checked = None
    self.candidate = None
    self.since = 0.

  def update(self, now, md, cs, *, valid, lateral_active, curvature=0., navigation=None):
    gap = self.checked is not None and not 0 < now - self.checked <= .2
    if gap:
      self.candidate = None
    if (not valid or not lateral_active or not math.isfinite(now) or not cs.canValid or cs.canTimeout or
        str(cs.gearShifter) != 'drive' or not math.isfinite(cs.vEgo) or cs.vEgo < 30 / 3.6 or
        cs.steeringPressed or cs.trailerConnected or (cs.leftBlinker and cs.rightBlinker)):
      self.candidate = None
      self.checked = now
      return None
    if self.frame == md.frameId:
      return None
    if self.frame is not None and md.frameId < self.frame:
      self.candidate = None
    self.frame, self.checked = md.frameId, now
    direction = forecast_direction(md)
    source = 'forecast_desire'
    if not direction:
      direction, source = path_direction(md, curvature), 'forecast_path'
    if not direction and navigation is not None:
      distance = navigation.maneuverDistance
      if (navigation.maneuverType in ('off ramp', 'fork') and math.isfinite(distance) and
          0 <= distance <= min(1500., max(250., cs.vEgo * 15.))):
        modifier = navigation.maneuverModifier
        direction = 1 if 'left' in modifier else 2 if 'right' in modifier else 0
        source = 'navigation_exit'
    candidate = (direction, source) if direction else None
    if candidate != self.candidate:
      self.candidate, self.since = candidate, now
    return candidate if candidate and now - self.since >= .3 else None
