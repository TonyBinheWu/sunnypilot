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


def test_chase_uses_signed_rear_positions_and_suppresses_duplicates():
  from opendbc.car import structs
  from openpilot.selfdrive.ui.onroad.reality_scene import rear_points

  car = structs.CarState(canValid=True, displayRearLeftDistance=9, displayRearLeftLateral=3)
  lead = Obj(status=True, radar=True, dRel=-9.5, yRel=3)
  center = Obj(status=True, radar=True, dRel=-12, yRel=0)
  errors = Obj(canError=False, radarFault=False, wrongConfig=False, radarUnavailableTemporary=False)
  radar = Obj(leadOne=lead, leadTwo=center, leadsLeft=[lead], leadsRight=[], leadsCenter=[], radarErrors=errors)
  assert rear_points(car, radar) == ((-9, -3), (-12, 0))
  errors.canError = True
  assert rear_points(car, radar) == ((-9, -3),)
  car.canValid = False
  assert not rear_points(car, radar)


def test_model_only_geometry_draws_observed_surface_and_separate_classes():
  line = lambda y: Obj(x=[4, 10, 20], y=[y] * 3)
  model = Obj(position=line(0), laneLines=[], laneLineProbs=[], leadsV3=[],
              roadEdges=[line(-4), line(4)], roadEdgeStds=[.1, .2])
  for profile in defaults()['devices'].values():
    scene = RealityScene(profile)
    rect = rl.Rectangle(0, 0, 536, 240)
    bare = scene.geometry(rect, model, None, model_only=True)
    objects = [('person', 8., -2.), ('motorcycle', 12., 1.)]
    assert len(scene.geometry(rect, model, None, objects=objects, model_only=True)) == len(bare) + 4
    model.roadEdgeStds[0] = .8
    assert len(scene.geometry(rect, model, None, model_only=True)) < len(bare)
    model.roadEdgeStds[0] = .1


def test_possible_junction_requires_two_measured_openings_and_narrowing():
  from openpilot.selfdrive.ui.onroad.reality_scene import road_opening
  x = list(range(0, 60, 2))
  center = [n * .05 for n in x]
  spread = [3. if 18 <= n < 30 else 0. for n in x]
  edges = [Obj(x=x, y=[y + sign * (4 + w) for y, w in zip(center, spread)]) for sign in (-1, 1)]
  model = Obj(position=Obj(x=x, y=center), roadEdges=edges, roadEdgeStds=[.2, .2])
  assert road_opening(model) == (18., 30.)
  model.roadEdgeStds[0] = .8
  assert road_opening(model) is None
  model.roadEdgeStds[0] = .2
  model.roadEdges[1] = Obj(x=x, y=[y + 4 for y in center])
  assert road_opening(model) is None


def test_directional_meshes_and_crossroad_project_on_both_displays():
  import math
  for profile in defaults()['devices'].values():
    scene = RealityScene(profile)
    rect = rl.Rectangle(0,0,540,360)
    scene.junction = [[(0,0),(0,24)], [(0,24),(18,24)], [(0,24),(-18,24)], [(0,24),(0,48)]]
    def vertices(heading):
      faces = scene.geometry(rect,None,None,objects=[('car',21,2,heading)],model_only=True)
      return tuple((v.x,v.y) for v in faces[-1][0])
    assert len({vertices(h) for h in (0,math.pi,math.pi/2,-math.pi/2)}) == 4
    assert len(scene.geometry(rect,None,None,model_only=True)) == 4
