"""Passive low-speed command/response records. Never discovers or sets EPS limits.

Only bounded aggregate data is retained, with asynchronous/throttled Params writes.
No position, route, timestamps of trips, or driver identity is collected here.
"""
import json
import math

VERSION = 1
PROFILE_KEY = 'LowSpeedSteerObservations'
STATUS_KEY = 'LowSpeedSteerStatus'
REASONS = ('off', 'inactive', 'can', 'fault', 'driver', 'stationary', 'gear', 'factory', 'model', 'invalid',
           'demand', 'qualifying', 'following', 'taper', 'ceiling', 'request_cut', 'rate_or_yield')
PEAKS = ('requested', 'command', 'angle', 'angleRate')


def decode(raw, fingerprint):
  """Reject malformed, cross-car and incompatible records, never migrate limits."""
  try:
    if not raw or len(raw) > 8192:
      return None
    data = json.loads(raw)
    if data['version'] != VERSION or data['fingerprint'] != fingerprint or data['control'] != 'torque':
      return None
    stats = data['stats']
    if type(stats['samples']) is not int or not 0 <= stats['samples'] <= 2**31-1:
      return None
    for side in ('left', 'right'):
      for key in PEAKS:
        v = stats[side][key]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 <= v <= 100000:
          return None
    if set(stats['reasons']) - set(REASONS):
      return None
    if any(type(v) is not int or not 0 <= v <= 2**31-1 for v in stats['reasons'].values()):
      return None
    return data
  except (ValueError, TypeError, KeyError):
    return None


class SteeringObservations:
  def __init__(self, fingerprint, params, runtime):
    self.params, self.runtime = params, runtime
    self.data = {'version': VERSION, 'fingerprint': fingerprint, 'control': 'torque',
                 'stats': {'samples': 0, 'left': dict.fromkeys(PEAKS, 0), 'right': dict.fromkeys(PEAKS, 0), 'reasons': {}}}
    try:
      previous = decode(params.get(PROFILE_KEY), fingerprint)
      if previous:
        self.data['stats'] = previous['stats']
    except Exception:
      pass
    self.previous = None
    self.next_status = self.next_save = 0.
    self.dirty = False
    self.was_enabled = self.was_active = False

  def update(self, *, now, enabled, active, cs, requested, command, target_angle, base, ceiling, up, down, reason):
    values = (now, cs.vEgo, cs.vEgoRaw, cs.steeringAngleDeg, cs.steeringTorque, requested, command, target_angle, base, ceiling, up, down)
    if not all(math.isfinite(v) and abs(v) <= 1e12 for v in values):
      self.previous = None
      return
    angle, rate = cs.steeringAngleDeg, None
    if self.previous is not None:
      dt = now - self.previous[0]
      if .005 <= dt <= .05:
        rate = (angle - self.previous[1]) / dt
        if abs(rate) > 100000:
          rate = None
    self.previous = now, angle
    reason = reason if reason in REASONS else 'invalid'
    stats = self.data['stats']
    # Observe only this optional mode; no background profile collection when off.
    if enabled:
      stats['reasons'][reason] = min(2**31-1, stats['reasons'].get(reason, 0) + 1)
      self.dirty = True
      if (active and cs.canValid and not cs.canTimeout and not cs.steerFaultTemporary and not cs.steerFaultPermanent
          and not cs.steeringPressed and abs(cs.steeringTorque) <= 250 and cs.gearShifter == 'drive'
          and not cs.standstill and min(cs.vEgo, cs.vEgoRaw) >= 0 and .3 <= max(cs.vEgo, cs.vEgoRaw) < 40/3.6
          and reason not in ('model', 'invalid', 'request_cut')):
        stats['samples'] = min(2**31-1, stats['samples'] + 1)
        side = stats['left' if requested >= 0 else 'right']
        for key, value in zip(PEAKS, (requested, command, angle, rate)):
          if value is not None:
            side[key] = min(100000, max(side[key], abs(value)))
    stopped = (self.was_enabled and not enabled) or (self.was_active and not active)
    self.was_enabled, self.was_active = enabled, active
    if now >= self.next_status or stopped:
      self.next_status = now + 1.
      snapshot = dict(self.data, monotonic=now, enabled=enabled,
                      current={'reason': reason, 'requested': requested, 'command': command,
                               'targetAngle': target_angle, 'angle': angle, 'angleRate': rate,
                               'base': base, 'ceiling': ceiling, 'up': up, 'down': down})
      try:
        self.runtime.put_nonblocking(STATUS_KEY, json.dumps(snapshot, allow_nan=False))
      except Exception:
        pass
    if self.dirty and (now >= self.next_save or stopped):
      # Write the first aggregate promptly, then at most once/minute or on exit.
      self.next_save = now + 60.
      self.dirty = False
      try:
        self.params.put_nonblocking(PROFILE_KEY, json.dumps(self.data, allow_nan=False))
      except Exception:
        self.dirty = True
