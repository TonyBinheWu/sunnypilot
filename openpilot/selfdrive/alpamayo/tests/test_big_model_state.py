from openpilot.selfdrive.alpamayo.planner import GAP_FAIL_S, LOAD_TIMEOUT_S, STABLE_S, BigModelState

DT = .05


def run(state, start, seconds, usable, engaged):
  """Feed frames at 20 Hz; returns the last frame's result and time."""
  t, drives = start, False
  for _ in range(round(seconds/DT)):
    t += DT
    drives = state.update(t, usable, engaged)
  return drives, t


def active_state():
  state = BigModelState(0.)
  drives, t = run(state, 60., STABLE_S+.2, True, False)
  assert drives and state.state == BigModelState.ACTIVE
  return state, t


def test_loading_needs_stable_plans():
  state = BigModelState(0.)
  assert not state.update(1., False, False) and state.state == BigModelState.LOADING
  drives, t = run(state, 60., STABLE_S-.5, True, False)
  assert not drives and state.state == BigModelState.LOADING  # the small model's action stays
  drives, t = run(state, t, 4., False, False)  # first-use gap after the first plans
  assert state.state == BigModelState.LOADING
  drives, t = run(state, t, STABLE_S+.2, True, False)
  assert drives and state.state == BigModelState.ACTIVE


def test_load_timeout_fails_and_recovers_when_not_engaged():
  state = BigModelState(0.)
  assert not state.update(LOAD_TIMEOUT_S+1, False, False) and state.state == BigModelState.FAILED
  drives, t = run(state, LOAD_TIMEOUT_S+1, STABLE_S+1, True, True)
  assert not drives and state.state == BigModelState.FAILED  # never takes over while engaged
  drives, t = run(state, t, .1, True, False)
  assert drives and state.state == BigModelState.ACTIVE


def test_short_gap_disengaged_keeps_active_and_uses_the_small_model():
  state, t = active_state()
  drives, t = run(state, t, GAP_FAIL_S/2, False, False)
  assert not drives and state.state == BigModelState.ACTIVE
  assert state.update(t+DT, True, True) and state.state == BigModelState.ACTIVE


def test_long_gap_fails_until_disengaged():
  state, t = active_state()
  drives, t = run(state, t, GAP_FAIL_S+.2, False, True)
  assert not drives and state.state == BigModelState.FAILED
  drives, t = run(state, t, STABLE_S+1, True, True)
  assert not drives and state.state == BigModelState.FAILED
  drives, t = run(state, t, .1, True, False)
  assert drives and state.state == BigModelState.ACTIVE


def test_first_unusable_frame_during_engagement_latches_local_fallback():
  state, t = active_state()
  assert not state.update(t+DT, False, True)
  assert state.state == BigModelState.FAILED
  drives, t = run(state, t+DT, STABLE_S+1, True, True)
  assert not drives
  assert state.update(t+DT, True, False)
