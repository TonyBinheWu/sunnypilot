"""Exercise the observed lane horizon with the compiled production acados solver."""
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.selfdrive.controls.lib.lane_change_guard import HOLD_HORIZON_S, LaneChangeGuard, solution_in_lane
from openpilot.selfdrive.controls.lib.lateral_mpc_lib.lat_mpc import LateralMpc
from openpilot.selfdrive.modeld.constants import ModelConstants


@pytest.mark.parametrize('speed', [12., 30.])
@pytest.mark.parametrize('side', [-1, 1])
@pytest.mark.parametrize('bend', [-.0007, 0., .0007])
def test_unconfirmed_crossing_solves_inside_observed_current_lane(speed, side, bend):
  times = np.array(ModelConstants.T_IDXS)
  x = speed * times
  lx = np.array(ModelConstants.X_IDXS)
  lines = [NS(x=lx, y=bend*lx**2 + shift) for shift in (-5.4, -1.8, 1.8, 5.4)]
  y = bend*x**2 + side*np.clip(times-.4, 0., 2.)*1.65
  md = NS(frameId=0, position=NS(x=x, y=y, t=times), laneLines=lines, laneLineProbs=[.95]*4, laneLineStds=[.1]*4,
          meta=NS(driverConfirmedLaneChange='none', laneChangeDirection='none', laneChangeState='off'))
  guard = LaneChangeGuard()
  for frame in range(7):
    md.frameId = frame
    mode, center = guard.update(md, now=frame*.05, fresh=True, active=True, speed_ok=True)
  assert mode == 'hold'

  mpc = LateralMpc()
  horizon = int(np.searchsorted(times, HOLD_HORIZON_S, side='right'))
  mpc.set_weights(1., .1, 0., .05, 800., reference_points=horizon)
  # Analytic heading and yaw rate of the test lane. The lateral reference
  # itself comes from the guard, matching the planner's normal solver interface.
  yaw = np.arctan(2*bend*x)
  yaw_rate = 2*bend*speed / (1+(2*bend*x)**2)**1.5
  p = np.column_stack([np.full_like(x, speed), np.ones_like(x)])
  for _ in range(6):
    mpc.run(np.zeros(4), p, center, yaw, yaw_rate)
    assert mpc.solution_status == 0 and np.isfinite(mpc.cost)
    assert solution_in_lane(md, mpc.x_sol, horizon)
  near = slice(0, horizon)
  solved_x, solved_y = mpc.x_sol[near, 0], mpc.x_sol[near, 1]
  assert np.max(np.abs(solved_y - bend*solved_x**2)) < .65
