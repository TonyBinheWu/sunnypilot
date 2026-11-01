from types import SimpleNamespace
from unittest.mock import patch

from opendbc.car.car_helpers import interfaces
from opendbc.car.structs import car
from opendbc.car.toyota.values import CAR
from openpilot.cereal import messaging
from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.sunnypilot.mici.layouts import steering
from openpilot.sunnypilot.selfdrive.controls.lib.low_speed_steering import (
  low_speed_tune_block_reason, low_speed_tune_vehicle_blocker, supports_low_speed_tune,
)
from tools.diagnostics.check_low_speed_steering import availability_report


def persisted_cp(model):
  # Use the actual UI serialization path and natural tuning; never force torque in this fixture.
  cp = interfaces[model].get_non_essential_params(model)
  return messaging.log_from_bytes(cp.to_bytes(), car.CarParams)


class TestLowSpeedAvailability(OpenpilotTestCase):
  def test_rav4_and_corolla_c4_persisted_params(self):
    params = Params()
    for model in (CAR.TOYOTA_RAV4, CAR.TOYOTA_RAV4_TSS2, CAR.TOYOTA_COROLLA, CAR.TOYOTA_COROLLA_TSS2):
      cp = persisted_cp(model)
      state = SimpleNamespace(CP=cp, params=params, is_offroad=lambda: True)
      with self.subTest(model=model), patch.object(steering, "ui_state", state):
        self.assertTrue(supports_low_speed_tune(cp))
        self.assertIsNone(low_speed_tune_block_reason(cp, params, True))
        self.assertTrue(steering.can_change_low_speed_tune())
        for key, reason in (("NeuralNetworkLateralControl", "nnlc"), ("LateralJerkTorqueController", "jerk")):
          params.put_bool(key, True, block=True)
          self.assertFalse(steering.can_change_low_speed_tune())
          self.assertEqual(low_speed_tune_block_reason(cp, params, True), reason)
          params.put_bool(key, False, block=True)

  def test_explicit_offroad_conflict_resolution_preserves_other_settings(self):
    params = Params()
    params.put_bool("NeuralNetworkLateralControl", True, block=True)
    params.put_bool("LateralJerkTorqueController", True, block=True)
    params.put_bool("LowSpeedSteeringTune", False, block=True)
    params.put_bool("EnforceTorqueControl", True, block=True)
    cp = persisted_cp(CAR.TOYOTA_RAV4_TSS2)
    before = cp.to_dict()
    with patch.object(steering, "ui_state", SimpleNamespace(CP=cp, params=params, is_offroad=lambda: True)):
      self.assertTrue(steering.clear_low_speed_tune_conflicts())
      self.assertTrue(steering.can_change_low_speed_tune())
      self.assertFalse(params.get_bool("NeuralNetworkLateralControl"))
      self.assertFalse(params.get_bool("LateralJerkTorqueController"))
      self.assertFalse(params.get_bool("LowSpeedSteeringTune"))
      self.assertTrue(params.get_bool("EnforceTorqueControl"))
      self.assertEqual(cp.to_dict(), before)

  def test_conflict_resolution_does_not_write_onroad_or_for_ineligible_cars(self):
    params = Params()
    for cp, offroad in ((persisted_cp(CAR.TOYOTA_RAV4_TSS2), False),
                         (persisted_cp(CAR.TOYOTA_RAV4_TSS2_2023), True), (None, True)):
      params.put_bool("NeuralNetworkLateralControl", True, block=True)
      params.put_bool("LateralJerkTorqueController", True, block=True)
      state = SimpleNamespace(CP=cp, params=params, is_offroad=lambda value=offroad: value)
      with patch.object(steering, "ui_state", state):
        self.assertFalse(steering.clear_low_speed_tune_conflicts())
        self.assertTrue(params.get_bool("NeuralNetworkLateralControl"))
        self.assertTrue(params.get_bool("LateralJerkTorqueController"))

  def test_reasons_do_not_relax_safety_or_lta_checks(self):
    params = Params()
    self.assertEqual(low_speed_tune_block_reason(None, params, True), "no_car")
    self.assertEqual(low_speed_tune_block_reason(persisted_cp(CAR.TOYOTA_RAV4_TSS2), params, False), "onroad")
    self.assertEqual(low_speed_tune_vehicle_blocker(persisted_cp(CAR.TOYOTA_RAV4_TSS2_2023)), "angle")
    cp = interfaces[CAR.TOYOTA_RAV4_TSS2].get_non_essential_params(CAR.TOYOTA_RAV4_TSS2)
    cp.dashcamOnly = True
    self.assertEqual(low_speed_tune_vehicle_blocker(cp), "dashcam")
    cp.dashcamOnly = False
    cp.safetyConfigs[0].safetyModel = car.CarParams.SafetyModel.noOutput
    self.assertEqual(low_speed_tune_vehicle_blocker(cp), "configuration")
    self.assertFalse(supports_low_speed_tune(cp))
    cp.carFingerprint = "UNKNOWN"
    self.assertEqual(low_speed_tune_vehicle_blocker(cp), "unsupported")

  def test_read_only_report_explains_persisted_vehicle_conflicts(self):
    params = Params()
    params.put_bool("IsOffroad", True, block=True)
    params.put_bool("NeuralNetworkLateralControl", True, block=True)
    cp = interfaces[CAR.TOYOTA_COROLLA_TSS2].get_non_essential_params(CAR.TOYOTA_COROLLA_TSS2)
    params.put("CarParamsPersistent", cp.to_bytes(), block=True)
    before = params.get("CarParamsPersistent")
    report = availability_report(params)
    self.assertTrue(report["vehicle_supported"])
    self.assertEqual(report["block_reason"], "nnlc")
    self.assertEqual(report["car"]["platform"], str(CAR.TOYOTA_COROLLA_TSS2))
    self.assertEqual(params.get("CarParamsPersistent"), before)
    self.assertTrue(params.get_bool("NeuralNetworkLateralControl"))
