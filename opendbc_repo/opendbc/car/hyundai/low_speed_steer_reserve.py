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
    self.reason = 'off'
    self.speed_weight = 0.

  def update(self, *, enabled, active, cs, base, model_frame, demand):
    self.speed_weight = 0.
    if model_frame is not None and model_frame != self.model_frame:
      self.model_frame = model_frame
      self.model_age = 0
    else:
      self.model_age += 1

    if not enabled:
      self.demand_frames = self.direction = 0
      self.reason = 'off'
      return base

    wheels = (cs.wheelSpeeds.fl, cs.wheelSpeeds.fr, cs.wheelSpeeds.rl, cs.wheelSpeeds.rr)
    speed = max(cs.vEgo, cs.vEgoRaw, *wheels)
    wheels_valid = (all(math.isfinite(v) for v in wheels) and min(wheels) >= .3
                    and max(wheels) - min(wheels) <= 3. / 3.6)
    healthy = (cs.canValid and not cs.canTimeout and not cs.steerFaultTemporary
               and not cs.steerFaultPermanent and not cs.steeringPressed and not cs.standstill
               and cs.gearShifter == "drive" and math.isfinite(cs.steeringTorque)
               and abs(cs.steeringTorque) <= 250)
    eligible = (enabled and active and healthy and 0 < base < RESERVE_MAX
                and math.isfinite(cs.vEgo) and math.isfinite(cs.vEgoRaw) and wheels_valid
                and 0.3 <= speed < END_SPEED and min(cs.vEgo, cs.vEgoRaw) >= 0
                and model_frame is not None and self.model_age <= MODEL_MAX_AGE_FRAMES and math.isfinite(demand))
    self.reason = ('off' if not enabled else 'inactive' if not active else
                   'can' if not cs.canValid or cs.canTimeout else
                   'fault' if cs.steerFaultTemporary or cs.steerFaultPermanent else
                   'driver' if cs.steeringPressed or abs(cs.steeringTorque) > 250 else
                   'stationary' if cs.standstill or speed < 0.3 else
                   'gear' if cs.gearShifter != 'drive' else
                   'factory' if speed >= END_SPEED else
                   'model' if model_frame is None or self.model_age > MODEL_MAX_AGE_FRAMES else
                   'invalid' if not eligible else 'demand' if abs(demand) < .99 else 'qualifying')
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
    self.speed_weight = weight
    ceiling = int(base + (RESERVE_MAX - base) * weight)
    requested = max(base, math.ceil(abs(demand) * base))
    self.reason = 'ceiling' if requested > ceiling else 'taper' if weight < 1 else 'following'
    return min(ceiling, requested)

  def rates(self, *, requested, previous, base, up, down):
    """Demand-dependent slew, without changing the baseline mapping.

    Only qualified sustained demand can add slew. Reversals/driver overrides
    cancel eligibility in update(); no observation/profile value is used here.
    Integers match the transmitted CAN command resolution.
    """
    if self.speed_weight <= 0 or not all(math.isfinite(v) for v in (requested, previous, base, up, down)) or base <= 0:
      return up, down
    gap = abs(requested - previous)
    urgency = min(1., gap / max(base * .25, 1.))
    # A single change of direction must requalify; don't accelerate a reversal
    # while winding the previous command back through zero.
    if requested * previous < 0:
      return up, down
    weight = self.speed_weight * urgency
    # CarState speeds are float32; avoid an extra step-down at exact thresholds.
    return up + math.floor(max(0, 4-up) * weight + 1e-6), down + math.floor(max(0, 4-down) * weight + 1e-6)
