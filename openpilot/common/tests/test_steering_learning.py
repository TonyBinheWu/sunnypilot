import math
from types import SimpleNamespace as NS

from openpilot.common.steering_learning import LearningReader, number, section


class Params(dict):
  # Deliberately provides no write/reset methods.
  def get(self, key):
    return super().get(key)


class Sm(dict):
  def __init__(self, seen=True):
    super().__init__(liveDelay=NS(calPerc=80, status='unestimated', lateralDelay=.3, lateralDelayEstimate=.153, validBlocks=4),
                     liveTorqueParameters=NS(calPerc=56, liveValid=False, useParams=True, latAccelFactorFiltered=2.5,
                       frictionCoefficientFiltered=.1, totalBucketPoints=5560, latAccelFactorRaw=2.75, frictionCoefficientRaw=.084))
    self.seen = dict.fromkeys(self, seen)
    self.valid = dict.fromkeys(self, True)
    self.recv_time = dict.fromkeys(self, 99.5)


def test_progress_is_distinct_from_validation_and_applied_values():
  reader = LearningReader(Params(), now=lambda: 100.)
  status = reader.snapshot(Sm())
  assert status['delay']['progress'] == 80
  assert status['delay']['status'] == 'learning'
  assert status['delay']['applied'] == .3
  assert status['delay']['estimate'] == .153
  assert status['torque']['progress'] == 56
  assert status['torque']['status'] == 'learning'
  assert status['torque']['samples'] == 5560


def test_expired_data_retains_history_but_never_claims_live():
  reader = LearningReader(Params(), now=lambda: 103.)
  result = reader.snapshot(Sm())
  assert result['delay']['source'] == result['torque']['source'] == 'stale'
  assert result['torque']['progress'] == 56


def test_invalid_transport_and_future_timestamps_are_not_live():
  sm = Sm()
  sm.valid['liveDelay'] = False
  sm.recv_time['liveTorqueParameters'] = 101.
  result = LearningReader(Params(), now=lambda: 100.).snapshot(sm)
  assert result['delay']['source'] == result['torque']['source'] == 'stale'


def test_missing_data_does_not_invent_zero_percent():
  result = LearningReader(Params(), now=lambda: 100., cache_loader=lambda: {}).snapshot(Sm(False))
  assert result['delay']['progress'] is None
  assert result['torque']['source'] == 'unavailable'


def test_saved_data_is_labeled_and_cache_reads_are_throttled():
  clock, calls = [100.], []
  def cache():
    calls.append(1)
    return {'liveDelay': {'calPerc': 80, 'status': 'unestimated', 'lateralDelay': .3}}
  reader = LearningReader(Params(), now=lambda: clock[0], cache_loader=cache)
  for _ in range(3):
    assert reader.snapshot(Sm(False))['delay']['source'] == 'cached'
  assert len(calls) == 1
  clock[0] += 6.
  reader.snapshot(Sm(False))
  assert len(calls) == 2


def test_custom_settings_are_displayed_instead_of_claiming_learner_values_apply():
  params = Params(SteerActuatorDelay=b'20', LateralTorqueCustom=b'1', LateralTorqueAccelFactor=b'2600', LateralTorqueFriction=b'70')
  result = LearningReader(params, now=lambda: 100.).snapshot(Sm())
  assert result['delay']['custom'] and result['delay']['applied'] == .2
  assert result['torque']['custom'] and result['torque']['factor'] == 2.6
  assert math.isclose(result['torque']['friction'], .07)


def test_unsupported_torque_does_not_claim_active_learning():
  assert section('liveTorqueParameters', {'calPerc': 80, 'liveValid': True, 'useParams': False})['status'] == 'unsupported'


def test_nonfinite_unknown_and_out_of_range_numbers_remain_unknown():
  for bad in [None, True, float('nan'), float('inf'), -1, '56']:
    assert number(bad) is None
  for bad in [-1, 101, float('nan')]:
    assert section('liveDelay', {'calPerc': bad})['progress'] is None


def test_cache_checks_vehicle_and_torque_identity():
  from openpilot.cereal import car, log
  def cp(fingerprint='KIA_SORENTO_2024', friction=.1):
    value = car.CarParams.new_message()
    value.carFingerprint = fingerprint
    tuning = value.lateralTuning.init('torque')
    tuning.friction, tuning.latAccelFactor = friction, 2.5
    return value.to_bytes()
  delay = log.Event.new_message()
  delay.init('liveDelay').calPerc = 80
  delay.liveDelay.status = 'unestimated'
  torque = log.Event.new_message()
  torque.init('liveTorqueParameters').calPerc = 56
  torque.liveTorqueParameters.useParams = True
  params = Params(CarParamsPrevRoute=cp(), CarParams=cp(), LiveDelay=delay.to_bytes(), LiveTorqueParameters=torque.to_bytes())
  result = LearningReader(params, now=lambda: 100.).snapshot(Sm(False))
  assert result['delay']['source'] == result['torque']['source'] == 'cached'
  params['CarParams'] = cp('KIA_EV6')
  result = LearningReader(params, now=lambda: 100.).snapshot(Sm(False))
  assert result['delay']['source'] == result['torque']['source'] == 'unavailable'
  params['CarParams'] = cp(friction=.15)
  result = LearningReader(params, now=lambda: 100.).snapshot(Sm(False))
  assert result['delay']['source'] == 'cached'
  assert result['torque']['source'] == 'unavailable'
