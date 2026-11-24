from types import SimpleNamespace as NS

import pytest

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.autospeed import Autospeed


def scene(accel, stop=False, yaw=0.):
  return NS(action=NS(desiredAcceleration=accel, shouldStop=stop), position=NS(t=[1.]),
            velocity=NS(x=[30.]), orientationRate=NS(z=[yaw]))


@pytest.mark.parametrize('mpc,model,source,expected', [
  (-2., -1., 'lead0', -2.), (1., -1.5, 'e2e', -1.5), (1., 1., 'cruise', .036),
])
def test_most_restrictive_candidate(mpc, model, source, expected):
  result = Autospeed(.05).update(scene(model), 0., 0, 31., 35., 0., mpc, 'lead0', False)
  assert result[0] == pytest.approx(expected)
  assert result[1:] == (source, False)


def test_stop_survives_other_winning_source_and_curve_reset():
  control = Autospeed(.05)
  accel, source, stop = control.update(scene(0., True, .2), 0., 3, 30., 35., 0., -2., 'lead1', False)
  assert (accel, source, stop) == (-2., 'lead1', True)
  assert control.curve.accel_offset < 0.
  control.reset(.2)
  assert control.curve.accel_offset == 0. and control.a_cruise == .2


def test_speed_ceiling_and_more_relaxed_gap():
  control = Autospeed(.05)
  for _ in range(100):
    accel, source, stop = control.update(scene(.5), 0., log.LongitudinalPersonality.moreRelaxed, 30., 25., 0., 1., 'lead0', False)
  assert (accel, source, stop) == (-.5, 'cruise', False)
