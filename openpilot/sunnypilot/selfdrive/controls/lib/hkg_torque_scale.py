"""Keep HKG control/learning in stock torque units while retaining extra headroom."""
import numpy as np

from opendbc.car.hyundai.values import CarControllerParams, HyundaiFlags
from opendbc.sunnypilot.car.hyundai.torque import supports_low_speed_torque


class HkgTorqueScale:
  # Hyundai torque tuning and NNLC models use the stock CAN-FD 270-unit scale.
  REFERENCE_MAX = 270

  def __init__(self, CP):
    self.enabled = supports_low_speed_torque(CP) and bool(CP.flags & HyundaiFlags.CANFD_DYNAMIC_TORQUE)
    self.params = CarControllerParams(CP) if self.enabled else None

  def controller_limit(self, speed: float) -> float:
    if self.params is None:
      return 1.0
    # Match CarController's vEgoRaw quantization and integer CAN limit exactly.
    rate_speed = float(np.ceil(max(0., speed) * 1000.)) / 1000.
    maximum = int(float(np.interp(rate_speed, *self.params.STEER_MAX_LOOKUP)) + 0.5)
    return maximum / self.REFERENCE_MAX

  def normalize(self, torque: float, speed: float) -> float:
    return torque / self.controller_limit(speed)

  def learning_torque(self, actuators) -> float:
    if self.enabled:
      return actuators.torqueOutputCan / self.REFERENCE_MAX
    return actuators.torque
