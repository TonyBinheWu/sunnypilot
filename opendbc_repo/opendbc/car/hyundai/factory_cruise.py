"""Receive-only factory cruise on Hyundai/Kia/Genesis harnesses."""
from opendbc.car.hyundai.values import CAR, HyundaiFlags


def fresh_values(parser, message, signal):
  values = parser.vl[message]
  timestamp = parser.ts_nanos[message][signal]
  if timestamp and 0 <= parser._last_update_nanos - timestamp <= 500_000_000:
    return values
  return {}


def update_ccnc_cruise(ret, pt, camera, speed_factor):
  # Actual longitudinal intervention comes from the brake controller. Camera
  # requests can disagree while another controller owns SCC or after cancel.
  feedback = fresh_values(pt, "TCS", "ACC_REQ")
  scc = fresh_values(camera, "SCC_CONTROL", "MainMode_ACC")
  ret.cruiseState.enabled = feedback.get("ACC_REQ") == 1
  ret.cruiseState.available = scc.get("MainMode_ACC") == 1 or ret.cruiseState.enabled
  ret.cruiseState.speed = scc.get("VSetDis", 0) * speed_factor
  ret.cruiseState.standstill = ret.cruiseState.enabled and scc.get("InfoDisplay", 0) >= 4
  gap = int(scc.get("DISTANCE_SETTING", 0))
  ret.pcmCruiseGap = gap if 1 <= gap <= 4 else 0


def update_non_scc_state(ret, CP, pt, cam, speed_conv):
  if CP.flags & HyundaiFlags.EV:
    status, ready, active = "LABEL11", "CC_React", "CC_ACT"
    speed, target = "E_EMS11", "Cruise_Limit_Target"
  elif CP.flags & HyundaiFlags.HYBRID:
    status, ready, active = "E_CRUISE_CONTROL", "CRUISE_LAMP_M", "CRUISE_LAMP_S"
    speed, target = "ELECT_GEAR", "SLC_SET_SPEED"
  else:
    status, ready, active = "EMS16", "CRUISE_LAMP_M", "CRUISE_LAMP_S"
    speed, target = "LVR12", "CF_Lvr_CruiseSet"

  lamps = fresh_values(pt, status, active)
  ret.cruiseState.available = bool(lamps.get(ready))
  ret.cruiseState.enabled = bool(lamps.get(active))
  ret.cruiseState.nonAdaptive = True
  ret.cruiseState.speed = fresh_values(pt, speed, target).get(target, 0) * speed_conv
  if CP.carFingerprint != CAR.KIA_FORTE_2019_NON_SCC:
    parser = pt if CP.carFingerprint == CAR.GENESIS_G70_2021_NON_SCC else cam
    fca = fresh_values(parser, "FCA11", "CF_VSM_Warn")
    warning = bool(fca.get("CF_VSM_Warn"))
    braking = bool(fca.get("CF_VSM_DecCmdAct") or fca.get("FCA_CmdAct"))
    ret.stockFcw = warning and not braking
    ret.stockAeb = warning and braking
