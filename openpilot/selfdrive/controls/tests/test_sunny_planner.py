from types import SimpleNamespace as NS

import numpy as np
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
  sm = Inputs(modelV2=model, carState=NS(vEgo=25., vCruise=110., aEgo=0., canValid=True, canTimeout=False,
                                         standstill=False, cruiseState=NS(standstill=False), softHoldActive=0,
                                         gasPressed=False, brakePressed=False),
              controlsState=NS(forceDecel=False, longControlState=module.LongCtrlState.pid), liveParameters=NS(roll=0.),
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


@pytest.mark.parametrize('type_,modifier,name', [('turn', 'right', 'turn right'), ('fork', 'left', 'branch left'),
                                                 ('roundabout', '', 'roundabout'), ('turn', 'uturn', 'uturn')])
def test_junction_withholds_only_extra_opening_lead_recovery(monkeypatch, type_, modifier, name):
  monkeypatch.setattr(module, "Params", lambda: NS(get_bool=lambda _: False))
  cp = NS(openpilotLongitudinalControl=True, longitudinalActuatorDelay=.2)
  planner = module.LongitudinalPlanner(cp, init_v=25., sunny=True)
  sm = inputs()
  model = sm['modelV2']
  model.action.desiredAcceleration, model.action.shouldStop, model.orientationRate.z = .15, False, [0.]
  lead = sm['radarState'].leadOne
  lead.status = lead.radar = True
  lead.radarTrackId, lead.vRel, lead.dRel, lead.vLead, lead.vLeadK = 5, 2., 80., 27., 27.
  lead.aLeadTau = 1.5
  step = NS(type=type_, modifier=modifier, distance=300.)
  report = NS(routeMatch='matched', carrotRouteId=1, approachManeuver='', locationMonoTime=0)
  sm.update(navInstructionCarrot=NS(allManeuvers=[step]), navRoute=NS(carrotRouteId=1, coordinates=[0, 1]), mapRenderState=report)
  sm.valid = dict.fromkeys(sm, True)
  for frame in range(130):
    stamp = 10_000_000_000 + frame * 50_000_000
    sm.logMonoTime = dict.fromkeys(sm, stamp)
    sm['radarState'].mdMonoTime = stamp
    report.locationMonoTime = stamp
    if frame == 60:
      assert planner.speed_reason == 'openingLead'
    step.distance, report.approachManeuver = (30., name) if 60 <= frame < 90 else (300., '')
    planner.update(sm)
    if 60 <= frame < 110:
      assert not planner.output_should_stop and planner.output_a_target == pytest.approx(.15)
  assert planner.speed_reason == 'openingLead'


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


@pytest.mark.parametrize("interrupt", ["cut_in", "cut_in_risk", "disappeared", "lead_braking", "closing", "braking",
                                       "stop", "curve", "stale", "gas", "ceiling", "force_decel"])
def test_opening_lead_recovery_requires_continuous_eligible_observations(monkeypatch, interrupt):
  monkeypatch.setattr(module, "Params", lambda: NS(get_bool=lambda _: False))
  planner = module.LongitudinalPlanner(NS(openpilotLongitudinalControl=True, longitudinalActuatorDelay=.2), init_v=25., sunny=True)
  sm = inputs()
  model = sm["modelV2"]
  model.action.desiredAcceleration, model.action.shouldStop = .15, False
  model.orientationRate.z = [0.]
  lead = sm["radarState"].leadOne
  lead.status = lead.radar = True
  lead.radarTrackId, lead.vRel, lead.dRel = 5, 2., 80.
  lead.vLead = lead.vLeadK = 27.
  lead.aLeadTau = 1.5
  for i in range(80):
    radar_frame(sm, i)
    planner.update(sm)
    if i <= 20:
      assert planner.output_a_target <= .151
  assert planner.speed_reason == "openingLead"
  assert .15 < planner.output_a_target <= .501

  if interrupt == "cut_in":
    lead.radarTrackId, lead.dRel = 8, 18.
  elif interrupt == "cut_in_risk":
    sm['radarState'].leadCutInRisk.status = True
  elif interrupt == "disappeared":
    lead.status = False
  elif interrupt == "lead_braking":
    lead.aLeadK = -.8
  elif interrupt == "closing":
    lead.vRel = -2.
  elif interrupt == "braking":
    model.action.desiredAcceleration = -.3
  elif interrupt == "stop":
    model.action.shouldStop = True
  elif interrupt == "curve":
    model.orientationRate.z = [.2]
  elif interrupt == "stale":
    sm.logMonoTime["modelV2"] += 250_000_000
  elif interrupt == "gas":
    sm["carState"].gasPressed = True
  elif interrupt == "ceiling":
    sm["carState"].vCruise = 90.
  else:
    sm["controlsState"].forceDecel = True
  planner.update(sm)
  assert planner.speed_reason != "openingLead"
  assert planner.output_a_target <= model.action.desiredAcceleration
  if interrupt == "stop":
    assert planner.output_should_stop


def radar_frame(sm, frame):
  stamp = 10_000_000_000 + frame * 50_000_000
  sm.logMonoTime.update(modelV2=stamp, radarState=stamp)
  sm['radarState'].mdMonoTime = stamp


@pytest.fixture
def empty_road(monkeypatch):
  # Fix the solver trajectory so its positive synthetic-lead ceiling is
  # distinguishable from the model's request on every platform.
  monkeypatch.setattr(module, 'Params', lambda: NS(get_bool=lambda _: False))
  source = module.LongitudinalPlanSource
  planner = module.LongitudinalPlanner(NS(openpilotLongitudinalControl=True, longitudinalActuatorDelay=.2),
                                       init_v=25., init_a=1., sunny=True)
  sm = inputs()
  sm['modelV2'].action.desiredAcceleration = .8
  sm['modelV2'].action.shouldStop = False
  solver = NS(accel=.2, updates=0, crash_count=0)

  def update(leads, personality):
    assert leads is planner.leads
    solver.updates += 1
    planner.mpc.crash_cnt = solver.crash_count
    planner.mpc.source = source.lead1 if leads.leadTwo.status else source.lead0
    planner.mpc.v_solution = 25. + solver.accel * module.T_IDXS_MPC
    planner.mpc.a_solution = np.full_like(module.T_IDXS_MPC, solver.accel)
    planner.mpc.j_solution = np.zeros_like(module.T_IDXS_MPC[:-1])

  monkeypatch.setattr(planner.mpc, 'update', update)
  return planner, sm, solver


def test_empty_road_model_target_and_immediate_follow_protection(empty_road):
  planner, sm, solver = empty_road
  for frame in range(40):
    radar_frame(sm, frame)
    previous = planner.output_a_target
    planner.update(sm)
    if frame < 10:
      assert planner.output_a_target == pytest.approx(.2)
    else:
      assert planner.output_a_target <= previous + .8 * planner.dt + 1e-7
  assert planner.output_a_target == pytest.approx(.8) and planner.speed_reason == 'e2e'
  assert solver.updates == 40
  out = {}
  planner.publish(sm, NS(send=out.__setitem__))
  plan = out['longitudinalPlan'].longitudinalPlan
  assert plan.longitudinalPlanSource == 'e2e' and plan.aTarget == pytest.approx(.8)
  assert planner.mpc.source == module.LongitudinalPlanSource.lead0

  sm['radarState'].leadTwo.status = True
  solver.accel, solver.crash_count = -2., 3
  radar_frame(sm, 40)
  planner.update(sm)
  planner.publish(sm, NS(send=out.__setitem__))
  plan = out['longitudinalPlan'].longitudinalPlan
  assert plan.fcw and plan.aTarget == pytest.approx(-2.) and plan.longitudinalPlanSource == 'lead1'
  assert solver.updates == 41

  sm['radarState'].leadTwo.status = False
  solver.accel, solver.crash_count = .2, 0
  radar_frame(sm, 41)
  planner.update(sm)
  assert planner.speed_reason == 'mpc' and planner.clear_since_ns == sm['radarState'].mdMonoTime


@pytest.mark.parametrize('model_accel,expected', [(.15, .50), (.45, .60)])
@pytest.mark.parametrize('interrupt', ['cut_in', 'lost_track', 'lead_braking', 'closing', 'track_change'])
def test_opening_gap_recovery_respects_model_stop_and_follow_ceiling(empty_road, model_accel, expected, interrupt):
  planner, sm, solver = empty_road
  model, lead = sm['modelV2'], sm['radarState'].leadOne
  model.action.desiredAcceleration, model.orientationRate.z = model_accel, [0.]
  lead.status = lead.radar = True
  lead.radarTrackId, lead.vRel, lead.dRel = 4, 3., 90.
  solver.accel = 1.0
  for frame in range(80):
    radar_frame(sm, frame)
    planner.update(sm)
    if frame <= 20:
      assert planner.output_a_target == pytest.approx(model_accel)
  assert planner.speed_reason == 'openingLead' and planner.output_a_target == pytest.approx(expected)

  solver.accel = .10
  radar_frame(sm, 80)
  planner.update(sm)
  assert planner.speed_reason == 'lead0' and planner.output_a_target == pytest.approx(.10)
  radar_frame(sm, 81)
  solver.accel = 1.
  if interrupt == 'cut_in':
    sm['radarState'].leadCutInRisk.status = True
  elif interrupt == 'lost_track':
    lead.status = False
  elif interrupt == 'lead_braking':
    lead.aLeadK = -1.
  elif interrupt == 'closing':
    lead.vRel = -1.
  else:
    lead.radarTrackId = 5
  planner.update(sm)
  assert planner.speed_reason == 'e2e' and planner.output_a_target == pytest.approx(model_accel)
  radar_frame(sm, 82)
  sm['radarState'].leadCutInRisk.status = False
  model.action.desiredAcceleration, model.action.shouldStop = -.9, True
  planner.update(sm)
  assert planner.output_should_stop and planner.output_a_target == pytest.approx(-.9)


def test_empty_road_keeps_set_speed_and_model_braking(empty_road):
  planner, sm, _ = empty_road
  for frame in range(45):
    radar_frame(sm, frame)
    planner.update(sm)
  sm['carState'].vCruise = 70.
  for frame in range(45, 105):
    radar_frame(sm, frame)
    planner.update(sm)
  assert planner.speed_reason == 'cruise' and planner.output_a_target < 0.
  sm['modelV2'].action.desiredAcceleration = -2.
  radar_frame(sm, 105)
  planner.update(sm)
  assert planner.speed_reason == 'e2e' and planner.output_a_target == pytest.approx(-2.)


@pytest.mark.parametrize('interrupt', ['leadOne', 'leadTwo', 'leadCutInRisk', 'radarFault', 'canError', 'wrongConfig',
                                      'radarUnavailableTemporary', 'stale', 'future', 'gap', 'reverse', 'duplicate',
                                      'invalidRadar', 'canInvalid', 'canTimeout', 'brake', 'gas', 'standstill',
                                      'stock', 'disabled', 'disengaged', 'softHold', 'cruiseHold', 'forceDecel',
                                      'modelStop', 'mpcBrake', 'fcw'])
def test_clear_road_requires_healthy_observations_and_retains_mpc(empty_road, interrupt):
  planner, sm, solver = empty_road
  for frame in range(10):
    radar_frame(sm, frame)
    planner.update(sm)
  last_stamp = sm['radarState'].mdMonoTime
  radar_frame(sm, 10)
  cs, radar = sm['carState'], sm['radarState']
  if interrupt in ('leadOne', 'leadTwo', 'leadCutInRisk'):
    getattr(radar, interrupt).status = True
  elif interrupt in ('radarFault', 'canError', 'wrongConfig', 'radarUnavailableTemporary'):
    setattr(radar.radarErrors, interrupt, True)
  elif interrupt in ('stale', 'future', 'gap', 'reverse', 'duplicate'):
    if interrupt == 'gap':
      radar_frame(sm, 13)
    else:
      radar.mdMonoTime = {'stale': last_stamp - 200_000_000, 'future': last_stamp + 60_000_000,
                          'reverse': last_stamp - 10_000_000, 'duplicate': last_stamp}[interrupt]
  elif interrupt == 'invalidRadar':
    sm.all_checks = lambda names: 'radarState' not in names
  elif interrupt == 'canInvalid':
    cs.canValid = False
  elif interrupt in ('canTimeout', 'brake', 'gas', 'standstill'):
    setattr(cs, {'gas': 'gasPressed', 'brake': 'brakePressed'}.get(interrupt, interrupt), True)
  elif interrupt == 'stock':
    planner.CP.openpilotLongitudinalControl = False
  elif interrupt == 'disabled':
    sm['controlsState'].longControlState = module.LongCtrlState.off
  elif interrupt == 'disengaged':
    sm['selfdriveState'].enabled = False
  elif interrupt == 'softHold':
    cs.softHoldActive = 1
  elif interrupt == 'cruiseHold':
    cs.cruiseState.standstill = True
  elif interrupt == 'forceDecel':
    sm['controlsState'].forceDecel = True
  elif interrupt == 'modelStop':
    sm['modelV2'].action.shouldStop = True
  elif interrupt == 'mpcBrake':
    solver.accel = -.6
  elif interrupt == 'fcw':
    solver.crash_count = 3
  planner.update(sm)
  assert planner.output_a_target <= solver.accel + 1e-6
  assert solver.updates == 11
  if interrupt == 'modelStop':
    assert planner.output_should_stop


def highway_inputs():
  sm = inputs()
  model = sm["modelV2"]
  times = module.ModelConstants.T_IDXS
  model.position.t = times
  model.position.x = [25. * t for t in times]
  model.velocity.x = [25.] * len(times)
  model.orientation.x = model.orientationRate.z = [0.] * len(times)
  model.action.desiredAcceleration, model.action.shouldStop = -.04, False
  model.meta.disengagePredictions.brakePressProbs = [.01, .01]
  model.meta.disengagePredictions.gasPressProbs = [.9, .9]
  sm["carState"].steeringAngleDeg = sm["liveParameters"].angleOffsetDeg = 0.
  return sm


def sunny_planner(monkeypatch, *, dec, radar=True, direct=True, assist=None):
  keys = {"DynamicExperimentalControl": dec, assist: True}
  monkeypatch.setattr(module, "Params", lambda: NS(get_bool=lambda key: keys.get(key, False)))
  cp = NS(openpilotLongitudinalControl=direct, radarUnavailable=not radar, longitudinalActuatorDelay=.5,
          wheelbase=2.9, steerRatio=14.3, visionPlannerSetup="native" if direct else "stock")
  return module.LongitudinalPlanner(cp, init_v=25., sunny=True)


def tick(planner, sm, *, radar_age_ns=0):
  sm.logMonoTime = dict.fromkeys(sm, sm.logMonoTime["modelV2"] + 50_000_000)
  sm["radarState"].mdMonoTime = sm.logMonoTime["radarState"] - radar_age_ns
  planner.update(sm)


@pytest.mark.parametrize("dec,mode,expected_accel", [(False, "blended", -.04), (True, "decAcc", .8)])
@pytest.mark.parametrize("radar", [True, False])
def test_clear_road_uses_model_unless_dec_selects_acc(monkeypatch, dec, mode, expected_accel, radar):
  sm = highway_inputs()
  planner = sunny_planner(monkeypatch, dec=dec, radar=radar)
  for i in range(80):
    before = planner.output_a_target
    tick(planner, sm)
    if i > 0 and planner.longitudinal_mode == "decAcc":
      assert planner.output_a_target <= before + .8 * planner.dt + 1e-6
  assert planner.longitudinal_mode == mode
  assert planner.output_a_target == pytest.approx(expected_accel, abs=1e-5)
  assert planner.speed_reason == ("accComfort" if dec else "e2e")
  out = {}
  planner.publish(sm, NS(send=out.__setitem__))
  assert out["longitudinalPlan"].longitudinalPlan.longitudinalMode == mode
  sm["carState"].vCruise = 90.  # 25 m/s
  tick(planner, sm)
  assert planner.output_a_target <= 0.


@pytest.mark.parametrize("hazard", ["stop", "braking", "brakeProbability", "coast", "steering", "curve", "shortPath",
                                    "standstill", "brakePedal", "forceDecel", "noTrajectory", "noPedals", "stale", "junction"])
def test_dec_gives_model_priority_immediately(monkeypatch, hazard):
  sm = highway_inputs()
  planner = sunny_planner(monkeypatch, dec=True)
  for _ in range(35):
    tick(planner, sm)
  assert planner.longitudinal_mode == "decAcc" and planner.output_a_target > .5
  model = sm["modelV2"]
  if hazard == "stop":
    model.action.shouldStop = True
  elif hazard == "braking":
    model.action.desiredAcceleration = -1.5
  elif hazard == "brakeProbability":
    model.meta.disengagePredictions.brakePressProbs = [.5, .8]
  elif hazard == "coast":
    model.meta.disengagePredictions.gasPressProbs = [.1, .1]
  elif hazard == "steering":
    model.action.desiredCurvature = .01
  elif hazard == "curve":
    model.orientationRate.z = [.25] * len(model.position.t)
  elif hazard == "shortPath":
    model.position.x = [t * 2. for t in model.position.t]
  elif hazard == "standstill":
    sm["carState"].standstill, sm["carState"].vEgo = True, 0.
  elif hazard == "brakePedal":
    sm["carState"].brakePressed = True
  elif hazard == "forceDecel":
    sm["controlsState"].forceDecel = True
  elif hazard == "noTrajectory":
    model.position.x = []
  elif hazard == "noPedals":
    model.meta.disengagePredictions.gasPressProbs = []
  elif hazard == "stale":
    sm.logMonoTime["modelV2"] += 300_000_000
  elif hazard == "junction":
    monkeypatch.setattr(module, "nearby_maneuver", lambda *args: "turn right")
  tick(planner, sm)
  assert planner.longitudinal_mode == "decBlended"
  assert planner.output_a_target <= model.action.desiredAcceleration + 1e-6
  if hazard == "stop":
    assert planner.output_should_stop


@pytest.mark.parametrize("dec", [True, False])
@pytest.mark.parametrize("lead_field,reason", [("leadOne", "lead0"), ("leadTwo", "lead1")])
def test_closing_lead_keeps_its_braking_authority(monkeypatch, dec, lead_field, reason):
  sm = highway_inputs()
  planner = sunny_planner(monkeypatch, dec=dec)
  for _ in range(60):
    tick(planner, sm)
  lead = getattr(sm["radarState"], lead_field)
  lead.status, lead.dRel, lead.vLead, lead.vLeadK, lead.vRel, lead.aLeadTau = True, 20., 7., 7., -18., 1.5
  tick(planner, sm)
  # The first RTI solve can still reflect the old open road. The model's braking already applies.
  assert planner.output_a_target <= sm["modelV2"].action.desiredAcceleration + 1e-6
  tick(planner, sm)
  assert planner.speed_reason == reason
  assert planner.output_a_target < -1.


@pytest.mark.parametrize("fault", ["cutIn", "radarFault", "radarUnavailable", "staleRadar", "futureRadar", "canTimeout", "softHold"])
def test_dec_drops_acc_when_clear_road_evidence_is_lost(monkeypatch, fault):
  sm = highway_inputs()
  planner = sunny_planner(monkeypatch, dec=True)
  for _ in range(40):
    tick(planner, sm)
  assert planner.longitudinal_mode == "decAcc"
  cs, radar = sm["carState"], sm["radarState"]
  radar.leadCutInRisk.status = fault == "cutIn"
  radar.radarErrors.radarFault = fault == "radarFault"
  radar.radarErrors.radarUnavailableTemporary = fault == "radarUnavailable"
  cs.canTimeout, cs.softHoldActive = fault == "canTimeout", int(fault == "softHold")
  age = {"staleRadar": module.MAX_RADAR_AGE_NS, "futureRadar": -1}.get(fault, 0)
  tick(planner, sm, radar_age_ns=age)
  assert planner.longitudinal_mode == "decBlended"
  assert planner.output_a_target <= sm["modelV2"].action.desiredAcceleration + 1e-6

  radar.leadCutInRisk.status = radar.radarErrors.radarFault = radar.radarErrors.radarUnavailableTemporary = False
  cs.canTimeout, cs.softHoldActive = False, 0
  for _ in range(10):
    tick(planner, sm)
    assert planner.longitudinal_mode == "decBlended"
  for _ in range(15):
    tick(planner, sm)
  assert planner.longitudinal_mode == "decAcc"


@pytest.mark.parametrize("assist,source", [("SunnyMapCurve", "mapCurve"), ("SunnySpeedLimit", "speedLimit")])
def test_dec_respects_optional_speed_assists(monkeypatch, assist, source):
  sm = highway_inputs()
  planner = sunny_planner(monkeypatch, dec=True, assist=assist)
  for _ in range(40):
    sm["carrotMan"].positionFixMonoTime = sm.logMonoTime["modelV2"]
    tick(planner, sm)
  assert planner.longitudinal_mode == "decAcc"
  assert planner.output_a_target < 0. and planner.speed_reason == source


def test_stock_and_disengaged_never_report_active_dec(monkeypatch):
  sm = highway_inputs()
  planner = sunny_planner(monkeypatch, dec=True, direct=False)
  for _ in range(20):
    tick(planner, sm)
  out = {}
  planner.publish(sm, NS(send=out.__setitem__))
  plan = out["longitudinalPlan"].longitudinalPlan
  assert plan.speedConstraint == "stockLong" and not plan.longitudinalMode
  planner = sunny_planner(monkeypatch, dec=True)
  sm["controlsState"].longControlState = module.LongCtrlState.off
  tick(planner, sm)
  assert not planner.longitudinal_mode


def test_dec_restarts_after_an_unsuccessful_solve(monkeypatch):
  sm = highway_inputs()
  planner = sunny_planner(monkeypatch, dec=True)
  for _ in range(30):
    tick(planner, sm)
  assert planner.longitudinal_mode == "decAcc"
  solver = planner.mpc.solver

  class FailedSolve:
    def solve(self):
      return 1

    def __getattr__(self, name):
      return getattr(solver, name)

  planner.mpc.solver = FailedSolve()
  tick(planner, sm)
  assert planner.mpc.solution_status == 1 and planner.longitudinal_mode == "decBlended"
  assert planner.output_a_target <= 0.
  planner.mpc.solver = solver
  tick(planner, sm)
  assert planner.mpc.solution_status == 0 and planner.longitudinal_mode == "decBlended"
  for _ in range(25):
    tick(planner, sm)
  assert planner.longitudinal_mode == "decAcc"


def test_dec_acc_converges_to_cruise_ceiling(monkeypatch):
  sm = highway_inputs()
  planner = sunny_planner(monkeypatch, dec=True)
  cs, model = sm["carState"], sm["modelV2"]
  cs.vCruise = 120.
  for _ in range(1000):  # straight, level, ideal acceleration tracking for 50 seconds
    model.position.x = [cs.vEgo * t for t in model.position.t]
    model.velocity.x = [cs.vEgo] * len(model.position.t)
    tick(planner, sm)
    cs.aEgo = float(planner.output_a_target)
    cs.vEgo += cs.aEgo * planner.dt
    assert cs.vEgo * 3.6 <= cs.vCruise + 1e-5
  assert cs.vEgo * 3.6 == pytest.approx(cs.vCruise, abs=.1)
