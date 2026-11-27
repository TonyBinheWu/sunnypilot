#!/usr/bin/env python3
import math
import numpy as np

from openpilot.common.params import Params

import openpilot.cereal.messaging as messaging
from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX
from openpilot.cereal import log
from openpilot.common.constants import CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.navigation.helpers import nearby_maneuver
from openpilot.selfdrive.controls.lib.cruise_coasting import no_coasting_lead
from openpilot.selfdrive.controls.lib.curve_speed import CurveSpeed
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.sunny_longitudinal import DynamicExperimentalControl, acc_comfort_limit
from openpilot.selfdrive.controls.lib.upstream_mpc.long_mpc import LongitudinalMpc, LongitudinalPlanSource, STOP_DISTANCE, get_T_FOLLOW
from openpilot.selfdrive.controls.lib.upstream_mpc.long_mpc import T_IDXS as T_IDXS_MPC
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N, smooth_value
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX, V_CRUISE_UNSET
from openpilot.common.swaglog import cloudlog

J_CRUISE_VALS = [1.6, 1.2, 0.8, 0.6]
J_CRUISE_BP = [0., 10.0, 25., 40.]
A_CRUISE_MIN = -0.5
ACCEL_BOOST = {  # m/s^2
  log.LongitudinalPersonality.relaxed: 0.0,
  log.LongitudinalPersonality.standard: 0.05,
  log.LongitudinalPersonality.aggressive: 0.15,
}
CONTROL_N_T_IDX = ModelConstants.T_IDXS[:CONTROL_N]
MAX_RADAR_AGE_NS = 150_000_000
CLEAR_ROAD_CONFIRM_NS = 500_000_000


# Adapted from commaai/openpilot 88d47a473. The fork has a different delay helper.
def should_stop(speed, accel):
  return speed < .3 and accel < .1


def get_accel_from_plan(speeds, accels, times, action_t):
  delay = max(.3, action_t)
  return 2 * (np.interp(delay, times, speeds) - speeds[0]) / delay - accels[0]


def get_cruise_accel(v_cruise, v_ego, a_cruise_prev, a_target_prev, dt, *, dec=False):
  target_accel = v_cruise - v_ego
  lower = a_cruise_prev
  if not dec:
    target_accel = smooth_value(target_accel, a_cruise_prev, tau=1.0, dt=dt)
    lower = min(a_cruise_prev, a_target_prev)
  target_accel = np.clip(target_accel, A_CRUISE_MIN, ACCEL_MAX)
  j_cruise = np.interp(v_ego, J_CRUISE_BP, J_CRUISE_VALS)
  target_accel = float(np.clip(target_accel, lower - j_cruise * dt, a_cruise_prev + j_cruise * dt))

  return target_accel


def assisted_ceiling(sm, cruise, map_curve, speed_limit):
  reason = 'cruise'
  stamp = sm.logMonoTime['modelV2']
  if map_curve and sm.all_checks(['carrotMan']):
    road = sm['carrotMan']
    cap = road.routeCurveKph * CV.KPH_TO_MS
    if (0 < road.positionFixMonoTime and 0 <= stamp - road.positionFixMonoTime < 2e9 and
        0 <= stamp - sm.logMonoTime['carrotMan'] < 2e9 and 0 < cap < cruise):
      cruise, reason = cap, 'mapCurve'
  if speed_limit and sm.all_checks(['navInstruction']):
    cap = sm['navInstruction'].speedLimit
    if 0 <= stamp - sm.logMonoTime['navInstruction'] < 2e9 and 0 < cap < cruise:
      cruise, reason = cap, 'speedLimit'
  return cruise, reason


def camera_leads(model, v_ego):
  """Build the MPC's two lead observations from the current camera frame."""
  state = log.RadarState.new_message()
  if not model.velocity.x or not math.isfinite(model.velocity.x[0]):
    return state
  for i, observation in enumerate(model.leadsV3):
    if i >= 2:
      break
    if not all((observation.x, observation.y, observation.v, observation.a)):
      continue
    x, y, v, a = (values[0] for values in (observation.x, observation.y, observation.v, observation.a))
    if not all(map(math.isfinite, (x, y, v, a, observation.prob, v_ego))) or observation.prob <= .5 or x <= 1.52:
      continue
    lead = state.leadOne if i == 0 else state.leadTwo
    lead.status = True
    lead.modelProb = observation.prob
    lead.dRel = x - 1.52  # camera-to-bumper offset used by upstream RadarD
    lead.yRel = -y
    lead.vRel = v - model.velocity.x[0]
    lead.vLead = lead.vLeadK = v_ego + lead.vRel
    lead.aLeadK = a
    lead.aLeadTau = .3
    lead.radarTrackId = -1
  return state


class LongitudinalPlanner:
  def __init__(self, CP, init_v=0.0, init_a=0.0, dt=DT_MDL, *, vision_only=False, sunny=False):
    self.vision_only = vision_only
    self.sunny = sunny
    self.dec_enabled = False
    if sunny:
      settings = Params()
      self.dec_enabled = settings.get_bool("DynamicExperimentalControl")
      self.vision_curve = settings.get_bool("SunnyVisionCurve")
      self.map_curve = settings.get_bool("SunnyMapCurve")
      self.speed_limit = settings.get_bool("SunnySpeedLimit")
    self.dec = None
    self.previous_model_stamp = 0
    self.longitudinal_mode = ''
    self.CP = CP
    self.mpc = LongitudinalMpc(dt=dt)
    self.fcw = False
    self.dt = dt
    self.curve_speed = CurveSpeed(dt)
    self.opening_track = None
    self.opening_since = self.last_radar_time = 0
    self.clear_since_ns = self.last_clear_sample_ns = 0

    self.v_desired_filter = FirstOrderFilter(init_v, 2.0, self.dt)
    self.a_cruise = init_a
    self.output_a_target = init_a
    self.output_should_stop = False

    self.v_desired_trajectory = np.zeros(CONTROL_N)
    self.a_desired_trajectory = np.zeros(CONTROL_N)
    self.j_desired_trajectory = np.zeros(CONTROL_N)

  def opening_lead_boost(self, sm, eligible):
    """Modest recovery only during sustained separation from the same tracked lead."""
    lead, second = self.leads.leadOne, self.leads.leadTwo
    stamp = self.leads.mdMonoTime
    if not (eligible and lead.status and lead.radar and lead.radarTrackId >= 0 and
            lead.vRel > 0.5 and lead.aLeadK >= -0.2 and
            lead.dRel > STOP_DISTANCE + (self.t_follow + 0.5) * sm['carState'].vEgo and
            not (second.status and second.dRel < lead.dRel) and not self.leads.leadCutInRisk.status):
      self.opening_track = None
      return 0.
    if self.opening_track != lead.radarTrackId or not 0 <= stamp - self.last_radar_time < MAX_RADAR_AGE_NS:
      self.opening_track = lead.radarTrackId
      self.opening_since = stamp
    self.last_radar_time = stamp
    seconds = (stamp - self.opening_since) * 1e-9
    return min(0.35, 0.2 * lead.vRel, 0.2 * max(0., seconds - 1.))

  def confirmed_clear_road(self, eligible):
    """Release the synthetic lead ceiling only after consecutive healthy, empty radar observations."""
    radar = self.leads
    stamp = radar.mdMonoTime
    if not (eligible and no_coasting_lead(radar)):
      self.clear_since_ns = self.last_clear_sample_ns = 0
      return False
    if not self.clear_since_ns or not 0 <= stamp - self.last_clear_sample_ns < MAX_RADAR_AGE_NS:
      self.clear_since_ns = stamp
    self.last_clear_sample_ns = stamp
    return stamp - self.clear_since_ns >= CLEAR_ROAD_CONFIRM_NS

  def dec_acc_limit(self, sm, eligible, clear_road, curve_offset):
    """Return the ACC comfort limit only while the current frame permits cruise following."""
    model, cs = sm['modelV2'], sm['carState']
    stamp = sm.logMonoTime['modelV2']
    previous_stamp, self.previous_model_stamp = self.previous_model_stamp, stamp
    leads = (self.leads.leadOne, self.leads.leadTwo)
    if not (eligible and self.mpc.solution_status == 0 and not self.leads.leadCutInRisk.status
            and (clear_road or any(lead.status for lead in leads))
            and previous_stamp > 0 and 0 < stamp - previous_stamp < MAX_RADAR_AGE_NS
            and all(abs(stamp - sm.logMonoTime[k]) < MAX_RADAR_AGE_NS for k in ('radarState', 'controlsState', 'carState'))
            and DynamicExperimentalControl.valid_trajectory(model)):
      self.dec = None
      return None

    if self.dec is None:
      self.dec = DynamicExperimentalControl(not self.CP.radarUnavailable)
    urgency = self.dec.slowdown_urgency(cs.vEgo, model.position.x[-1])
    selected = self.dec.update(cs, urgency, leads[0], self.mpc.crash_cnt)
    if selected != 'acc' or self.dec.duration < 10 or urgency > .24 or self.mpc.crash_cnt:
      return None
    # A cut-in or a closing lead can appear one frame before the MPC starts braking.
    if any(lead.status and not (math.isfinite(lead.dRel) and math.isfinite(lead.vRel) and math.isfinite(lead.aLeadK)
                                and lead.dRel > STOP_DISTANCE + self.t_follow * cs.vEgo and lead.vRel >= -.5 and lead.aLeadK >= -.2)
           for lead in leads):
      return None
    brake = model.meta.disengagePredictions.brakePressProbs
    gas = model.meta.disengagePredictions.gasPressProbs
    if not (len(brake) >= 2 and 0. <= brake[1] < .3 and len(gas) >= 2 and .4 < gas[1] <= 1.
            and model.action.desiredAcceleration >= -.2 and curve_offset >= 0.
            and abs(model.action.desiredCurvature) * cs.vEgo**2 < 1.5):
      return None
    preview = [abs(v * yaw) for t, v, yaw in zip(model.position.t, model.velocity.x, model.orientationRate.z, strict=True)
               if 0. <= t <= 3.]
    if not preview or not all(a < 1.5 for a in preview) or nearby_maneuver(sm, stamp, cs.vEgo) is not None:
      return None
    return acc_comfort_limit(self.CP, cs.vEgo, cs.steeringAngleDeg - sm['liveParameters'].angleOffsetDeg)

  def update(self, sm):
    v_ego = sm['carState'].vEgo
    if self.vision_only or self.sunny:
      model = sm['modelV2']
      self.camera_input_valid = sm.all_checks(['modelV2', 'carState', 'liveParameters']) and all(map(math.isfinite, (
        v_ego, sm['carState'].aEgo, sm['liveParameters'].roll, model.action.desiredAcceleration,
        model.action.desiredCurvature)))
      if not self.camera_input_valid:
        self.opening_track = None
        self.clear_since_ns = self.last_clear_sample_ns = 0
        self.dec = None
        self.previous_model_stamp = 0
        self.longitudinal_mode = ''
        return
    personality = sm['selfdriveState'].personality.raw
    if personality == log.LongitudinalPersonality.moreRelaxed:
      personality = log.LongitudinalPersonality.relaxed
    self.t_follow = get_T_FOLLOW(personality)
    raw_ceiling = sm['carState'].vCruise
    self.ceiling_available = math.isfinite(raw_ceiling) and 0 <= raw_ceiling < V_CRUISE_UNSET
    self.cruise_target = min(raw_ceiling, V_CRUISE_MAX) if self.ceiling_available else 0.
    v_cruise = self.cruise_target * CV.KPH_TO_MS if self.ceiling_available else v_ego
    ceiling_reason = 'cruise'
    if self.sunny:
      v_cruise, ceiling_reason = assisted_ceiling(sm, v_cruise, self.map_curve, self.speed_limit)
    if sm['controlsState'].forceDecel:
      v_cruise = 0.0

    long_control_off = sm['controlsState'].longControlState == LongCtrlState.off

    # Reset current state when not engaged, or user is controlling the speed
    reset_state = long_control_off if self.CP.openpilotLongitudinalControl else not sm['selfdriveState'].enabled
    # PCM cruise speed may be updated a few cycles later, check if initialized
    reset_state = reset_state or not self.ceiling_available

    if reset_state:
      self.v_desired_filter.x = v_ego
      self.output_a_target = np.clip(sm['carState'].aEgo, ACCEL_MIN, ACCEL_MAX)
      self.a_cruise = self.output_a_target
      self.curve_speed.reset()

    # Prevent divergence, smooth in current v_ego
    self.v_desired_filter.x = max(0.0, self.v_desired_filter.update(v_ego))

    # No change cost when user is controlling the speed, or when standstill
    prev_accel_constraint = not (reset_state or sm['carState'].standstill)

    self.mpc.set_weights(prev_accel_constraint, personality=personality)
    if self.CP.openpilotLongitudinalControl:
      self.mpc.set_cur_state(self.v_desired_filter.x, self.output_a_target)
    else:
      self.mpc.set_cur_state(v_ego, sm['carState'].aEgo)
    self.leads = camera_leads(sm['modelV2'], v_ego) if self.vision_only else sm['radarState']
    self.mpc.update(self.leads, personality=personality)

    self.v_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.v_solution)
    self.a_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.a_solution)
    self.j_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC[:-1], self.mpc.j_solution)

    # TODO counter is only needed because radar is glitchy, remove once radar is gone
    self.fcw = self.mpc.crash_cnt > 2 and not sm['carState'].standstill
    if self.fcw:
      cloudlog.info("FCW triggered")

    # Save starting point for next iteration
    a_prev = self.output_a_target

    action_t =  self.CP.longitudinalActuatorDelay + DT_MDL
    output_a_target_mpc = get_accel_from_plan(self.v_desired_trajectory, self.a_desired_trajectory, CONTROL_N_T_IDX,
                                              action_t=action_t)
    output_should_stop_mpc = should_stop(v_ego, output_a_target_mpc)
    curve_offset = self.curve_speed.update(sm['modelV2'], sm['liveParameters'].roll) if not self.sunny or self.vision_curve else 0.
    output_a_target_e2e = sm['modelV2'].action.desiredAcceleration + curve_offset
    speed_scale = np.interp(v_ego, [5.0, 10.0], [0.0, 1.0])
    accel_scale = np.interp(output_a_target_e2e, [-1.0, -0.5], [0.0, 1.0])
    if not self.sunny:
      output_a_target_e2e += ACCEL_BOOST[personality] * speed_scale * accel_scale
    output_should_stop_e2e = sm['modelV2'].action.shouldStop

    direct = self.CP.openpilotLongitudinalControl and sm['selfdriveState'].enabled and not reset_state
    dec_active = self.dec_enabled and direct
    self.a_cruise = get_cruise_accel(v_cruise, v_ego, self.a_cruise, self.output_a_target, self.dt, dec=dec_active)
    if not self.ceiling_available or (dec_active and (v_ego >= v_cruise or sm['controlsState'].forceDecel)):
      self.a_cruise = min(self.a_cruise, 0.)
    cruise_should_stop = should_stop(v_ego, self.a_cruise)

    clear_road = False
    recovery = 0.
    previous_mode = self.longitudinal_mode
    acc_limit = None
    if self.sunny:
      cs = sm['carState']
      errors = self.leads.radarErrors
      stamp = self.leads.mdMonoTime
      eligible = (direct
                  and cs.canValid and not cs.canTimeout and not (cs.standstill or cs.cruiseState.standstill or cs.softHoldActive)
                  and not (cs.brakePressed or cs.gasPressed or sm['controlsState'].forceDecel)
                  and not (self.fcw or output_should_stop_mpc or output_should_stop_e2e)
                  and output_a_target_mpc > 0. and sm.all_checks(['radarState', 'controlsState', 'selfdriveState'])
                  and 0 < stamp <= sm.logMonoTime['radarState']
                  and 0 <= sm.logMonoTime['modelV2'] - stamp < MAX_RADAR_AGE_NS
                  and not (errors.canError or errors.radarFault or errors.wrongConfig or errors.radarUnavailableTemporary))
      clear_road = self.confirmed_clear_road(eligible)
      self.longitudinal_mode = 'blended' if direct else ''
      if self.dec_enabled:
        acc_limit = self.dec_acc_limit(sm, eligible, clear_road, curve_offset)
        if direct:
          self.longitudinal_mode = 'decAcc' if acc_limit is not None else 'decBlended'
      opening = (eligible and self.leads.leadOne.status and v_ego > 5. and v_cruise - v_ego > 2.
                 and 0. < output_a_target_e2e < 0.6 and curve_offset == 0.
                 and abs(model.action.desiredCurvature) * v_ego**2 < 1.)
      if opening:
        trajectory = zip(model.position.t, model.velocity.x, model.orientationRate.z, strict=False)
        preview = [abs(v * yaw) for t, v, yaw in trajectory if 0. <= t <= 3.]
        opening = (bool(preview) and all(a < 1. for a in preview)
                   and nearby_maneuver(sm, sm.logMonoTime['modelV2'], v_ego) is None)
      recovery = min(self.opening_lead_boost(sm, opening), max(0., 0.6 - output_a_target_e2e))
      output_a_target_e2e += recovery
      if clear_road:
        # Both MPC obstacles are placeholders. The driver's speed ceiling still applies.
        # Use the existing cruise ramp when releasing a previous limit; braking stays immediate.
        rise = np.interp(v_ego, J_CRUISE_BP, J_CRUISE_VALS) * self.dt
        output_a_target_e2e = min(output_a_target_e2e, a_prev + rise)
    candidates = [(self.a_cruise, LongitudinalPlanSource.cruise, cruise_should_stop)]
    if acc_limit is None:
      candidates.append((output_a_target_e2e, LongitudinalPlanSource.e2e, output_should_stop_e2e))
    if not clear_road:
      candidates.insert(0, (output_a_target_mpc, self.mpc.source, output_should_stop_mpc))

    output_a_target, self.plan_source, _ = min(candidates, key=lambda c: c[0])
    self.speed_reason = {LongitudinalPlanSource.lead0: 'lead0', LongitudinalPlanSource.lead1: 'lead1',
                         LongitudinalPlanSource.cruise: 'cruise', LongitudinalPlanSource.e2e: 'e2e'}[self.plan_source]
    if self.plan_source == LongitudinalPlanSource.cruise and sm['controlsState'].forceDecel:
      self.speed_reason = 'forceDecel'
    elif self.speed_reason == 'cruise':
      self.speed_reason = ceiling_reason
    elif self.plan_source == LongitudinalPlanSource.e2e and recovery > 0.:
      self.speed_reason = 'openingLead'
    elif self.plan_source == LongitudinalPlanSource.e2e and curve_offset < 0:
      self.speed_reason = 'e2eCurve'
    elif self.speed_reason in ('lead0', 'lead1'):
      lead = self.leads.leadOne if self.speed_reason == 'lead0' else self.leads.leadTwo
      if not lead.status:
        self.speed_reason = 'mpc'
      elif self.vision_only:
        self.speed_reason = 'visionLead'
    self.output_should_stop = any(should_stop for _, _, should_stop in candidates)
    if acc_limit is not None and output_a_target > acc_limit:
      output_a_target, self.speed_reason = acc_limit, 'accComfort'
    if acc_limit is not None or (previous_mode == 'decAcc' and self.longitudinal_mode == 'decBlended'):
      rise_limit = a_prev + np.interp(v_ego, J_CRUISE_BP, J_CRUISE_VALS) * self.dt
      if output_a_target > rise_limit:
        output_a_target, self.speed_reason = rise_limit, 'cruiseRamp'
    self.output_a_target = np.clip(output_a_target, ACCEL_MIN, ACCEL_MAX)

    self.v_desired_filter.x = self.v_desired_filter.x + self.dt * (self.output_a_target + a_prev) / 2.0

  def publish(self, sm, pm):
    plan_send = messaging.new_message('longitudinalPlan')

    if (self.vision_only or self.sunny) and not self.camera_input_valid:
      plan_send.valid = False
      plan_send.longitudinalPlan.plannerProfile = 'sunny' if self.sunny else 'visionE2e'
      pm.send('longitudinalPlan', plan_send)
      return
    required = ['carState', 'controlsState', 'selfdriveState', 'modelV2', 'liveParameters']
    if not self.vision_only:
      required.append('radarState')
    plan_send.valid = sm.all_checks(required)

    longitudinalPlan = plan_send.longitudinalPlan
    longitudinalPlan.modelMonoTime = sm.logMonoTime['modelV2']
    longitudinalPlan.processingDelay = (plan_send.logMonoTime - sm.logMonoTime['modelV2']) / 1e9
    longitudinalPlan.solverExecutionTime = self.mpc.solve_time

    longitudinalPlan.speeds = self.v_desired_trajectory.tolist()
    longitudinalPlan.accels = self.a_desired_trajectory.tolist()
    longitudinalPlan.jerks = self.j_desired_trajectory.tolist()

    longitudinalPlan.hasLead = self.leads.leadOne.status
    if self.vision_only:
      longitudinalPlan.cameraLeadState = self.leads
    longitudinalPlan.longitudinalPlanSource = self.plan_source
    longitudinalPlan.fcw = self.fcw

    longitudinalPlan.aTarget = float(self.output_a_target)
    longitudinalPlan.shouldStop = bool(self.output_should_stop)
    longitudinalPlan.allowBrake = True

    longitudinalPlan.plannerProfile = 'visionE2e' if self.vision_only else 'sunny' if self.sunny else 'upstream'
    if self.vision_only or self.sunny:
      longitudinalPlan.visionPlannerSetup = getattr(self.CP, "visionPlannerSetup", "")
    longitudinalPlan.speedConstraint = self.speed_reason if self.CP.openpilotLongitudinalControl else 'stockLong'
    longitudinalPlan.longitudinalMode = self.longitudinal_mode
    longitudinalPlan.allowThrottle = self.ceiling_available
    longitudinalPlan.vTargetNow = float(max(0., sm['carState'].vEgo + self.output_a_target * self.dt))
    longitudinalPlan.jTargetNow = float(self.j_desired_trajectory[0])
    longitudinalPlan.cruiseTarget = self.cruise_target
    longitudinalPlan.tFollow = self.t_follow
    pm.send('longitudinalPlan', plan_send)
