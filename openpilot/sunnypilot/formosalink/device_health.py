"""Read-only health adapter. Missing/stale telemetry never becomes a zero reading."""
import math
from openpilot.sunnypilot.formosalink.telemetry import source_valid


def number(value,minimum=-40,maximum=200,zero=False):
  return round(float(value),1) if type(value) in (int,float) and math.isfinite(value) and minimum<=value<=maximum and (zero or value!=0) else None


def fresh(sm,service,age=5):
  try:
    return source_valid(sm,service,age)
  except (KeyError,AttributeError,TypeError):
    return False


def collect_health(sm,brand):
  result={"health_valid":fresh(sm,"deviceState"),"vehicle_soc_percent":None,"soc_status":"unsupported",
          "egpu_status":"unknown","egpu_temp_c":None,"egpu_memory_temp_c":None}
  if result["health_valid"]:
    state=sm["deviceState"]
    result["device_model"]=str(state.deviceType)
    for key,field in (("cpu_temperatures","cpuTempC"),("gpu_temperatures","gpuTempC"),("pmic_temperatures","pmicTempC"),("modem_temperatures","modemTempC")):
      result[key]=[number(v) for v in getattr(state,field,[])][:32]
    for key,field in (("memory_temp_c","memoryTempC"),("dsp_temp_c","dspTempC"),("intake_temp_c","intakeTempC"),("exhaust_temp_c","exhaustTempC"),("gnss_temp_c","gnssTempC"),("bottom_soc_temp_c","bottomSocTempC"),("max_temp_c","maxTempC")):
      result[key]=number(getattr(state,field,None))
    zones=list(getattr(state,"thermalZones",[]))[:32]
    result["thermal_names"]=[str(z.name)[:96] for z in zones]
    result["thermal_values"]=[number(z.temp) for z in zones]
    present=getattr(state,"chestnutPresent",None)
    if present is not None:
      result["egpu_status"]="installed_unavailable" if present else "not_installed"
    if present and fresh(sm,"chestnutGpuState"):
      gpu=sm["chestnutGpuState"]
      result["egpu_temp_c"]=number(gpu.tempC)
      result["egpu_memory_temp_c"]=number(gpu.memoryTempC)
      if result["egpu_temp_c"] is not None:
        result["egpu_status"]="available"
  # Audited decoder: currently only comma body publishes fuelGauge as battery SOC.
  # Other brands leave the primitive at 0. Do not interpret that default as SOC.
  if brand=="body":
    result["soc_status"]="stale"
    if fresh(sm,"carState",2) and sm["carState"].canValid:
      soc=number(sm["carState"].fuelGauge,0,1,zero=True)
      if soc is not None:
        result.update(vehicle_soc_percent=round(float(sm["carState"].fuelGauge)*100,1),soc_status="available")
  return result
