"""Read-only adapter. No CAN publisher, location, camera, params writes or RPC."""
import math
import time

from openpilot.sunnypilot.formosalink.protocol import VERSION, validate_snapshot


def finite(value):
  try:
    result = float(value)
    return result if math.isfinite(result) else None
  except (TypeError, ValueError):
    return None


def maximum(values):
  return max((v for item in values if (v := finite(item)) is not None), default=None)


def source_valid(sm, service, maximum_age):
  # A low-rate observer cannot use receive-frequency checks designed for a
  # high-rate subscriber. Validate the producer timestamp and validity instead.
  age = time.monotonic() - sm.logMonoTime[service] / 1e9
  return bool(sm.seen[service] and sm.valid[service] and -1 <= age <= maximum_age)


def collect(sm, metadata, sequence, now=None):
  """Accept a fake SubMaster in host tests; stale sources always become null."""
  sm.update(0)
  device_valid = source_valid(sm, "deviceState", 5)
  car_valid = source_valid(sm, "carState", 2)
  metrics = {**metadata, "sample_valid": bool(device_valid), "started": None, "speed_kph": None,
             "cpu_temp_c": None, "gpu_temp_c": None, "memory_percent": None, "free_space_percent": None,
             "thermal_status": None, "device_type": None}
  if device_valid:
    device = sm["deviceState"]
    metrics.update(started=bool(device.started), cpu_temp_c=maximum(device.cpuTempC), gpu_temp_c=maximum(device.gpuTempC),
                   memory_percent=finite(device.memoryUsagePercent), free_space_percent=finite(device.freeSpacePercent),
                   thermal_status=str(device.thermalStatus), device_type=str(device.deviceType))
    if device.started and car_valid:
      speed = finite(sm["carState"].vEgo)
      metrics["speed_kph"] = round(max(0, speed) * 3.6, 1) if speed is not None else None
  return validate_snapshot({"version": VERSION, "sequence": sequence, "sampled_at": time.time() if now is None else now,
                            "metrics": metrics})


class OpenpilotSampler:
  def __init__(self):
    from openpilot.cereal import messaging
    try:
      from openpilot.common.version import get_version
    except ImportError:
      from openpilot.system.version import get_version
    from openpilot.common.git import get_branch, get_commit
    self.sm = messaging.SubMaster(["deviceState", "carState"])
    self.metadata = {"software_version": get_version(), "branch": get_branch(), "commit": get_commit()}

  def sample(self, sequence):
    return collect(self.sm, self.metadata, sequence)


class DemoSampler:
  def sample(self, sequence):
    return {"version": VERSION, "sequence": sequence, "sampled_at": time.time(), "metrics": {
      "sample_valid": True, "started": False, "cpu_temp_c": 46, "gpu_temp_c": 43,
      "memory_percent": 31, "free_space_percent": 72, "device_type": "DEMO · not a vehicle",
      "thermal_status": "green", "software_version": "FormosaPilot demo", "branch": "demo", "commit": "demo"}}
