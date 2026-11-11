import numpy as np

from opendbc.car import Bus, gen_empty_fingerprint
from opendbc.car.hyundai.interface import CarInterface
from opendbc.car.hyundai.values import CAR, CarControllerParams, HyundaiFlags
from opendbc.car.structs import car, CarControl, CarControlSP
from opendbc.car.vehicle_model import VehicleModel
from opendbc.sunnypilot.car.hyundai.torque import configure_low_speed_torque
from openpilot.cereal import log
from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.car.helpers import convert_to_capnp
from openpilot.selfdrive.controls.lib.latcontrol_torque import LatControlTorque as TorqueV1
from openpilot.selfdrive.locationd.torqued import TorqueEstimator, VERSION
from openpilot.sunnypilot.selfdrive.controls.lib.hkg_torque_scale import HkgTorqueScale
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_v0 import LatControlTorque as TorqueV0


def make_controller(cls, model, enabled):
  cp = CarInterface.get_params(model, gen_empty_fingerprint(), [], False, False, False)
  cp_sp = CarInterface.get_params_sp(cp, model, gen_empty_fingerprint(), [], False, False, False)
  configure_low_speed_torque(cp, enabled)
  ci = CarInterface(cp, cp_sp)
  if cp.flags & HyundaiFlags.CCNC:
    camera = ci.can_parsers[Bus.cam]
    ci.CS.msg_161 = dict(camera.vl["CCNC_0x161"])
    ci.CS.msg_162 = dict(camera.vl["CCNC_0x162"])
    ci.CS.msg_1b5 = dict(camera.vl["FR_CMR_03_50ms"])
  controller = cls(cp.as_reader(), convert_to_capnp(cp_sp).as_reader(), ci, 0.01)
  return controller, ci, VehicleModel(cp)


def update(controller, ci, vm, speed, curvature, active=True, pressed=False):
  state = car.CarState.new_message(vEgo=speed, vEgoRaw=speed, steeringPressed=pressed)
  params = log.VehicleParameters.new_message()
  request, _, pid_log = controller.update(active, state, vm, params, False, curvature, None, False, 0.2)
  ci.CS.out.vEgo = speed
  ci.CS.out.vEgoRaw = speed
  ci.CS.out.steeringTorque = 0
  cc = CarControl(enabled=active, latActive=active)
  cc.actuators.torque = float(request)
  applied, _ = ci.apply(cc.as_reader(), CarControlSP(), ci.CC.frame * 10_000_000)
  return request, applied, pid_log


class TestHkgTorqueScale(OpenpilotTestCase):
  def test_small_alternating_requests_keep_stock_can_gain(self):
    # Exercise actual v0/v1 -> Hyundai CarController, including its rate limiter.
    for cls in (TorqueV0, TorqueV1):
      for model in (CAR.KIA_SORENTO_2024, CAR.HYUNDAI_IONIQ_5, CAR.GENESIS_GV60_EV_1ST_GEN):
        for speed in (1., 5., 13., 15., 17.):
          with self.subTest(controller=cls.__module__, model=model, speed=speed):
            tuned, ci, vm = make_controller(cls, model, True)
            stock, stock_ci, stock_vm = make_controller(cls, model, False)
            for frame in range(120):
              curvature = 0.0001 if (frame // 5) % 2 else -0.0001
              request, applied, _ = update(tuned, ci, vm, speed, curvature)
              base_request, _, _ = update(stock, stock_ci, stock_vm, speed, curvature)
              maximum = {1.: 409, 5.: 409, 13.: 409, 15.: 340, 17.: 270}[speed]
              # Compare demand before the different (unchanged) 4/6 and 2/3
              # CAN rate envelopes; they need not produce identical transients.
              self.assertAlmostEqual(request * maximum, base_request * 270, places=4)
              self.assertAlmostEqual(applied.torque, applied.torqueOutputCan / maximum, places=6)

  def test_headroom_and_speed_transition_match_vehicle_limits(self):
    for cls in (TorqueV0, TorqueV1):
      for speed, maximum in ((5., 409), (13., 409), (15., 340), (17., 270)):
        controller, ci, vm = make_controller(cls, CAR.KIA_SORENTO_2024, True)
        before = ci.CP.to_dict()
        for sign in (-1, 1):
          with self.subTest(controller=cls.__module__, speed=speed, sign=sign):
            for _ in range(250):
              request, applied, _ = update(controller, ci, vm, speed, sign * 0.1)
              self.assertLessEqual(abs(request), 1. + 1e-6)
              self.assertLessEqual(abs(applied.torqueOutputCan), maximum)
            self.assertEqual(abs(applied.torqueOutputCan), maximum)
        self.assertAlmostEqual(controller.steer_max, maximum / 270)
        self.assertEqual(ci.CP.to_dict(), before)
      self.assertEqual(update(controller, ci, vm, 5., 0.1, active=False)[1].torqueOutputCan, 0)

  def test_learning_uses_can_units_and_separate_cache_version(self):
    _, ci, _ = make_controller(TorqueV0, CAR.KIA_SORENTO_2024, True)
    _, stock_ci, _ = make_controller(TorqueV0, CAR.KIA_SORENTO_2024, False)
    estimator = TorqueEstimator(ci.CP.as_reader())
    stock = TorqueEstimator(stock_ci.CP.as_reader())
    for maximum in (409, 340, 270):
      output = car.CarOutput.new_message()
      output.actuatorsOutput.torqueOutputCan = 81
      output.actuatorsOutput.torque = 81 / maximum
      estimator.handle_log(0., "carOutput", output)
      self.assertAlmostEqual(estimator.raw_points["steer_torque"][-1], -0.3)
    self.assertEqual(estimator.get_msg().lateralTorqueParameters.version, VERSION + 100)
    self.assertEqual(stock.get_msg().lateralTorqueParameters.version, VERSION)
    self.assertNotEqual(estimator.get_restore_key(ci.CP, VERSION), estimator.get_restore_key(ci.CP, estimator.version))
    self.assertNotEqual(estimator.get_restore_key(ci.CP, VERSION), estimator.get_restore_key(stock_ci.CP, VERSION))

  def test_reference_and_quantization_match_opendbc(self):
    _, ci, _ = make_controller(TorqueV0, CAR.KIA_SORENTO_2024, True)
    _, stock_ci, _ = make_controller(TorqueV0, CAR.KIA_SORENTO_2024, False)
    self.assertEqual(HkgTorqueScale.REFERENCE_MAX, CarControllerParams(stock_ci.CP).STEER_MAX)
    scale = HkgTorqueScale(ci.CP)
    for speed in np.linspace(12.9, 17.1, 421):
      ci.CS.out.vEgoRaw = float(speed)
      ci.CC.apply_torque_last = round(scale.controller_limit(ci.CS.out.vEgoRaw) * 270)
      cc = CarControl(enabled=True, latActive=True)
      cc.actuators.torque = 1.
      applied, _ = ci.apply(cc.as_reader(), CarControlSP(), ci.CC.frame * 10_000_000)
      self.assertAlmostEqual(scale.controller_limit(ci.CS.out.vEgoRaw) * 270, applied.torqueOutputCan)

  def test_old_normalization_cache_is_not_restored(self):
    _, ci, _ = make_controller(TorqueV0, CAR.KIA_SORENTO_2024, True)
    cached = log.Event.new_message()
    cached.init("lateralTorqueParameters")
    cached.lateralTorqueParameters.version = VERSION
    cached.lateralTorqueParameters.valid = True
    cached.lateralTorqueParameters.latAccelFactorFiltered = 99.
    params = Params()
    params.put("CarParamsPrevRoute", ci.CP.to_bytes(), block=True)
    params.put("LiveTorqueParameters", cached.to_bytes(), block=True)
    estimator = TorqueEstimator(ci.CP.as_reader())
    self.assertAlmostEqual(estimator.filtered_params["latAccelFactor"].x, ci.CP.lateralTuning.torque.latAccelFactor)
