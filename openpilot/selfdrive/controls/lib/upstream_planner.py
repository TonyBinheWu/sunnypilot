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
from openpilot.selfdrive.controls.lib.curve_speed import CurveSpeed
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.sunny_longitudinal import DynamicExperimentalControl, ModelAccelBoost, acc_comfort_limit
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


# Adapted from commaai/openpilot 88d47a473. The fork has a different delay helper.
def should_stop(speed, accel):
  return speed < .3 and accel < .1


def get_accel_from_plan(speeds, accels, times, action_t):
  delay = max(.3, action_t)
  return 2 * (np.interp(delay, times, speeds) - speeds[0]) / delay - accels[0]


def get_cruise_accel(v_cruise, v_ego, a_cruise_prev, a_target_prev, dt, *, sunny=False):
  target_accel = v_cruise - v_ego
  previous_lower = a_cruise_prev
  if not sunny:
    target_accel = smooth_value(target_accel, a_cruise_prev, tau=1.0, dt=dt)
    previous_lower = min(a_cruise_prev, a_target_prev)
  target_accel = np.clip(target_accel, A_CRUISE_MIN, ACCEL_MAX)
  j_cruise = np.interp(v_ego, J_CRUISE_BP, J_CRUISE_VALS)
  target_accel = float(np.clip(target_accel, previous_lower - j_cruise * dt, a_cruise_prev + j_cruise * dt))

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
    if sunny:
      settings = Params()
      self.vision_curve = settings.get_bool("SunnyVisionCurve")
      self.map_curve = settings.get_bool("SunnyMapCurve")
      self.speed_limit = settings.get_bool("SunnySpeedLimit")
      self.dec_enabled = settings.get_bool("DynamicExperimentalControl")
      self.dec = None
      self.model_boost = ModelAccelBoost()
      self.previous_model_stamp = 0
    self.longitudinal_mode = ''
    self.acc_ceiling = None
    self.CP = CP
    self.mpc = LongitudinalMpc(dt=dt)
    self.fcw = False
    self.dt = dt
    self.curve_speed = CurveSpeed(dt)
    self.opening_track = None
    self.opening_since = self.last_radar_time = 0

    self.v_desired_filter = FirstOrderFilter(init_v, 2.0, self.dt)
    self.a_cruise = init_a
    self.output_a_target = init_a
    self.output_should_stop = False

    self.v_desired_trajectory = np.zeros(CONTROL_N)
    self.a_desired_trajectory = np.zeros(CONTROL_N)
    self.j_desired_trajectory = np.zeros(CONTROL_N)

  def opening_lead_boost(self, sm, eligible):
    """Modest recovery only during sustained separation from the same tracked lead."""
    lead = self.leads.leadOne
    second = self.leads.leadTwo
    cs = sm['carState']
    stamp = sm.logMonoTime['radarState']
    if not (eligible and lead.status and lead.radar and lead.radarTrackId >= 0 and
            lead.vRel > 0.5 and lead.aLeadK >= -0.2 and
            lead.dRel > STOP_DISTANCE + (self.t_follow + 0.5) * cs.vEgo and
            not (second.status and second.dRel < lead.dRel) and
            sm.all_checks(['radarState', 'controlsState', 'selfdriveState']) and
            0 <= sm.logMonoTime['modelV2'] - stamp < 150_000_000):
      self.opening_track = None
      return 0.
    if self.opening_track != lead.radarTrackId or not 0 <= stamp - self.last_radar_time < 150_000_000:
      self.opening_track = lead.radarTrackId
      self.opening_since = stamp
    self.last_radar_time = stamp
    seconds = (stamp - self.opening_since) * 1e-9
    return min(0.35, 0.2 * lead.vRel, 0.2 * max(0., seconds - 1.))

  def sunny_model_adjustment(self, sm, v_cruise, model_accel, curve_offset, personality, reset_state):
    cs = sm['carState']
    v_ego, model = cs.vEgo, sm['modelV2']
    stamp = sm.logMonoTime['modelV2']
    maneuver = nearby_maneuver(sm, stamp, v_ego)
    preview = [abs(v * yaw) for t, v, yaw in zip(model.position.t, model.velocity.x, model.orientationRate.z, strict=False)
               if 0. <= t <= 3.]
    # A new lead can appear one solve before the MPC reacts. Withhold discretionary acceleration on that frame.
    clear_gap = all(not lead.status or (math.isfinite(lead.dRel) and math.isfinite(lead.vRel) and math.isfinite(lead.aLeadK)
                    and lead.dRel > STOP_DISTANCE + self.t_follow * v_ego and lead.vRel >= -.5 and lead.aLeadK >= -.2)
                    for lead in (self.leads.leadOne, self.leads.leadTwo))
    direct = self.CP.openpilotLongitudinalControl and sm['selfdriveState'].enabled and not reset_state
    eligible = (direct and
                v_ego > 5. and v_cruise - v_ego > 2. and not sm['controlsState'].forceDecel and
                0. < model_accel < 0.6 and not model.action.shouldStop and
                curve_offset == 0. and abs(model.action.desiredCurvature) * v_ego**2 < 1. and
                not cs.standstill and not cs.gasPressed and not cs.brakePressed and not self.fcw)
    eligible = eligible and clear_gap and maneuver is None and bool(preview) and all(a < 1. for a in preview)
    recovery = min(self.opening_lead_boost(sm, eligible), max(0., 0.6 - model_accel))

    healthy = (direct and self.previous_model_stamp > 0 and 0 < stamp - self.previous_model_stamp < 150_000_000
               and sm.all_checks(['radarState', 'controlsState', 'selfdriveState'])
               and all(abs(stamp - sm.logMonoTime[k]) < 150_000_000 for k in ('radarState', 'controlsState', 'carState'))
               and self.mpc.solution_status == 0)
    self.previous_model_stamp = stamp
    self.longitudinal_mode = ('decBlended' if self.dec_enabled else 'blended') if direct else ''
    trajectory_ok = healthy and DynamicExperimentalControl.valid_trajectory(model)
    urgency = DynamicExperimentalControl.slowdown_urgency(v_ego, model.position.x[-1]) if trajectory_ok else 1.
    if self.dec_enabled and trajectory_ok:
      if self.dec is None:
        self.dec = DynamicExperimentalControl(not self.CP.radarUnavailable)
      selected = self.dec.update(cs, urgency, self.leads.leadOne, self.mpc.crash_cnt)
      if selected == 'acc' and self.dec.duration >= 10:
        self.longitudinal_mode = 'decAcc'
    else:
      self.dec = None

    # Retain model braking, navigation turns and curve anticipation even in DEC's ACC phase.
    open_path = (clear_gap and urgency <= .24 and bool(preview) and all(a < 1.5 for a in preview)
                 and abs(model.action.desiredCurvature) * v_ego**2 < 1.5 and maneuver is None
                 and not (cs.standstill or cs.gasPressed or cs.brakePressed or sm['controlsState'].forceDecel
                          or self.mpc.crash_cnt or model.action.shouldStop or curve_offset < 0.))
    brake_probs = model.meta.disengagePredictions.brakePressProbs
    gas_probs = model.meta.disengagePredictions.gasPressProbs
    allow_recovery = (open_path and model_accel >= -.2 and len(brake_probs) >= 2 and 0. <= brake_probs[1] < .3)
    if self.dec_enabled:
      allow_recovery = allow_recovery and len(gas_probs) >= 2 and .4 < gas_probs[1] <= 1.
    self.acc_ceiling = None
    if self.longitudinal_mode == 'decAcc':
      if allow_recovery:
        self.acc_ceiling = acc_comfort_limit(self.CP, v_ego, cs.steeringAngleDeg - sm['liveParameters'].angleOffsetDeg)
      if self.acc_ceiling is None:
        self.longitudinal_mode = 'decBlended'
    if allow_recovery and v_ego < v_cruise and self.longitudinal_mode != 'decAcc':
      model_boost = self.model_boost.update(model, v_ego, model_accel, personality, self.dt)
    else:
      self.model_boost.boost = 0.
      model_boost = 0.
    if model_boost > recovery:
      return model_boost, 'e2eBoost'
    return recovery, 'openingLead' if recovery > 0. else ''

  def update(self, sm):
    v_ego = sm['carState'].vEgo
    if self.vision_only or self.sunny:
      model = sm['modelV2']
      self.camera_input_valid = sm.all_checks(['modelV2', 'carState', 'liveParameters']) and all(map(math.isfinite, (
        v_ego, sm['carState'].aEgo, sm['liveParameters'].roll, model.action.desiredAcceleration,
        model.action.desiredCurvature)))
      if not self.camera_input_valid:
        self.opening_track = None
        if self.sunny:
          self.dec = None
          self.model_boost.boost = 0.
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
    if not self.sunny:
      speed_scale = np.interp(v_ego, [5.0, 10.0], [0.0, 1.0])
      accel_scale = np.interp(output_a_target_e2e, [-1.0, -0.5], [0.0, 1.0])
      output_a_target_e2e += ACCEL_BOOST[personality] * speed_scale * accel_scale
    output_should_stop_e2e = sm['modelV2'].action.shouldStop

    self.a_cruise = get_cruise_accel(v_cruise, v_ego, self.a_cruise, self.output_a_target, self.dt, sunny=self.sunny)
    if self.sunny and (sm['controlsState'].forceDecel or v_ego >= v_cruise):
      self.a_cruise = min(self.a_cruise, 0.)
    if not self.ceiling_available:
      self.a_cruise = min(self.a_cruise, 0.)
    cruise_should_stop = should_stop(v_ego, self.a_cruise)

    previous_mode = self.longitudinal_mode
    model_adjustment = ''
    if self.sunny:
      boost, model_adjustment = self.sunny_model_adjustment(sm, v_cruise, output_a_target_e2e, curve_offset, personality, reset_state)
      output_a_target_e2e += boost

    candidates = [(output_a_target_mpc, self.mpc.source, output_should_stop_mpc),
                  (self.a_cruise, LongitudinalPlanSource.cruise, cruise_should_stop)]
    if self.longitudinal_mode != 'decAcc':
      candidates.append((output_a_target_e2e, LongitudinalPlanSource.e2e, output_should_stop_e2e))

    output_a_target, self.mpc.source, _ = min(candidates, key=lambda c: c[0])
    self.speed_reason = {LongitudinalPlanSource.lead0: 'lead0', LongitudinalPlanSource.lead1: 'lead1',
                         LongitudinalPlanSource.cruise: 'cruise', LongitudinalPlanSource.e2e: 'e2e'}[self.mpc.source]
    if self.mpc.source == LongitudinalPlanSource.cruise and sm['controlsState'].forceDecel:
      self.speed_reason = 'forceDecel'
    elif self.speed_reason == 'cruise' and self.a_cruise < output_a_target_mpc:
      self.speed_reason = ceiling_reason
    elif self.mpc.source == LongitudinalPlanSource.e2e and model_adjustment:
      self.speed_reason = model_adjustment
    elif self.mpc.source == LongitudinalPlanSource.e2e and curve_offset < 0:
      self.speed_reason = 'e2eCurve'
    elif self.speed_reason in ('lead0', 'lead1'):
      lead = self.leads.leadOne if self.speed_reason == 'lead0' else self.leads.leadTwo
      if not lead.status:
        self.speed_reason = 'mpc'
      elif self.vision_only:
        self.speed_reason = 'visionLead'
    self.output_should_stop = any(should_stop for _, _, should_stop in candidates)
    if self.longitudinal_mode == 'decAcc' and output_a_target > self.acc_ceiling:
      output_a_target = self.acc_ceiling
      self.speed_reason = 'accComfort'
    if self.longitudinal_mode == 'decAcc' or (previous_mode == 'decAcc' and self.longitudinal_mode == 'decBlended'):
      # Cruise may have built up while the model was limiting speed. Slew only increases at handover.
      ramp_limit = a_prev + np.interp(v_ego, J_CRUISE_BP, J_CRUISE_VALS) * self.dt
      if output_a_target > ramp_limit:
        output_a_target = ramp_limit
        self.speed_reason = 'cruiseRamp'
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
    longitudinalPlan.longitudinalPlanSource = self.mpc.source
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
