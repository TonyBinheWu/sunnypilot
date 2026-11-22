import numpy as np
import pytest

from openpilot.cereal import custom, log
from openpilot.selfdrive.controls.tests import test_desire_helper_stalk as stalk
from openpilot.selfdrive.modeld.driving_inputs import driver_maneuver_command, driving_model_inputs
from openpilot.selfdrive.modeld.jetlink.inputs import fill_inputs


def fixture():
  harness = stalk.TestDesireHelperStalkRequest()
  harness.setup_method()
  return harness


@pytest.mark.parametrize("turn", ["turn left", "turn right", "fork left", "fork right", "atc left", "atc right"])
@pytest.mark.parametrize("speed", [15., 90.])
def test_destination_changes_do_not_authorize_steering(turn, speed):
  route, no_route = fixture(), fixture()
  nav = custom.CarrotMan.new_message(atcType=turn, xTurnInfo=1, xDistToTurn=10)
  none = custom.CarrotMan.new_message()
  for i in range(120):
    route.carrot_man = driver_maneuver_command(nav if 10 <= i < 80 else none)
    no_route.carrot_man = driver_maneuver_command(none)
    for h in (route, no_route):
      h.update(left_blinker=False, v_kph=speed)
      assert h.helper.desire == log.Desire.none
      assert h.helper.lane_change_state == log.LaneChangeState.off
      assert h.helper.atc_active == 0
      assert not h.helper.auto_turn_signal


def test_opposing_exit_hint_preserves_driver_stalk_request():
  nav = custom.CarrotMan.new_message(atcType="fork right", xTurnInfo=4, xDistToTurn=45)
  for guidance in (nav, custom.CarrotMan.new_message()):
    h = fixture()
    h.carrot_man = driver_maneuver_command(guidance)
    h.start_and_cross()
    assert h.helper.desire == log.Desire.laneChangeLeft
    assert h.helper.lane_change_direction == log.LaneChangeDirection.left
    h.finish()


@pytest.mark.parametrize("side", ["LEFT", "RIGHT", "", "invalid"])
def test_only_explicit_manual_command_fields_survive(side):
  nav = custom.CarrotMan.new_message(atcType="turn right", xTurnInfo=2, xDistToTurn=30,
                                     carrotCmdIndex=77, carrotCmd="LANECHANGE", carrotArg=side)
  cmd = driver_maneuver_command(nav)
  assert not cmd.atcType and not cmd.xTurnInfo and not cmd.xDistToTurn
  if side in ("LEFT", "RIGHT"):
    assert (cmd.carrotCmd, cmd.carrotArg, cmd.carrotCmdIndex) == ("LANECHANGE", side, 77)
  else:
    assert not cmd.carrotCmd


def test_destination_payload_cleared_every_frame_preserves_manual_desire_pulse():
  views = {key: np.ones(shape, dtype=np.float32) for key, shape in
           (("desire", 8), ("action_t", 2), ("traffic_convention", 2), ("nav_map", (256, 256)), ("navigation", 47))}
  previous = np.zeros(8, np.float32)
  for desire, expected in [(0, 0), (3, 1), (3, 0), (0, 0), (3, 1)]:
    views["navigation"].fill(1)
    views["nav_map"].fill(255)
    fill_inputs(views, driving_model_inputs(desire, False, .3, .275), previous)
    assert not views["navigation"].any() and not views["nav_map"].any()
    assert views["desire"][3] == expected and views["desire"].sum() == expected
    np.testing.assert_allclose(views["action_t"], [.3, .275])
    np.testing.assert_array_equal(views["traffic_convention"], [1, 0])
