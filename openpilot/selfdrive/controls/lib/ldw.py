import math

from openpilot.cereal import log
from openpilot.common.constants import CV


CAMERA_OFFSET = 0.04
LDW_MIN_SPEED = 31 * CV.MPH_TO_MS
LANE_DEPARTURE_THRESHOLD = 0.1
LEFT_MARGIN = 1.08 + CAMERA_OFFSET
RIGHT_MARGIN = 1.08 - CAMERA_OFFSET


class LaneDepartureWarning:
  def __init__(self):
    self.left = self.right = False
    self.last_sample = None
    self.last_frame_id = None
    self.quiet_until = 0.
    self.candidate = None
    self.since = 0.

  def update(self, now, modelV2, CS, CC, *, valid):
    self.left = self.right = False
    continuous = self.last_sample is not None and 0 < now - self.last_sample <= .2
    if not continuous:
      self.candidate = None
    if self.last_sample is None or now < self.last_sample:
      self.quiet_until = now + 5.
    self.last_sample = now
    if CS.leftBlinker or CS.rightBlinker:
      self.quiet_until = now + 5.
    old_frame = self.last_frame_id
    self.last_frame_id = modelV2.frameId
    if (not valid or not math.isfinite(now) or not math.isfinite(CS.vEgo) or CS.vEgo <= LDW_MIN_SPEED or now < self.quiet_until or
        (old_frame is not None and modelV2.frameId <= old_frame)):
      self.candidate = None
      return

    lines, probs = modelV2.laneLines, modelV2.laneLineProbs
    if len(lines) < 3 or len(probs) < 3 or not len(lines[1].y) or not len(lines[2].y):
      self.candidate = None
      return
    left, right = -lines[1].y[0], lines[2].y[0]
    if not CC.latActive:
      self.candidate = None
      prediction = modelV2.meta.desirePrediction
      if len(prediction) > log.Desire.laneChangeRight:
        self.left = bool(probs[1] > .5 and left < LEFT_MARGIN and prediction[log.Desire.laneChangeLeft] > LANE_DEPARTURE_THRESHOLD)
        self.right = bool(probs[2] > .5 and right < RIGHT_MARGIN and prediction[log.Desire.laneChangeRight] > LANE_DEPARTURE_THRESHOLD)
      return

    # The planner may intend to stay in lane even while tracking close to its edge.
    # Require agreement from both inner lines and sustained proximity on the same side.
    side = None
    if (.9 <= probs[1] <= 1. and .9 <= probs[2] <= 1. and
        2.6 <= left + right <= 4.2 and modelV2.meta.desire == log.Desire.none and
        modelV2.meta.laneChangeState == log.LaneChangeState.off):
      if left < LEFT_MARGIN:
        side = 'left'
      elif right < RIGHT_MARGIN:
        side = 'right'
    if side != self.candidate:
      self.candidate, self.since = side, now
    if side is not None and now - self.since >= .35:
      self.left, self.right = side == 'left', side == 'right'

  @property
  def warning(self) -> bool:
    return bool(self.left or self.right)
