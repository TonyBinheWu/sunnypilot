"""Explicit device information allowlist; never export arbitrary Params."""
from pathlib import Path


class DeviceInformation:
  def __init__(self, sm, params):
    self.sm, self.params = sm, params

  def capture(self):
    from openpilot.common.hardware import HARDWARE
    result = {}
    from openpilot.common.version import get_version
    from openpilot.common.git import get_branch, get_commit
    result.update(version=get_version(),branch=get_branch(),commit=get_commit())
    for key, method in (("serial", "get_serial"), ("os_version", "get_os_version"), ("hardware", "get_device_type")):
      try:
        result[key] = str(getattr(HARDWARE, method)())[:160]
      except Exception:
        pass
    for key, param in (("vehicle_vin", "CarVin"),):
      try:
        value = self.params.get(param)
        if value is not None:
          result[key] = str(value)[:160]
      except Exception:
        pass
    try:
      bundle = self.params.get("CarPlatformBundle") or {}
      for key in ("brand","platform"):
        if isinstance(bundle.get(key),str):
          result["vehicle_"+key] = bundle[key][:160]
    except Exception:
      pass
    try:
      result["uptime_seconds"] = int(float(Path("/proc/uptime").read_text().split()[0]))
      state = self.sm["deviceState"]
      for key, field in (("network_type", "networkType"), ("network_strength", "networkStrength"),
                         ("thermal_status", "thermalStatus"), ("memory_percent", "memoryUsagePercent"),
                         ("free_space_percent", "freeSpacePercent"), ("power_watts", "powerDrawW"),
                         ("fan_percent", "fanSpeedPercentDesired"), ("screen_brightness", "screenBrightnessPercent")):
        result[key] = str(getattr(state, field))[:160]
      result["cpu_temperatures"] = [round(float(v), 1) for v in state.cpuTempC][:32]
      result["gpu_temperatures"] = [round(float(v), 1) for v in state.gpuTempC][:32]
    except Exception:
      pass
    return result


class NativeTranslations:
  def __init__(self):
    from openpilot.system.ui.lib.multilang import load_translations
    root = Path(__file__).resolve().parents[2] / "selfdrive/ui/translations"
    self.translations = {}
    for language, filename in (("zh-TW", "app_zh-CHT.po"), ("ja", "app_ja.po")):
      try:
        self.translations[language] = load_translations(root / filename)[0]
      except Exception:
        self.translations[language] = {}

  def __call__(self, text):
    return {"en": text, **{lang: values.get(text) or text for lang, values in self.translations.items()}}
