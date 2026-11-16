from types import SimpleNamespace as NS

import pytest

from opendbc.car import structs
from opendbc.car.hyundai import carcontroller
from opendbc.car.hyundai.low_speed_steer_reserve import LowSpeedSteerReserve, supports_reserve
from opendbc.car.hyundai.tests.test_steering_handover_controller import setup_controller, step


def state(**kw):
  return structs.CarState(canValid=True, vEgo=7, vEgoRaw=7, gearShifter='drive', **kw)


def warm(helper, cs=None, **kw):
  args = dict(enabled=True, active=True, cs=cs or state(), base=270, demand=1.2)
  args.update(kw)
  return [helper.update(model_frame=n // 5, **args) for n in range(100)]


@pytest.mark.parametrize('speed,ceiling', [(10, 409), (30, 409), (35, 339), (40, 270), (100, 270)])
@pytest.mark.parametrize('sign', [-1, 1])
def test_speed_ceiling_and_sustained_demand(speed, ceiling, sign):
  cs = state()
  cs.vEgo = cs.vEgoRaw = speed / 3.6
  trace = warm(LowSpeedSteerReserve(), cs, demand=sign * 1.2)
  assert trace[:29] == [270] * 29
  assert trace[-1] == ceiling


@pytest.mark.parametrize('overrides', [dict(enabled=False), dict(active=False), dict(demand=.8),
                                    dict(demand=float('nan')), dict(base=409), dict(base=450)])
def test_no_unrequested_boost(overrides):
  assert set(warm(LowSpeedSteerReserve(), **overrides)) == {overrides.get('base', 270)}


@pytest.mark.parametrize('field,value', [('canValid', False), ('canTimeout', True), ('steerFaultTemporary', True),
                                       ('steerFaultPermanent', True), ('steeringPressed', True),
                                       ('standstill', True), ('steeringTorque', 251), ('gearShifter', 'reverse'),
                                       ('vEgoRaw', float('nan'))])
def test_health_loss_cancels_reserve_and_requires_requalification(field, value):
  helper, cs = LowSpeedSteerReserve(), state()
  assert warm(helper, cs)[-1] == 409
  previous = getattr(cs, field)
  setattr(cs, field, value)
  assert helper.update(enabled=True, active=True, cs=cs, base=270, model_frame=100, demand=1.2) == 270
  setattr(cs, field, previous)
  assert helper.update(enabled=True, active=True, cs=cs, base=270, model_frame=101, demand=1.2) == 270


def test_missing_stale_model_and_direction_reversal():
  helper, cs = LowSpeedSteerReserve(), state()
  assert warm(helper, cs)[-1] == 409
  args = dict(enabled=True, active=True, cs=cs, base=270, demand=1.2)
  assert helper.update(model_frame=None, **args) == 270
  assert all(helper.update(model_frame=19, **args) == 270 for _ in range(50))
  assert warm(helper, cs)[-1] == 409
  assert helper.update(model_frame=100, **dict(args, demand=-1.2)) == 270


def test_filtered_speed_cannot_hide_fast_raw_speed():
  cs = state()
  cs.vEgoRaw = 40 / 3.6
  assert set(warm(LowSpeedSteerReserve(), cs)) == {270}


def torque_fixture(monkeypatch, enabled=True):
  controller, cs, cc, settings = setup_controller(monkeypatch, angle=False, camera=False)
  # Fixture CP is generic: this test explicitly selects supported Hyundai torque control.
  controller.reserve_supported = True
  settings['LowSpeedSteerReserve'] = int(enabled)
  monkeypatch.setattr(carcontroller, 'Params',
                      lambda: NS(get_int=lambda k: settings.get(k, 0), get_bool=lambda k: bool(settings.get(k, 0))))
  cs.out = state()
  cc.actuators.torque = 1.5
  return controller, cs, cc, settings


@pytest.mark.parametrize('sign', [-1, 1])
def test_real_can_packing_rates_and_feedback_scale(monkeypatch, sign):
  controller, cs, cc, _ = torque_fixture(monkeypatch)
  cc.actuators.torque *= sign
  trace = [step(controller, cs, cc) for _ in range(300)]
  values = [a.torqueOutputCan for a, _ in trace]
  assert abs(values[-1]) == 405  # 1.5 * unchanged 270 baseline
  assert all(abs(v) <= 409 for v in values)
  assert all(abs(b - a) <= 2 for a, b in zip(values, values[1:]))
  output, messages = trace[-1]
  data = next(data for addr, data, _ in messages if addr == 0x12a)
  assert ((int.from_bytes(data, 'little') >> 41) & 0x7ff) - 1024 == sign * 405
  assert output.torque == pytest.approx(sign * 1.5)
  assert controller.params.STEER_MAX == 270


def test_small_requests_unchanged_and_disabled_restores_baseline(monkeypatch):
  controller, cs, cc, settings = torque_fixture(monkeypatch)
  cc.actuators.torque = .5
  assert [step(controller, cs, cc) for _ in range(100)][-1][0].torqueOutputCan == 135
  cc.actuators.torque = 2
  assert [step(controller, cs, cc) for _ in range(200)][-1][0].torqueOutputCan == 409
  settings['LowSpeedSteerReserve'] = 0
  trace = [step(controller, cs, cc)[0].torqueOutputCan for _ in range(150)]
  assert trace[-1] == 270
  assert all(abs(b - a) <= 3 for a, b in zip(trace, trace[1:]))
  cc.latActive = False
  assert step(controller, cs, cc)[0].torqueOutputCan == 0


def test_custom_limit_reverting_to_zero_restores_factory_scale(monkeypatch):
  controller, cs, cc, settings = torque_fixture(monkeypatch, enabled=False)
  settings['CustomSteerMax'] = 300
  cc.actuators.torque = .5
  assert [step(controller, cs, cc) for _ in range(200)][-1][0].torqueOutputCan == 150
  settings['CustomSteerMax'] = 0
  assert [step(controller, cs, cc) for _ in range(100)][-1][0].torqueOutputCan == 135


def test_support_scope():
  cp = structs.CarParams(brand='hyundai', steerControlType='torque')
  cp.lateralTuning.init('torque')
  from opendbc.car.hyundai.values import HyundaiFlags
  cp.flags = int(HyundaiFlags.CANFD)
  assert supports_reserve(cp)
  cp.flags |= int(HyundaiFlags.ANGLE_CONTROL)
  assert not supports_reserve(cp)
  cp.flags = 0
  assert not supports_reserve(cp)
  cp.brand = 'toyota'
  cp.flags = int(HyundaiFlags.CANFD)
  assert not supports_reserve(cp)
