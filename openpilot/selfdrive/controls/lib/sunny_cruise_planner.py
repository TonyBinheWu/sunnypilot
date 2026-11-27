"""Cruise and lead MPC from sunnypilot release-mici (3d22676469, MIT).

Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot and contributors.
"""
import math

import numpy as np
from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX

from openpilot.cereal import log
from openpilot.common.constants import CV
from openpilot.common.driving_planner import SUNNY_RELEASE, SUNNY_RELEASE_VISION
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX, V_CRUISE_UNSET
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.sunny_longitudinal import DynamicExperimentalControl, acc_comfort_limit
from openpilot.selfdrive.controls.lib.upstream_mpc.long_mpc import STOP_DISTANCE, LongitudinalPlanSource, get_T_FOLLOW
from openpilot.selfdrive.controls.lib.upstream_planner import (
  CONTROL_N_T_IDX, T_IDXS_MPC, LongitudinalPlanner, assisted_ceiling, camera_leads, get_accel_from_plan, model_throttle_limit,
)


def make_longitudinal_planner(CP, init_v=0.):
  if CP.drivingPlannerMode in (SUNNY_RELEASE, SUNNY_RELEASE_VISION):
    return SunnyCruisePlanner(CP, init_v=init_v, vision_only=CP.drivingPlannerMode == SUNNY_RELEASE_VISION)
  return LongitudinalPlanner(CP, init_v=init_v, sunny=True)


def valid_observations(model):
  if len(model.leadsV3) < 2 or not DynamicExperimentalControl.valid_trajectory(model):
    return False
  for i in range(2):
    obs = model.leadsV3[i]
    if not (0. <= obs.prob <= 1. and all(len(v) and math.isfinite(v[0]) for v in (obs.x, obs.y, obs.v, obs.a))):
      return False
  return all(np.isfinite(series).all() for series in (model.position.x, model.position.t, model.velocity.x, model.orientationRate.z))


def valid_fused_leads(radar, stamp):
  errors = radar.radarErrors
  if not (0 < radar.mdMonoTime and 0 <= stamp - radar.mdMonoTime <= 150_000_000):
    return False
  if errors.canError or errors.radarFault or errors.wrongConfig or errors.radarUnavailableTemporary:
    return False
  return all(not lead.status or all(map(math.isfinite, (lead.dRel, lead.vLead, lead.aLeadK, lead.aLeadTau, lead.modelProb)))
             for lead in (radar.leadOne, radar.leadTwo))


class SunnyCruisePlanner(LongitudinalPlanner):
  def __init__(self, CP, init_v=0., init_a=0., dt=DT_MDL, *, vision_only=False):
    super().__init__(CP, init_v, init_a, dt, sunny=True, vision_only=vision_only)
    self.planner_profile = 'sunnyVision' if vision_only else 'sunnyRelease'
    self.lead_filters = [FirstOrderFilter(0., .2, dt) for _ in range(2)]
    self.a_desired = init_a
    self.prev_upper = ACCEL_MAX
    self.last_eof = 0
    self.camera_input_valid = False

  def invalidate(self):
    if self.camera_input_valid:
      self.mpc.reset()
    self.camera_input_valid = False
    self.dec = None
    self.longitudinal_mode = ''
    self.allow_throttle = False
    self.curve_speed.reset()
    for filt in self.lead_filters:
      filt.x = 0.

  def update(self, sm):
    cs, model = sm['carState'], sm['modelV2']
    sd, controls = sm['selfdriveState'], sm['controlsState']
    stamp, eof = sm.logMonoTime['modelV2'], model.timestampEof
    v_ego = cs.vEgo
    gas = model.meta.disengagePredictions.gasPressProbs
    steer_angle = cs.steeringAngleDeg - sm['liveParameters'].angleOffsetDeg
    upper = acc_comfort_limit(self.CP, v_ego, steer_angle)
    was_valid = self.camera_input_valid
    if not (0 < eof <= stamp and stamp - eof <= 250_000_000
            and all(abs(stamp - sm.logMonoTime[k]) <= 150_000_000 for k in ('carState', 'controlsState'))):
      self.invalidate()
      return
    continuous = ((not self.previous_model_stamp or 0 < stamp - self.previous_model_stamp <= 150_000_000)
                  and eof > self.last_eof)
    self.previous_model_stamp, self.last_eof = max(stamp, self.previous_model_stamp), max(eof, self.last_eof)
    if not (continuous
            and sm.all_checks(['modelV2', 'carState', 'controlsState', 'selfdriveState', 'liveParameters'])
            and cs.canValid and not cs.canTimeout and upper is not None and valid_observations(model)
            and all(map(math.isfinite, (v_ego, cs.aEgo, sm['liveParameters'].roll, model.action.desiredAcceleration,
                                        model.action.desiredCurvature))) and len(gas) > 1 and 0. <= gas[1] <= 1.):
      self.invalidate()
      return
    if self.vision_only:
      self.leads = camera_leads(model, v_ego, self.lead_filters)
    else:
      if not sm.all_checks(['radarState']) or not valid_fused_leads(sm['radarState'], stamp):
        self.invalidate()
        return
      self.leads = sm['radarState']

    self.camera_input_valid = True
    self.ceiling_available = math.isfinite(cs.vCruise) and 0. < cs.vCruise < V_CRUISE_UNSET
    self.cruise_target = min(cs.vCruise, V_CRUISE_MAX) if self.ceiling_available else 0.
    if self.ceiling_available:
      v_cruise, ceiling_reason = assisted_ceiling(sm, self.cruise_target * CV.KPH_TO_MS, self.map_curve, self.speed_limit)
    else:
      v_cruise, ceiling_reason = v_ego, 'cruiseUnset'
    if controls.forceDecel:
      v_cruise, ceiling_reason = 0., 'forceDecel'
    active = self.CP.openpilotLongitudinalControl and sd.enabled and controls.longControlState != LongCtrlState.off
    reset = not active or not self.ceiling_available
    if reset or not was_valid:
      self.v_desired_filter.x = v_ego
      self.a_desired = float(np.clip(cs.aEgo, ACCEL_MIN, upper))
      self.prev_upper = upper
      self.curve_speed.reset()
    self.v_desired_filter.x = max(0., self.v_desired_filter.update(v_ego))

    self.allow_throttle, upper = model_throttle_limit(sm, v_ego, gas[1], upper)

    if self.dec is None:
      self.dec = DynamicExperimentalControl(not self.vision_only and not self.CP.radarUnavailable)
    urgency = self.dec.slowdown_urgency(v_ego, model.position.x[-1])
    mode = self.dec.update(cs, urgency, self.leads.leadOne, self.mpc.crash_cnt)
    dec_active = self.dec_enabled and sd.experimentalMode
    blended = sd.experimentalMode and (not dec_active or mode == 'blended')
    personality = sd.personality.raw
    if personality == log.LongitudinalPersonality.moreRelaxed:
      personality = log.LongitudinalPersonality.relaxed
    self.t_follow = get_T_FOLLOW(personality, cruise_obstacle=True)
    self.mpc.set_weights(not (reset or cs.standstill), personality)
    self.mpc.set_cur_state(self.v_desired_filter.x, self.a_desired)
    self.mpc.update(self.leads, personality=personality, v_cruise=v_cruise)
    if self.mpc.solution_status or not all(np.isfinite(s).all() for s in (self.mpc.v_solution, self.mpc.a_solution, self.mpc.j_solution)):
      self.invalidate()
      return

    self.v_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.v_solution)
    self.a_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.a_solution)
    self.j_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC[:-1], self.mpc.j_solution)
    previous_a = self.a_desired
    self.a_desired = float(np.interp(self.dt, CONTROL_N_T_IDX, self.a_desired_trajectory))
    self.v_desired_filter.x += self.dt * (previous_a + self.a_desired) / 2.
    target = get_accel_from_plan(self.v_desired_trajectory, self.a_desired_trajectory, CONTROL_N_T_IDX,
                                 self.CP.longitudinalActuatorDelay + DT_MDL)
    self.plan_source = self.mpc.source
    self.output_should_stop = self.v_desired_trajectory[0] < self.CP.vEgoStopping and target < .1
    self.fcw = self.mpc.crash_cnt > 2 and not cs.standstill
    curve = self.curve_speed.update(model, sm['liveParameters'].roll) if self.vision_curve else 0.
    # Preserve explicit stop intent, imminent braking and the fork's optional vision curve assist even during a mode transition.
    cut_in = not self.vision_only and self.leads.leadCutInRisk.status
    if model.action.shouldStop or self.mpc.crash_cnt or cut_in or model.action.desiredAcceleration <= -1. or curve < 0.:
      blended = True
    model_accel = model.action.desiredAcceleration + curve
    if blended:
      self.output_should_stop |= model.action.shouldStop
      if model_accel < target:
        target, self.plan_source = model_accel, LongitudinalPlanSource.e2e
    self.longitudinal_mode = ('decBlended' if blended else 'decAcc') if dec_active else 'blended' if blended else 'acc'
    if not active:
      self.longitudinal_mode = ''
    self.speed_reason = {LongitudinalPlanSource.cruise: ceiling_reason, LongitudinalPlanSource.e2e: 'e2eCurve' if curve < 0. else 'e2e',
                         LongitudinalPlanSource.lead0: 'visionLead' if self.vision_only else 'lead0',
                         LongitudinalPlanSource.lead1: 'visionLead' if self.vision_only else 'lead1'}[self.plan_source]
    self.prev_upper = float(np.clip(upper, self.prev_upper - .05, self.prev_upper + .05))
    if target > self.prev_upper:
      self.speed_reason = 'accComfort' if self.allow_throttle else 'modelCoast'
    self.output_a_target = float(np.clip(target, ACCEL_MIN, self.prev_upper))
    if self.output_a_target > 0.:
      # The MPC rate cost can retain positive acceleration for the first few frames of a sudden cut-in.
      closing = any(lead.status and lead.vLead < v_ego - .5 and lead.dRel <= STOP_DISTANCE + self.t_follow * v_ego
                    for lead in (self.leads.leadOne, self.leads.leadTwo))
      for limited, reason in ((not active, 'inactive'), (cs.brakePressed or cs.gasPressed, 'driverOverride'),
                              (cs.softHoldActive, 'softHold'), (controls.forceDecel, 'forceDecel'),
                              (self.output_should_stop, 'stopPlan'), (self.fcw, 'collisionWarning'), (cut_in, 'cutIn'),
                              (closing, 'closingLead'), (not self.ceiling_available, 'cruiseUnset'), (v_ego >= v_cruise, ceiling_reason)):
        if limited:
          self.output_a_target, self.speed_reason = 0., reason
          break
