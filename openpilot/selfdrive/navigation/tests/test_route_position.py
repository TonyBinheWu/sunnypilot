import numpy as np
import pytest

from openpilot.selfdrive.navigation.route import RouteTracker


def test_rejected_gps_cannot_poison_progress_and_block_recovery():
  route = np.array([[127., 37.], [127., 37.01]])
  tracker = RouteTracker(route)
  expected = tracker.update_pose(127., 37.001)
  progress = tracker.progress
  # This far-away fix projects forward on the same long segment but must
  # never become the monotonic progress floor for later, correct fixes.
  assert tracker.update_pose(127.01, 37.008) is None
  assert tracker.progress == progress
  assert tracker.update_pose(127., 37.001) == expected


def test_invalid_first_position_does_not_seed_route_progress():
  tracker = RouteTracker(np.array([[127., 37.], [127., 37.01]]))
  assert tracker.update_pose(128., 38.) is None
  assert tracker.progress == -np.inf
  assert tracker.update_pose(127., 37.001) is not None


def test_valid_positions_preserve_original_projection_and_extrapolation():
  route = np.array([[127., 37.], [127., 37.01]])
  original, guarded = RouteTracker(route), RouteTracker(route)
  for lat in np.linspace(37., 37.005, 50):
    expected = original.pose(original.project(127., lat) + 3.)
    assert guarded.update_pose(127., lat, 3.) == pytest.approx(expected)
    assert guarded.progress == original.progress


def test_extrapolation_rejection_also_retains_previous_progress():
  tracker = RouteTracker(np.array([[127., 37.], [127., 37.01]]))
  tracker.update_pose(127., 37.001)
  progress = tracker.progress
  assert tracker.update_pose(127., 37.002, 100.) is None
  assert tracker.progress == progress


def test_return_leg_uses_course_at_startup_and_abstains_when_ambiguous():
  m = 1 / 111320.
  route = np.array([[0, 0], [0, 300*m], [8*m, 300*m], [8*m, 0]])
  tracker = RouteTracker(route)
  assert tracker.match_pose(3*m, 100*m) == ('ambiguous', None)
  assert tracker.progress == -np.inf
  state, pose = tracker.match_pose(3*m, 100*m, course=180.)
  assert state == 'matched' and pose[2] == pytest.approx(180.)
  assert tracker.progress > 400
  previous = tracker.progress
  assert tracker.match_pose(3*m, 80*m, course=0.) == ('headingConflict', None)
  assert tracker.progress == previous
  assert tracker.match_pose(3*m, 80*m, course=179.)[0] == 'matched'


def test_course_cannot_pull_fix_onto_distant_parallel_road():
  m = 1 / 111320.
  tracker = RouteTracker(np.array([[0, 0], [0, 300*m], [35*m, 300*m], [35*m, 0]]))
  assert tracker.match_pose(m, 100*m, course=180.) == ('headingConflict', None)
  assert tracker.progress == -np.inf


def test_equally_plausible_same_direction_laps_and_degenerate_route():
  m = 1 / 111320.
  tracker = RouteTracker(np.array([[0, 0], [0, 300*m], [100*m, 300*m], [100*m, 0], [5*m, 0], [5*m, 300*m]]))
  assert tracker.match_pose(2*m, 100*m, course=0.) == ('ambiguous', None)
  assert RouteTracker(np.zeros((3, 2))).match_pose(0., 0.) == ('offRoute', None)


@pytest.mark.parametrize('side,turn', [(1., 'turn right'), (-1., 'turn left')])
def test_nearby_turn_is_compared_to_route_geometry_only_when_unambiguous(side, turn):
  m = 1 / 111320.
  tracker = RouteTracker(np.array([[0, 0], [0, 120*m], [side*100*m, 120*m]]))
  assert tracker.match_pose(0, 100*m, course=0.)[0] == 'matched'
  other = 'turn left' if turn == 'turn right' else 'turn right'
  assert tracker.contradicts_turn(other, 20.)
  assert not tracker.contradicts_turn(turn, 20.)
  assert not tracker.contradicts_turn(other, 65.)
  assert not tracker.contradicts_turn('branch left', 20.)
