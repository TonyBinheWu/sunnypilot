import math
from types import SimpleNamespace

import pytest

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.upstream_planner import LongitudinalPlanner


@pytest.mark.parametrize("brand", ["toyota", "subaru", "hyundai", "honda"])
@pytest.mark.parametrize("owns_long", [True, False])
def test_vision_planning_without_a_radar_publisher(brand, owns_long):
  cp = SimpleNamespace(brand=brand, openpilotLongitudinalControl=owns_long, longitudinalActuatorDelay=.2)
  planner = LongitudinalPlanner(cp, vision_only=True)
  model = log.ModelDataV2.new_message()
  model.velocity.x = [12.]
  model.action.desiredAcceleration = -.7
  model.action.shouldStop = True
  leads = model.init("leadsV3", 2)
  for lead in leads:
    lead.x, lead.y, lead.v, lead.a = [25.], [1.], [10.], [0.]
    lead.prob = .95
  leads[1].x = [float("nan")]

  class Inputs(dict):
    logMonoTime = {"modelV2": 1}
    def all_checks(self, names):
      return all(name in self for name in names)

  sm = Inputs(modelV2=model, carState=SimpleNamespace(vEgo=12., vCruise=110., aEgo=0., standstill=False),
              controlsState=SimpleNamespace(forceDecel=False, longControlState="pid"),
              selfdriveState=SimpleNamespace(personality=SimpleNamespace(raw=1), enabled=True),
              liveParameters=SimpleNamespace(roll=0.))
  sent = {}
  planner.update(sm)
  planner.publish(sm, SimpleNamespace(send=sent.__setitem__))
  msg = sent["longitudinalPlan"]
  plan = msg.longitudinalPlan
  assert msg.valid and plan.plannerProfile == "visionE2e"
  assert plan.shouldStop and math.isfinite(plan.aTarget) and plan.aTarget < 0
  assert plan.cruiseTarget == 110
  assert plan.cameraLeadState.leadOne.vRel == -2.
  assert plan.cameraLeadState.leadOne.status and not plan.cameraLeadState.leadOne.radar
  assert not plan.cameraLeadState.leadTwo.status
  assert (plan.speedConstraint == "stockLong") == (not owns_long)
  model.init("leadsV3", 0)
  planner.update(sm)
  assert not planner.leads.leadOne.status
  model.action.desiredAcceleration = math.nan
  planner.update(sm)
  planner.publish(sm, SimpleNamespace(send=sent.__setitem__))
  assert not sent["longitudinalPlan"].valid
