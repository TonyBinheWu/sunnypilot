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
from openpilot.selfdrive.controls.lib.curve_speed import CurveSpeed
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.upstream_mpc.long_mpc import LongitudinalMpc, LongitudinalPlanSource, get_T_FOLLOW
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


def get_cruise_accel(v_cruise, v_ego, a_cruise_prev, a_target_prev, dt):
  target_accel = smooth_value(v_cruise - v_ego, a_cruise_prev, tau=1.0, dt=dt)
  target_accel = np.clip(target_accel, A_CRUISE_MIN, ACCEL_MAX)
  j_cruise = np.interp(v_ego, J_CRUISE_BP, J_CRUISE_VALS)
  target_accel = float(np.clip(target_accel, min(a_cruise_prev, a_target_prev) - j_cruise * dt, a_cruise_prev + j_cruise * dt))

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
    self.CP = CP
    self.mpc = LongitudinalMpc(dt=dt)
    self.fcw = False
    self.dt = dt
    self.curve_speed = CurveSpeed(dt)

    self.v_desired_filter = FirstOrderFilter(init_v, 2.0, self.dt)
    self.a_cruise = init_a
    self.output_a_target = init_a
    self.output_should_stop = False

    self.v_desired_trajectory = np.zeros(CONTROL_N)
    self.a_desired_trajectory = np.zeros(CONTROL_N)
    self.j_desired_trajectory = np.zeros(CONTROL_N)

  def update(self, sm):
    v_ego = sm['carState'].vEgo
    if self.vision_only or self.sunny:
      model = sm['modelV2']
      self.camera_input_valid = sm.all_checks(['modelV2', 'carState', 'liveParameters']) and all(map(math.isfinite, (
        v_ego, sm['carState'].aEgo, sm['liveParameters'].roll, model.action.desiredAcceleration,
        model.action.desiredCurvature)))
      if not self.camera_input_valid:
        return
    personality = sm['selfdriveState'].personality.raw
    if personality == log.LongitudinalPersonality.moreRelaxed:
      personality = log.LongitudinalPersonality.relaxed
    self.t_follow = get_T_FOLLOW(personality)
    v_cruise_kph = min(sm['carState'].vCruise, V_CRUISE_MAX)
    v_cruise = v_cruise_kph * CV.KPH_TO_MS
    ceiling_reason = 'cruise'
    if self.sunny:
      v_cruise, ceiling_reason = assisted_ceiling(sm, v_cruise, self.map_curve, self.speed_limit)
    if sm['controlsState'].forceDecel:
      v_cruise = 0.0

    long_control_off = sm['controlsState'].longControlState == LongCtrlState.off

    # Reset current state when not engaged, or user is controlling the speed
    reset_state = long_control_off if self.CP.openpilotLongitudinalControl else not sm['selfdriveState'].enabled
    # PCM cruise speed may be updated a few cycles later, check if initialized
    v_cruise_initialized = sm['carState'].vCruise != V_CRUISE_UNSET
    reset_state = reset_state or not v_cruise_initialized

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

    self.a_cruise = get_cruise_accel(v_cruise, v_ego, self.a_cruise, self.output_a_target, self.dt)
    cruise_should_stop = should_stop(v_ego, self.a_cruise)

    candidates = [(output_a_target_mpc, self.mpc.source, output_should_stop_mpc),
                  (self.a_cruise, LongitudinalPlanSource.cruise, cruise_should_stop),
                  (output_a_target_e2e, LongitudinalPlanSource.e2e, output_should_stop_e2e)]

    output_a_target, self.mpc.source, _ = min(candidates, key=lambda c: c[0])
    self.speed_reason = {LongitudinalPlanSource.lead0: 'lead0', LongitudinalPlanSource.lead1: 'lead1',
                         LongitudinalPlanSource.cruise: 'cruise', LongitudinalPlanSource.e2e: 'e2e'}[self.mpc.source]
    if self.mpc.source == LongitudinalPlanSource.cruise and sm['controlsState'].forceDecel:
      self.speed_reason = 'forceDecel'
    elif self.speed_reason == 'cruise' and self.a_cruise < output_a_target_mpc:
      self.speed_reason = ceiling_reason
    elif self.mpc.source == LongitudinalPlanSource.e2e and curve_offset < 0:
      self.speed_reason = 'e2eCurve'
    elif self.speed_reason in ('lead0', 'lead1'):
      lead = self.leads.leadOne if self.speed_reason == 'lead0' else self.leads.leadTwo
      if not lead.status:
        self.speed_reason = 'mpc'
      elif self.vision_only:
        self.speed_reason = 'visionLead'
    self.output_should_stop = any(should_stop for _, _, should_stop in candidates)
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
    longitudinalPlan.allowThrottle = True
    longitudinalPlan.vTargetNow = float(max(0., sm['carState'].vEgo + self.output_a_target * self.dt))
    longitudinalPlan.jTargetNow = float(self.j_desired_trajectory[0])
    longitudinalPlan.cruiseTarget = min(sm['carState'].vCruise, V_CRUISE_MAX)
    longitudinalPlan.tFollow = self.t_follow
    pm.send('longitudinalPlan', plan_send)
