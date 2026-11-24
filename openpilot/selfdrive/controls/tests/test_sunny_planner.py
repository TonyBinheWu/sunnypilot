from types import SimpleNamespace as NS

import pytest

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib import upstream_planner as module


class Inputs(dict):
  def all_checks(self, names):
    return all(name in self for name in names)


def inputs():
  model = log.ModelDataV2.new_message()
  model.action.desiredAcceleration = -1.3
  model.action.shouldStop = True
  model.position.t, model.velocity.x, model.orientationRate.z = [1.], [25.], [.3]
  sm = Inputs(modelV2=model, carState=NS(vEgo=25., vCruise=110., aEgo=0., standstill=False),
              controlsState=NS(forceDecel=False, longControlState="pid"), liveParameters=NS(roll=0.),
              selfdriveState=NS(personality=NS(raw=1), enabled=True), radarState=log.RadarState.new_message(),
              carrotMan=NS(routeCurveKph=72., positionFixMonoTime=9_900_000_000), navInstruction=NS(speedLimit=15.))
  sm.logMonoTime = dict.fromkeys(sm, 10_000_000_000)
  return sm


@pytest.mark.parametrize("map_on,limit_on,expected,source", [
  (False, False, 30., "cruise"), (True, False, 20., "mapCurve"),
  (False, True, 15., "speedLimit"), (True, True, 15., "speedLimit"),
])
def test_independent_ceiling_inputs(map_on, limit_on, expected, source):
  sm = inputs()
  assert module.assisted_ceiling(sm, 30., map_on, limit_on) == (expected, source)
  sm["carrotMan"].positionFixMonoTime = 1
  sm.logMonoTime["navInstruction"] = 1
  assert module.assisted_ceiling(sm, 30., map_on, limit_on) == (30., "cruise")
  sm = inputs()
  assert module.assisted_ceiling(sm, 12., map_on, limit_on) == (12., "cruise")


@pytest.mark.parametrize("curve", [False, True])
def test_blended_model_brakes_with_optional_assists_off(monkeypatch, curve):
  monkeypatch.setattr(module, "Params", lambda: NS(get_bool=lambda key: key == "SunnyVisionCurve" and curve))
  cp = NS(openpilotLongitudinalControl=True, longitudinalActuatorDelay=.2, visionPlannerSetup="native")
  planner = module.LongitudinalPlanner(cp, sunny=True)
  sm = inputs()
  planner.update(sm)
  assert planner.output_should_stop
  assert planner.output_a_target <= -1.3 + 1e-6
  assert (planner.curve_speed.accel_offset < 0.) == curve
  out = {}
  planner.publish(sm, NS(send=out.__setitem__))
  assert out["longitudinalPlan"].valid
  assert out["longitudinalPlan"].longitudinalPlan.plannerProfile == "sunny"
  assert out["longitudinalPlan"].longitudinalPlan.cruiseTarget == 110.
  sm["modelV2"].action.desiredAcceleration = float("nan")
  planner.update(sm)
  planner.publish(sm, NS(send=out.__setitem__))
  assert not out["longitudinalPlan"].valid


def test_closing_lead_wins_even_with_model_requesting_acceleration(monkeypatch):
  monkeypatch.setattr(module, "Params", lambda: NS(get_bool=lambda _: False))
  planner = module.LongitudinalPlanner(NS(openpilotLongitudinalControl=True, longitudinalActuatorDelay=.2), init_v=25., sunny=True)
  sm = inputs()
  sm["modelV2"].action.desiredAcceleration = 1.
  lead = sm["radarState"].leadOne
  lead.status, lead.dRel, lead.vLead, lead.vLeadK, lead.vRel = True, 20., 7., 7., -18.
  lead.aLeadTau = 1.5
  planner.update(sm)
  assert planner.speed_reason == "lead0" and planner.output_a_target < 0.
  assert planner.output_should_stop


@pytest.mark.parametrize("missing", [-1., 255., float("nan")])
def test_missing_set_speed_never_requests_acceleration(monkeypatch, missing):
  monkeypatch.setattr(module, "Params", lambda: NS(get_bool=lambda _: False))
  planner = module.LongitudinalPlanner(NS(openpilotLongitudinalControl=True, longitudinalActuatorDelay=.2), sunny=True)
  sm = inputs()
  sm["carState"].vCruise = missing
  sm["modelV2"].action.desiredAcceleration = 1.
  planner.update(sm)
  out = {}
  planner.publish(sm, NS(send=out.__setitem__))
  plan = out["longitudinalPlan"].longitudinalPlan
  assert not plan.allowThrottle and plan.aTarget <= 0. and plan.cruiseTarget == 0.
