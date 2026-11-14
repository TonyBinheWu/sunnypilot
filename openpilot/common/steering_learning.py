"""Read-only presentation of steering learners; never changes learner state."""
import math
import time

SERVICES = ('liveDelay', 'liveTorqueParameters')
FRESH_SECONDS = 2.0


def number(value, minimum=0., maximum=None):
  if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
    return None
  return value if value >= minimum and (maximum is None or value <= maximum) else None


def section(kind, data=None, *, source='unavailable', age=None, overrides=None):
  """Keep unknown progress unknown; reported progress is not elapsed time."""
  data, overrides = data or {}, overrides or {}
  result = {'source': source, 'ageSeconds': age, 'progress': number(data.get('calPerc'), maximum=100),
            'status': 'unavailable', 'custom': False}
  if not data:
    return result
  if kind == 'liveDelay':
    status = str(data.get('status', ''))
    result['status'] = {'estimated': 'valid', 'unestimated': 'learning', 'invalid': 'invalid'}.get(status, 'unavailable')
    override = number(overrides.get('delay'))
    result.update(applied=number(data.get('lateralDelay')), estimate=number(data.get('lateralDelayEstimate')),
                  blocks=number(data.get('validBlocks')), custom=bool(override and override > 0))
    if result['custom']:
      result['applied'] = override * .01
  else:
    supported = data.get('useParams') is True
    result['status'] = 'unsupported' if not supported else 'valid' if data.get('liveValid') is True else 'learning'
    custom = bool(number(overrides.get('torque')) and overrides['torque'] > 0)
    result.update(factor=number(data.get('latAccelFactorFiltered')), friction=number(data.get('frictionCoefficientFiltered')),
                  samples=number(data.get('totalBucketPoints')), custom=custom,
                  estimateFactor=number(data.get('latAccelFactorRaw')), estimateFriction=number(data.get('frictionCoefficientRaw')))
    if custom:
      factor, friction = number(overrides.get('factor')), number(overrides.get('friction'))
      result['factor'] = factor * .001 if factor is not None else None
      result['friction'] = friction * .001 if friction is not None else None
  return result


def extract(message, kind):
  fields = ('calPerc', 'status', 'lateralDelay', 'lateralDelayEstimate', 'validBlocks') if kind == 'liveDelay' else (
    'calPerc', 'liveValid', 'useParams', 'latAccelFactorFiltered', 'frictionCoefficientFiltered', 'totalBucketPoints',
    'latAccelFactorRaw', 'frictionCoefficientRaw')
  result = {}
  for key in fields:
    try:
      value = getattr(message, key)
      result[key] = value if isinstance(value, (int, float, bool)) else str(value)
    except (AttributeError, RuntimeError):
      pass
  return result


class LearningReader:
  """Uses an existing SubMaster. Cache reads are throttled and never written."""
  def __init__(self, params, *, now=time.monotonic, cache_loader=None):
    self.params, self.now = params, now
    self.cache_loader = cache_loader or self._load_cache
    self.cached = {}
    self.next_cache = 0.

  def _get(self, name):
    try:
      return self.params.get(name)
    except Exception:
      return None

  def _value(self, name):
    try:
      return float(self._get(name))
    except (TypeError, ValueError):
      return None

  def _load_cache(self):
    from openpilot.cereal import car, log
    previous, current = self._get('CarParamsPrevRoute'), self._get('CarParams') or self._get('CarParamsPersistent')
    if not previous or not current:
      return {}
    with car.CarParams.from_bytes(previous) as prev, car.CarParams.from_bytes(current) as cur:
      if prev.carFingerprint != cur.carFingerprint:
        return {}
      torque_compatible = prev.lateralTuning.which() == cur.lateralTuning.which() == 'torque'
      if torque_compatible:
        torque_compatible = (prev.lateralTuning.torque.friction == cur.lateralTuning.torque.friction and
                             prev.lateralTuning.torque.latAccelFactor == cur.lateralTuning.torque.latAccelFactor)
    result = {}
    for kind, key in [('liveDelay', 'LiveDelay'), ('liveTorqueParameters', 'LiveTorqueParameters')]:
      if kind == 'liveTorqueParameters' and not torque_compatible:
        continue
      raw = self._get(key)
      if raw and len(raw) <= 1024 * 1024:
        try:
          with log.Event.from_bytes(raw, traversal_limit_in_words=2**20) as event:
            if event.which() == kind:
              result[kind] = extract(getattr(event, kind), kind)
        except Exception:
          pass
    return result

  def snapshot(self, sm):
    now = self.now()
    overrides = {'delay': self._value('SteerActuatorDelay'), 'torque': self._value('LateralTorqueCustom'),
                 'factor': self._value('LateralTorqueAccelFactor'), 'friction': self._value('LateralTorqueFriction')}
    snapshots = {}
    for kind in SERVICES:
      data, age, source = None, None, 'unavailable'
      try:
        stamp = sm.recv_time[kind]
        seen = getattr(sm, 'seen', {}).get(kind, False)
        if seen:
          age = now - stamp
          data = extract(sm[kind], kind)
          source = 'live' if sm.valid[kind] and 0 <= age < FRESH_SECONDS else 'stale'
          age = max(0., age) if math.isfinite(age) else None
      except (KeyError, AttributeError, TypeError):
        pass
      if data is None:
        if now >= self.next_cache:
          try:
            self.cached = self.cache_loader()
          except Exception:
            self.cached = {}
          self.next_cache = now + 5.
        data = self.cached.get(kind)
        if data:
          source = 'cached'
      snapshots[kind] = section(kind, data, source=source, age=age, overrides=overrides)
    return {'ok': True, 'delay': snapshots['liveDelay'], 'torque': snapshots['liveTorqueParameters']}
