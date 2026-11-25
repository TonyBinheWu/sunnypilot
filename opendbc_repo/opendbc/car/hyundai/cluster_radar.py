import math

import numpy as np


def healthy_radar(errors):
  return not (errors.canError or errors.radarFault or errors.wrongConfig or errors.radarUnavailableTemporary)


class EV6ClusterCorners:
  """Measured adjacent-lane corner targets for the instrument cluster only."""

  def __init__(self):
    self.stamp = 0
    self.expires = 0
    self.previous = {}
    self.neighbors = {}

  def update(self, event, model, now):
    stamp = event.logMonoTime
    previous = self.previous if 0 < stamp - self.stamp <= 150_000_000 else {}
    self.expires = 0
    self.previous = {}
    self.neighbors = {}
    if stamp <= self.stamp or not 0 <= now - stamp <= 150_000_000:
      return
    self.stamp = stamp
    if not (event.valid and healthy_radar(event.liveTracks.errors)
            and model is not None and model.timestampEof and 0 <= now - model.timestampEof <= 250_000_000
            and len(model.laneLines) == len(model.laneLineProbs) == 4):
      return
    self.expires = min(stamp + 150_000_000, model.timestampEof + 250_000_000)

    lanes = {}
    for side, start in (("LF", 0), ("RF", 2)):
      boundaries = []
      for index in (start, start + 1):
        line = model.laneLines[index]
        x, y = list(line.x), list(line.y)
        if (model.laneLineProbs[index] >= 0.5 and len(x) == len(y) and len(x) >= 2
            and all(math.isfinite(v) for v in (*x, *y)) and all(a < b for a, b in zip(x, x[1:]))):
          boundaries.append((np.asarray(x), np.asarray(y)))
      if len(boundaries) == 2:
        lanes[side] = boundaries

    for p in event.liveTracks.points:
      source = str(p.radarSource)
      if source not in ("corner180", "corner235") or not p.measured:
        continue
      d, y = p.dRel, p.yRel
      # These sensors clip alongside/behind objects to zero longitudinal range.
      # A stationary return can also be roadside infrastructure.
      if not (1 <= d <= 110 and 0.1 <= abs(y) <= 12.7 and math.isfinite(p.vLead) and abs(p.vLead) > 2.5):
        continue
      side = "LF" if y > 0 else "RF"
      bounds = lanes.get(side)
      x = d + 1.52  # model camera reference
      if not bounds or not all(xs[0] <= x <= xs[-1] for xs, _ in bounds):
        continue
      left, right = (np.interp(x, xs, ys) for xs, ys in bounds)
      if not (2.4 <= right - left <= 5 and left + 0.3 < -y < right - 0.3):
        continue
      key = (source, p.trackId, side)
      self.previous[key] = (d, y)
      last = previous.get(key)
      if last and abs(d - last[0]) <= 5 and abs(y - last[1]) <= 1:
        if side not in self.neighbors or d < self.neighbors[side][0]:
          self.neighbors[side] = (d, abs(y))

  def fill(self, values, now):
    if self.stamp <= now <= self.expires:
      for side, (distance, lateral) in self.neighbors.items():
        if not values.get(f"{side}_DETECT"):
          values[f"{side}_DETECT"] = 1
          values[f"{side}_DETECT_DISTANCE"] = distance
          values[f"{side}_DETECT_LATERAL"] = lateral
