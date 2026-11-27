from types import SimpleNamespace as NS

import pytest

from openpilot.cereal import car, log
from openpilot.common.driving_planner import SUNNY_BLENDED, SUNNY_RELEASE, SUNNY_RELEASE_VISION, selected_sunny_mode
from openpilot.selfdrive.controls.lib import upstream_planner
from openpilot.selfdrive.controls.lib.sunny_cruise_planner import make_longitudinal_planner
from openpilot.selfdrive.controls.tests.test_sunny_planner import highway_inputs


def setup_planner(monkeypatch, *, camera=True, dec=True):
  monkeypatch.setattr(upstream_planner, 'Params', lambda: NS(get_bool=lambda key: dec and key == 'DynamicExperimentalControl'))
  cp = car.CarParams.new_message()
  cp.openpilotLongitudinalControl = True
  cp.wheelbase, cp.steerRatio, cp.vEgoStopping, cp.longitudinalActuatorDelay = 2.9, 16., .3, .5
  cp.drivingPlannerMode = selected_sunny_mode(cp, 2 if camera else 1)
  engine = make_longitudinal_planner(cp)
  sm = highway_inputs()
  sm['carControl'] = NS(orientationNED=[0., 0., 0.])
  sm['selfdriveState'].experimentalMode = True
  sm['carState'].vCruise = 120.
  for lead in sm['modelV2'].init('leadsV3', 2):
    lead.prob = 0.
    lead.x, lead.y, lead.v, lead.a = [120.], [0.], [30.], [0.]
  return engine, sm


def advance(sm):
  cs, model = sm['carState'], sm['modelV2']
  stamp = sm.logMonoTime['modelV2'] + 50_000_000
  sm.logMonoTime = dict.fromkeys(sm, stamp)
  sm['radarState'].mdMonoTime = stamp - 50_000_000
  model.timestampEof = stamp - 60_000_000
  model.position.x = [cs.vEgo * t for t in model.position.t]
  model.velocity.x = [cs.vEgo] * len(model.position.t)


@pytest.mark.parametrize('set_speed', [5., 35.])
@pytest.mark.parametrize('personality', list(log.LongitudinalPersonality.schema.enumerants.values()))
@pytest.mark.parametrize('experimental', [False, True])
def test_converges_to_cruise_setting(monkeypatch, set_speed, personality, experimental):
  planner, sm = setup_planner(monkeypatch, camera=False)
  cs, state = sm['carState'], sm['selfdriveState']
  cs.vEgo, cs.vCruise = set_speed - 1., set_speed * 3.6
  state.experimentalMode, state.personality.raw = experimental, personality
  for _ in range(400):
    advance(sm)
    sm['modelV2'].action.desiredAcceleration = cs.aEgo + .1
    planner.update(sm)
    assert planner.camera_input_valid
    cs.aEgo = planner.output_a_target
    cs.vEgo += cs.aEgo * .05
  assert cs.vEgo == pytest.approx(set_speed, abs=.01)


@pytest.mark.parametrize('camera', [False, True])
@pytest.mark.parametrize('scene', ['empty', 'distant', 'slowing'])
def test_highway_recovery_and_braking_closed_loop(monkeypatch, camera, scene):
  p, sm = setup_planner(monkeypatch, camera=camera)
  cs = sm['carState']
  gap = 120.
  min_command, peak_speed = 0., cs.vEgo
  for frame in range(900):
    advance(sm)
    if scene != 'empty':
      lead_speed = 120. / 3.6 if scene == 'distant' else max(10., 25. - 2. * max(0., frame * .05 - 5.))
      lead = sm['radarState'].leadOne
      lead.status, lead.modelProb, lead.aLeadTau = True, .98, .3
      lead.dRel, lead.vLead, lead.vRel = gap, lead_speed, lead_speed - cs.vEgo
      obs = sm['modelV2'].leadsV3[0]
      obs.prob, obs.x, obs.v = .98, [gap + 1.52], [lead_speed]
      gap += (lead_speed - cs.vEgo) * .05
      assert gap > 5.
    p.update(sm)
    assert p.camera_input_valid
    cs.aEgo = p.output_a_target
    cs.vEgo += cs.aEgo * .05
    peak_speed = max(peak_speed, cs.vEgo)
    min_command = min(min_command, cs.aEgo)
    if frame == 399 and scene != 'slowing':
      assert 119. <= cs.vEgo * 3.6 <= 120.01
  assert peak_speed * 3.6 <= 120.01
  if scene == 'slowing':
    assert min_command < -1. and 34. <= cs.vEgo * 3.6 <= 38. and 15. < gap < 28.
  else:
    assert cs.vEgo * 3.6 == pytest.approx(120., abs=.05)


@pytest.mark.parametrize('bad', ['eof', 'duplicate', 'missing_camera_leads', 'bad_lead', 'trajectory', 'gas_prob', 'can', 'control_age'])
def test_missing_observations_do_not_become_clear_road(monkeypatch, bad):
  p, sm = setup_planner(monkeypatch)
  advance(sm)
  p.update(sm)
  assert p.camera_input_valid
  advance(sm)
  m = sm['modelV2']
  if bad == 'eof':
    m.timestampEof -= 300_000_000
  elif bad == 'duplicate':
    m.timestampEof = p.last_eof
  elif bad == 'missing_camera_leads':
    m.init('leadsV3', 1)
  elif bad == 'bad_lead':
    m.leadsV3[0].v = [float('nan')]
  elif bad == 'trajectory':
    m.position.x = [float('nan')] * len(m.position.x)
  elif bad == 'gas_prob':
    m.meta.disengagePredictions.gasPressProbs = []
  elif bad == 'can':
    sm['carState'].canTimeout = True
  else:
    sm.logMonoTime['controlsState'] -= 300_000_000
  p.update(sm)
  sent = []
  p.publish(sm, NS(send=lambda _, msg: sent.append(msg)))
  assert not sent[0].valid and sent[0].longitudinalPlan.plannerProfile == 'sunnyVision'
  assert not p.allow_throttle


def test_sensor_selection_and_model_fallback(monkeypatch):
  vision, sm = setup_planner(monkeypatch)
  fused, _ = setup_planner(monkeypatch, camera=False)
  cs = sm['carState']
  radar = sm['radarState']
  lead = radar.leadOne
  lead.status, lead.modelProb, lead.dRel, lead.vLead, lead.aLeadTau = True, .99, 25., 17., .3
  for _ in range(50):
    advance(sm)
    for p in (vision, fused):
      p.update(sm)
  assert vision.output_a_target > .4 and not vision.leads.leadOne.status
  assert fused.output_a_target < -.5 and fused.speed_reason == 'lead0'
  del sm['radarState']
  sm.logMonoTime = dict.fromkeys(sm, sm.logMonoTime['modelV2'] + 50_000_000)
  sm['modelV2'].timestampEof += 50_000_000
  vision.update(sm)
  fused.update(sm)
  assert vision.camera_input_valid and not fused.camera_input_valid
  assert cs.vCruise == 120.


def test_second_lead_and_cut_in_override_empty_road_resume(monkeypatch):
  p, sm = setup_planner(monkeypatch, camera=False)
  sm['modelV2'].action.desiredAcceleration = .6
  for _ in range(40):
    advance(sm)
    p.update(sm)
  assert p.output_a_target > .2
  sm['radarState'].leadCutInRisk.status = True
  advance(sm)
  p.update(sm)
  assert p.output_a_target == 0. and p.speed_reason == 'cutIn'
  sm['radarState'].leadCutInRisk.status = False
  second = sm['radarState'].leadTwo
  second.status, second.dRel, second.vLead, second.vRel, second.aLeadTau = True, 30., 17., -8., .3
  for _ in range(10):
    advance(sm)
    second.dRel += second.vRel * .05
    p.update(sm)
    assert p.output_a_target <= 0.
  assert p.output_a_target < 0. and p.speed_reason == 'lead1'


@pytest.mark.parametrize('event', ['stopping', 'hard_braking', 'lower_set_speed', 'unset', 'force_decel', 'driver_brake', 'gas', 'soft_hold'])
def test_cruise_never_accelerates_through_stop_or_override(monkeypatch, event):
  p, sm = setup_planner(monkeypatch)
  for _ in range(30):
    advance(sm)
    p.update(sm)
  assert p.output_a_target > .3
  cs, m = sm['carState'], sm['modelV2']
  if event == 'stopping':
    m.action.shouldStop = True
  elif event == 'hard_braking':
    m.action.desiredAcceleration = -1.5
  elif event == 'lower_set_speed':
    cs.vCruise = 80.
  elif event == 'unset':
    cs.vCruise = 255.
  elif event == 'force_decel':
    sm['controlsState'].forceDecel = True
  elif event == 'driver_brake':
    cs.brakePressed = True
  elif event == 'gas':
    cs.gasPressed = True
  else:
    cs.softHoldActive = 1
  advance(sm)
  p.update(sm)
  assert p.camera_input_valid and p.output_a_target <= 0.
  if event == 'stopping':
    assert p.output_should_stop
  if event == 'hard_braking':
    assert p.output_a_target <= -1.49


def test_profile_only_on_supported_active_longitudinal(monkeypatch):
  p, sm = setup_planner(monkeypatch, dec=False)
  for _ in range(40):
    advance(sm)
    p.update(sm)
  assert p.longitudinal_mode == 'blended' and p.output_a_target == pytest.approx(-.04)
  cp = p.CP
  assert selected_sunny_mode(cp, 0) == selected_sunny_mode(cp, 88) == SUNNY_BLENDED
  assert selected_sunny_mode(cp, 1) == SUNNY_RELEASE
  cp.radarUnavailable = True
  assert selected_sunny_mode(cp, 1) == selected_sunny_mode(cp, 2) == SUNNY_RELEASE_VISION
  cp.passive = True
  assert selected_sunny_mode(cp, 2) == SUNNY_BLENDED
  cp.passive, cp.openpilotLongitudinalControl = False, False
  assert selected_sunny_mode(cp, 1) == SUNNY_BLENDED
