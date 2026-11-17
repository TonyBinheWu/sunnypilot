import ast
import math
import time
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.car import structs
from opendbc.car.hyundai.phase1 import PHASE1_PLATFORMS, supports_phase1, phase1_enabled
from opendbc.car.hyundai.low_speed_steer_reserve import supports_reserve
from opendbc.car.hyundai.values import CAR
from opendbc.car.hyundai.interface import CarInterface
from openpilot.selfdrive.controls.lib.hkg_phase1 import CurveSpeedEnvelope, curve_speed_target, low_speed_response_tau, smooth_curvature
from openpilot.selfdrive.modeld.constants import ModelConstants

TIMES = np.array(ModelConstants.T_IDXS)


def model(curve=.012, speed=25., frame=1):
  curve = np.broadcast_to(curve, TIMES.shape)
  return NS(frameId=frame, position=NS(x=TIMES * speed, y=TIMES * 0., z=TIMES * 0.),
            velocity=NS(x=np.full_like(TIMES, speed)), orientationRate=NS(z=curve * speed))


def state(**kwargs):
  return structs.CarState(vEgo=25., canValid=True, gearShifter='drive', **kwargs)


def update(helper, m, cs=None, **kwargs):
  args = dict(enabled=True, fresh=True, active=True, dt=.05)
  args.update(kwargs)
  return helper.update(state() if cs is None else cs, m, 30., **args)


@pytest.mark.parametrize('fingerprint', sorted(PHASE1_PLATFORMS))
def test_every_registered_variant_supports_both_existing_control_interfaces(fingerprint):
  cp = CarInterface.get_non_essential_params(fingerprint)
  assert supports_phase1(cp)
  for kind in ('torque', 'angle'):
    cp.steerControlType = kind
    assert supports_phase1(cp)
  cp.dashcamOnly = True
  assert not supports_phase1(cp)


@pytest.mark.parametrize('fingerprint', [c for c in CAR if c not in PHASE1_PLATFORMS])
def test_other_hyundai_platforms_do_not_gain_authority(fingerprint):
  cp = NS(brand='hyundai', carFingerprint=fingerprint, dashcamOnly=False, notCar=False, steerControlType='torque')
  assert not supports_phase1(cp)


def test_setting_off_and_other_brand_are_inert():
  cp = NS(brand='hyundai', carFingerprint='KIA_EV6', dashcamOnly=False, notCar=False, steerControlType='torque')
  assert not phase1_enabled(cp, NS(get_bool=lambda k: False))
  assert phase1_enabled(cp, NS(get_bool=lambda k: k == 'HkgPhase1Assist'))
  cp.brand = 'toyota'
  assert not phase1_enabled(cp, NS(get_bool=lambda k: True))


def test_angle_variants_do_not_enter_torque_reserve():
  cp = CarInterface.get_non_essential_params('HYUNDAI_IONIQ_5')
  cp.steerControlType = 'angle'
  assert supports_phase1(cp)
  assert not supports_reserve(cp)


def test_low_speed_target_is_exactly_unchanged_and_large_requests_have_less_lag():
  for speed in (0., 5., 30/3.6, 40/3.6):
    assert smooth_curvature(.1, -.03, speed, .01) == pytest.approx(.1)
  small = smooth_curvature(.0001, 0., 30., .01) / .0001
  large = smooth_curvature(.01, 0., 30., .01) / .01
  assert 0 < small < large < 1


def test_low_speed_turn_in_reduces_only_existing_lag_with_speed_taper():
  assert low_speed_response_tau(.02, .01, 5., .1) == pytest.approx(.06)
  assert low_speed_response_tau(-.02, -.01, 5., .1) == pytest.approx(.06)
  assert low_speed_response_tau(.02, .01, 35/3.6, .1) == pytest.approx(.08)
  assert low_speed_response_tau(.02, .01, 40/3.6, .1) == .1
  for target, previous in ((.01, .02), (-.02, .01), (.01, .01)):
    assert low_speed_response_tau(target, previous, 5., .1) == .1
  assert low_speed_response_tau(.02, .01, 0., .1) == .1
  assert low_speed_response_tau(.02, .01, 5., 0.) == 0.


def test_highway_small_oscillation_is_attenuated_without_bias_or_unbounded_lag():
  original, filtered, previous = [], [], 0.
  for i in range(1500):
    value = .001 + .0001 * math.sin(i * .01 * 2 * math.pi * 3)
    previous = smooth_curvature(value, previous, 30., .01)
    original.append(value)
    filtered.append(previous)
  assert np.std(filtered[500:]) < .65 * np.std(original[500:])
  assert np.mean(filtered[500:]) == pytest.approx(.001, abs=1e-6)
  previous = 0.
  for _ in range(25):
    previous = smooth_curvature(.001, previous, 30., .01)
  assert previous > .95 * .001


def test_highway_shaping_combines_with_original_filter_without_multiplying_lag():
  previous = 0.
  for _ in range(60):
    previous = smooth_curvature(.0001, previous, 30., .01, base_tau=.1)
  # Base .1 + at most .08 s: >95% response after .6 s. Applying
  # both filters against the final previous value instead would fail this.
  assert .95 * .0001 < previous <= .0001
  expected = (1. - math.exp(-.01 / .06)) * .02
  assert smooth_curvature(.02, 0., 5., .01, base_tau=.06) == pytest.approx(expected)


@pytest.mark.parametrize('sign', [-1, 1])
def test_curve_preview_slows_before_entry_and_release_is_bounded(sign):
  h = CurveSpeedEnvelope()
  m = model(np.where(TIMES >= 2., sign * .012, 0.))
  assert curve_speed_target(m, 25.) < 25.
  assert update(h, m) == 30.
  # Same frame cannot confirm or advance the envelope.
  for _ in range(3):
    assert update(h, m) == 30.
  m.frameId = 2
  assert update(h, m) == 30.
  m.frameId = 3
  previous = update(h, m)
  assert 24.9 < previous < 25.
  for frame in range(4, 40):
    m.frameId = frame
    value = update(h, m)
    assert previous - .06 - 1e-9 <= value <= previous
    previous = value
  straight = model(0., frame=40)
  value = update(h, straight)
  assert value - previous == pytest.approx(.025)
  assert update(h, straight) == value
  for _ in range(6):
    update(h, straight)
  assert h.ceiling is None


def test_current_bend_minimum_speed_never_becomes_stop_and_lower_cruise_wins():
  h = CurveSpeedEnvelope()
  for i in range(500):
    value = update(h, model(.19, frame=i))
  assert value >= 5.
  assert h.update(state(), model(frame=501), 4., enabled=True, fresh=True, active=True, dt=.05) == 4.


@pytest.mark.parametrize('field', ['gasPressed', 'brakePressed', 'steeringPressed', 'canTimeout', 'steerFaultTemporary', 'steerFaultPermanent'])
def test_driver_and_fault_reset_prevents_stale_speed_constraint(field):
  h = CurveSpeedEnvelope()
  for i in range(4):
    update(h, model(frame=i))
  assert h.ceiling is not None
  cs = state(**{field: True})
  assert update(h, model(frame=5), cs) == 30.
  assert h.ceiling is None
  assert update(h, model(frame=6)) == 30.


@pytest.mark.parametrize('kwargs', [dict(enabled=False), dict(fresh=False), dict(active=False)])
def test_disabled_stale_and_disengaged_are_exact_passthrough(kwargs):
  h = CurveSpeedEnvelope()
  for i in range(4):
    update(h, model(frame=i))
  assert update(h, model(frame=6), **kwargs) == 30.
  assert h.ceiling is None


def test_invalid_geometry_repeated_or_restarted_model_cannot_latch_a_cap():
  h = CurveSpeedEnvelope()
  for i in range(4):
    update(h, model(frame=i))
  assert update(h, model(frame=0)) == 30.
  m = model(frame=5)
  m.position.x[4] = math.nan
  assert update(h, m) == 30.
  m = model(frame=6)
  m.orientationRate.z = [0.]
  assert update(h, m) == 30.
  m = model(0.)
  m.orientationRate.z[10] = 2.
  assert curve_speed_target(m, 25.) == math.inf


def test_invalid_far_tail_does_not_discard_valid_near_preview():
  m = model()
  expected = curve_speed_target(m, 25.)
  m.position.x[-1] = math.nan
  assert curve_speed_target(m, 25.) == expected


def production_method(name):
  path = Path(__file__).resolve().parents[1] / 'lib/longitudinal_planner.py'
  cls = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.ClassDef) and n.name == 'LongitudinalPlanner')
  node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
  scope = {"time": time}
  exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), scope)
  return scope[name]


@pytest.mark.parametrize('direct,mode,lat,long,enabled,valid,reset', [
  (True, 'acc', True, True, True, True, False),
  (False, 'acc', True, True, True, True, False),
  (True, 'blended', True, True, True, True, False),
  (True, 'acc', False, True, True, True, False),
  (True, 'acc', True, False, True, True, False),
  (True, 'acc', True, True, False, True, False),
  (True, 'acc', True, True, True, False, False),
  (True, 'acc', True, True, True, True, True),
])
def test_production_planner_admission(direct, mode, lat, long, enabled, valid, reset):
  class SM(dict):
    frame = 10
    recv_time = {'modelV2': time.monotonic()}

    def all_checks(self, services):
      return valid

  sm = SM(carState=state(), modelV2=model(), carControl=NS(latActive=lat, longActive=long), selfdriveState=NS(enabled=enabled))
  planner = NS(hkg_phase1_enabled=True, hkg_curve=CurveSpeedEnvelope(), dt=.05,
               CP=NS(openpilotLongitudinalControl=direct), mpc=NS(mode=mode))
  for frame in range(4):
    sm['modelV2'].frameId = frame
    value = production_method('update_hkg_curve_speed')(planner, sm, 30., reset)
  assert (value < 30.) == (direct and mode == 'acc' and lat and long and enabled and valid and not reset)
  # Expired data releases immediately, regardless of a previously qualified cap.
  sm.recv_time = {'modelV2': time.monotonic() - .3}
  assert production_method('update_hkg_curve_speed')(planner, sm, 30., reset) == 30.


@pytest.mark.parametrize('carrot_speed,cap,mode,reset,expected', [
  (30., 20., 'acc', False, 20.), (10., 20., 'acc', False, 10.),
  (0., 20., 'acc', False, 0.), (30., None, 'acc', False, 30.),
  (30., float('nan'), 'acc', False, 30.), (30., -1., 'acc', False, 30.),
  (30., 20., 'acc', True, 30.), (30., 20., 'blended', False, 35.),
])
def test_mpc_curve_ceiling_survives_carrot_speed_assignment_without_raising_stop_target(carrot_speed, cap, mode, reset, expected):
  # Execute the actual MPC input preparation. The native numerical solver and
  # obstacle optimization are outside this boundary regression.
  import copy
  from openpilot.cereal import log
  path = Path(__file__).resolve().parents[1] / 'lib/longitudinal_mpc_lib/long_mpc.py'
  cls = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.ClassDef) and n.name == 'LongitudinalMpc')
  method = copy.deepcopy(next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'update'))
  stop = next(i for i,n in enumerate(method.body) if isinstance(n, ast.Assign) and
              any(isinstance(t, ast.Name) and t.id == 'lead_0_obstacle' for t in n.targets))
  method.body = method.body[:stop] + [ast.Return(value=ast.Tuple(elts=[ast.Name(id='v_cruise', ctx=ast.Load()),
    ast.Name(id='stop_x', ctx=ast.Load())], ctx=ast.Load()))]
  scope = dict(log=log, math=math, np=np, A_CHANGE_COST_STARTING=200., desired_follow_distance=lambda *a: 0.)
  exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(path), 'exec'), scope)
  mpc = NS(mode=mode, x0=[0.,25.,0.], process_lead=lambda lead: (np.zeros((2,2)), 0.))
  carrot = NS(get_T_FOLLOW=lambda *a: 1.5, jerk_factor=1., comfort_brake=2.5, stop_distance=6.,
              v_cruise=carrot_speed, stop_dist=5., mode=mode)
  speed, stop_distance = scope['update'](mpc, carrot, reset, NS(leadOne=NS(status=False), leadTwo=NS(status=False)),
    35., None, None, None, None, curve_speed_ceiling=cap)
  assert speed == expected
  assert stop_distance == (1000. if mode == 'blended' else 5.)


def test_real_cereal_model_arrays_are_accepted():
  from openpilot.cereal import log
  m = model()
  wire_model = log.ModelDataV2.new_message(frameId=1,
    position=dict(x=m.position.x.tolist(), y=m.position.y.tolist(), z=m.position.z.tolist()),
    velocity=dict(x=m.velocity.x.tolist()), orientationRate=dict(z=m.orientationRate.z.tolist()))
  assert curve_speed_target(wire_model.as_reader(), 25.) == pytest.approx(curve_speed_target(m, 25.))


@pytest.mark.parametrize('fields', [dict(canValid=False), dict(standstill=True), dict(gearShifter='reverse'),
                                  dict(vEgo=2.), dict(vEgo=float('nan'))])
def test_invalid_vehicle_state_does_not_slow_or_retain_a_target(fields):
  cs = state()
  for k, v in fields.items():
    setattr(cs, k, v)
  helper = CurveSpeedEnvelope()
  for frame in range(6):
    assert update(helper, model(frame=frame), cs) == 30.
  assert helper.ceiling is None
