import sys
from types import ModuleType, SimpleNamespace

import pytest


# The production modules are available on the Linux device. Windows unit-test
# hosts need small import shims for platform-only hardware and Params bindings;
# the tests below exercise the tuning refresh directly without constructing
# either dependency.
if sys.platform == "win32":
  hardware_module = ModuleType("openpilot.system.hardware")
  hardware_module.PC = True
  sys.modules.setdefault("openpilot.system.hardware", hardware_module)

  params_module = ModuleType("openpilot.common.params")
  params_module.Params = object
  sys.modules.setdefault("openpilot.common.params", params_module)

from opendbc.car.hyundai.values import CAR, HyundaiFlags
import openpilot.selfdrive.controls.lib.longcontrol as longcontrol_module
from openpilot.selfdrive.controls.lib.longcontrol import LongControl


def make_cp(brand="hyundai"):
  return SimpleNamespace(
    brand=brand,
    flags=0, openpilotLongitudinalControl=True,
    longitudinalTuning=SimpleNamespace(
      kpBP=[0.0], kpV=[9.0], kiBP=[0.0], kiV=[9.0], kf=9.0,
    ),
    startingState=False,
    vEgoStarting=0.5,
    stopAccel=0.0,
    stoppingDecelRate=0.8,
  )


def stop_inputs(*, soft_hold=0, a_ego=0., nearby=False):
  cs = SimpleNamespace(softHoldActive=soft_hold, vEgo=.1, aEgo=a_ego, brakePressed=False,
                       cruiseState=SimpleNamespace(standstill=False))
  plan = SimpleNamespace(aTarget=-.5, vTargetNow=.1, jTargetNow=0., shouldStop=True)
  radar = SimpleNamespace(leadOne=SimpleNamespace(status=nearby, dRel=3.))
  return cs, plan, radar


@pytest.mark.parametrize("brand", ["hyundai", "toyota", "gm", "mock"])
def test_stop_calibration_comes_from_vehicle(brand):
  cp = make_cp(brand)
  cp.stopAccel = -1.25
  control = LongControl(cp)
  assert control.stopping_accel == cp.stopAccel
  if brand == "hyundai":
    assert (control.pid.k_p, control.pid.k_i, control.pid.k_f) == (1., 0., 1.)
  elif brand == "toyota":
    assert (control.pid.k_p, control.pid.k_i, control.pid.k_f) == (0., 0., 1.)
  else:
    assert (control.pid.k_p, control.pid.k_i, control.pid.k_f) == (9., 9., 9.)


@pytest.mark.parametrize("a_ego", [-1.5, -.5, 0.])
@pytest.mark.parametrize("lead", [True, False])
def test_model_stop_and_release_follow_vehicle_interlocks(a_ego, lead):
  cp = make_cp()
  cp.stopAccel = -.6
  control = LongControl(cp)
  state = longcontrol_module.LongCtrlState
  control.long_control_state = state.pid
  control.last_output_accel = -.8
  cs, plan, radar = stop_inputs(a_ego=a_ego, nearby=lead)
  assert control.update(True, cs, plan, (-3.5, 2.), 0., radar)[0] == -.8
  assert control.long_control_state == state.stopping
  plan.shouldStop = False
  for brake, hold, expected in ((True, False, state.stopping), (False, True, state.stopping), (False, False, state.pid)):
    cs.brakePressed, cs.cruiseState.standstill = brake, hold
    control.update(True, cs, plan, (-3.5, 2.), 0., radar)
    assert control.long_control_state == expected
  cs.softHoldActive = 1
  assert control.update(True, cs, plan, (-3.5, 2.), 0., radar)[0] == cp.stopAccel


def test_ray_pedal_uses_vehicle_speed_pid():
  cp = make_cp()
  cp.carFingerprint = CAR.KIA_RAY_EV
  cp.flags = HyundaiFlags.CC_ONLY_CAR | HyundaiFlags.PEDAL_INTERCEPTOR
  cp.longitudinalTuning.kpV, cp.longitudinalTuning.kiV, cp.longitudinalTuning.kf = [.85], [.05], 1.2
  control = LongControl(cp)
  assert not control.hyundai_fixed_longitudinal_tuning
  assert not control.use_accel_pid
  assert (control.pid.k_p, control.pid.k_i, control.pid.k_f) == (.85, .05, 1.2)


@pytest.mark.parametrize("fingerprint,flags,longitudinal", [
  (CAR.KIA_RAY_EV, HyundaiFlags.CC_ONLY_CAR, True),
  (CAR.KIA_RAY_EV, HyundaiFlags.PEDAL_INTERCEPTOR, True),
  (CAR.KIA_RAY_EV, HyundaiFlags.CC_ONLY_CAR | HyundaiFlags.PEDAL_INTERCEPTOR, False),
  (CAR.HYUNDAI_SONATA, HyundaiFlags.CC_ONLY_CAR | HyundaiFlags.PEDAL_INTERCEPTOR, True),
  (CAR.HYUNDAI_CASPER_EV, HyundaiFlags.CAMERA_SCC, True),
])
def test_other_hyundai_configurations_keep_fixed_tuning(fingerprint, flags, longitudinal):
  cp = make_cp()
  cp.carFingerprint, cp.flags, cp.openpilotLongitudinalControl = fingerprint, flags, longitudinal
  control = LongControl(cp)
  assert control.hyundai_fixed_longitudinal_tuning
  assert (control.pid.k_p, control.pid.k_i, control.pid.k_f) == (1., 0., 1.)
