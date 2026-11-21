import time
from types import SimpleNamespace

import pytest

from openpilot.cereal import car, log
from openpilot.selfdrive.controls.lib.dec.dec import ExperimentalModeSelector


class Messages(dict):
  healthy = True

  def all_checks(self, services):
    return self.healthy and all(key in self for key in services)


def observation(endpoint=200., lead=False):
  model = log.ModelDataV2.new_message()
  model.position.x = [endpoint * i / 32 for i in range(33)]
  model.orientation.x = [0.] * 33
  radar = log.RadarState.new_message()
  radar.leadOne.status = lead
  sm = Messages(carState=car.CarState.new_message(vEgo=15., vCruise=70.),
                selfdriveState=log.SelfdriveState.new_message(experimentalMode=True),
                modelV2=model, radarState=radar)
  sm.recv_time = {'modelV2': time.monotonic()}
  sm.logMonoTime = {'modelV2': 1_000_000_000, 'carState': 1_000_000_000}
  return sm


def selector(*, radarless=False, longitudinal=True):
  cp = car.CarParams.new_message(radarUnavailable=radarless, openpilotLongitudinalControl=longitudinal)
  return ExperimentalModeSelector(cp, SimpleNamespace(crash_cnt=0))


@pytest.mark.parametrize('radarless,lead,endpoint,expected', [
  (True, False, 5., 'blended'), (False, False, 5., 'blended'),
  (False, True, 5., 'acc'), (True, False, 200., 'acc'),
])
def test_dec_uses_current_trajectory_and_lead(radarless, lead, endpoint, expected):
  mode = selector(radarless=radarless)
  sm = observation(endpoint, lead)
  assert mode.select(sm, True) == expected
  for _ in range(10):
    mode.select(sm, True)
  assert mode.controller._mode_manager.mode_duration == 1
  sm.logMonoTime['modelV2'] += 50_000_000
  mode.select(sm, True)
  assert len(mode.controller._lead_filter.history) == 2


def test_stock_acc_and_experimental_switches():
  sm = observation()
  assert selector(longitudinal=False).select(sm, True) == 'acc'
  mode = selector()
  assert mode.select(sm, True) == 'acc'
  assert mode.select(sm, False) == 'blended'
  assert mode.controller is None
  sm['selfdriveState'].experimentalMode = False
  assert mode.select(sm, True) == 'acc'


@pytest.mark.parametrize('fault', ['service', 'stale', 'partial', 'nan', 'unset', 'zero_stamp', 'late_delivery'])
def test_invalid_observation_resets_dec_and_valid_observation_recovers(fault):
  mode = selector()
  sm = observation()
  assert mode.select(sm, True) == 'acc'
  previous = mode.controller
  if fault == 'service':
    sm.healthy = False
  elif fault == 'stale':
    sm.recv_time['modelV2'] -= .5
  elif fault == 'partial':
    sm['modelV2'].orientation.x = [0.]
  elif fault == 'nan':
    sm['modelV2'].position.x = [float('nan')] * 33
  elif fault == 'unset':
    sm['carState'].vCruise = 255.
  elif fault == 'late_delivery':
    sm.logMonoTime['carState'] += 500_000_000
  else:
    sm.logMonoTime['modelV2'] = 0
  assert mode.select(sm, True) == 'blended'
  assert mode.controller is None
  assert mode.select(observation(), True) == 'acc'
  assert mode.controller is not previous


@pytest.mark.parametrize('delta', [-50_000_000, 500_000_000])
def test_clock_discontinuity_discards_prior_stop_history(delta):
  mode = selector()
  sm = observation(5.)
  assert mode.select(sm, True) == 'blended'
  sm = observation(200.)
  sm.logMonoTime['modelV2'] += delta
  sm.logMonoTime['carState'] += delta
  assert mode.select(sm, True) == 'acc'
