import math


def executing_indicators(sm, cs, cc, now, panda_index=0):
  """EV6 mode 0 HUD feedback for the current apply tick only."""
  def fresh(service, age):
    stamp = sm.logMonoTime[service]
    return sm.valid[service] and sm.alive[service] and stamp > 0 and 0 <= now - stamp <= age

  if (not cc.enabled or not cs.canValid or cs.canTimeout or str(cs.gearShifter) != "drive" or
      cc.cruiseControl.cancel or cs.cruiseCancelState or not math.isfinite(cs.vEgo) or cs.vEgo <= 0. or cs.brakePressed or cs.gasPressed or
      cs.parkingBrake or cs.brakeHoldActive or cs.espActive or cs.stockAeb or cs.stockFcw or
      not fresh("carControl", 150_000_000) or not fresh("pandaStates", 500_000_000) or panda_index >= len(sm["pandaStates"])):
    return 0, False
  panda = sm["pandaStates"][panda_index]
  if not panda.controlsAllowed or panda.safetyRxChecksInvalid or str(panda.safetyModel) != "hyundaiCanfd":
    return 0, False

  direction = 0
  model = sm["modelV2"]
  if (cc.latActive and not (cs.steeringPressed or cs.steerFaultTemporary or cs.steerFaultPermanent)
      and fresh("modelV2", 250_000_000) and model.timestampEof > 0 and 0 <= now - model.timestampEof <= 250_000_000
      and str(model.meta.laneChangeState) in ("laneChangeStarting", "laneChangeFinishing")):
    side = str(model.meta.laneChangeDirection)
    if side == "left" and not cs.leftBlindspot:
      direction = 3
    elif side == "right" and not cs.rightBlindspot:
      direction = 4

  plan = sm["longitudinalPlan"]
  nav_active = (cc.longActive and str(cc.actuators.longControlState) == "pid" and not cc.cruiseControl.override and not cs.accFaulted and
                fresh("longitudinalPlan", 250_000_000) and plan.modelMonoTime > 0 and 0 <= now - plan.modelMonoTime <= 250_000_000
                and str(plan.longitudinalPlanSource) == "cruise" and not (plan.fcw or plan.shouldStop)
                and plan.speedConstraint in ("mapCurve", "speedLimit", "carrot/route"))
  return direction, nav_active
