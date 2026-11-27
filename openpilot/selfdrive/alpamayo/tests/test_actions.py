from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from openpilot.cereal import log
from openpilot.selfdrive.alpamayo.planner import PlanSelector


@pytest.mark.parametrize(('yaw_rate', 'sign'), [(.05, -1), (-.05, 1), (0., 0)])
def test_query_aligned_action_uses_carrot_control_conventions(yaw_rate, sign):
  selector = PlanSelector()
  base, speed = 4_000_000_000, 8.
  for i in range(-10, 16):
    selector.motion(base+i*50_000_000, speed, yaw_rate*i*.05)
  duration = np.arange(1, 65)*.1
  yaw = duration*yaw_rate
  x = speed*np.sin(yaw)/yaw_rate if sign else speed*duration
  y = speed*(1-np.cos(yaw))/yaw_rate if sign else np.zeros(64)
  for i in range(2):
    msg = log.Event.new_message()
    p = msg.init('alpamayoPlan')
    q = base+i*200_000_000
    p.queryMonoTime, p.readyMonoTime = q, q+220_000_000
    p.x, p.y, p.yaw = x.tolist(), y.tolist(), yaw.tolist()
    selector.receive(p, p.readyMonoTime)
  result = selector.candidate_action(base+450_000_000, speed, .3, .4, .2)
  assert result is not None
  assert np.sign(result['desiredCurvature']) == sign
  assert abs(result['desiredAcceleration']) < .01
  assert result['desiredVelocity'] == pytest.approx(8., abs=.01)
  assert result['shouldStop'] is False
  assert selector.candidate_action(base+450_000_000, 20., .3, .4, .2) is None


def test_longitudinal_guard_preserves_stronger_deceleration():
  # The real method is exercised in isolation from native MPC, which supplies the targets.
  import ast
  from pathlib import Path
  from openpilot.selfdrive.alpamayo.tests.test_carrot_port import advance, observations
  from openpilot.selfdrive.controls.lib.near_radar import ClosingLead
  file = Path(__file__).resolve().parents[2]/'controls/lib/longitudinal_planner.py'
  cls = next(n for n in ast.parse(file.read_text(encoding='utf8')).body if isinstance(n, ast.ClassDef) and n.name == 'LongitudinalPlanner')
  method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'apply_near_radar')
  sm = observations()
  sm.update(carControl=SimpleNamespace(longActive=True), selfdriveState=SimpleNamespace(enabled=True))
  planner = SimpleNamespace(near_radar=ClosingLead(), CP=SimpleNamespace(openpilotLongitudinalControl=True),
                            coasting=Mock(), coasting_target=1., output_a_target=.4,
                            output_v_target_now=5., output_j_target_now=.2, signal_constraint='')
  ns = {'boot_time_ns': lambda: sm.logMonoTime['radarState']}
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(file), 'exec'), ns)
  for i in range(3):
    advance(sm, 4_000_000_000+i*50_000_000)
    ns['apply_near_radar'](planner, sm, False)
  assert (planner.output_a_target, planner.output_v_target_now, planner.coasting_target) == (0., 3., 0.)
  planner.output_a_target = -2.
  ns['apply_near_radar'](planner, sm, False)
  assert planner.output_a_target == -2.
  sm['carState'].gasPressed = True
  planner.output_a_target = .3
  ns['apply_near_radar'](planner, sm, False)
  assert planner.output_a_target == .3 and planner.near_radar.count == 0
