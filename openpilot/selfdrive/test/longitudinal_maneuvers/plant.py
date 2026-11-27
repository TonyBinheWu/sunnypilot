#!/usr/bin/env python3
from types import SimpleNamespace
import numpy as np

from openpilot.cereal import log
import openpilot.cereal.messaging as messaging
from openpilot.common.driving_planner import selected_sunny_mode
from openpilot.common.realtime import Ratekeeper, DT_CTRL, DT_MDL
from openpilot.selfdrive.controls.lib.longcontrol import LongControl, LongCtrlState
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.controls.lib.sunny_cruise_planner import make_longitudinal_planner
from openpilot.selfdrive.controls.radar_constants import LEAD_ACCEL_TAU, RADAR_TO_CAMERA


class Plant:
  def __init__(self, lead_relevancy=False, speed=0.0, distance_lead=2.0,
               enabled=True, only_lead2=False, only_radar=False, e2e=False, personality=0, force_decel=False,
               cruise_planner=0, ideal_accel=False):
    self.rate = 1. / DT_MDL

    self.v_lead_prev = 0.0

    self.distance = 0.
    self.speed = speed
    self.should_stop = False
    self.acceleration = 0.0

    # lead car
    self.lead_relevancy = lead_relevancy
    self.distance_lead = distance_lead
    self.enabled = enabled
    self.only_lead2 = only_lead2
    self.only_radar = only_radar
    self.e2e = e2e
    self.personality = personality
    self.force_decel = force_decel
    self.ideal_accel = ideal_accel

    self.rk = Ratekeeper(self.rate, print_delay_threshold=100.0)
    self.ts = 1. / self.rate
    self.sm = messaging.SubMaster(['modelV2', 'radarState', 'carState', 'carControl', 'controlsState',
                                   'selfdriveState', 'liveParameters'], poll='modelV2')

    from opendbc.car.honda.values import CAR
    from opendbc.car.honda.interface import CarInterface

    cp = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
    cp.drivingPlannerMode = selected_sunny_mode(cp, cruise_planner)
    self.planner = make_longitudinal_planner(cp, init_v=self.speed)
    self.controller = LongControl(cp)
    self.get_accel_limits = CarInterface.get_pid_accel_limits
    self.plans = {}
    self.plan_sink = SimpleNamespace(send=self.plans.__setitem__)

  @property
  def current_time(self):
    return float(self.rk.frame) / self.rate

  def step(self, v_lead=0.0, prob_lead=1.0, v_cruise=50., pitch=0.0, prob_throttle=1.0):
    # ******** publish a fake model going straight and fake calibration ********
    # note that this is worst case for MPC, since model will delay long mpc by one time step
    radar = messaging.new_message('radarState')
    control = messaging.new_message('controlsState')
    ss = messaging.new_message('selfdriveState')
    car_state = messaging.new_message('carState')
    lp = messaging.new_message('liveParameters')
    car_control = messaging.new_message('carControl')
    model = messaging.new_message('modelV2')
    a_lead = (v_lead - self.v_lead_prev)/self.ts
    self.v_lead_prev = v_lead

    if self.lead_relevancy:
      d_rel = np.maximum(0., self.distance_lead - self.distance)
      v_rel = v_lead - self.speed
      if self.only_radar:
        status = True
      elif prob_lead > .5:
        status = True
      else:
        status = False
    else:
      d_rel = 200.
      v_rel = 0.
      prob_lead = 0.0
      status = False

    lead = log.RadarState.LeadData.new_message()
    lead.dRel = float(d_rel)
    lead.yRel = 0.0
    lead.vRel = float(v_rel)
    lead.aRel = float(a_lead - self.acceleration)
    lead.vLead = float(v_lead)
    lead.vLeadK = float(v_lead)
    lead.aLeadK = float(a_lead)
    # TODO use real radard logic for this
    lead.aLeadTau = float(LEAD_ACCEL_TAU)
    lead.status = status
    lead.modelProb = float(prob_lead)
    if not self.only_lead2:
      radar.radarState.leadOne = lead
    radar.radarState.leadTwo = lead

    # Simulate model predicting slightly faster speed
    # this is to ensure lead policy is effective when model
    # does not predict slowdown in e2e mode
    position = log.XYZTData.new_message()
    position.x = [float(x) for x in (self.speed + 0.5) * np.array(ModelConstants.T_IDXS)]
    position.t = ModelConstants.T_IDXS
    model.modelV2.position = position
    model.modelV2.orientation.x = model.modelV2.orientationRate.z = [0.] * len(position.t)
    for i, obs in enumerate(model.modelV2.init('leadsV3', 2)):
      obs.prob = float(prob_lead) if self.lead_relevancy and (i == 1 or not self.only_lead2) else 0.
      obs.x, obs.y, obs.v, obs.a = [float(d_rel + RADAR_TO_CAMERA)], [0.], [float(v_lead)], [float(a_lead)]
    model.modelV2.action.desiredAcceleration = float(self.acceleration + 0.1)
    velocity = log.XYZTData.new_message()
    velocity.x = [float(x) for x in (self.speed + 0.5) * np.ones_like(ModelConstants.T_IDXS)]
    velocity.x[0] = float(self.speed) # always start at current speed
    model.modelV2.velocity = velocity
    acceleration = log.XYZTData.new_message()
    acceleration.x = [float(x) for x in np.zeros_like(ModelConstants.T_IDXS)]
    model.modelV2.acceleration = acceleration
    model.modelV2.meta.disengagePredictions.gasPressProbs = [float(prob_throttle) for _ in range(6)]
    model.modelV2.meta.disengagePredictions.brakePressProbs = [0., 0.]

    control.controlsState.longControlState = self.controller.long_control_state
    ss.selfdriveState.experimentalMode = self.e2e
    ss.selfdriveState.enabled = self.enabled
    ss.selfdriveState.personality = self.personality
    control.controlsState.forceDecel = self.force_decel
    car_state.carState.vEgo = float(self.speed)
    car_state.carState.aEgo = float(self.acceleration)
    car_state.carState.canValid = True
    car_state.carState.standstill = bool(self.speed < 0.01)
    car_state.carState.vCruise = float(v_cruise * 3.6)
    car_control.carControl.orientationNED = [0., float(pitch), 0.]

    # ******** get controlsState messages for plotting ***
    sim_time = 10. + self.current_time
    stamp = round(sim_time * 1e9)
    model.modelV2.timestampEof = radar.radarState.mdMonoTime = stamp - 50_000_000
    messages = [model, radar, car_state, car_control, control, ss, lp]
    for msg in messages:
      msg.valid, msg.logMonoTime = True, stamp
    self.sm.update_msgs(sim_time, messages)
    self.planner.update(self.sm)
    self.planner.publish(self.sm, self.plan_sink)
    event = self.plans['longitudinalPlan']
    plan = event.longitudinalPlan
    self.should_stop = plan.shouldStop
    fcw = self.planner.fcw
    self.distance_lead = self.distance_lead + v_lead * self.ts

    # Apply the published stop/hold intent at the control rate, even when the MPC's feedforward approaches zero.
    for tick in range(round(self.ts / DT_CTRL)):
      cs = car_state.carState
      cs.vEgo, cs.aEgo = float(self.speed), float(self.acceleration)
      limits = self.get_accel_limits(self.planner.CP, self.speed, v_cruise if np.isfinite(v_cruise) else self.speed)
      self.acceleration, _, _ = self.controller.update(self.enabled and event.valid, cs, plan, limits,
                                                       tick * DT_CTRL, radar.radarState)
      if self.ideal_accel and self.controller.long_control_state == LongCtrlState.pid:
        self.acceleration = plan.aTarget
      self.speed = max(0., self.speed + self.acceleration * DT_CTRL)
      if self.speed == 0.:
        self.acceleration = 0.
      self.distance += self.speed * DT_CTRL

    # *** radar model ***
    if self.lead_relevancy:
      d_rel = np.maximum(0., self.distance_lead - self.distance)
      v_rel = v_lead - self.speed
    else:
      d_rel = 200.
      v_rel = 0.

    # print at 5hz
    # if (self.rk.frame % (self.rate // 5)) == 0:
    #   print("%2.2f sec   %6.2f m  %6.2f m/s  %6.2f m/s2   lead_rel: %6.2f m  %6.2f m/s"
    #         % (self.current_time, self.distance, self.speed, self.acceleration, d_rel, v_rel))


    # ******** update prevs ********
    self.rk.monitor_time()

    return {
      "distance": self.distance,
      "speed": self.speed,
      "acceleration": self.acceleration,
      "requested_acceleration": plan.aTarget,
      "should_stop": self.should_stop,
      "distance_lead": self.distance_lead,
      "fcw": fcw,
    }

# simple engage in standalone mode
def plant_thread():
  plant = Plant()
  while 1:
    plant.step()


if __name__ == "__main__":
  plant_thread()
