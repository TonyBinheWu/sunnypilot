from types import SimpleNamespace as NS

import pytest

from openpilot.selfdrive.carrot.server.services.world_scene import ContactHistory, ERROR_FLAGS, path_beyond_edge, world_observations


def sources():
  class SM(dict):
    pass
  now = 10_000_000_000
  errors = NS(**dict.fromkeys(ERROR_FLAGS, False))
  p = NS(radarSource="corner235", trackId=31, vRel=-4., dRel=9., yRel=2., measured=True, measurementMonoTime=20_000_000_000)
  lead = NS(status=True, radar=True, radarTrackId=31, dRel=9., yRel=2.)
  sm = SM(liveTracks=NS(points=[p], errors=errors), radarState=NS(leadOne=lead, leadTwo=lead, radarErrors=errors),
          carState=NS(canValid=True, leftBlindspot=True, rightBlindspot=False), carControl=NS(longActive=True),
          longitudinalPlan=NS(hasLead=True, longitudinalPlanSource="lead1", fcw=False),
          modelV2=NS(timestampEof=20_000_000_000, visionCompute="usbGpu", visionCameraInputs="roadWide", frameId=11,
                     position=NS(x=[], y=[], t=[]), roadEdges=[], roadEdgeStds=[]))
  sm.seen, sm.valid, sm.logMonoTime = dict.fromkeys(sm, True), dict.fromkeys(sm, True), dict.fromkeys(sm, now)
  sm.history = ContactHistory()
  p.measurementMonoTime -= 90_000_000
  world_observations(sm, 10., 20., sm.history)
  p.measurementMonoTime = 20_000_000_000
  return sm


def test_world_uses_original_sensor_stamp_and_distinct_clock_for_capture():
  sm = sources()
  result = world_observations(sm, 10., 20., sm.history)
  assert result["model"]["cameras"] == ["road", "wide"]
  assert result["contacts"][0]["y"] == -2. and result["following"]["nativeId"] == "31"
  assert result["signals"] == {"leftBlindspot": 300}
  sm["liveTracks"].points[0].measurementMonoTime -= 500_000_000
  result = world_observations(sm, 10., 21., sm.history)
  assert "model" not in result and "following" not in result and not result["contacts"]
  assert result["signals"] == {"leftBlindspot": 300}


@pytest.mark.parametrize("field,value", [("radarSource","corner430"), ("radarSource","scc"), ("dRel",.2),
                                         ("dRel",float("nan")), ("measured",False), ("measurementMonoTime",0)])
def test_unpositioned_or_unmeasured_echo_never_gets_a_location(field, value):
  sm = sources()
  setattr(sm["liveTracks"].points[0], field, value)
  row = world_observations(sm, 10., 20., sm.history)
  assert not row["contacts"] and "following" not in row


def test_held_slot_cannot_confirm_itself_or_survive_suspend():
  sm = sources()
  history = ContactHistory()
  for now in (10., 10.1):
    assert not world_observations(sm, now, now + 10., history)["contacts"]
  sm["liveTracks"].points[0].measurementMonoTime += 110_000_000
  assert world_observations(sm, 10.11, 20.11, history)["contacts"]
  assert not world_observations(sm, 10.12, 24., history)["contacts"]


def test_no_false_lock_or_false_gpu_provenance():
  sm = sources()
  sm["carControl"].longActive = False
  sm["modelV2"].visionCompute = "nonUsb"
  sm["longitudinalPlan"].fcw = True
  row = world_observations(sm, 10., 20., sm.history)
  assert "following" not in row and "model" not in row and "plannerFcw" in row["signals"]
  sm["carControl"].longActive = True
  p = sm["liveTracks"].points[0]
  sm["liveTracks"].points.append(p)
  assert not world_observations(sm, 10., 20., sm.history)["contacts"]
  sm["liveTracks"].points.pop()
  sm["liveTracks"].errors.canError = True
  assert not world_observations(sm, 10., 20., sm.history)["contacts"]
  sm.valid = dict.fromkeys(sm, False)
  assert world_observations(sm, 10., 20., sm.history) == {"contacts": [], "signals": {}}


def test_closing_notice_needs_longitudinal_approach_in_the_front_on_two_real_measurements():
  sm = sources()
  car, p = sm["carState"], sm["liveTracks"].points[0]
  car.gearShifter, car.vEgo = "drive", 17.
  p.radarSource, p.dRel, p.yRel, p.vRel = "frontRadar", 9., -.2, -6.
  assert "closing" not in world_observations(sm, 10., 20., sm.history)
  p.measurementMonoTime += 30_000_000
  result = world_observations(sm, 10.031, 20.031, sm.history)
  assert result["closing"]["nativeId"] == "31"
  car.gearShifter = "reverse"
  assert "closing" not in world_observations(sm, 10.04, 20.04, sm.history)
  car.gearShifter = "drive"
  p.yRel = 1.4
  assert "closing" not in world_observations(sm, 10.04, 20.04, sm.history)


def test_boundaries_use_matched_distances_and_require_two_supported_samples():
  model = sources()["modelV2"]
  model.position = NS(x=[3, 6, 8], y=[0., -3., -3.], t=[.4, .8, 1.])
  model.roadEdges, model.roadEdgeStds = [NS(x=[2., 9.], y=[-1.7, -1.6])], [.14]
  assert path_beyond_edge(model) == "left"
  model.roadEdges[0].x[1] = 7.
  assert path_beyond_edge(model) is None
  model.roadEdges[0].x[1] = 9.
  model.roadEdgeStds = [.8]
  assert path_beyond_edge(model) is None
