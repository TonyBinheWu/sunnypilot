from types import SimpleNamespace as NS

import pytest

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.ldw import LaneDepartureWarning


class Drive:
  def __init__(self):
    self.ldw = LaneDepartureWarning()
    self.model = NS(frameId=0, laneLines=[NS(y=[y]) for y in (-5., -1., 2.5, 6.)],
                    laneLineProbs=[1.] * 4, meta=NS(desire=log.Desire.none, laneChangeState=log.LaneChangeState.off,
                                                   desirePrediction=[0.] * 8))
    self.cs = NS(vEgo=27., leftBlinker=False, rightBlinker=False)
    self.cc = NS(latActive=True)
    self.tick(1.)

  def tick(self, now, *, valid=True, advance=True):
    if advance:
      self.model.frameId += 1
    self.ldw.update(now, self.model, self.cs, self.cc, valid=valid)
    return self.ldw.left, self.ldw.right


@pytest.mark.parametrize('right', [False, True])
def test_assisted_near_stripe_requires_continuous_same_side_evidence(right):
  d = Drive()
  if right:
    d.model.laneLines[1].y, d.model.laneLines[2].y = [-2.5], [1.]
  for i in range(7):
    assert d.tick(7. + i * .05) == (False, False)
  assert d.tick(7.36) == (not right, right)
  d.model.laneLines[1].y, d.model.laneLines[2].y = [-1.75], [1.75]
  assert d.tick(7.41) == (False, False)


@pytest.mark.parametrize('reason', ['invalid', 'frozen', 'gap', 'uncertain', 'wrong_width', 'no_lines',
                                    'signal', 'changing', 'turn', 'slow', 'nan'])
def test_invalid_or_intentional_departures_clear_warning(reason):
  d = Drive()
  for i in range(11):
    d.tick(7 + i * .05)
  assert d.ldw.warning
  if reason == 'uncertain':
    d.model.laneLineProbs[2] = .7
  elif reason == 'wrong_width':
    d.model.laneLines[2].y = [3.8]
  elif reason == 'no_lines':
    d.model.laneLines = []
  elif reason == 'signal':
    d.cs.leftBlinker = True
  elif reason == 'changing':
    d.model.meta.laneChangeState = log.LaneChangeState.laneChangeStarting
  elif reason == 'turn':
    d.model.meta.desire = log.Desire.turnRight
  elif reason == 'slow':
    d.cs.vEgo = 5.
  elif reason == 'nan':
    d.model.laneLines[1].y = [float('nan')]
  assert d.tick(8. if reason == 'gap' else 7.55, valid=reason != 'invalid', advance=reason != 'frozen') == (False, False)


def test_manual_ldw_requires_prediction_and_uses_five_seconds_of_real_time_after_signal():
  d = Drive()
  d.cc.latActive = False
  assert d.tick(7.) == (False, False)
  d.model.meta.desirePrediction[log.Desire.laneChangeLeft] = .3
  assert d.tick(7.1) == (True, False)
  d.cs.leftBlinker = True
  assert d.tick(7.15) == (False, False)
  d.cs.leftBlinker = False
  assert d.tick(12.14) == (False, False)
  assert d.tick(12.16) == (True, False)
