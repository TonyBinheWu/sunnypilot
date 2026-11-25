import pytest

from opendbc.car import structs
from opendbc.car.hyundai.low_speed_steer_reserve import LowSpeedSteerReserve, supports_reserve
from opendbc.car.hyundai.tests.test_steering_handover_controller import setup_controller, step
from opendbc.car.hyundai.values import CAR, HyundaiFlags, uses_ev6_adas_torque


def state(**kw):
  return structs.CarState(canValid=True, vEgo=7, vEgoRaw=7, gearShifter='drive',
                          wheelSpeeds=dict(fl=7,fr=7,rl=7,rr=7), **kw)


def warm(helper, cs=None, **kw):
  args = dict(enabled=True, active=True, cs=cs or state(), base=270, demand=2.)
  args.update(kw)
  return [helper.update(model_frame=n // 5, **args) for n in range(100)]


@pytest.mark.parametrize('speed,ceiling', [(10, 409), (30, 409), (35, 339), (40, 270), (100, 270)])
@pytest.mark.parametrize('sign', [-1, 1])
def test_speed_ceiling_and_sustained_demand(speed, ceiling, sign):
  cs = state()
  cs.vEgo = cs.vEgoRaw = speed / 3.6
  trace = warm(LowSpeedSteerReserve(), cs, demand=sign * 2.)
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


def torque_fixture(monkeypatch, enabled=True, cp=None):
  controller, cs, cc, settings = setup_controller(monkeypatch, angle=False, camera=False, cp_override=cp)
  # Fixture CP is generic: this test explicitly selects supported Hyundai torque control.
  controller.reserve_supported = True
  settings['LowSpeedSteerReserve'] = int(enabled)
  cs.out = state()
  cc.actuators.torque = 1.5
  return controller, cs, cc, settings


def ev6_adas_controller(monkeypatch, enabled=False):
  model = CAR.KIA_EV6
  flags = HyundaiFlags.CANFD | HyundaiFlags.CANFD_HDA2
  cp = structs.CarParams(brand='hyundai', carFingerprint=model, flags=int(flags), steerControlType='torque',
                         wheelbase=model.config.specs.wheelbase, steerRatio=model.config.specs.steerRatio)
  cp.lateralTuning.init('torque')
  controller, cs, cc, settings = torque_fixture(monkeypatch, enabled=enabled, cp=cp)
  cs.cam_0x362 = cs.cam_0x2a4 = None
  return controller, cs, cc, settings


@pytest.mark.parametrize('sign', [-1, 1])
@pytest.mark.parametrize('desire,normal,lane_change,expected_step', [(0, 5, 1, 2), (3, 1, 5, 2), (0, 1, 5, 1), (4, 5, 1, 1)])
def test_ev6_adas_manual_rise_during_sustained_turn(monkeypatch, sign, desire, normal, lane_change, expected_step):
  controller, cs, cc, settings = ev6_adas_controller(monkeypatch)
  settings.update(CustomSteerDeltaUp=normal, CustomSteerDeltaUpLC=lane_change, MaxAngleFrames=100)
  cc.hudControl.modelDesire = desire
  cc.actuators.torque = sign * 0.8
  cs.out.steeringAngleDeg = sign * 360
  requests = []
  for frame in range(183):
    actuators, messages = step(controller, cs, cc)
    data, = [data for addr, data, bus in messages if addr == 0x50 and bus == 0]
    torque = ((int.from_bytes(data, 'little') >> 41) & 0x7ff) - 1024
    assert torque == actuators.torqueOutputCan == sign * min(round(384 * 0.8), (frame + 1) * expected_step)
    requests.append(bool(data[6] & 0x10))
  assert requests == ([True] * 89 + [False] * 2) * 2 + [True]
  assert (settings['CustomSteerDeltaUp'], settings['CustomSteerDeltaUpLC']) == (normal, lane_change)


@pytest.mark.parametrize('sign', [-1, 1])
@pytest.mark.parametrize('reserve,phase1', [(False, False), (True, False), (False, True), (True, True)])
def test_ev6_adas_speed_boundary_and_driver_withdrawal(monkeypatch, sign, reserve, phase1):
  controller, cs, cc, settings = ev6_adas_controller(monkeypatch, reserve)
  settings.update(HkgPhase1Assist=int(phase1), CustomSteerMax=30000, CustomSteerDeltaDown=1)
  cc.actuators.torque = sign * 1.5
  cs.out.vEgoRaw = 10.999
  def command():
    output, _ = step(controller, cs, cc)
    return sign * output.torqueOutputCan
  assert [command() for _ in range(195)] == [min(2 * n, 384) for n in range(1, 196)]
  cs.out.vEgoRaw = 11.0
  assert [command() for _ in range(20)] == [max(330, 384 - 3 * n) for n in range(1, 21)]
  cs.out.vEgoRaw = 10.999
  assert [command() for _ in range(27)] == list(range(332, 385, 2))
  cs.out.steeringPressed = True
  cs.out.steeringTorque = -1000 * sign
  assert [command() for _ in range(130)] == [max(0, 384 - 3 * n) for n in range(1, 131)]
  cs.out.steeringPressed, cs.out.steeringTorque = False, 0
  settings['CustomSteerMax'] = 150
  assert [command() for _ in range(200)][-1] == 150


@pytest.mark.parametrize('field,value', [('canValid', False), ('canTimeout', True), ('steerFaultTemporary', True),
                                         ('steerFaultPermanent', True), ('vEgoRaw', float('nan')), ('vEgoRaw', -1)])
def test_ev6_adas_fault_releases_and_recovers_from_zero(monkeypatch, field, value):
  controller, cs, cc, _ = ev6_adas_controller(monkeypatch)
  for _ in range(100):
    step(controller, cs, cc)
  healthy = getattr(cs.out, field)
  setattr(cs.out, field, value)
  output, msgs = step(controller, cs, cc)
  assert output.torqueOutputCan == 0
  data, = [data for addr, data, bus in msgs if addr == 0x50 and bus == 0]
  assert not (data[6] & 0x10)
  setattr(cs.out, field, healthy)
  assert step(controller, cs, cc)[0].torqueOutputCan == 2


@pytest.mark.parametrize('model,hda2,extra,protocol,expected', [
  (CAR.KIA_EV6, True, 0, 'torque', True),
  (CAR.KIA_EV6, True, HyundaiFlags.CANFD_HDA2_ALT_STEERING, 'torque', True),
  (CAR.KIA_EV6, True, HyundaiFlags.CAMERA_SCC, 'torque', False),
  (CAR.KIA_EV6, True, HyundaiFlags.CANFD_CAMERA_SCC, 'torque', False),
  (CAR.KIA_EV6, False, 0, 'torque', False),
  (CAR.KIA_EV6, True, HyundaiFlags.ANGLE_CONTROL, 'angle', False),
  (CAR.KIA_EV6_PE, True, 0, 'torque', False),
  (CAR.HYUNDAI_IONIQ_5, True, 0, 'torque', False),
])
def test_ev6_adas_scope(model, hda2, extra, protocol, expected):
  flags = HyundaiFlags.CANFD | extra | (HyundaiFlags.CANFD_HDA2 if hda2 else 0)
  cp = structs.CarParams(carFingerprint=model, steerControlType=protocol, flags=int(flags))
  assert uses_ev6_adas_torque(cp) is expected


@pytest.mark.parametrize('sign', [-1, 1])
@pytest.mark.parametrize('camera_scc', [False, True])
def test_sorento_reserve_reaches_target_at_factory_rise_rate(monkeypatch, sign, camera_scc):
  model = CAR.KIA_SORENTO_2024
  flags = HyundaiFlags.CANFD | (HyundaiFlags.CANFD_HDA2 | HyundaiFlags.CAMERA_SCC if camera_scc else 0)
  cp = structs.CarParams(brand='hyundai', carFingerprint=model, flags=int(flags),
                         steerControlType='torque', wheelbase=model.config.specs.wheelbase, steerRatio=model.config.specs.steerRatio)
  cp.lateralTuning.init('torque')
  controller, cs, cc, settings = torque_fixture(monkeypatch, enabled=False, cp=cp)
  settings['HkgPhase1Assist'] = 1
  cc.actuators.torque = sign * 1.5
  previous = 0
  for _ in range(250):
    _, messages = step(controller, cs, cc)
    payload = next(data for addr, data, _ in messages if addr == 0x12a)
    torque = ((int.from_bytes(payload, 'little') >> 41) & 0x7ff) - 1024
    assert 0 <= sign * (torque - previous) <= 2
    previous = torque
  assert previous == sign * 405
  cc.latActive = False
  assert step(controller, cs, cc)[0].torqueOutputCan == 0


@pytest.mark.parametrize('sign', [-1, 1])
def test_real_can_packing_rates_and_feedback_scale(monkeypatch, sign):
  controller, cs, cc, _ = torque_fixture(monkeypatch)
  cc.actuators.torque *= sign
  trace = [step(controller, cs, cc) for _ in range(300)]
  values = [a.torqueOutputCan for a, _ in trace]
  assert abs(values[-1]) == 405  # 1.5 * unchanged 270 baseline
  assert all(abs(v) <= 409 for v in values)
  assert all(abs(b - a) <= 4 for a, b in zip(values, values[1:]))
  assert max(abs(b-a) for a,b in zip(values[:29],values[1:29])) <= 2
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


@pytest.mark.parametrize('demand,expected', [(1., 270), (1.1, 297), (1.2, 324), (1.5, 405), (2., 409)])
def test_only_requested_headroom_is_available(demand, expected):
  assert warm(LowSpeedSteerReserve(), demand=demand)[-1] == expected


def test_enabled_mode_uses_factory_max_and_slew_even_with_manual_values(monkeypatch):
  controller, cs, cc, settings = torque_fixture(monkeypatch)
  settings.update(CustomSteerMax=409, CustomSteerDeltaUp=20, CustomSteerDeltaDown=30,
                  CustomSteerDeltaUpLC=25, CustomSteerDeltaDownLC=35)
  cc.hudControl.modelDesire = 3
  cc.actuators.torque = 2.
  trace = [step(controller, cs, cc)[0].torqueOutputCan for _ in range(300)]
  assert trace[-1] == 409 and max(abs(b-a) for a,b in zip(trace, trace[1:])) == 4
  cs.out.vEgo = cs.out.vEgoRaw = 100 / 3.6
  trace = [step(controller, cs, cc)[0].torqueOutputCan for _ in range(100)]
  assert trace[-1] == 270 and max(abs(b-a) for a,b in zip(trace, trace[1:])) <= 3
  assert controller.params.STEER_MAX == 270
  assert (controller.params.STEER_DELTA_UP, controller.params.STEER_DELTA_DOWN) == (2, 3)
  assert settings['CustomSteerMax'] == 409 and settings['CustomSteerDeltaUpLC'] == 25
  settings['LowSpeedSteerReserve'] = 0
  for _ in range(100):
    step(controller, cs, cc)
  assert controller.params.STEER_MAX == 409
  assert (controller.params.STEER_DELTA_UP, controller.params.STEER_DELTA_DOWN) == (25, 35)


def test_demand_follow_reaches_same_target_sooner_without_scaling_small_commands(monkeypatch):
  controller,cs,cc,_=torque_fixture(monkeypatch)
  dynamic=[step(controller,cs,cc)[0].torqueOutputCan for _ in range(300)]
  controller,cs,cc,_=torque_fixture(monkeypatch)
  controller.low_speed_steer_reserve.rates=lambda **kw:(kw['up'],kw['down'])
  factory=[step(controller,cs,cc)[0].torqueOutputCan for _ in range(300)]
  assert dynamic[-1]==factory[-1]==405
  assert next(i for i,v in enumerate(dynamic) if v>=400)+30 < next(i for i,v in enumerate(factory) if v>=400)
  assert max(abs(b-a) for a,b in zip(dynamic,dynamic[1:]))==4


@pytest.mark.parametrize('speed,max_up,max_down', [(10,4,4),(30,4,4),(35,3,3),(40,2,3),(100,2,3)])
def test_dynamic_rate_taper_and_exit(speed,max_up,max_down):
  helper=LowSpeedSteerReserve()
  cs=state()
  cs.vEgo=cs.vEgoRaw=speed/3.6
  warm(helper,cs)
  assert helper.rates(requested=400,previous=100,base=270,up=2,down=3)==(max_up,max_down)
  assert helper.rates(requested=101,previous=100,base=270,up=2,down=3)==(2,3)
  assert helper.rates(requested=-400,previous=100,base=270,up=2,down=3)==(2,3)


@pytest.mark.parametrize('field,value', [('steeringPressed',True),('canValid',False),('steerFaultTemporary',True),
                                       ('standstill',True),('gearShifter','reverse')])
def test_health_loss_withdraws_extra_rate_immediately(field,value):
  helper,cs=LowSpeedSteerReserve(),state()
  warm(helper,cs)
  assert helper.rates(requested=400,previous=100,base=270,up=2,down=3)==(4,4)
  setattr(cs,field,value)
  helper.update(enabled=True,active=True,cs=cs,base=270,model_frame=100,demand=1.5)
  assert helper.rates(requested=400,previous=100,base=270,up=2,down=3)==(2,3)


def test_fastest_wheel_cannot_be_hidden_by_filtered_or_rescaled_ego_speed():
  helper,cs=LowSpeedSteerReserve(),state()
  cs.wheelSpeeds=dict(fl=40/3.6,fr=40/3.6,rl=40/3.6,rr=40/3.6)
  assert set(warm(helper,cs))=={270}
  assert helper.rates(requested=400,previous=100,base=270,up=2,down=3)==(2,3)
  cs.wheelSpeeds=dict(fl=7,fr=7,rl=7,rr=8)
  assert set(warm(helper,cs))=={270}  # inconsistent wheel speed cannot grant headroom


@pytest.mark.parametrize('fingerprint', ['KIA_EV6', 'HYUNDAI_IONIQ_5', 'KIA_CARNIVAL_4TH_GEN', 'KIA_SORENTO_4TH_GEN'])
def test_phase1_selects_same_bounded_can_path_and_keeps_driver_withdrawal(monkeypatch, fingerprint):
  controller, cs, cc, settings = torque_fixture(monkeypatch, enabled=False)
  controller.CP.brand = 'hyundai'
  controller.CP.carFingerprint = fingerprint
  controller.CP.steerControlType = 'torque'
  settings['HkgPhase1Assist'] = 1
  settings['CustomSteerMax'] = 409
  settings['CustomSteerDeltaUp'] = 10
  trace = [step(controller, cs, cc)[0].torqueOutputCan for _ in range(300)]
  assert trace[-1] == 405
  assert controller.params.STEER_MAX == 270
  assert max(abs(b-a) for a,b in zip(trace,trace[1:])) <= 4
  cs.out.steeringPressed = True
  cs.out.steeringTorque = -2000
  withdrawn = [step(controller, cs, cc)[0].torqueOutputCan for _ in range(200)]
  assert withdrawn[-1] == 0
  assert controller.low_speed_steer_reserve.reason == 'driver'
  # User settings remain stored; disabling both modes restores their selection.
  assert settings['CustomSteerMax'] == 409
  assert settings['CustomSteerDeltaUp'] == 10
