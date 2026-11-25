import asyncio
import json
import time
from types import SimpleNamespace

from openpilot.selfdrive.carrot.server.features.ws import planner_status


def test_status_uses_fresh_active_planner_and_control_messages():
  class Replay(dict):
    def update(self, timeout):
      assert timeout == 0

  sm = Replay(longitudinalPlan=SimpleNamespace(plannerProfile="upstream", speedConstraint="e2e", visionPlannerSetup=""),
              controlsState=SimpleNamespace(steeringInfluence="model+limit"),
              carControl=SimpleNamespace(longActive=True))
  sm.valid = sm.seen = dict.fromkeys(sm, True)
  sm.logMonoTime = dict.fromkeys(sm, time.monotonic_ns())
  request = SimpleNamespace(app={"planner_status_reader": {"sm": sm}})

  def read():
    return json.loads(asyncio.run(planner_status(request)).text)

  assert read() == {"profile": "upstream", "speed": "e2e", "steering": "model+limit"}
  sm["longitudinalPlan"].visionPlannerSetup = "stock"
  assert read()["setup"] == "stock"
  sm["carControl"].longActive = False
  assert read()["speed"] == "inactive"
  sm["longitudinalPlan"].speedConstraint = "stockLong"
  assert read()["speed"] == "stockLong"
  sm["longitudinalPlan"].speedConstraint = "e2e"
  sm["carState"] = SimpleNamespace(vCruise=110.)
  sm.valid["carState"] = True
  sm.logMonoTime["carState"] = time.monotonic_ns()
  assert read()["cruiseCeilingKph"] == 110.
  sm["carState"].vCruise = 255.
  assert "cruiseCeilingKph" not in read()
  sm.logMonoTime["carControl"] = 0
  assert "speed" not in read()
  stamp = time.monotonic_ns()
  sm["navRoute"] = SimpleNamespace(carrotRouteId=91, coordinates=[0, 1])
  sm["mapRenderState"] = SimpleNamespace(carrotRouteId=91, locationMonoTime=stamp, routeMatch="ambiguous")
  for key in ("navRoute", "mapRenderState"):
    sm.valid[key] = sm.seen[key] = True
    sm.logMonoTime[key] = stamp
  assert read()["routeCheck"] == "ambiguous"
  assert "approachManeuver" not in read()
  sm["mapRenderState"].routeMatch, sm["mapRenderState"].approachManeuver = "matched", "turn left"
  sm["carState"].vEgo = 10.
  sm["navInstructionCarrot"] = SimpleNamespace(allManeuvers=[SimpleNamespace(type="turn", modifier="left", distance=20.)])
  sm.valid["navInstructionCarrot"] = sm.seen["navInstructionCarrot"] = True
  sm.logMonoTime["navInstructionCarrot"] = stamp
  assert read()["approachManeuver"] == "turn left"
  sm["navInstructionCarrot"].allManeuvers[0].modifier = "right"
  assert "approachManeuver" not in read()
  sm["mapRenderState"].carrotRouteId = 92
  assert "routeCheck" not in read()
  sm["mapRenderState"].carrotRouteId = 91
  sm["mapRenderState"].locationMonoTime = stamp - 3_000_000_000
  assert "routeCheck" not in read()
  sm.logMonoTime = dict.fromkeys(sm, 0)
  assert read() == {}
