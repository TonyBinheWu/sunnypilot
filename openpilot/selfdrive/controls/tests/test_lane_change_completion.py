from types import SimpleNamespace as NS

import pytest

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.desire_lib.lane_change_completion import LaneChangeCompletion
from openpilot.selfdrive.controls.tests.test_desire_helper_stalk import TestDesireHelperStalkRequest as StalkFixture


def cs(**changes):
  return NS(**dict(dict(canValid=True, canTimeout=False, trailerConnected=False, gearShifter='drive', vEgo=30., aEgo=0.,
                       steeringPressed=False, steeringTorque=0., blinkerLever=0, leftBlinker=False, rightBlinker=False), **changes))


def md(frame, left, right, confidence=1.):
  return NS(frameId=frame, laneLines=[NS(y=[v]) for v in (-5., left, right, 5.)], laneLineProbs=[1., confidence, confidence, 1.])


def crossing(direction):
  rows = [(-1.6, 1.6), (-.8, 2.4), (-.4, 2.8), (-2.2, 1.), (-1.6, 1.6)]
  if direction == 2:
    rows = [(-right, -left) for left, right in rows]
  return rows + [(-1.6, 1.6)] * 17


@pytest.mark.parametrize('direction', [1, 2])
def test_requires_crossing_and_stable_target_center_then_fires_once(direction):
  observer = LaneChangeCompletion()
  result = [observer.update(10 + n * .05, md(n, *row), cs(), direction, active=True, valid=True)
            for n, row in enumerate(crossing(direction))]
  assert sum(result) == 1
  assert not any(result[:16])


@pytest.mark.parametrize('failure', ['no_crossing', 'one_line', 'uncertain', 'stale', 'driver', 'inactive',
                                   'can_invalid', 'can_timeout', 'park', 'low_speed'])
def test_lamp_end_timer_noise_or_takeover_is_not_completion(failure):
  observer = LaneChangeCompletion()
  rows = [(-1.6, 1.6)] * 30 if failure == 'no_crossing' else crossing(1)
  results = []
  for n, row in enumerate(rows):
    if failure == 'one_line':
      row = row[0], 1.6
    model = md(0 if failure == 'stale' else n, *row, confidence=.1 if failure == 'uncertain' else 1.)
    results.append(observer.update(10 + n * .05, model,
      cs(steeringPressed=failure == 'driver', steeringTorque=-400., canValid=failure != 'can_invalid',
         canTimeout=failure == 'can_timeout', gearShifter='park' if failure == 'park' else 'drive',
         vEgo=0. if failure == 'low_speed' else 30.), 1, active=failure != 'inactive', valid=True))
  assert not any(results)


@pytest.mark.parametrize('direction', [1, 2])
def test_confirmed_target_center_ends_desire_even_if_model_probability_stays_high(direction):
  fixture = StalkFixture()
  fixture.setup_method()
  helper = fixture.helper
  helper.lane_change_state = log.LaneChangeState.laneChangeStarting
  helper.lane_change_direction = direction
  helper.maneuver_type = 'lane_change'
  helper.lane_change_ll_prob = .1
  helper.prev_desire_enabled = True
  car = cs(leftBlinker=direction == 1, rightBlinker=direction == 2)
  for n, row in enumerate(crossing(direction)):
    from unittest.mock import patch
    with patch('openpilot.selfdrive.controls.lib.desire_helper.time.monotonic', return_value=10 + n * .05):
      helper.update(car, md(n, *row), True, .99, fixture.carrot_man, NS(), indicator_valid=True)
  assert helper.lane_notice_source == 'lane_completed'
  assert helper.lane_notice_direction == direction
  assert helper.lane_change_state == log.LaneChangeState.preLaneChange
  assert helper.desire == log.Desire.none
  # Holding the same lamp is not permission for another lane.
  assert helper.next_lane_change


@pytest.mark.parametrize('direction', [1, 2])
def test_confirmed_completion_keeps_an_explicit_queued_driver_request(direction):
  from unittest.mock import patch
  fixture = StalkFixture()
  fixture.setup_method()
  helper = fixture.helper
  helper.lane_change_state = log.LaneChangeState.laneChangeStarting
  helper.lane_change_direction = direction
  helper.maneuver_type = 'lane_change'
  helper.lane_change_ll_prob = .1
  helper.prev_desire_enabled = True
  car = cs(leftBlinker=direction == 1, rightBlinker=direction == 2)
  # The real stalk logic has already admitted this explicit following request.
  # Use its internal constants rather than duplicating the encoding here.
  from openpilot.selfdrive.controls.lib.desire_lib.constants import BLINKER_LEFT, BLINKER_RIGHT
  helper.queued_lane_change = BLINKER_LEFT if direction == 1 else BLINKER_RIGHT
  for n, row in enumerate(crossing(direction)):
    with patch('openpilot.selfdrive.controls.lib.desire_helper.time.monotonic', return_value=10 + n * .05):
      helper.update(car, md(n, *row), True, .99, fixture.carrot_man, NS(), indicator_valid=True)
    if helper.lane_notice_source == 'lane_completed':
      break
  assert helper.lane_notice_source == 'lane_completed'
  assert helper.desire == log.Desire.none
  assert helper.lane_change_state == log.LaneChangeState.preLaneChange
  assert not helper.next_lane_change
  assert helper.queued_lane_change == (BLINKER_LEFT if direction == 1 else BLINKER_RIGHT)
