from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.lane_change_guard import LaneChangeGuard, LaneHoldControl
from openpilot.selfdrive.controls.tests.test_lane_model_speed_planner import inputs, make_planner
from openpilot.selfdrive.controls.tests.test_lateral_startup_control import control_fixture


def road(frame, side=0, *, authorized=0, poor=False, curve=.0007, velocity=30, center_offset=0.):
  md = log.ModelDataV2.new_message(frameId=frame)
  t = 10 * (np.arange(33) / 32.)**2
  x = velocity*t
  lx = 192 * (np.arange(33) / 32.)**2
  # A curve followed in lane does not cross its boundaries. The optional
  # lateral motion reaches the neighbouring lane by 2.5 seconds.
  center = center_offset + curve*x**2
  drift = (1 if side == 2 else -1 if side == 1 else 0) * np.clip(t - .4, 0., 2.) * 1.65
  md.position.x, md.position.y, md.position.t = x.tolist(), (center + drift).tolist(), t.tolist()
  md.laneLines = [dict(x=lx.tolist(), y=(center_offset+shift+curve*lx**2).tolist()) for shift in (-5.4, -1.8, 1.8, 5.4)]
  md.laneLineProbs = [1., .95 if not poor or side==1 else .1, .95 if not poor or side==2 else .1, 1.]
  md.laneLineStds = [.1]*4
  if authorized:
    md.meta.driverConfirmedLaneChange = md.meta.laneChangeDirection = authorized
    md.meta.laneChangeState = 'laneChangeStarting'
  return md


def run(guard, frame, side=0, **kw):
  return guard.update(road(frame, side, **kw), now=frame*.05, fresh=True, active=True, speed_ok=True)


@pytest.mark.parametrize('side', [1, 2])
@pytest.mark.parametrize('speed', [12, 30])
def test_city_and_highway_crossing_requires_matching_driver(side, speed):
  guard = LaneChangeGuard()
  for n in range(8):
    mode, center = run(guard, n, side, velocity=speed, authorized=3-side)
  assert mode == 'hold'
  assert abs(center[0]) < .01
  assert run(guard, 8, side, velocity=speed, authorized=side)[0] == 'released'
  assert run(guard, 9, side, velocity=speed, authorized=side)[0] == 'off'


def test_forecast_curve_spike_duplicate_and_old_state_cannot_authorize_a_crossing():
  guard = LaneChangeGuard()
  for n in range(15):
    md = road(n, side=2 if n == 5 else 0)
    md.meta.desirePrediction = [0., 0., 0., 1., 0., 0., 0., 0.]*4
    assert guard.update(md, now=n*.05, fresh=True, active=True, speed_ok=True)[0] == 'off'
  for n in range(15, 26):
    md = road(n, side=1)
    md.meta.laneChangeDirection, md.meta.laneChangeState = 'left', 'laneChangeStarting'
    mode, _ = guard.update(md, now=n*.05, fresh=True, active=True, speed_ok=True)
  assert mode == 'hold'
  assert guard.update(md, now=1.32, fresh=True, active=True, speed_ok=True)[0] == 'takeover'


@pytest.mark.parametrize('failure', ['line', 'relabel', 'speed', 'stale'])
def test_loss_of_credible_lane_requests_handover(failure):
  guard = LaneChangeGuard()
  for n in range(8):
    mode, _ = run(guard, n, 1, poor=failure=='line')
  if failure == 'line':
    assert mode == 'takeover'
    return
  md = road(8, 1, center_offset=.65 if failure=='relabel' else 0.)
  assert guard.update(md, now=.4, fresh=failure!='stale', active=True, speed_ok=failure!='speed')[0] == 'takeover'


def test_requires_stable_containment_before_returning_raw_path():
  guard = LaneChangeGuard()
  for n in range(6):
    run(guard, n, 2)
  modes = [run(guard, n)[0] for n in range(6, 23)]
  assert modes[0] == 'hold' and modes.count('released') == 1 and modes[-1] == 'off'


@pytest.mark.parametrize('failure', ['stale', 'nan', 'invalid', 'reset'])
def test_control_handover_is_latched_until_confirmed_park(failure):
  control = LaneHoldControl()
  plan = log.LateralPlan.new_message(laneGuard='hold', mpcSolutionValid=True, useLaneLines=True)
  plan.curvatures = plan.psis = [0.]*17
  plan.distances = list(range(17))
  assert control.update(plan,fresh=True,requested=True,parked=False) == (True,False)
  if failure == 'nan':
    plan.curvatures = [float('nan')]*17
  if failure == 'invalid':
    plan.mpcSolutionValid = False
  if failure == 'reset':
    plan.laneGuard = 'off'
  assert control.update(plan,fresh=failure!='stale',requested=True,parked=False) == (False,True)
  plan.laneGuard = 'off'
  for requested in (False, True):
    assert control.update(plan,fresh=True,requested=requested,parked=False) == (False,True)
  assert control.update(plan,fresh=True,requested=False,parked=True) == (False,False)


def test_planner_uses_observed_center_through_mpc_in_laneless_mode():
  sm = inputs(lane_speed=0)
  sm['carControl'].latActive = True
  sm['carState'].gearShifter, sm['carState'].standstill = 'drive', False
  planner = make_planner()
  clock = planner.update.__globals__['time']
  base = sm['modelV2']
  # Stand in only for the native solver in this routing test. Its output
  # must follow the input reference or the planner should request handover.
  def solve(x0, p, y, heading, yaw_rate):
    planner.lat_mpc.x_sol[:, 0] = list(sm['modelV2'].position.x)
    planner.lat_mpc.x_sol[:, 1] = y
  planner.lat_mpc.run = solve
  for frame in range(30):
    md = road(frame, 2)
    md.position.z = [0.]*33
    for target in ('velocity', 'orientation', 'orientationRate', 'acceleration'):
      for key, value in vars(getattr(base, target)).items():
        setattr(getattr(md, target), key, value.tolist())
    sm['modelV2'] = md
    now = frame*.05
    md.timestampEof = round(now*1e9)
    clock.monotonic = lambda: now
    sm.logMonoTime.update(dict.fromkeys(sm, round(now*1e9)))
    planner.update(sm, NS(atc_active=True))
  assert planner.lane_guard_mode == 'hold' and planner.lanelines_active
  assert planner.lat_mpc.reference_points < 33
  assert planner.y_pts[0] == pytest.approx(0.)
  planner.lat_mpc.run = lambda *args: planner.lat_mpc.x_sol.__setitem__((slice(4, None),1), 20.)
  md.frameId += 1
  now += .05
  sm.logMonoTime.update(dict.fromkeys(sm, round(now*1e9)))
  planner.update(sm, NS(atc_active=True))
  assert planner.lane_guard_mode == 'takeover'


def test_control_routes_hold_despite_disabled_lane_mode_then_inhibits_steering():
  import time
  control, step = control_fixture()
  control.sm['carrotMan'].vTurnSpeed = 0
  p = control.sm['lateralPlan']
  p.laneGuard, p.useLaneLines, p.mpcSolutionValid = 'hold', True, True
  p.psis = [0.]*17
  p.curvatures, p.distances = [.001]*17, list(range(17))
  p.modelMonoTime = control.sm.logMonoTime['lateralPlan'] = time.monotonic_ns()
  assert step()[0].latActive and control.lanefull_mode_enabled
  p.laneGuard = 'takeover'
  cc = step()[0]
  assert not cc.latActive and cc.actuators.torque == 0.
