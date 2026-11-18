"""Confirm one observed lane crossing followed by stable target-lane centering."""
import math


class LaneChangeCompletion:
  def __init__(self):
    self.reset()

  def reset(self):
    self.direction = 0
    self.frame = None
    self.checked = None
    self.nearest = None
    self.crossed = False
    self.centered_since = None
    self.last_center = None
    self.delivered = False

  def update(self, now, md, cs, direction, *, active, valid):
    if (not active or not valid or direction not in (1, 2) or not cs.canValid or cs.canTimeout or
        cs.trailerConnected or str(cs.gearShifter) != 'drive' or
        not all(math.isfinite(v) for v in (cs.vEgo, cs.steeringTorque)) or cs.vEgo < 30 / 3.6 or
        (cs.steeringPressed and cs.steeringTorque * (1 if direction == 1 else -1) < 0)):
      self.reset()
      return False
    if direction != self.direction or self.checked is not None and not 0 < now - self.checked <= .15:
      self.reset()
    if self.frame == md.frameId:
      return False
    try:
      left, right = float(md.laneLines[1].y[0]), float(md.laneLines[2].y[0])
      probabilities = list(md.laneLineProbs[1:3])
      if (not all(math.isfinite(v) for v in (now, left, right, *probabilities)) or
          len(probabilities) != 2 or min(probabilities) < .5 or max(probabilities) > 1 or
          not left < 0 < right or not 2.5 <= right - left <= 4.8):
        self.reset()
        return False
    except (AttributeError, IndexError, TypeError, ValueError):
      self.reset()
      return False
    self.direction, self.frame, self.checked = direction, md.frameId, now
    selected = abs(left if direction == 1 else right)
    if self.nearest is None or selected < self.nearest[0]:
      self.nearest = selected, left, right
    near, old_left, old_right = self.nearest
    sign = -1 if direction == 1 else 1
    # Both boundaries must relabel together after approaching the original line.
    # A timer, one flashing lamp or one noisy boundary is not a completed change.
    self.crossed |= (near < 1. and selected - near > 1.5 and
                     min(sign * (left - old_left), sign * (right - old_right)) > 1.5 and
                     abs((right - left) - (old_right - old_left)) < .4)
    center = (left + right) * .5
    stable = self.crossed and abs(center) <= .35 and (self.last_center is None or abs(center - self.last_center) < .08)
    self.last_center = center
    self.centered_since = (now if self.centered_since is None else self.centered_since) if stable else None
    if self.centered_since is not None and now - self.centered_since >= .6 and not self.delivered:
      self.delivered = True
      return True
    return False
