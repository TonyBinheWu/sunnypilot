from types import SimpleNamespace as NS

import pytest

from openpilot.cereal import log
from openpilot.selfdrive.controls.tests.test_desire_helper_stalk import TestDesireHelperStalkRequest as StalkFixture


@pytest.mark.parametrize('direction', [log.LaneChangeDirection.left, log.LaneChangeDirection.right])
@pytest.mark.parametrize('phase', [log.LaneChangeState.laneChangeStarting, log.LaneChangeState.laneChangeFinishing])
@pytest.mark.parametrize('lamp_on', [False, True])
@pytest.mark.parametrize('pressed,opposing', [(True, True), (True, False), (False, True)])
def test_takeover_tracks_active_change_after_one_touch_lamp_ends(direction, phase, lamp_on, pressed, opposing):
  fixture = StalkFixture()
  fixture.setup_method()
  helper = fixture.helper
  helper.lane_change_state, helper.lane_change_direction = phase, direction
  helper.maneuver_type = 'lane_change'
  helper.lane_change_ll_prob = .4
  helper.prev_desire_enabled = True
  helper.queued_lane_change = 1 if direction == log.LaneChangeDirection.left else 2
  left = direction == log.LaneChangeDirection.left
  torque = (-354. if left else 354.) * (1 if opposing else -1)
  cs = NS(canValid=True, leftBlinker=lamp_on and left, rightBlinker=lamp_on and not left,
          vEgo=30., aEgo=0., trailerConnected=False, steeringPressed=pressed, steeringTorque=torque,
          blinkerLever=0)
  # Keep the model's completion probability high: cancellation must come from
  # the driver's takeover, not a simulated completed lane change.
  helper.update(cs, NS(), True, .5, fixture.carrot_man, NS())
  if pressed and opposing:
    assert helper.lane_change_state == log.LaneChangeState.off
    assert helper.lane_change_direction == log.LaneChangeDirection.none
    assert helper.desire == log.Desire.none
    assert helper.queued_lane_change == 0
    for _ in range(15):
      helper.update(cs, NS(), True, .5, fixture.carrot_man, NS())
      assert helper.desire == log.Desire.none
  else:
    assert helper.lane_change_state == phase
    assert helper.lane_change_direction == direction
