"""Read-only report for Honda/Toyota low-speed steering setting availability."""
import json

from opendbc.car.structs import car
from openpilot.cereal import messaging
from openpilot.common.hardware import HARDWARE
from openpilot.common.params import Params
from openpilot.common.version import get_version
from openpilot.sunnypilot.selfdrive.controls.lib.low_speed_steering import (
  LowSpeedSteeringTune, low_speed_tune_block_reason, supports_low_speed_tune,
)


def availability_report(params: Params | None = None) -> dict:
  params = params if params is not None else Params()
  offroad = params.get_bool("IsOffroad") if params.get("IsOffroad") is not None else None
  result = {
    "version": get_version(),
    "device": HARDWARE.get_device_type(),
    "offroad": offroad,
    "settings": {key: params.get_bool(key) for key in (
      "LowSpeedSteeringTune", "EnforceTorqueControl", "NeuralNetworkLateralControl",
      "LateralJerkTorqueController", "OpenpilotEnabledToggle",
    )},
    "car": None,
    "vehicle_supported": False,
    "block_reason": "no_car",
    "would_enable_with_current_car_params": False,
  }
  data = params.get("CarParamsPersistent")
  if data is not None:
    try:
      cp = messaging.log_from_bytes(data, car.CarParams)
      result["car"] = {
        "brand": cp.brand,
        "platform": cp.carFingerprint,
        "steering": str(cp.steerControlType),
        "tuning": cp.lateralTuning.which(),
        "dashcam_only": cp.dashcamOnly,
        "passive": cp.passive,
        "safety": [{"model": str(config.safetyModel), "param": config.safetyParam} for config in cp.safetyConfigs],
      }
      result["vehicle_supported"] = supports_low_speed_tune(cp)
      result["block_reason"] = low_speed_tune_block_reason(cp, params, offroad is True)
      result["would_enable_with_current_car_params"] = bool(LowSpeedSteeringTune(cp, 0.01, params).enabled)
    except Exception as error:
      result["block_reason"] = "invalid_car_params"
      result["error"] = type(error).__name__
  if offroad is None:
    result["block_reason"] = "offroad_state_unknown"
  return result


if __name__ == "__main__":
  print(json.dumps(availability_report(), ensure_ascii=False, indent=2))
