from types import SimpleNamespace as Obj

import pyray as rl

from openpilot.selfdrive.ui.layout_profile import defaults
from openpilot.selfdrive.ui.onroad.reality_scene import RealityScene, ego_lamps, fresh, vehicle_points


def test_scene_uses_only_supported_observations():
  line = Obj(x=[2, 10, 20], y=[0, 0, 1])
  model = Obj(position=line, laneLines=[line], laneLineProbs=[0.1], leadsV3=[Obj(prob=0.9, x=[10], y=[2])])
  fused = Obj(status=True, dRel=10, yRel=-2)
  errors = Obj(canError=False, radarFault=False, wrongConfig=False, radarUnavailableTemporary=False)
  radar = Obj(leadOne=fused, leadTwo=fused, leadsCenter=[], leadsLeft=[], leadsRight=[], radarErrors=errors)
  assert vehicle_points(model, radar) == [(10, 2)]
  errors.radarFault = True
  assert not vehicle_points(None, radar)
  for profile in defaults()["devices"].values():
    scene = RealityScene(profile)
    rect = rl.Rectangle(0, 0, 536, 240)
    assert not scene.geometry(rect, None, None)
    low = scene.geometry(rect, model, None)
    model.laneLineProbs = [0.9]
    assert len(scene.geometry(rect, model, None)) > len(low)
    model.laneLineProbs = [0.1]


def test_session_and_timestamp_gate():
  sm = Obj(valid={"modelV2": True}, recv_frame={"modelV2": 4}, logMonoTime={"modelV2": 1_000_000_000})
  state = Obj(sm=sm, started_frame=3)
  assert fresh(state, "modelV2", 0.5, 1.1)
  assert not fresh(state, "modelV2", 0.5, 1.5)
  assert not fresh(state, "modelV2", 0.5, 0.9)
  state.started_frame = 5
  assert not fresh(state, "modelV2", 0.5, 1.1)

def test_ego_lamps_follow_reported_phase_and_only_color_the_ego():
  from opendbc.car import structs

  car = structs.CarState(canValid=True, brakeLights=True, leftBlinker=True, rightBlinker=True)
  for state, expected in (("dark", (True, False, False)), ("left", (True, True, False)),
                          ("right", (True, False, True)), ("both", (True, True, True))):
    car.turnLampState = state
    assert ego_lamps(car, .75) == expected
  car.turnLampState = "unknown"
  assert ego_lamps(car, .25) == (True, True, True)
  assert ego_lamps(car, .75) == (True, False, False)
  car.canValid = False
  assert ego_lamps(car, .25) == ego_lamps(None, .25) == (False, False, False)
  for profile in defaults()["devices"].values():
    scene = RealityScene(profile)
    rect = rl.Rectangle(0, 0, 536, 240)
    base = scene.geometry(rect, None, None, True)
    lit = scene.geometry(rect, None, None, True, (True, True, True))
    assert len(lit) == len(base) + 4
    assert not scene.geometry(rect, None, None, False, (True, True, True))
