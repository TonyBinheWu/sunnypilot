from types import SimpleNamespace as NS

import pytest

from opendbc.car import structs
from opendbc.car.hyundai.values import HyundaiFlags
from openpilot.selfdrive.controls.lib import latcontrol_torque


def make_controller(monkeypatch, enabled, fingerprint="", phase1=False):
  settings = {'LowSpeedSteerReserve': enabled, 'CustomSteerMax': 0, 'HkgPhase1Assist': phase1}
  monkeypatch.setattr(latcontrol_torque, 'Params', lambda: NS(
    get_bool=lambda k: bool(settings.get(k, 0)), get_int=lambda k: settings.get(k, 0)))
  cp = structs.CarParams(carFingerprint=fingerprint, brand='hyundai', flags=int(HyundaiFlags.CANFD), steerControlType='torque', steerLimitTimer=.4)
  cp.lateralTuning.init('torque')
  cp.lateralTuning.torque = dict(kp=1, ki=0, kf=1, useSteeringAngle=True, latAccelFactor=3.2)
  # Controlled geometry/torque mapping isolates the real controller/PID clipping.
  ci = NS(use_nnff=False, use_nnff_lite=False,
          torque_from_lateral_accel=lambda: lambda inputs, *a, **kw: inputs.lateral_acceleration / 3.2)
  lac = latcontrol_torque.LatControlTorque(cp.as_reader(), ci)
  cs = structs.CarState(vEgo=7, vEgoRaw=7, gearShifter='drive', canValid=True,
                        wheelSpeeds=dict(fl=7,fr=7,rl=7,rr=7))
  vm = NS(get_steer_from_curvature=lambda *a: 0., calc_curvature=lambda *a: 0.)
  lp = NS(roll=0., angleOffsetDeg=0.)
  cc = structs.CarControl(latActive=True)
  return lac, cs, vm, lp, cc, settings


def run(fixture, curvature, ticks=150):
  lac, cs, vm, lp, cc, _ = fixture
  trace = []
  for _ in range(ticks):
    model = NS(frameId=lac.frame // 5, orientation=NS(x=[]))
    trace.append(lac.update(True, cs, vm, lp, False, curvature, cc, False, model)[0])
  return trace


@pytest.mark.parametrize('sign', [-1, 1])
def test_real_pid_extends_clipping_without_changing_small_demand(monkeypatch, sign):
  off = run(make_controller(monkeypatch, False), sign * .003)
  on = run(make_controller(monkeypatch, True), sign * .003)
  assert on == off
  off = run(make_controller(monkeypatch, False), sign * .04)
  on = run(make_controller(monkeypatch, True), sign * .04)
  assert max(map(abs, off)) == 1
  assert abs(on[-1]) == pytest.approx(409 / 270)
  assert all(abs(v) <= 1 for v in on[:30])


def test_real_pid_speed_exit_and_setting_off(monkeypatch):
  f = make_controller(monkeypatch, True)
  assert abs(run(f, .04)[-1]) > 1
  f[1].vEgo = f[1].vEgoRaw = 40 / 3.6
  assert all(abs(v) <= 1 for v in run(f, .04, 5))
  f[1].vEgo = f[1].vEgoRaw = 7
  assert abs(run(f, .04)[-1]) > 1
  f[-1]['LowSpeedSteerReserve'] = False
  assert abs(run(f, .04, 100)[-1]) == 1


def test_manual_max_does_not_change_enabled_factory_normalization(monkeypatch):
  f = make_controller(monkeypatch, True)
  f[-1]['CustomSteerMax'] = 409
  assert abs(run(f, .04)[-1]) == pytest.approx(409 / 270)
  assert f[0].reserve_base == 270
  f[1].vEgo = f[1].vEgoRaw = 100 / 3.6
  assert abs(run(f, .04)[-1]) <= 1
  assert f[0].reserve_base == 270
  f[-1]['LowSpeedSteerReserve'] = False
  run(f, .04, 100)
  assert f[0].reserve_base == 409


@pytest.mark.parametrize('fingerprint', ['KIA_EV6', 'HYUNDAI_IONIQ_5', 'KIA_CARNIVAL_4TH_GEN', 'KIA_SORENTO_4TH_GEN'])
def test_phase1_switch_uses_existing_real_pid_headroom_and_live_off(monkeypatch, fingerprint):
  f = make_controller(monkeypatch, False, fingerprint, True)
  assert abs(run(f, .04)[-1]) == pytest.approx(409 / 270)
  assert f[0].reserve_base == 270
  f[-1]['HkgPhase1Assist'] = False
  assert abs(run(f, .04, 100)[-1]) == 1


def test_phase1_does_not_enable_reserve_on_other_platform(monkeypatch):
  f = make_controller(monkeypatch, False, 'HYUNDAI_TUCSON_4TH_GEN', True)
  assert abs(run(f, .04)[-1]) == 1
