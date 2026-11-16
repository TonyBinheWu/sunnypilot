"""Optional torque headroom; all values retain the original CAN torque scale.

This is not an EPS capability estimate. The CAN driver/rate/safety limits remain
authoritative. Never multiply the baseline torque mapping by the reserve ceiling.
"""
import math

from opendbc.car.hyundai.values import HyundaiFlags

RESERVE_MAX = 409
FULL_SPEED = 30.0 / 3.6
END_SPEED = 40.0 / 3.6
DEMAND_FRAMES = 30  # 0.30 s at the existing 100 Hz control rate
MODEL_MAX_AGE_FRAMES = 25


def supports_reserve(cp):
  return (cp.brand == "hyundai" and bool(cp.flags & HyundaiFlags.CANFD)
          and not bool(cp.flags & HyundaiFlags.ANGLE_CONTROL)
          and cp.steerControlType == "torque" and cp.lateralTuning.which() == "torque")


class LowSpeedSteerReserve:
  def __init__(self):
    self.model_frame = None
    self.model_age = MODEL_MAX_AGE_FRAMES + 1
    self.demand_frames = 0
    self.direction = 0

  def update(self, *, enabled, active, cs, base, model_frame, demand):
    if model_frame is not None and model_frame != self.model_frame:
      self.model_frame = model_frame
      self.model_age = 0
    else:
      self.model_age += 1

    speed = max(cs.vEgo, cs.vEgoRaw)
    healthy = (cs.canValid and not cs.canTimeout and not cs.steerFaultTemporary
               and not cs.steerFaultPermanent and not cs.steeringPressed and not cs.standstill
               and cs.gearShifter == "drive" and math.isfinite(cs.steeringTorque)
               and abs(cs.steeringTorque) <= 250)
    eligible = (enabled and active and healthy and 0 < base < RESERVE_MAX
                and math.isfinite(cs.vEgo) and math.isfinite(cs.vEgoRaw)
                and 0.3 <= speed < END_SPEED and min(cs.vEgo, cs.vEgoRaw) >= 0
                and model_frame is not None and self.model_age <= MODEL_MAX_AGE_FRAMES and math.isfinite(demand))
    direction = 1 if demand > 0 else -1
    if eligible and abs(demand) >= 0.99:
      self.demand_frames = self.demand_frames + 1 if direction == self.direction else 1
      self.direction = direction
    else:
      self.demand_frames = 0
      self.direction = 0
    if self.demand_frames < DEMAND_FRAMES:
      return base

    weight = min(1.0, (END_SPEED - speed) / (END_SPEED - FULL_SPEED))
    return int(base + (RESERVE_MAX - base) * weight)
