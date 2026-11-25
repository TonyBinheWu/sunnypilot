from types import SimpleNamespace as NS

import pytest

from opendbc.can.dbc import DBC
from opendbc.can.parser import get_raw_value
from opendbc.car import Bus, structs, get_safety_config
from opendbc.car.hyundai import carcontroller, hyundaicanfd
from opendbc.car.hyundai.values import CAR, HyundaiFlags


def setup_controller(monkeypatch, *, mode=None, angle=True, camera=True, cp_override=None):
  settings = {"MaxAngleFrames": 89}
  if mode is not None:
    settings["SteerHandoverMode"] = mode  # leftover value on an upgraded device

  def get_int(key):
    assert key != "SteerHandoverMode", "retired setting must not be read"
    return settings.get(key, 0)

  params = NS(get_int=get_int, get_bool=lambda key: bool(get_int(key)),
              get=lambda key, return_default=False: settings.get(key, return_default and key == "HyundaiShowStockSigns"))
  monkeypatch.setattr(carcontroller, "Params", lambda: params)
  monkeypatch.setattr(hyundaicanfd, "Params", lambda: params)
  # Keep actual angle limiting, legacy authority and steering
  # CAN packing. Unrelated cluster/button paths are outside this fixture.
  monkeypatch.setattr(hyundaicanfd, "create_lfahda_cluster", lambda *a, **kw: [])
  monkeypatch.setattr(hyundaicanfd, "create_lfa_icon_non_camera_scc", lambda *a, **kw: [])
  monkeypatch.setattr(carcontroller.CarController, "create_button_messages", lambda *a, **kw: [])
  flags = HyundaiFlags.CANFD
  if angle:
    flags |= HyundaiFlags.ANGLE_CONTROL
  if camera:
    flags |= HyundaiFlags.CAMERA_SCC
  cp = structs.CarParams(carFingerprint=CAR.KIA_EV6, flags=int(flags), wheelbase=3.0, steerRatio=14.26)
  if cp_override is not None:
    cp = cp_override
  cp.safetyConfigs = [get_safety_config(structs.CarParams.SafetyModel.hyundaiCanfd)]
  controller = carcontroller.CarController({Bus.pt: "hyundai_canfd_generated"}, cp)
  controller.lkas_max_torque = 25
  cs = NS(out=structs.CarState(canValid=True, steeringPressed=True, steeringTorque=300, vEgoRaw=15),
          modelV2=NS(frameId=1, position=NS(yStd=[0.1] * 33)), is_metric=True,
          adrv_0x161=None, mdps=None, steer_touch_2af=None, lfa_alt={}, lfa={})
  cs.cp_cam = NS(ts_nanos={}, vl_all={}, _last_update_nanos=0, counter=255)
  cc = structs.CarControl(enabled=True, latActive=True)
  cc.actuators.steeringAngleDeg = 0.5
  return controller, cs, cc, settings


def step(controller, cs, cc, *, fresh=True, camera_frames=1):
  now = (controller.frame + 1) * 10_000_000
  if controller.lfa_cadence is not None:
    cs.cp_cam._last_update_nanos = now
    counters = [(cs.cp_cam.counter + n + 1) % 256 for n in range(camera_frames)]
    cs.cp_cam.vl_all["LFA"] = {"COUNTER": counters}
    if counters:
      cs.cp_cam.counter = counters[-1]
      cs.cp_cam.ts_nanos["LFA"] = {"COUNTER": now}
  if fresh:
    cs.modelV2.frameId = controller.frame // 5 + 1
  return controller.update(cc.as_reader(), cs, now)


@pytest.mark.parametrize("previous, invalid", [(None, None), (None, -1), (None, 101), (92, 0)])
@pytest.mark.parametrize("sign", [-1, 1], ids=["right", "left"])
def test_high_angle_request_recovers_after_two_frames_with_invalid_setting(monkeypatch, previous, invalid, sign):
  model = CAR.KIA_SORENTO_2024
  specs = model.config.specs
  cp = structs.CarParams(brand="hyundai", carFingerprint=model, flags=int(HyundaiFlags.CANFD),
                         wheelbase=specs.wheelbase, steerRatio=specs.steerRatio)
  controller, cs, cc, settings = setup_controller(monkeypatch, angle=False, camera=False, cp_override=cp)
  cs.out.steeringPressed = False
  cs.out.steeringTorque = 0
  cc.actuators.torque = sign * 0.4
  if previous is not None:
    settings["MaxAngleFrames"] = previous
    for _ in range(50):
      step(controller, cs, cc)
  if invalid is None:
    del settings["MaxAngleFrames"]
  else:
    settings["MaxAngleFrames"] = invalid

  cs.out.steeringAngleDeg = sign * carcontroller.MAX_ANGLE
  lfa = DBC("hyundai_canfd_generated").name_to_msg["LFA"]
  torque_signal = lfa.sigs["TORQUE_REQUEST"]
  frames = previous or carcontroller.MAX_ANGLE_FRAMES
  expected_cycle = [1] * frames + [0] * carcontroller.MAX_ANGLE_CONSECUTIVE_FRAMES
  requests = []
  for _ in range(2 * len(expected_cycle) + 1):
    output, messages = step(controller, cs, cc)
    data = next(data for addr, data, _ in messages if addr == lfa.address)
    requests.append(get_raw_value(data, lfa.sigs["STEER_REQ"]))
    wire_torque = get_raw_value(data, torque_signal) * torque_signal.factor + torque_signal.offset
    assert wire_torque == output.torqueOutputCan
    assert sign * wire_torque > 0
  assert requests == expected_cycle * 2 + [1]

  cc.latActive = False
  _, messages = step(controller, cs, cc)
  data = next(data for addr, data, _ in messages if addr == lfa.address)
  assert get_raw_value(data, lfa.sigs["STEER_REQ"]) == 0
  assert get_raw_value(data, torque_signal) * torque_signal.factor + torque_signal.offset == 0


@pytest.mark.parametrize("camera", [False, True])
def test_experimental_output_reaches_can_without_mutating_legacy(monkeypatch, camera):
  controller, cs, cc, _ = setup_controller(monkeypatch, mode=3, camera=camera)
  for _ in range(115):
    actuators, messages = step(controller, cs, cc)
  assert 70 < actuators.torqueOutputCan <= 80
  assert controller.lkas_max_torque == 25
  assert cs.out.steeringPressed
  if camera:
    data = next(data for address, data, bus in messages if address == 0xCB)
    assert abs(data[6] - actuators.torqueOutputCan) <= 0.5
  else:
    data = next(data for address, data, bus in messages if address == 0x12A)
    assert abs(data[12] - actuators.torqueOutputCan) <= 0.5
  assert actuators.steeringAngleDeg == pytest.approx(0.5)


@pytest.mark.parametrize("saved", [None, 0, 1, 2, 3, -1, 99])
def test_combined_recovery_is_standard_regardless_of_retired_setting(monkeypatch, saved):
  controller, cs, cc, _ = setup_controller(monkeypatch, mode=saved)
  for _ in range(115):
    output, _ = step(controller, cs, cc)
  assert controller.steer_handover.mode == 3
  assert 70 < output.torqueOutputCan <= 80
  assert controller.lkas_max_torque == 25


def test_retired_setting_changes_cannot_reset_recovery(monkeypatch):
  controller, cs, cc, settings = setup_controller(monkeypatch)
  for _ in range(100):
    step(controller, cs, cc)
  assert controller.steer_handover.state == "offering"
  offer_since = controller.steer_handover.offer_since
  for saved in (0, 1, 2, 3):
    settings["SteerHandoverMode"] = saved
    for _ in range(5):
      output, _ = step(controller, cs, cc)
    assert controller.steer_handover.mode == 3
    assert controller.steer_handover.offer_since == offer_since
    assert controller.steer_handover.effort is not None
  # The unchanged no-response timeout may start gradual withdrawal here.
  assert output.torqueOutputCan > 25


@pytest.mark.parametrize("bad_input", ["can", "temporary", "permanent", "model", "uncertain", "frozen"])
def test_controller_rejects_unhealthy_or_stale_input(monkeypatch, bad_input):
  controller, cs, cc, _ = setup_controller(monkeypatch, mode=3)
  for _ in range(115):
    step(controller, cs, cc)
  if bad_input == "can":
    cs.out.canValid = False
  elif bad_input == "temporary":
    cs.out.steerFaultTemporary = True
  elif bad_input == "permanent":
    cs.out.steerFaultPermanent = True
  elif bad_input == "model":
    cs.modelV2 = None
  elif bad_input == "uncertain":
    cs.modelV2.position.yStd = [0.5] * 33
  for _ in range(20):
    actuators, _ = step(controller, cs, cc, fresh=bad_input not in ("frozen", "model"))
  assert actuators.torqueOutputCan == 25


@pytest.mark.parametrize("camera", [False, True])
def test_torque_control_does_not_call_handover(monkeypatch, camera):
  def unexpected_handover(*args, **kwargs):
    pytest.fail("torque-control platform must not use angle handover")

  traces = []
  for mode in range(4):
    controller, cs, cc, _ = setup_controller(monkeypatch, mode=mode, angle=False, camera=camera)
    monkeypatch.setattr(controller.steer_handover, "update", unexpected_handover)
    cc.actuators.torque = 0.1
    trace = [step(controller, cs, cc) for _ in range(120)]
    traces.append([(a.torqueOutputCan, a.steeringAngleDeg, messages) for a, messages in trace])
    assert controller.steer_handover.mode == 0
  assert all(trace == traces[0] for trace in traces[1:])


def test_disengagement_clears_authority_and_experimental_evidence(monkeypatch):
  controller, cs, cc, _ = setup_controller(monkeypatch, mode=3)
  for _ in range(115):
    step(controller, cs, cc)
  cc.latActive = False
  output, messages = step(controller, cs, cc)
  assert output.torqueOutputCan == 0
  assert next(data[6] for address, data, bus in messages if address == 0xCB) == 0
  assert controller.steer_handover.effort is None


@pytest.mark.parametrize("camera", [False, True])
def test_combined_recovery_preserves_legacy_angle_commands(monkeypatch, camera):
  angles = []
  for legacy in (False, True):
    controller, cs, cc, _ = setup_controller(monkeypatch, camera=camera)
    if legacy:
      monkeypatch.setattr(controller.steer_handover, "update", lambda **kw: kw["baseline"])
    trace = []
    for tick in range(300):
      cc.actuators.steeringAngleDeg = 30 if tick < 150 else -10
      cs.out.steeringAngleDeg = 25 if tick < 120 else 20
      cs.out.steeringTorque = 350 if tick < 100 else 0
      cs.out.steeringPressed = tick < 100
      output, _ = step(controller, cs, cc)
      trace.append(output.steeringAngleDeg)
    angles.append(trace)
  assert all(trace == angles[0] for trace in angles[1:])


@pytest.mark.parametrize("camera", [False, True])
def test_recovery_selected_total_cap_reaches_both_can_paths(monkeypatch, camera):
  controller, cs, cc, _ = setup_controller(monkeypatch, camera=camera)
  cc.actuators.steeringAngleDeg = 12
  for _ in range(100):
    step(controller, cs, cc)
  cs.out.steeringPressed = False
  cs.out.steeringTorque = 0
  for _ in range(10):
    step(controller, cs, cc)
  assert controller.steer_handover.state == "recover"
  # Force the independent legacy recovery ahead: it cannot bypass the helper.
  controller.lkas_max_torque = 250
  output, messages = step(controller, cs, cc)
  assert 25 < output.torqueOutputCan < 80
  address, byte = (0xCB, 6) if camera else (0x12A, 12)
  data = next(data for addr, data, _ in messages if addr == address)
  assert abs(data[byte] - output.torqueOutputCan) <= 0.5


@pytest.mark.parametrize('angle', [False, True])
def test_missing_camera_template_cannot_accumulate_first_transmitted_command(monkeypatch, angle):
  controller, cs, cc, settings = setup_controller(monkeypatch, angle=angle)
  settings.update(CustomSteerMax=409, CustomSteerDeltaUp=3)
  cs.out.steeringPressed = False
  cs.out.steeringTorque = 0
  cs.out.steeringAngleDeg = -2.2
  cc.actuators.torque = 1.0
  cc.actuators.steeringAngleDeg = 30
  attr = 'lfa_alt' if angle else 'lfa'
  setattr(cs, attr, None)
  address = 0xCB if angle else 0x12A
  for _ in range(200):
    output, messages = step(controller, cs, cc)
    assert not any(addr == address for addr, _, _ in messages)
    assert output.torqueOutputCan == 0
    assert controller.apply_torque_last == 0
    assert controller.apply_angle_last == pytest.approx(-2.2)
    assert controller.lkas_max_torque == 0
    assert cc.latActive  # local guard must not mutate the subscription
  setattr(cs, attr, {})
  output, messages = step(controller, cs, cc)
  data = next(data for addr, data, _ in messages if addr == address)
  if angle:
    assert output.torqueOutputCan == controller.params.ANGLE_MIN_TORQUE
    assert abs(output.steeringAngleDeg - cs.out.steeringAngleDeg) <= 1.0
    assert data[6] == controller.params.ANGLE_MIN_TORQUE
  else:
    assert output.torqueOutputCan == 3
    assert ((int.from_bytes(data, 'little') >> 41) & 0x7ff) - 1024 == 3


@pytest.mark.parametrize('angle', [False, True])
def test_initial_template_guard_does_not_rearm_during_operation(monkeypatch, angle):
  controller, cs, cc, _ = setup_controller(monkeypatch, angle=angle)
  cs.out.steeringPressed = False
  cs.out.steeringTorque = 0
  cc.actuators.torque = 1.0
  cc.actuators.steeringAngleDeg = 30
  step(controller, cs, cc)
  assert controller.steering_template_ready
  setattr(cs, 'lfa_alt' if angle else 'lfa', None)
  for _ in range(10):
    output, _ = step(controller, cs, cc)
    assert output.torqueOutputCan > 0
  cc.latActive = False
  step(controller, cs, cc)
  cc.latActive = True
  output, _ = step(controller, cs, cc)
  assert output.torqueOutputCan > 0 and controller.steering_template_ready


def test_sorento_camera_release_and_clean_restart_without_fresh_lfa(monkeypatch):
  model = CAR.KIA_SORENTO_2024
  cp = structs.CarParams(brand="hyundai", carFingerprint=model, flags=int(HyundaiFlags.CANFD | HyundaiFlags.CAMERA_SCC),
                         steerControlType="torque", wheelbase=model.config.specs.wheelbase, steerRatio=model.config.specs.steerRatio)
  controller, cs, cc, _ = setup_controller(monkeypatch, angle=False, cp_override=cp)
  cs.out.steeringPressed = False
  cs.out.steeringTorque = 0
  cs.mdps = {"STEERING_COL_TORQUE": 0}
  cs.lfa = {"STEER_REQ": 0}
  cc.actuators.torque = 0.6

  def commands(count):
    output, messages = step(controller, cs, cc, camera_frames=count)
    assert any(addr == 0xEA for addr, _, _ in messages)
    return output.torqueOutputCan, [payload for addr, payload, _ in messages if addr == 0x12A]

  for _ in range(30):
    last, _ = commands(1)
  assert last > 10
  assert commands(0) == (last, [])
  cc.latActive = False
  torque, packets = commands(0)
  assert torque == 0 and len(packets) == 1 and not packets[0][6] & 16
  cc.latActive = True
  assert commands(1)[0] == 2
  for _ in range(8):
    torque, packets = commands(0)
  assert torque == 0 and len(packets) == 1 and not packets[0][6] & 16
  assert commands(1)[0] == 0  # first frame after an interruption is neutral
  assert commands(1)[0] == 2


def test_camera_lfa_cadence_does_not_replay_batches_or_infer_missing_frames():
  cadence = carcontroller.CameraLfaCadence()
  parser = NS(ts_nanos={}, vl_all={}, _last_update_nanos=0)

  def poll(ms, counters, *, batch_ms=None):
    parser._last_update_nanos = ms * 1_000_000
    parser.ts_nanos["LFA"] = {"COUNTER": (ms if batch_ms is None else batch_ms) * 1_000_000}
    parser.vl_all["LFA"] = {"COUNTER": counters}
    return cadence.poll(parser, (ms + 1000) * 1_000_000)

  assert poll(10, [254, 255]) == (True, True)
  assert poll(20, [254, 255], batch_ms=10) == (True, True)
  assert poll(30, [255]) == (True, False)
  assert poll(40, [0]) == (True, True)
  assert poll(50, [15]) == (True, True)
  assert poll(60, [15]) == (True, False)
  assert poll(130, [16], batch_ms=65) == (False, False)
  assert poll(140, [17]) == (False, False)
  assert poll(150, [18]) == (True, True)
