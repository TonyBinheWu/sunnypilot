import ast
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from openpilot.cereal import log


def check(meta, *, left_bsd=False, right_bsd=False):
  source = Path(__file__).parents[1] / 'selfdrived.py'
  tree = ast.parse(source.read_text(encoding='utf-8'))
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SelfdriveD')
  method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'update_events')
  branch = next(n for n in method.body if isinstance(n, ast.If) and
                ast.unparse(n.test) == "self.sm['modelV2'].meta.laneChangeState == LaneChangeState.preLaneChange")
  wrapper = ast.parse('def run(self, CS): pass')
  wrapper.body[0].body = [branch]
  env = dict(LaneChangeState=log.LaneChangeState, LaneChangeDirection=log.LaneChangeDirection, EventName=log.OnroadEvent.EventName)
  exec(compile(ast.fix_missing_locations(wrapper), str(source), 'exec'), env)
  events = []
  env['run'](NS(sm={'modelV2': NS(meta=meta)}, events=NS(add=events.append)), NS(leftBlindspot=left_bsd, rightBlindspot=right_bsd))
  return events


@pytest.mark.parametrize('source', ['lane_completed', 'lane_cancelled', 'lane_unverified', 'lane_waiting_driver'])
@pytest.mark.parametrize('side', ['left', 'right'])
def test_ended_held_request_does_not_repeat_preparation_but_bsd_warning_is_preserved(source, side):
  meta = NS(laneChangeState=log.LaneChangeState.preLaneChange, laneChangeDirection=getattr(log.LaneChangeDirection, side), indicatorPrepareSource=source)
  assert check(meta) == []
  assert check(meta, **{side + '_bsd': True}) == [log.OnroadEvent.EventName.laneChangeBlocked]


def test_unknown_direction_never_becomes_a_right_instruction_and_new_requests_still_warn():
  meta = NS(laneChangeState=log.LaneChangeState.preLaneChange, laneChangeDirection=log.LaneChangeDirection.none, indicatorPrepareSource='')
  assert check(meta) == []
  for side in ('left', 'right'):
    meta.laneChangeDirection = getattr(log.LaneChangeDirection, side)
    expected = log.OnroadEvent.EventName.preLaneChangeLeft if side == 'left' else log.OnroadEvent.EventName.preLaneChangeRight
    assert check(meta) == [expected]
  meta.laneChangeState = log.LaneChangeState.laneChangeStarting
  assert check(meta) == [log.OnroadEvent.EventName.laneChange]
