"""Exercise production Panda TX/forwarding, not a reimplementation of limits."""
import pytest

from opendbc.car.hyundai.values import HyundaiSafetyFlags as F
from opendbc.car.structs import CarParams
from opendbc.safety.tests.common import CANPackerPanda
from opendbc.safety.tests.libsafety import libsafety_py


class Guard:
  def __init__(self, param=0):
    self.s = libsafety_py.libsafety
    assert self.s.set_safety_hooks(CarParams.SafetyModel.hyundaiCanfd, param) == 0
    self.s.init_tests()
    self.packer = CANPackerPanda('hyundai_canfd_generated')
    self.param, self.now, self.counter = param, 1_000_000, 0
    self.pt = 1 if param & F.CANFD_LKA_STEERING and not param & F.CAMERA_SCC else 0
    self.s.set_timer(self.now)

  def rx(self, name, values, *, bus=None, corrupt=False):
    values = dict(values, COUNTER=self.counter % 256)
    msg = self.packer.make_can_msg_panda(name, self.pt if bus is None else bus, values)
    if corrupt:
      msg[0].data[0] ^= 1
    return self.s.safety_rx_hook(msg)

  def sensors(self, speed=20, driver=0, *, bus=None):
    self.counter += 1
    assert self.rx('WHEEL_SPEEDS', {f'WHEEL_SPEED_{p}': speed for p in range(1,5)}, bus=bus)
    assert self.rx('MDPS', {'STEERING_COL_TORQUE': driver}, bus=bus)

  def seed(self, value=0):
    self.s.set_desired_torque_last(value)
    self.s.set_rt_torque_last(value)
    self.s.set_torque_driver(0,0)

  def command(self, torque, request=True, *, addr='LFA', bus=None, angle_active=0):
    values = {'TORQUE_REQUEST': torque, 'STEER_REQ': int(request), 'LKAS_ANGLE_ACTIVE': angle_active}
    return self.packer.make_can_msg_panda(addr, self.pt if bus is None else bus, values)

  def tx(self, torque, **kw):
    return bool(self.s.safety_tx_hook(self.command(torque, **kw)))


@pytest.mark.parametrize('param,addr,bus', [(0,'LFA',0), (int(F.CAMERA_SCC),'LFA',0),
  (int(F.CANFD_LKA_STEERING),'LKAS',0),
  (int(F.CANFD_LKA_STEERING|F.CANFD_LKA_STEERING_ALT),'LKAS_ALT',0),
  (int(F.CANFD_LKA_STEERING|F.LONG),'LFA',1),
  (int(F.CANFD_LKA_STEERING|F.LONG|F.CAMERA_SCC),'LFA',0)])
@pytest.mark.parametrize('sign', [-1,1])
def test_controls_amplitude_rate_driver_and_request_protection(param,addr,bus,sign):
  g = Guard(param)
  g.seed()
  assert not g.tx(sign,addr=addr,bus=bus)  # disabled means disabled without explicit AOL
  g.s.set_controls_allowed(True)
  g.seed(512*sign)
  assert g.tx(512*sign,addr=addr,bus=bus)
  g.seed(512*sign)
  assert not g.tx(513*sign,addr=addr,bus=bus)
  g.seed(100*sign)
  assert g.tx(102*sign,addr=addr,bus=bus)
  g.seed(100*sign)
  assert not g.tx(103*sign,addr=addr,bus=bus)
  g.seed(100*sign)
  assert not g.tx(100*sign,request=False,addr=addr,bus=bus)
  g.s.set_torque_driver(-1000*sign,-1000*sign)
  g.seed(100*sign)
  g.s.set_torque_driver(-1000*sign,-1000*sign)
  assert not g.tx(100*sign,addr=addr,bus=bus)


@pytest.mark.parametrize('speed,up,down', [(0,2,3),(20,4,3),(30,4,3),(35,3,3),(40,2,3),(100,2,3)])
@pytest.mark.parametrize('sign', [-1,1])
def test_independent_wheel_speed_bounds(speed,up,down,sign):
  g=Guard()
  g.sensors(speed)
  g.s.set_controls_allowed(True)
  g.seed(100*sign)
  assert g.tx((100+up)*sign)
  g.seed(100*sign)
  assert not g.tx((101+up)*sign)
  g.seed(100*sign)
  g.s.set_torque_driver(-1000*sign,-1000*sign)
  assert g.tx((100-down)*sign)
  g.seed(100*sign)
  g.s.set_torque_driver(-1000*sign,-1000*sign)
  assert not g.tx((101-down)*sign)  # must yield at least the configured decrement


@pytest.mark.parametrize('bad', ['stale','wheel_crc','driver_crc','counter','wrong_bus','wheel_spread','reverse','driver'])
def test_bad_sensor_input_cannot_raise_rate(bad):
  g=Guard()
  g.sensors()
  if bad=='stale':
    g.now+=100001;g.s.set_timer(g.now)
  elif bad in ('wheel_crc','driver_crc'):
    name='WHEEL_SPEEDS' if bad=='wheel_crc' else 'MDPS'
    g.rx(name,{},corrupt=True)
  elif bad=='counter':
    for _ in range(8):g.rx('WHEEL_SPEEDS',{})
  elif bad=='wrong_bus':
    g=Guard(int(F.CANFD_LKA_STEERING|F.CAMERA_SCC))
    g.sensors(bus=1)
  elif bad=='reverse':
    g.rx('WHEEL_SPEEDS',dict(WHEEL_SPEED_1=20,WHEEL_SPEED_2=20,WHEEL_SPEED_3=20,WHEEL_SPEED_4=20,MOVING_BACKWARD=1))
  elif bad=='driver':
    g.s.set_torque_driver(251,251)
  else:
    g.rx('WHEEL_SPEEDS',dict(WHEEL_SPEED_1=20,WHEEL_SPEED_2=20,WHEEL_SPEED_3=20,WHEEL_SPEED_4=35))
  g.s.set_controls_allowed(True)
  g.seed(100)
  if bad=='driver':g.s.set_torque_driver(251,251)
  assert not g.tx(104)


def test_aol_is_explicit_fresh_and_reset_with_safety_mode():
  g=Guard(int(F.CANFD_ALWAYS_LATERAL))
  g.sensors()
  g.seed()
  assert not g.s.get_controls_allowed()
  assert g.tx(4)
  g.now+=100001;g.s.set_timer(g.now)
  assert not g.tx(4)
  g=Guard()
  g.sensors()
  assert not g.tx(2)


def test_bad_tx_crc_cannot_advance_history_or_fill_forward_cache():
  g=Guard(int(F.CAMERA_SCC))
  g.s.set_controls_allowed(True)
  msg=g.command(2)
  msg[0].data[0]^=1
  assert not g.s.safety_tx_hook(msg)
  assert not g.tx(4)  # invalid CRC did not advance the factory-rate history
  assert g.tx(2)
  assert not g.tx(200)


def test_rt_envelope_is_still_112_per_250ms():
  g=Guard()
  g.sensors()
  g.s.set_controls_allowed(True)
  g.s.set_desired_torque_last(112)
  g.s.set_rt_torque_last(0)
  assert not g.tx(113)


def test_wrong_bus_and_angle_format_cannot_bypass_torque_checks():
  g=Guard(int(F.CANFD_LKA_STEERING|F.LONG))
  g.s.set_controls_allowed(True)
  assert not g.tx(1,addr='LKAS',bus=1)
  assert not g.tx(1,addr='LKAS_ALT',bus=0)
  assert not g.tx(0,addr='LFA',bus=1,angle_active=2)


@pytest.mark.parametrize('sign', [-1, 1])
def test_ev6_adas_speed_transition_emits_admissible_steering(monkeypatch, sign):
  from opendbc.car.hyundai.tests.test_low_speed_steer_reserve import ev6_adas_controller
  from opendbc.car.hyundai.tests.test_steering_handover_controller import step

  controller, cs, cc, settings = ev6_adas_controller(monkeypatch, enabled=True)
  settings.update(MaxAngleFrames=100, CustomSteerDeltaUp=50, CustomSteerDeltaDown=1)
  cc.actuators.torque = sign
  guard = Guard(int(F.CANFD_LKA_STEERING))
  expected = {249: 384, 250: 381, 270: 330, 400: 327, 549: 0, 550: 2, 580: 0}
  for frame in range(600):
    cs.out.vEgoRaw = cs.out.vEgo = 10.99 if frame < 250 else 11.0
    cs.out.steeringAngleDeg = sign * min(frame * 2, 360)
    cs.out.steeringPressed = 400 <= frame < 550
    cs.out.steeringTorque = -sign * 1000 if cs.out.steeringPressed else 0
    cc.latActive = frame < 580
    guard.now += 10000
    guard.s.set_timer(guard.now)
    guard.sensors(cs.out.vEgoRaw * 3.6, cs.out.steeringTorque)
    guard.s.set_controls_allowed(cc.latActive)
    output, messages = step(controller, cs, cc)
    packet, = [libsafety_py.make_CANPacket(addr, bus, data) for addr, data, bus in messages if (addr, bus) == (0x50, 0)]
    assert guard.s.safety_tx_hook(packet), frame
    if frame in expected:
      assert sign * output.torqueOutputCan == expected[frame]


def test_redundant_output_histories_and_89_2_request_cuts_are_independent():
  g=Guard(int(F.CANFD_LKA_STEERING|F.LONG))
  g.s.set_controls_allowed(True)
  for n in range(100):
    g.now+=10000;g.s.set_timer(g.now)
    value=min(100,2*n)
    assert g.tx(value,addr='LFA',bus=1)
    assert g.tx(value,addr='LKAS',bus=0)
  for _ in range(2):
    g.now+=10000;g.s.set_timer(g.now)
    assert g.tx(100,request=False,addr='LFA',bus=1)
    assert g.tx(100,request=False,addr='LKAS',bus=0)
  assert not g.tx(100,request=False,addr='LFA',bus=1)
  assert not g.tx(100,request=False,addr='LKAS',bus=0)


def forwarded(g, stock_torque=0, *, advance=True):
  msg=g.command(stock_torque,bus=2,request=False)
  if advance:g.now+=10000
  g.s.set_timer(g.now)
  destination=g.s.safety_fwd_hook_packet_test(msg)
  data=bytes(msg[0].data)
  torque=(((data[6]&15)<<7)|(data[5]>>1))-1024
  return destination,torque


def test_buffered_outputs_are_rechecked_on_disengagement_driver_and_stale_speed():
  for reason in ('disengage','driver','speed'):
    g=Guard(int(F.CAMERA_SCC))
    g.sensors()
    g.s.set_controls_allowed(True)
    assert g.tx(4)
    assert g.tx(8)
    assert forwarded(g)==(0,4)
    if reason=='disengage':g.s.set_controls_allowed(False)
    elif reason=='driver':g.s.set_torque_driver(-1000,-1000)
    else:
      g.now+=100001;g.s.set_timer(g.now)
    # Not copied from the queue: original packet remains untouched.
    assert forwarded(g)==(-1,0)


def test_reuse_does_not_extend_a_request_cut_beyond_two_physical_frames():
  g=Guard(int(F.CAMERA_SCC))
  g.s.set_controls_allowed(True)
  assert g.tx(2)
  assert g.tx(4)
  for _ in range(100):
    assert forwarded(g)==(0,2 if _==0 else 4)
    assert g.tx(4)
  assert g.tx(4,request=False)
  assert g.tx(4,request=False)
  # Drain queued valid-request frames before the two request-cut frames.
  results=[forwarded(g) for _ in range(7)]
  assert any(result==(-1,0) for result in results)


@pytest.mark.parametrize('aol', [False,True])
def test_existing_angle_format_requires_explicit_control_type_and_admission(aol):
  param=int(F.CANFD_ANGLE_CONTROL | (F.CANFD_ALWAYS_LATERAL if aol else 0))
  g=Guard(param)
  g.sensors()
  values=dict(LKAS_ANGLE_ACTIVE=2,LKAS_ANGLE_CMD=20,LKAS_ANGLE_MAX_TORQUE=25)
  packet=lambda:g.packer.make_can_msg_panda('LFA_ALT',0,values)
  assert bool(g.s.safety_tx_hook(packet())) is aol
  g.s.set_controls_allowed(True)
  assert g.s.safety_tx_hook(packet())
  values['LKAS_ANGLE_MAX_TORQUE']=251
  assert not g.s.safety_tx_hook(packet())


def test_oem_emergency_angle_requires_matching_fresh_physical_camera_fields():
  g=Guard(int(F.CANFD_ANGLE_CONTROL))
  values=dict(COUNTER=1,LKAS_ANGLE_ACTIVE=3,LKAS_ANGLE_CMD=20,LKAS_ANGLE_MAX_TORQUE=255)
  packet=lambda bus:g.packer.make_can_msg_panda('LFA_ALT',bus,values)
  assert not g.s.safety_tx_hook(packet(0))
  assert g.s.safety_rx_hook(packet(2))
  assert g.s.safety_tx_hook(packet(0))
  values['LKAS_ANGLE_CMD']=21
  assert not g.s.safety_tx_hook(packet(0))
  values['LKAS_ANGLE_CMD']=20
  g.now+=100001;g.s.set_timer(g.now)
  assert not g.s.safety_tx_hook(packet(0))


def test_legacy_disabled_lfa_sentinel_is_specific_to_angle_control():
  g=Guard(int(F.CANFD_ANGLE_CONTROL|F.CAMERA_SCC))
  assert g.tx(-1024,request=False)
  assert not g.tx(-1024,request=True)
  g=Guard(int(F.CAMERA_SCC))
  assert not g.tx(-1024,request=False)


@pytest.mark.parametrize('camera', [False,True])
@pytest.mark.parametrize('sign', [-1,1])
def test_real_controller_stream_passes_production_panda_and_rx_paced_forwarding(monkeypatch,camera,sign):
  controller_stream(monkeypatch, camera, sign)


@pytest.mark.parametrize("camera_period_us", [None, 10000, 10150, 10200, 10250])
@pytest.mark.parametrize("sign", [-1, 1])
@pytest.mark.parametrize("saved_frames", [None, 80, 88, 89, 93, 100])
def test_sorento_sustained_turn_request_interval(monkeypatch, camera_period_us, sign, saved_frames):
  from opendbc.car.hyundai.tests.test_steering_handover_controller import setup_controller, step
  from opendbc.car.hyundai.values import CAR, HyundaiFlags

  camera = camera_period_us is not None
  model = CAR.KIA_SORENTO_2024
  flags = HyundaiFlags.CANFD | (HyundaiFlags.CAMERA_SCC if camera else 0)
  specs = model.config.specs
  cp = CarParams(brand="hyundai", carFingerprint=model, flags=int(flags), steerControlType="torque",
                 wheelbase=specs.wheelbase, steerRatio=specs.steerRatio)
  controller, cs, cc, settings = setup_controller(monkeypatch, angle=False, camera=camera, cp_override=cp)
  if saved_frames is None:
    del settings["MaxAngleFrames"]
  else:
    settings["MaxAngleFrames"] = saved_frames
  cs.out.gearShifter = "drive"
  cs.out.vEgo = cs.out.vEgoRaw = 30 / 3.6
  cs.out.steeringPressed = False
  cs.out.steeringTorque = 0
  cc.actuators.torque = sign * 0.4
  guard = Guard(int(F.CAMERA_SCC) if camera else 0)
  bend_torques = []
  # Host runs at 100 Hz. The physical camera on the affected platform runs
  # closer to 98 Hz, so forwarding can see fewer requests than host TX.
  next_camera_us = guard.now + 3500
  cut_starts = []
  previous_request = True
  for frame in range(1410):  # 2 s straight, 12 s in the bend, then disengage
    in_bend = 200 <= frame < 1400
    cs.out.steeringAngleDeg = sign * 87 if in_bend else 0
    cc.latActive = frame < 1400
    next_host_us = guard.now + 10000
    rx_count = 0
    while camera and next_camera_us < next_host_us:
      rx_count += 1
      guard.s.set_timer(next_camera_us)
      stock = guard.command(0, bus=2, request=False)
      destination = guard.s.safety_fwd_hook_packet_test(stock)
      if in_bend:
        assert destination == 0, (frame, "forwarding rejected")
        data = stock[0].data
        assert data[13] == 100  # ccNC Sorento MDPS damping, including request cuts
        forwarded_torque = (((data[6] & 15) << 7) | (data[5] >> 1)) - 1024
        assert sign * forwarded_torque > 0
        if bend_torques:
          assert forwarded_torque == bend_torques[0]
        request = bool(data[6] & 0x10)
        if previous_request and not request:
          cut_starts.append(next_camera_us)
        previous_request = request
      if not cc.latActive and frame > 1400 and destination == 0:
        assert not stock[0].data[6] & 0x10
        assert (((stock[0].data[6] & 15) << 7) | (stock[0].data[5] >> 1)) == 1024
      next_camera_us += camera_period_us
    guard.now = next_host_us
    guard.s.set_timer(guard.now)
    guard.sensors(30, 0)
    guard.s.set_controls_allowed(cc.latActive)
    output, messages = step(controller, cs, cc, camera_frames=rx_count)
    for addr, data, bus in messages:
      if addr == 0x12A:
        assert guard.s.safety_tx_hook(libsafety_py.make_CANPacket(addr, bus, data)), frame
    if in_bend:
      bend_torques.append(output.torqueOutputCan)
    elif not cc.latActive:
      assert output.torqueOutputCan == 0

  assert sign * bend_torques[0] > 0
  assert all(torque == bend_torques[0] for torque in bend_torques)
  if camera:
    assert len(cut_starts) >= 11
    assert all(0 < b - a < 1000000 for a, b in zip(cut_starts, cut_starts[1:]))


@pytest.mark.parametrize("sign", [-1, 1])
@pytest.mark.parametrize("camera_period_us", [10050, 10200])
def test_sorento_changing_torque_under_camera_clock_drift(monkeypatch, sign, camera_period_us):
  from opendbc.car.hyundai.tests.test_steering_handover_controller import setup_controller, step
  from opendbc.car.hyundai.values import CAR, HyundaiFlags

  model = CAR.KIA_SORENTO_2024
  cp = CarParams(brand="hyundai", carFingerprint=model, flags=int(HyundaiFlags.CANFD | HyundaiFlags.CAMERA_SCC),
                 steerControlType="torque", wheelbase=model.config.specs.wheelbase, steerRatio=model.config.specs.steerRatio)
  controller, cs, cc, _ = setup_controller(monkeypatch, angle=False, cp_override=cp)
  cs.out.steeringPressed = False
  cs.out.steeringTorque = 0
  cs.out.steeringAngleDeg = sign * 30
  cs.out.vEgo = cs.out.vEgoRaw = 40 / 3.6
  guard = Guard(int(F.CAMERA_SCC))
  guard.s.set_controls_allowed(True)
  next_camera = guard.now + 3500
  physical = []
  for frame in range(1800):
    cc.actuators.torque = sign * (0.95 if frame % 200 < 100 else 0.15)
    received = 0
    next_host = guard.now + 10000
    while next_camera < next_host:
      guard.s.set_timer(next_camera)
      packet = guard.command(0, bus=2, request=False)
      destination = guard.s.safety_fwd_hook_packet_test(packet)
      data = packet[0].data
      magnitude = sign * ((((data[6] & 15) << 7) | (data[5] >> 1)) - 1024)
      if frame > 10:
        assert destination == 0 and data[6] & 16 and magnitude > 0, (frame, destination, magnitude)
        physical.append(magnitude)
      next_camera += camera_period_us
      received += 1
    guard.now = next_host
    guard.s.set_timer(next_host)
    guard.sensors(40)
    _, messages = step(controller, cs, cc, camera_frames=received)
    for addr, data, bus in messages:
      if addr == 0x12A:
        assert guard.s.safety_tx_hook(libsafety_py.make_CANPacket(addr, bus, data))
  assert max(physical) - min(physical) > 150
  assert all(b - a <= 2 for a, b in zip(physical, physical[1:]))


def controller_stream(monkeypatch, camera, sign, *, fingerprint=None, phase1=None):
  from opendbc.car.hyundai.tests.test_low_speed_steer_reserve import torque_fixture
  from opendbc.car.hyundai.tests.test_steering_handover_controller import step
  from opendbc.car.hyundai.values import HyundaiFlags
  controller,cs,cc,settings=torque_fixture(monkeypatch, enabled=phase1 is None)
  if fingerprint is not None:
    controller.CP.brand = 'hyundai'
    controller.CP.carFingerprint = fingerprint
    controller.CP.steerControlType = 'torque'
    settings['HkgPhase1Assist'] = int(phase1)
  trace = []
  if camera:controller.CP.flags |= int(HyundaiFlags.CAMERA_SCC)
  g=Guard(int(F.CANFD_ALWAYS_LATERAL|(F.CAMERA_SCC if camera else 0)))
  prior=0
  for n in range(750):
    speed=25 if n<250 else 35 if n<300 else 40 if n<350 else 100 if n<400 else 25
    cs.out.vEgo=cs.out.vEgoRaw=speed/3.6
    cc.actuators.torque=sign*(.5 if n<80 else 2. if n<550 else 1.)
    cs.out.steeringAngleDeg=85 if 100<=n<250 else 0
    cs.out.steeringPressed=600<=n<650
    cs.out.steeringTorque=-sign*1000 if cs.out.steeringPressed else 0
    cc.latActive=n<700
    g.now+=10000;g.s.set_timer(g.now)
    g.sensors(speed,cs.out.steeringTorque)
    g.s.set_controls_allowed(cc.latActive)
    output,messages=step(controller,cs,cc)
    for addr,data,bus in messages:
      if addr in (0x12A,0x50,0x110,0xCB):
        msg=libsafety_py.make_CANPacket(addr,bus,data)
        assert g.s.safety_tx_hook(msg), (n,output.torqueOutputCan,prior)
    if camera:
      # Startup waits for two enqueued packets; subsequent output is RX-paced.
      dest,command=forwarded(g,advance=False)
      assert dest==0, (n,command,output.torqueOutputCan)
    prior=output.torqueOutputCan
    trace.append(prior)
  return trace


@pytest.mark.parametrize('fingerprint', ['KIA_EV6', 'HYUNDAI_IONIQ_5', 'KIA_CARNIVAL_4TH_GEN', 'KIA_SORENTO_4TH_GEN'])
@pytest.mark.parametrize('enabled', [False, True])
@pytest.mark.parametrize('camera', [False, True])
@pytest.mark.parametrize('sign', [-1, 1])
def test_four_families_switch_stream_retains_panda_and_forwarding_guards(monkeypatch, fingerprint, enabled, camera, sign):
  trace = controller_stream(monkeypatch, camera, sign, fingerprint=fingerprint, phase1=enabled)
  assert max(map(abs, trace)) <= (409 if enabled else 270)
  assert (max(map(abs, trace[80:250])) > 270) == enabled
  # A synthetic 35->40 km/h one-frame jump must unwind the old torque under
  # the existing 3-unit withdrawal guard, not abruptly cut it to the new cap.
  assert all(0 <= abs(a) - abs(b) <= 3 for a, b in zip(trace[299:325], trace[300:326], strict=True))
  assert max(map(abs, trace[325:400])) <= 270  # factory target reached before the 100 km/h segment
  assert trace[-1] == 0  # disengagement still removes authority
