"""Opt-in Honda/Toyota torque-controller tuning, retaining the vehicle's CAN/safety limits.

The low-speed error compensation, curvature history, roll/offset fade and center jerk
deadzone follow StarPilotHQ/StarPilot@98f8443122909a86c5a5fd628337c4077cd1f957,
selfdrive/controls/lib/latcontrol_torque.py. See docs/LOW_SPEED_STEERING_TUNE.md
for attribution, adaptations and the intentionally narrower activation scope.

Adapted portions are provided under the StarPilot MIT license:
+Copyright (c) 2018, Comma.ai, Inc.
Copyright (c) 2026, firestar5683 and StarPilot contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without
limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

import math
from collections import deque

import numpy as np

from opendbc.car.honda.values import CAR as HONDA
from opendbc.car.toyota.values import CAR as TOYOTA, ToyotaSafetyFlags
from opendbc.car.structs import CarParams
from openpilot.common.params import Params


def supports_low_speed_tune(CP: CarParams | None) -> bool:
  if CP is None or CP.dashcamOnly or CP.steerControlType != CarParams.SteerControlType.torque:
    return False
  if not CP.safetyConfigs:
    return False
  safety = CP.safetyConfigs[-1]
  if CP.brand == "toyota":
    return bool(CP.carFingerprint in TOYOTA and safety.safetyModel == CarParams.SafetyModel.toyota and
                not safety.safetyParam & ToyotaSafetyFlags.LTA)
  if CP.brand == "honda":
    return bool(CP.carFingerprint in HONDA and safety.safetyModel in (CarParams.SafetyModel.hondaNidec, CarParams.SafetyModel.hondaBosch))
  return False


class LowSpeedSteeringTune:
  def __init__(self, CP: CarParams, dt: float, params: Params | None = None):
    params = params if params is not None else Params()
    # Latch once at controller construction. A Params write during a drive cannot change the tuning.
    self.enabled = (params.get_bool("LowSpeedSteeringTune") and supports_low_speed_tune(CP) and
                    CP.lateralTuning.which() == "torque" and not params.get_bool("NeuralNetworkLateralControl") and
                    not params.get_bool("LateralJerkTorqueController"))
    self.active = False
    self.history = deque(maxlen=max(2, int(1.0 / dt)))

  @staticmethod
  def weight(speed: float) -> float:
    # Keep this port local to low speed: taper between 36 and 54 km/h.
    return float(np.interp(speed, [10.0, 15.0], [1.0, 0.0]))

  def reset(self, curvature: float) -> None:
    self.active = False
    self.history.clear()
    self.history.extend([curvature] * self.history.maxlen)

  def expected_accel(self, baseline: float, curvature: float, speed: float, delay_frames: int,
                     active: bool, steering_pressed: bool, append_first: bool) -> float:
    if not self.enabled:
      return baseline
    if not active or steering_pressed or not self.history:
      self.reset(curvature)
    self.active = active and not steering_pressed
    if append_first:
      self.history.append(curvature)
    index = max(1, min(delay_frames, len(self.history)))
    expected = self.history[-index] * speed ** 2
    if not append_first:
      self.history.append(curvature)
    if not self.active:
      return baseline
    weight = self.weight(speed)
    return baseline + weight * (expected - baseline)

  def scale_error(self, error: float, speed: float, kp: float) -> float:
    if not self.active or self.weight(speed) == 0:
      return error
    factor = (float(np.interp(speed, [0, 10, 20, 30], [12, 10.5, 8, 5])) / max(speed, 1.0)) ** 2
    return error * (1 + self.weight(speed) * factor / max(kp, 1e-3))

  def feedforward(self, baseline: float, roll: float, offset: float, speed: float) -> float:
    if not self.active:
      return baseline
    fade = float(np.interp(speed, [0.5, 2.5], [0.0, 1.0]))
    return baseline + (roll + offset) * (1 - fade)

  def friction_error(self, error: float, jerk: float, speed: float, setpoint: float, legacy_gain: float) -> float:
    baseline = error + legacy_gain * jerk
    if not self.active or self.weight(speed) == 0:
      return baseline
    deadzone = float(np.interp(speed, [0, 5, 12, 25], [0.08, 0.12, 0.18, 0.18]))
    deadzone *= float(np.interp(abs(setpoint), [0, 0.18, 0.35], [1, 1, 0]))
    bounded_jerk = float(np.clip(jerk, -2.5, 2.5))
    friction_jerk = math.copysign(max(abs(bounded_jerk) - deadzone, 0.0), bounded_jerk)
    return baseline + self.weight(speed) * (0.22 * friction_jerk - legacy_gain * jerk)
