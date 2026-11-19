"""Protect the lateral reference from an unconfirmed lane crossing."""
import math
import time
import numpy as np

HOLD_HORIZON_S = 4.0


class LaneChangeGuard:
  def __init__(self):
    self.near_center = None
    self.side = 0
    self.candidate = 0
    self.since = 0.
    self.clear_since = None
    self.last_time = None
    self.last_frame = None

  def update(self, md, *, now, fresh, active, speed_ok):
    """Return a reference on the current lane or request handover. All distances are metres."""
    if not active:
      self.__init__()
      return 'off', None
    frame = md.frameId
    discontinuity = self.last_time is not None and not 0 < now - self.last_time <= .2
    if not fresh or discontinuity or (self.last_frame is not None and frame <= self.last_frame):
      self.candidate = 0
      self.clear_since = None
      self.last_time = now
      self.last_frame = frame
      return ('takeover' if self.side else 'off'), None
    self.last_frame, self.last_time = frame, now
    active_change = str(md.meta.laneChangeState) in ('laneChangeStarting', 'laneChangeFinishing')
    direction = str(md.meta.driverConfirmedLaneChange)
    authorized = 0
    if active_change and direction == str(md.meta.laneChangeDirection):
      authorized = {'left': 1, 'right': 2}.get(direction, 0)
    crossing, center, contained = lane_evidence(md)
    side = crossing
    released = bool(authorized and authorized == self.side)
    if released:
      self.side = 0
      self.near_center = None
    if side == authorized:
      side = 0
    if side != self.candidate:
      self.candidate, self.since = side, now
    if side and now - self.since >= .15:
      self.side = side
    if not self.side:
      self.near_center = None
      self.clear_since = None
      return ('released' if released else 'off'), None
    if center is None or not speed_ok or (self.near_center is not None and abs(center[0] - self.near_center) > .45):
      return 'takeover', None
    self.near_center = center[0]
    if not side and contained:
      if self.clear_since is None:
        self.clear_since = now
      elif now - self.clear_since >= .6:
        self.side = 0
        self.clear_since = None
        return 'released', None
    else:
      self.clear_since = None
    return 'hold', center


def lane_evidence(md):
  """Compare path and boundaries at equal forward distances, including on bends."""
  pos = md.position
  x, y, t = (np.asarray(v) for v in (pos.x, pos.y, pos.t))
  if (len(x) != 33 or len(y) != len(x) or len(t) != len(x) or
      not all(np.isfinite(v).all() for v in (x, y, t)) or np.any(np.diff(x) <= 0) or
      np.any(np.diff(t) <= 0) or t[0] > .3 or t[-1] < HOLD_HORIZON_S or len(md.laneLines) < 3 or
      len(md.laneLineProbs) < 3 or len(md.laneLineStds) < 3):
    return 0, None, False
  # Sustained crossing of a boundary by the predicted vehicle centre. Check
  # the near position is on the original side to reject relabelled lanes.
  query = np.interp([0., .7, 1.1, 1.5, 1.9, 2.3, 2.7, 3.], t, x)
  path = np.interp(query, x, y)
  boundaries = []
  crossing = 0
  safe = True
  for side, sign in ((1, -1), (2, 1)):
    line = md.laneLines[side]
    lx, ly = np.asarray(line.x), np.asarray(line.y)
    prob, std = md.laneLineProbs[side], md.laneLineStds[side]
    if (len(lx) != 33 or len(ly) != len(lx) or not np.isfinite(lx).all() or not np.isfinite(ly).all()
        or np.any(np.diff(lx) <= 0) or lx[0] > query[0] + .5 or lx[-1] < query[-1]
        or not math.isfinite(prob) or not .5 <= prob <= 1 or not math.isfinite(std) or not 0 <= std < .30):
      continue
    margin = sign * (path - np.interp(query, lx, ly))
    if margin[0] < 0 and np.any((margin[1:-1] >= .10) & (margin[2:] >= .15)):
      crossing = side
    safe &= bool(np.all(margin < -.25))
    if prob >= .75 and std <= .20:
      boundaries.append((lx, ly))
  if len(boundaries) != 2:
    return crossing, None, False
  (ax, ay), (bx, by) = boundaries
  # Only the near horizon constrains the MPC. Leave two extra points for
  # the centred yaw smoothing window. Do not invent a lane beyond its data.
  last = min(len(x) - 1, np.searchsorted(t, HOLD_HORIZON_S, side='right') + 2)
  if min(ax[-1], bx[-1]) < x[last] or max(ax[0], bx[0]) > x[0] + .5:
    return crossing, None, False
  samples = np.minimum(x, x[last])
  left, right = np.interp(samples, ax, ay), np.interp(samples, bx, by)
  width = right - left
  if (not left[0] < 0 < right[0] or np.any(width < 2.5) or np.any(width > 4.8) or
      np.max(np.abs(width - width[0])) > .85):
    return crossing, None, False
  return crossing, (left + right) * .5, safe


def solution_in_lane(md, solution, count):
  """Check the solved centre path stays between both observed boundaries."""
  x, y = solution[:count, 0], solution[:count, 1]
  if count < 2 or not np.isfinite(solution).all() or np.any(np.diff(x) <= 0):
    return False
  for index, sign in ((1, -1), (2, 1)):
    line = md.laneLines[index]
    if x[-1] > line.x[-1] or np.any(sign * (y - np.interp(x, line.x, line.y)) > -.15):
      return False
  return True


class LaneHoldControl:
  """Do not fall back to raw model curvature on loss of a required centre plan."""
  def __init__(self):
    self.holding = False
    self.takeover = False
    self.takeover_since = 0

  def update(self, plan, *, fresh, requested, parked):
    mode = str(plan.laneGuard)
    if parked:
      self.takeover = False
    elif requested and (mode == 'takeover' or (self.holding and mode == 'off') or
                        (self.holding and not fresh) or
                        (mode == 'hold' and (not fresh or not usable_hold(plan)))):
      self.takeover = True
    # The vehicle can toggle latEnabled on its own. After handover only a
    # confirmed stationary Park clears the inhibit; ACC can continue independently.
    if not self.takeover:
      self.takeover_since = 0
    elif not self.takeover_since:
      self.takeover_since = time.monotonic_ns()
    self.holding = requested and fresh and mode == 'hold' and not self.takeover
    return self.holding, self.takeover


def usable_hold(plan):
  from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N

  if not plan.useLaneLines or not plan.mpcSolutionValid:
    return False
  arrays = (plan.curvatures, plan.psis, plan.distances)
  return (all(len(a) == CONTROL_N and all(math.isfinite(v) for v in a) for a in arrays)
          and all(b > a for a, b in zip(plan.distances, list(plan.distances)[1:])))
