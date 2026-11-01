import json
import math
from pathlib import Path

import numpy as np

from opendbc.car.car_helpers import interfaces
from opendbc.car.honda.values import CAR as HONDA
from opendbc.car.hyundai.values import CAR as HYUNDAI
from opendbc.car.structs import car
from opendbc.car.toyota.values import CAR as TOYOTA, ToyotaSafetyFlags
from opendbc.car.vehicle_model import VehicleModel
from openpilot.cereal import log
from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.car.helpers import convert_to_capnp
from openpilot.selfdrive.controls.lib.latcontrol_torque import LatControlTorque as TorqueV1
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_v0 import LatControlTorque as TorqueV0
from openpilot.sunnypilot.selfdrive.controls.lib.low_speed_steering import LowSpeedSteeringTune, supports_low_speed_tune
from openpilot.sunnypilot.sunnylink.capabilities import generate_capabilities
from openpilot.selfdrive.ui.translations.potools import extract_strings, parse_po
from openpilot.common.basedir import BASEDIR


def make_cp(model=TOYOTA.TOYOTA_PRIUS):
  interface = interfaces[model]
  cp = interface.get_non_essential_params(model)
  cp_sp = interface.get_non_essential_params_sp(cp, model)
  # Exercise the torque path for Honda without changing its physical steering mode.
  if cp.steerControlType == car.CarParams.SteerControlType.torque:
    interface.configure_torque_tune(model, cp.lateralTuning)
  return cp, cp_sp, interface


def make_controller(cls=TorqueV0, model=TOYOTA.TOYOTA_PRIUS, enabled=True):
  params = Params()
  params.put_bool("LowSpeedSteeringTune", enabled, block=True)
  cp, cp_sp, interface = make_cp(model)
  ci = interface(cp, cp_sp)
  controller = cls(cp.as_reader(), convert_to_capnp(cp_sp).as_reader(), ci, 0.01)
  return controller, VehicleModel(cp), cp


def run_frame(controller, vm, speed=5.0, curvature=0.0005, active=True, pressed=False, limited=False, roll=0.0):
  state = car.CarState.new_message(vEgo=speed, steeringPressed=pressed)
  params = log.VehicleParameters.new_message(roll=roll)
  return controller.update(active, state, vm, params, limited, curvature, None, False, 0.2)


class TestLowSpeedSteering(OpenpilotTestCase):
  def test_scope_and_safety_flags(self):
    for model in (TOYOTA.TOYOTA_PRIUS, TOYOTA.TOYOTA_COROLLA_TSS2, HONDA.HONDA_CIVIC):
      cp, _, _ = make_cp(model)
      before = cp.to_dict()
      self.assertTrue(supports_low_speed_tune(cp))
      self.assertEqual(cp.to_dict(), before)
      cp.dashcamOnly = True
      self.assertFalse(supports_low_speed_tune(cp))
      cp.dashcamOnly = False
      cp.carFingerprint = "UNKNOWN"
      self.assertFalse(supports_low_speed_tune(cp))
    for model in (TOYOTA.TOYOTA_RAV4_TSS2_2023, HYUNDAI.KIA_EV6):
      cp, _, _ = make_cp(model)
      self.assertFalse(supports_low_speed_tune(cp))
    cp, _, _ = make_cp()
    cp.safetyConfigs[0].safetyParam |= ToyotaSafetyFlags.LTA.value
    self.assertFalse(supports_low_speed_tune(cp))
    self.assertFalse(supports_low_speed_tune(None))

  def test_all_toyota_initialization_is_unchanged(self):
    Params().put_bool("LowSpeedSteeringTune", True, block=True)
    supported = 0
    for model in TOYOTA:
      cp, _, _ = make_cp(model)
      before = cp.to_dict()
      tuning = LowSpeedSteeringTune(cp, 0.01)
      supported += tuning.enabled
      self.assertEqual(cp.to_dict(), before, model)
      if cp.steerControlType == car.CarParams.SteerControlType.angle or cp.dashcamOnly:
        self.assertFalse(tuning.enabled, model)
    self.assertGreater(supported, 0)

  def test_latched_setting_and_alternative_controllers(self):
    controller, _, cp = make_controller()
    self.assertTrue(controller.low_speed_tune.enabled)
    Params().put_bool("LowSpeedSteeringTune", False, block=True)
    self.assertTrue(controller.low_speed_tune.enabled)
    self.assertFalse(LowSpeedSteeringTune(cp, 0.01).enabled)
    Params().put_bool("LowSpeedSteeringTune", True, block=True)
    for key in ("NeuralNetworkLateralControl", "LateralJerkTorqueController"):
      Params().put_bool(key, True, block=True)
      self.assertFalse(LowSpeedSteeringTune(cp, 0.01).enabled)
      Params().put_bool(key, False, block=True)
    cp.lateralTuning.init("pid")
    self.assertFalse(LowSpeedSteeringTune(cp, 0.01).enabled)

  def test_capabilities_follow_real_car_params(self):
    params = Params()
    self.assertFalse(generate_capabilities(params)["low_speed_steering_tune_available"])
    for model, expected in ((TOYOTA.TOYOTA_PRIUS, True), (HONDA.HONDA_CIVIC, True),
                            (TOYOTA.TOYOTA_RAV4_TSS2_2023, False), (HYUNDAI.KIA_EV6, False)):
      cp, _, _ = make_cp(model)
      params.put("CarParamsPersistent", cp.to_bytes(), block=True)
      self.assertEqual(generate_capabilities(params)["low_speed_steering_tune_available"], expected)

  def test_new_labels_are_extractable_and_translated(self):
    sources = ["openpilot/selfdrive/ui/sunnypilot/layouts/settings/steering.py",
               "openpilot/selfdrive/ui/sunnypilot/mici/layouts/steering.py"]
    extracted = {entry.msgid for entry in extract_strings(sources, BASEDIR)}
    _, entries = parse_po(Path(BASEDIR) / "openpilot/selfdrive/ui/translations/app_zh-CHT.po")
    translations = {entry.msgid: entry.msgstr for entry in entries}
    for key in ("Honda / Toyota Low-Speed Steering Tune (Experimental)", "Low-Speed Steering Tune",
                "Improve low-speed steering while keeping vehicle torque limits.",
                "Default off. Offroad changes apply next drive. Torque control only; disabled with NNLC or Lateral Jerk Torque Controller."):
      self.assertIn(key, extracted)
      self.assertTrue(translations.get(key))

  def test_gain_fade_and_friction_boundaries(self):
    controller, _, _ = make_controller()
    tune = controller.low_speed_tune
    tune.expected_accel(0, 0, 5, 20, True, False, False)
    self.assertAlmostEqual(tune.scale_error(0.01, 5, 11.5), 0.01 * (1 + (11.25 / 5) ** 2 / 11.5))
    for speed in (0.0, 0.3, 1.0, 5.0, 10.0, 12.5, 15.0, 30.0):
      self.assertTrue(math.isfinite(tune.scale_error(0.001, speed, 0.0)))
      self.assertAlmostEqual(tune.scale_error(-0.01, speed, 1.0), -tune.scale_error(0.01, speed, 1.0))
    self.assertEqual(tune.scale_error(0.01, 15, 1), 0.01)
    self.assertAlmostEqual(tune.feedforward(-0.5, 0.3, 0.2, 0.5), 0.0)
    self.assertAlmostEqual(tune.feedforward(-0.5, 0.3, 0.2, 1.5), -0.25)
    self.assertEqual(tune.feedforward(-0.5, 0.3, 0.2, 2.5), -0.5)
    self.assertEqual(tune.friction_error(0, 0.05, 5, 0, 0.3), 0.0)
    self.assertLess(abs(tune.friction_error(0, 1000, 5, 0, 0.0)), 0.55)
    self.assertEqual(tune.friction_error(0.1, 0.5, 15, 0, 0.3), 0.25)

  def test_curvature_history_does_not_create_acceleration_jerk(self):
    controller, _, _ = make_controller()
    tune = controller.low_speed_tune
    for speed in np.linspace(0.3, 8.0, 80):
      expected = tune.expected_accel(0.0, 0.005, speed, 20, True, False, False)
      self.assertAlmostEqual(expected, 0.005 * speed ** 2)
    tune.expected_accel(0.0, -0.01, 5, 20, False, False, False)
    self.assertAlmostEqual(tune.expected_accel(0, -0.01, 5, 20, True, False, False), -0.25)
    tune.expected_accel(0.0, 0.01, 5, 20, True, True, False)
    self.assertFalse(tune.active)
    self.assertAlmostEqual(tune.expected_accel(0, 0.01, 5, 20, True, False, False), 0.25)

  def test_v0_v1_response_limits_takeover_and_reengagement(self):
    for cls in (TorqueV0, TorqueV1):
      for model in (TOYOTA.TOYOTA_PRIUS, HONDA.HONDA_CIVIC):
        with self.subTest(controller=cls.__module__, model=model):
          tuned, vm, cp = make_controller(cls, model)
          baseline, baseline_vm, _ = make_controller(cls, model, enabled=False)
          tuned_before = cp.to_dict()
          for _ in range(100):
            tuned_out = run_frame(tuned, vm)[0]
            base_out = run_frame(baseline, baseline_vm)[0]
          self.assertGreater(abs(tuned_out), abs(base_out))
          for speed in (0.3, 1.0, 5.0, 10.0, 12.5, 15.0, 30.0):
            for curvature in (-0.1, 0.0, 0.1):
              output, _, _ = run_frame(tuned, vm, speed=speed, curvature=curvature)
              self.assertTrue(math.isfinite(output))
              self.assertLessEqual(abs(output), 1.0)
          run_frame(tuned, vm, pressed=True)
          self.assertFalse(tuned.low_speed_tune.active)
          self.assertEqual(tuned.pid.i, 0)
          output, _, _ = run_frame(tuned, vm, active=False)
          self.assertEqual(output, 0)
          self.assertEqual(tuned.pid.i, 0)
          run_frame(tuned, vm, limited=True)
          self.assertEqual(tuned.pid.i, 0)
          self.assertEqual(cp.to_dict(), tuned_before)

  def test_disabled_outputs_match_pre_port_fixture(self):
    fixture = json.loads(Path(__file__).with_name("low_speed_steering_baseline.json").read_text())
    for cls in (TorqueV0, TorqueV1):
      for model in (TOYOTA.TOYOTA_PRIUS, HONDA.HONDA_CIVIC):
        controller, vm, _ = make_controller(cls, model, enabled=False)
        actual = []
        for step in fixture["inputs"]:
          result = run_frame(controller, vm, **step)
          actual.append([result[0], result[2].error, result[2].f, result[2].desiredLateralJerk])
        expected = fixture["outputs"][f"{cls.__module__}:{model}"]
        np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)

  def test_high_speed_retains_original_calculations(self):
    for cls in (TorqueV0, TorqueV1):
      tuned, vm, _ = make_controller(cls)
      baseline, base_vm, _ = make_controller(cls, enabled=False)
      for _ in range(120):
        actual = run_frame(tuned, vm, speed=30, curvature=0.0001)
        expected = run_frame(baseline, base_vm, speed=30, curvature=0.0001)
        self.assertAlmostEqual(actual[0], expected[0], places=12)
