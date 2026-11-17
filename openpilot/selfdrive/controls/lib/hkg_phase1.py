"""Opt-in comfort targets, upstream of unchanged actuator and Panda guards.

These are software comfort choices, not learned or measured EPS capabilities.
No new steering authority, emergency maneuver or stock-ACC button transmission.
"""
import math
from statistics import median

from openpilot.selfdrive.modeld.constants import ModelConstants

CURVE_HORIZON = 4.0
CURVE_LAT_ACCEL = 2.0  # m/s^2 comfort target, not a hardware limit
CURVE_APPROACH_DECEL = 1.2  # m/s^2, speed-envelope construction only
CURVE_RELEASE_ACCEL = 0.5  # m/s^2, release of this ceiling only
CURVE_DELAY = 0.5  # s preview margin, not an identified actuator delay
MIN_CURVE_SPEED = 5.0  # m/s; this feature never requests a stop


def low_speed_response_tau(target, previous, speed, tau):
  """Reduce only existing same-direction turn-in lag; no target amplification.

  Return/reversal keeps the original filter. This also benefits angle variants
  without changing their steering protocol, angle ceiling or authority ramp.
  """
  if (not all(math.isfinite(v) for v in (target, previous, speed, tau)) or tau <= 0.
      or speed < .3 or target * previous < 0. or abs(target) <= abs(previous)):
    return tau
  weight = min(1., max(0., (40. - speed * 3.6) / 10.))
  return tau * (1. - .4 * weight)


def smooth_curvature(target, previous, speed, dt, base_tau=0.):
  """Extra bounded smoothing for small highway corrections, not low-speed turns.

  Large changes receive less filtering; no deadband or held steering target.
  Existing curvature accel/jerk clipping must still run after this function.
  """
  if not all(math.isfinite(v) for v in (target, previous, speed, dt, base_tau)) or dt <= 0:
    return target
  weight = min(1., max(0., (speed * 3.6 - 40.) / 40.))
  correction = abs(target - previous) * speed**2
  small = max(0., min(1., 1. - correction / .3))
  tau = max(0., base_tau) + weight * (.02 + .06 * small)
  # Integrate the extra time constant into the existing filter. Cascading two
  # steps that both use the final previous output multiplies their gains and
  # can turn a small comfort filter into nearly a second of steering lag.
  alpha = 1. - math.exp(-dt / tau) if tau > 0. else 1.
  return previous + (target - previous) * alpha


def curve_speed_target(model, speed):
  """Spatial preview: v_allowed^2 = a_lat/|k| + 2*a_decel*distance.

  Use only the near horizon, reject malformed geometry and remove isolated
  one-node curvature spikes. Repeated frames must not qualify a new curve.
  """
  arrays = (model.position.x, model.position.y, model.position.z, model.velocity.x, model.orientationRate.z)
  if any(len(a) != ModelConstants.IDX_N for a in arrays):
    return None
  n = sum(t <= CURVE_HORIZON for t in ModelConstants.T_IDXS)
  # DynamicListReader supports integer indexing, not Python slices.
  values = tuple(tuple(a[i] for i in range(n)) for a in arrays)
  if not all(math.isfinite(v) for a in values for v in a):
    return None
  x, y, z, velocity, yaw = values
  distances, curves = [0.], []
  for i in range(n):
    if velocity[i] < 2. or abs(yaw[i] / velocity[i]) > .2:
      return None
    curves.append(abs(yaw[i] / velocity[i]))
    if i:
      step = math.sqrt(sum((a[i] - a[i-1])**2 for a in (x, y, z)))
      duration = ModelConstants.T_IDXS[i] - ModelConstants.T_IDXS[i-1]
      if step > max(5., max(velocity[i], velocity[i-1], speed) * duration * 2.):
        return None
      distances.append(distances[-1] + step)
  if distances[-1] < 1.:
    return None
  ceiling = math.inf
  # Interior samples require neighboring evidence, including both ends of the
  # preview. A one-node spike at the horizon must not trigger braking either.
  for i in range(1, n-1):
    curve = median(curves[i-1:i+2])
    if curve <= 1e-5 or distances[i] > speed * CURVE_HORIZON:
      continue
    turn_speed_sq = max(MIN_CURVE_SPEED**2, CURVE_LAT_ACCEL / curve)
    distance = max(0., distances[i] - speed * CURVE_DELAY)
    ceiling = min(ceiling, math.sqrt(turn_speed_sq + 2. * CURVE_APPROACH_DECEL * distance))
  return ceiling


class CurveSpeedEnvelope:
  def __init__(self):
    self.reset()

  def reset(self):
    self.last_frame = None
    self.repeat_age = 0.
    self.confirmations = 0
    self.ceiling = None
    self.reason = 'inactive'

  def update(self, cs, model, cruise, *, enabled, fresh, active, dt):
    healthy = (cs.canValid and not cs.canTimeout and not cs.steerFaultTemporary and not cs.steerFaultPermanent
               and not cs.gasPressed and not cs.brakePressed and not cs.steeringPressed
               and cs.gearShifter == 'drive' and not cs.standstill)
    if (not enabled or not fresh or not active or not healthy
        or not all(math.isfinite(v) for v in (cs.vEgo, cruise, dt))
        or cs.vEgo < MIN_CURVE_SPEED or cruise <= 0. or not 0. < dt <= .1):
      self.reset()
      return cruise
    frame = int(model.frameId)
    if self.last_frame is not None and frame <= self.last_frame:
      if frame < self.last_frame:
        self.reset()
        return cruise
      self.repeat_age += dt
      if self.repeat_age > .2:
        self.reset()
        self.reason = 'repeated_model'
        return cruise
      return min(cruise, self.ceiling) if self.ceiling is not None else cruise
    if self.last_frame is not None and frame != self.last_frame + 1:
      self.reset()
    self.repeat_age = 0.
    target = curve_speed_target(model, cs.vEgo)
    if target is None:
      self.reset()
      self.reason = 'invalid_model'
      return cruise
    self.last_frame = frame
    target = min(cruise, target)
    if target < min(cs.vEgo, cruise) - .2:
      self.confirmations += 1
    else:
      self.confirmations = 0
    if self.ceiling is None:
      if self.confirmations < 3:
        self.reason = 'qualifying' if self.confirmations else 'straight'
        return cruise
      self.ceiling = min(cruise, cs.vEgo)
    delta = target - self.ceiling
    step = CURVE_RELEASE_ACCEL * dt if delta > 0. else CURVE_APPROACH_DECEL * dt
    self.ceiling += max(-step, min(step, delta))
    self.ceiling = max(MIN_CURVE_SPEED, min(cruise, self.ceiling))
    self.reason = 'release' if delta > 0. else 'curve'
    if self.ceiling >= cruise:
      self.ceiling = None
    return min(cruise, self.ceiling) if self.ceiling is not None else cruise
