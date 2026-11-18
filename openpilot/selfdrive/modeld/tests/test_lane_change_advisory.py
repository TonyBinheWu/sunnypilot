from copy import deepcopy
from types import SimpleNamespace as NS

import pytest

from openpilot.selfdrive.modeld.lane_change_advisory import LaneChangeAdvisory, forecast_direction


def model(direction=1):
  row = [0.] * 8
  row[0], row[direction + 2] = .2, .8
  return NS(frameId=0, meta=NS(desirePrediction=row * 4))


def car(**changes):
  return NS(**dict(dict(canValid=True, canTimeout=False, gearShifter='drive', vEgo=28., steeringPressed=False,
                       trailerConnected=False, leftBlinker=False, rightBlinker=False), **changes))


def tick(observer, md, cs, n, **changes):
  md.frameId = n
  return observer.update(10 + n * .05, md, cs, valid=True, lateral_active=True, **changes)


@pytest.mark.parametrize('direction', [1, 2])
def test_forecast_is_confirmed_without_creating_any_signal_or_desire(direction):
  observer, md, cs = LaneChangeAdvisory(), model(direction), car()
  original = deepcopy(md.meta.__dict__)
  for n in range(6):
    assert tick(observer, md, cs, n) is None
  assert tick(observer, md, cs, 7) == (direction, 'forecast_desire')
  assert md.meta.__dict__ == original
  assert vars(cs) == vars(car())


@pytest.mark.parametrize('failure', ['nan', 'not_normalized', 'opposite_rows', 'turn'])
def test_ambiguous_or_non_lane_predictions_are_not_announced(failure):
  md = model()
  if failure == 'nan':
    md.meta.desirePrediction[3] = float('nan')
  elif failure == 'not_normalized':
    md.meta.desirePrediction[0] = .9
  elif failure == 'opposite_rows':
    md.meta.desirePrediction[11:13] = [0., .8]
  else:
    md.meta.desirePrediction = [0., .8, 0., .2, 0., 0., 0., 0.] * 4
  assert forecast_direction(md) == 0


def test_repeated_frame_and_polling_never_confirm_a_forecast():
  observer, md, cs = LaneChangeAdvisory(), model(), car()
  for n in range(30):
    assert observer.update(10 + n * .05, md, cs, valid=True, lateral_active=True) is None


@pytest.mark.parametrize('changes', [dict(gearShifter='park'), dict(vEgo=0), dict(canValid=False),
                                    dict(canTimeout=True), dict(steeringPressed=True),
                                    dict(leftBlinker=True, rightBlinker=True)])
def test_invalid_or_driver_override_inputs_revoke_notice(changes):
  observer, md = LaneChangeAdvisory(), model()
  for n in range(8):
    tick(observer, md, car(), n)
  assert tick(observer, md, car(**changes), 8) is None
  assert tick(observer, md, car(), 9) is None


def test_exit_is_nearby_guidance_not_an_assertion_that_a_lane_change_is_needed():
  observer, md, cs = LaneChangeAdvisory(), model(), car()
  md.meta.desirePrediction = []
  nav = NS(maneuverType='off ramp', maneuverModifier='right', maneuverDistance=39000.)
  for n in range(8):
    assert tick(observer, md, cs, n, navigation=nav) is None
  nav.maneuverDistance = 350.
  for n in range(8, 16):
    value = tick(observer, md, cs, n, navigation=nav)
  assert value == (2, 'navigation_exit')
  assert tick(observer, md, cs, 16) is None
