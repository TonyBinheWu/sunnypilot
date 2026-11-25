"""Production control/CAN boundaries with real platform parameters; no live IPC.

Angle cases exercise the supported protocol branch synthetically. They do not
assert that every listed trim physically accepts angle control.
"""
import math
import time
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.car.hyundai.interface import CarInterface
from opendbc.car.hyundai.phase1 import PHASE1_PLATFORMS, phase1_enabled
from opendbc.car.hyundai.values import CAR, HyundaiFlags
from opendbc.car.hyundai.tests.test_steering_handover_controller import setup_controller, step
from openpilot.selfdrive.controls.lib import latcontrol_torque
from openpilot.selfdrive.controls.lib.drive_helpers import clip_curvature
from openpilot.selfdrive.controls.lib.hkg_phase1 import CurveSpeedEnvelope
from openpilot.selfdrive.controls.tests.test_hkg_phase1 import model, production_method, state
from openpilot.selfdrive.controls.tests.test_lateral_startup_control import control_fixture

FAMILIES = ('KIA_EV6', 'HYUNDAI_IONIQ_5', 'KIA_CARNIVAL_4TH_GEN', 'KIA_SORENTO_4TH_GEN')
PLATFORM_CONTROLS = [(p, 'angle' if CAR[p].config.flags & HyundaiFlags.ANGLE_CONTROL else 'torque')
                     for p in sorted(PHASE1_PLATFORMS)]


def platform(fingerprint, kind=None, camera=False):
  cp = CarInterface.get_non_essential_params(fingerprint)
  if kind is not None:
    # PE angle platforms must never be force-converted to a torque interface.
    assert kind == 'angle' or not cp.flags & HyundaiFlags.ANGLE_CONTROL
    cp.steerControlType = kind
  if kind == 'angle':
    cp.flags |= int(HyundaiFlags.ANGLE_CONTROL)
  if camera:
    cp.flags |= int(HyundaiFlags.CAMERA_SCC)
  return cp


def controls(monkeypatch, cp, enabled, speed):
  saved = {'HkgPhase1Assist': enabled, 'LowSpeedSteerReserve': False, 'CustomSteerMax': 0}
  params = NS(get_bool=lambda k: bool(saved.get(k, False)), get_int=lambda k: int(saved.get(k, 0)),
              get_float=lambda k: float(saved.get(k, 0)))
  monkeypatch.setattr(latcontrol_torque, 'Params', lambda: params)
  controller, tick = control_fixture(phase1=phase1_enabled(cp, params), cp_override=cp.as_reader())
  controller.lateral_startup.ready = controller.lateral_started = True
  controller.desired_curvature = 0.
  cs = controller.sm['carState']
  cs.steeringAngleDeg = 0.
  cs.vEgo = cs.vEgoRaw = speed / 3.6
  cs.wheelSpeeds = dict.fromkeys(('fl', 'fr', 'rl', 'rr'), speed / 3.6)
  return controller, tick, saved


def fresh_tick(controller, tick, frame, target):
  controller.sm['modelV2'].frameId = frame // 5
  controller.sm['modelV2'].action.desiredCurvature = target
  controller.sm.recv_time['modelV2'] = time.monotonic()
  return tick()[0]


@pytest.mark.parametrize('fingerprint,kind', PLATFORM_CONTROLS)
@pytest.mark.parametrize('speed', [25., 35., 60., 100.])
@pytest.mark.parametrize('sign', [-1, 1])
def test_all_registered_platforms_switch_roundtrip_keeps_final_limits(monkeypatch, fingerprint, kind, speed, sign):
  cp = platform(fingerprint, kind)
  target = sign * (.01 if speed <= 35 else .0001)
  first = []
  for enabled in (False, True, False):
    controller, tick, saved = controls(monkeypatch, cp, enabled, speed)
    before = cp.to_dict()
    previous = controller.desired_curvature
    trace = []
    for frame in range(70):
      cc = fresh_tick(controller, tick, frame, target)
      values = (cc.actuators.curvature, cc.actuators.torque, cc.actuators.steeringAngleDeg)
      assert all(math.isfinite(v) for v in values)
      assert abs(cc.actuators.curvature) <= abs(target) + 1e-9
      # The same production physical limiter must accept every emitted target.
      actual = controller.desired_curvature
      bounded, _ = clip_curvature(controller.sm['carState'].vEgo, previous, actual, 0.)
      assert actual == pytest.approx(bounded, abs=1e-12)
      assert cc.actuators.curvature == float(np.float32(actual))
      previous = actual
      trace.append(values)
    first.append(trace)
    assert cp.to_dict() == before  # no HDA/protocol/safety parameter mutation
    assert saved == {'HkgPhase1Assist': enabled, 'LowSpeedSteerReserve': False, 'CustomSteerMax': 0}
    # Live OFF must stop selecting the added profile without clearing PID state.
    saved['HkgPhase1Assist'] = False
    controller.hkg_phase1_enabled = phase1_enabled(cp, NS(get_bool=lambda k, values=saved: bool(values.get(k, False))))
    pid = getattr(controller.LaC, 'pid', None)
    incoming_integral = []
    if pid is not None:
      pid.i = .25
      def observe_update(*args, original=pid.update, instance=pid, observed=incoming_integral, **kwargs):
        observed.append(instance.i)
        return original(*args, **kwargs)
      monkeypatch.setattr(pid, 'update', observe_update)
    fresh_tick(controller, tick, 70, target)
    if pid is not None:
      assert controller.LaC.pid is pid
      # Preserve the input history; normal PID anti-windup may then reduce it.
      assert incoming_integral[0] == .25
    for frame in range(71, 150):
      fresh_tick(controller, tick, frame, target)
    assert not controller.hkg_phase1_enabled
    if pid is not None:
      assert not controller.LaC.reserve_enabled
  assert first[0] == first[2]  # OFF after an ON run reproduces the original trace
  if first[0][0][0] != 0.:  # respect any platform minimum steering speed
    if speed <= 35:
      # At 35 km/h both can initially hit the same physical jerk ceiling.
      # Added response must respect that boundary, then catch up sooner once
      # filtering, rather than the safety limiter, becomes the constraint.
      assert all(sign * on[0] >= sign * off[0] - 1e-9 for off, on in zip(first[0], first[1], strict=True))
      assert any(sign * on[0] > sign * off[0] + 1e-9 for off, on in zip(first[0], first[1], strict=True))
    else:
      assert abs(first[1][0][0]) < abs(first[0][0][0])


@pytest.mark.parametrize('fingerprint', FAMILIES)
@pytest.mark.parametrize('kind', ['torque', 'angle'])
@pytest.mark.parametrize('veto', ['driver', 'stale', 'can', 'temporary', 'permanent', 'fault_event', 'disengage'])
def test_family_switch_does_not_change_driver_fault_or_stale_fallback(monkeypatch, fingerprint, kind, veto):
  cp = platform(fingerprint, kind)
  outputs = []
  for enabled in (False, True):
    controller, tick, _ = controls(monkeypatch, cp, enabled, 100.)
    cs = controller.sm['carState']
    controller.sm['modelV2'].action.desiredCurvature = .0001
    if veto == 'driver':
      cs.steeringPressed = True
    elif veto == 'stale':
      controller.sm.recv_time['modelV2'] = time.monotonic() - 1.
    elif veto == 'can':
      cs.canValid = False
    elif veto == 'temporary':
      cs.steerFaultTemporary = True
    elif veto == 'permanent':
      cs.steerFaultPermanent = True
    elif veto == 'fault_event':
      from openpilot.cereal import log
      controller.sm['onroadEvents'] = [log.OnroadEvent.new_message(name='pandaCanFault')]
    else:
      cs.latEnabled = False
    cc = tick()[0]
    outputs.append((cc.latActive, cc.actuators.curvature, cc.actuators.torque, cc.actuators.steeringAngleDeg))
    if veto in ('temporary', 'permanent', 'fault_event', 'disengage'):
      assert not cc.latActive
      assert cc.actuators.torque == 0.
  assert outputs[0] == outputs[1]


@pytest.mark.parametrize('fingerprint', sorted(PHASE1_PLATFORMS))
@pytest.mark.parametrize('mode,direct', [('acc', True), ('acc', False), ('blended', True)])
def test_each_platform_curve_speed_off_on_off_resets_without_changing_stock_acc(fingerprint, mode, direct):
  class Messages(dict):
    def all_checks(self, services):
      return True

  cp = platform(fingerprint)
  cp.openpilotLongitudinalControl = direct
  saved = {'HkgPhase1Assist': False}
  params = NS(get_bool=lambda k: saved.get(k, False))
  planner = NS(CP=cp, hkg_phase1_enabled=False, hkg_curve=CurveSpeedEnvelope(), dt=.05, mpc=NS(mode=mode))
  sm = Messages(carState=state(), modelV2=model(), carControl=NS(latActive=True, longActive=direct), selfdriveState=NS(enabled=True))
  call = production_method('update_hkg_curve_speed')
  for enabled in (False, True, False, True):
    saved['HkgPhase1Assist'] = enabled
    planner.hkg_phase1_enabled = phase1_enabled(cp, params)
    for frame in range(4):
      sm['modelV2'].frameId += 1
      sm.recv_time = {'modelV2': time.monotonic()}
      value = call(planner, sm, 30., False)
      if frame < 2:
        assert value == 30.  # no old confirmation leaks across mode changes
    assert (value < 30.) == (enabled and direct and mode == 'acc')
    if not enabled or not direct or mode != 'acc':
      assert planner.hkg_curve_ceiling is None


@pytest.mark.parametrize('fingerprint', FAMILIES)
@pytest.mark.parametrize('camera', [False, True])
@pytest.mark.parametrize('sign', [-1, 1])
def test_angle_can_protocol_and_authority_identical_for_same_requests(monkeypatch, fingerprint, camera, sign):
  traces = []
  for enabled in (False, True):
    cp = platform(fingerprint, 'angle', camera)
    controller, cs, cc, saved = setup_controller(monkeypatch, angle=True, camera=camera, cp_override=cp)
    saved['HkgPhase1Assist'] = int(enabled)
    cs.out.steeringPressed = False
    cs.out.steeringTorque = 0.
    cs.out.vEgo = cs.out.vEgoRaw = 7.
    cc.actuators.steeringAngleDeg = sign * 20.
    trace = []
    for _ in range(100):
      output, messages = step(controller, cs, cc)
      assert abs(output.steeringAngleDeg) <= controller.params.ANGLE_LIMITS.STEER_ANGLE_MAX
      assert not controller.reserve_enabled
      trace.append((output.steeringAngleDeg, output.torqueOutputCan, messages))
    traces.append(trace)
  assert traces[0] == traces[1]
