"""Scene and driver-speed limits adapted from commaai/openpilot 88d47a473."""
import numpy as np

from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX
from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.curve_speed import CurveSpeed
from openpilot.selfdrive.controls.lib.drive_helpers import smooth_value

ACCEL_BOOST = {
  log.LongitudinalPersonality.aggressive: .15,
  log.LongitudinalPersonality.standard: .05,
}

class Autospeed:
  def __init__(self, dt):
    self.dt = dt
    self.curve = CurveSpeed(dt)
    self.a_cruise = 0.

  def reset(self, accel):
    self.curve.reset()
    self.a_cruise = float(np.clip(accel, ACCEL_MIN, ACCEL_MAX))

  def update(self, model, roll, personality, speed, ceiling, previous, mpc_accel, source, mpc_stop):
    scene = model.action.desiredAcceleration + self.curve.update(model, roll)
    scene += ACCEL_BOOST.get(personality, 0.) * np.interp(speed, [5., 10.], [0., 1.]) * np.interp(scene, [-1., -.5], [0., 1.])
    cruise = np.clip(smooth_value(ceiling - speed, self.a_cruise, tau=1., dt=self.dt), -.5, ACCEL_MAX)
    step = np.interp(speed, [0., 10., 25., 40.], [1.6, 1.2, .8, .6]) * self.dt
    self.a_cruise = float(np.clip(cruise, min(self.a_cruise, previous) - step, self.a_cruise + step))
    accel, source = min(((mpc_accel, source), (self.a_cruise, 'cruise'), (scene, 'e2e')), key=lambda c: c[0])
    stop = mpc_stop or model.action.shouldStop or (speed < .3 and self.a_cruise < .1)
    return float(np.clip(accel, ACCEL_MIN, ACCEL_MAX)), source, stop
