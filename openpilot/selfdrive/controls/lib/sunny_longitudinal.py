"""Longitudinal helpers adapted from sunnypilot (MIT).
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot and contributors.
DEC: release-mici 3d22676469.
"""
import math

import numpy as np

from openpilot.selfdrive.modeld.constants import ModelConstants


def acc_comfort_limit(cp, speed, steer_angle_deg):
  """Speed and measured lateral-acceleration envelope used by release-mici ACC."""
  if not all(map(math.isfinite, (speed, steer_angle_deg, cp.steerRatio, cp.wheelbase))) or min(cp.steerRatio, cp.wheelbase) <= 0.:
    return None
  total = np.interp(speed, [20., 40.], [1.7, 3.2])
  lateral = speed ** 2 * math.radians(steer_angle_deg) / (cp.steerRatio * cp.wheelbase)
  return min(np.interp(speed, [0., 10., 25., 40.], [1.6, 1.2, .8, .6]), math.sqrt(max(0., total**2 - lateral**2)))


class _SignalFilter:
  def __init__(self, measurement_noise, process_noise, alpha, smoothing):
    self.noise, self.process_noise = measurement_noise, process_noise
    self.alpha, self.smoothing = alpha, smoothing
    self.variance = 1.
    self.value = None

  def update(self, measurement):
    if self.value is None:
      self.value = float(measurement)
    else:
      self.variance = self.alpha * self.variance + self.process_noise
      gain = self.variance / (self.variance + self.noise)
      gain = gain * (1. - self.smoothing) + self.smoothing * .1
      self.value += gain * (measurement - self.value)
      self.variance *= 1. - gain
    return self.value


class DynamicExperimentalControl:
  """release-mici's filtered scene selection and mode-transition hysteresis."""
  def __init__(self, radar_available):
    self.radar_available = radar_available
    self.lead = _SignalFilter(.15, .05, 1.02, .8)
    self.slowdown = _SignalFilter(.1, .1, 1.05, .7)
    self.slowness = _SignalFilter(.1, .06, 1.015, .92)
    self.fcw = _SignalFilter(.2, .1, 1.1, .5)
    self.is_slow = False
    self.standstill_frames = 0
    self.mode = 'acc'
    self.confidence = {'acc': 1., 'blended': 0.}
    self.duration = self.timeout = 0
    self.emergency_override = False

  def _transition(self, requested, confidence, urgent):
    if urgent:
      self.mode = requested
      self.emergency_override = True
      self.timeout, self.duration = 15, 0
    else:
      other = 'acc' if requested == 'blended' else 'blended'
      self.confidence[requested] = min(1., self.confidence[requested] + .1 * confidence)
      self.confidence[other] = max(0., self.confidence[other] - .05)
      if (requested != self.mode and self.timeout == 0 and (self.duration >= 10 or self.emergency_override)
          and self.confidence[requested] > .6):
        self.mode = requested
        self.timeout, self.duration = 15, 0
    self.timeout = max(0, self.timeout - 1)
    self.duration += 1
    if self.duration > 20:
      self.emergency_override = False
    for mode in self.confidence:
      self.confidence[mode] *= .98
    return self.mode

  @staticmethod
  def valid_trajectory(model):
    return (len(model.position.x) == len(model.orientation.x) == len(model.position.t) ==
            len(model.velocity.x) == len(model.orientationRate.z) == ModelConstants.IDX_N
            and math.isfinite(model.position.x[-1]) and model.position.x[-1] >= 0.
            and math.isfinite(model.orientation.x[-1]))

  @staticmethod
  def slowdown_urgency(speed, endpoint):
    kph = speed * 3.6
    expected = np.interp(kph, [0., 10., 20., 30., 40., 50., 55., 60.], [32., 46., 64., 86., 108., 130., 145., 165.])
    urgency = max(0., 2. * (1. - endpoint / expected))
    if endpoint < expected * .3:
      urgency *= 2.
    urgency *= 1. + max(0., kph - 25.) / 80.
    return min(1., urgency)

  def update(self, cs, urgency, lead, crash_count):
    kph = cs.vEgo * 3.6
    self.standstill_frames = min(20, self.standstill_frames + 1) if cs.standstill else max(0, self.standstill_frames - 1)
    has_lead = self.lead.update(lead.status) > .45
    fcw = (self.fcw.value or 0.) > .5
    self.fcw.update(crash_count > 0)
    urgency = self.slowdown.update(urgency)
    slowdown = urgency > .3 * .8
    if self.standstill_frames <= 5 and not slowdown:
      value = self.slowness.update(kph <= cs.vCruise * 1.025)
      self.is_slow = value > .55 * (.8 if self.is_slow else 1.1)

    if fcw:
      return self._transition('blended', 1., True)
    if self.radar_available and has_lead and self.standstill_frames <= 3:
      return self._transition('acc', 1., False)
    if not self.radar_available and self.standstill_frames > 3:
      return self._transition('blended', .9, False)
    if slowdown:
      return self._transition('blended', min(1., urgency * (1.3 if self.radar_available else 1.5)), urgency > .7)
    if self.standstill_frames > 3:
      return self._transition('blended', .9, False)
    return self._transition('acc', .8 if self.is_slow else .7, False)
