"""Measured motion and causal learned bicycle-model history in forward/left/up."""
import math
from types import SimpleNamespace

import numpy as np
from scipy.spatial.transform import Rotation, Slerp

from openpilot.selfdrive.alpamayo.frontend import STATE_LIMITS, STATE_SAMPLE_OFFSETS_NS, Unavailable, required

AXES = np.diag([1., -1., -1.])


def measured_history(rows, query, rpy):
  rows = [r for r in rows if r.stamp <= query]
  if not rows or any(not r.valid and query-2_050_000_000 <= r.stamp for r in rows):
    raise Unavailable('Missing or invalid measured motion')
  rows = [r for r in rows if r.valid]
  ns = np.array([r.stamp for r in rows], dtype=np.int64)
  times = (ns-query)/1e9
  first = max(0, int(np.searchsorted(times, -1.9))-1)
  if len(times) < 2 or times[first] > -1.9 or times[-1] < -.1 or np.max(np.diff(times[first:])) > .15:
    raise Unavailable('Missing or discontinuous measured history')
  rotations = Rotation.from_euler('xyz', [r.value[0] for r in rows]).as_matrix()
  velocity = np.einsum('nij,nj->ni', rotations, np.array([r.value[1] for r in rows]))
  positions = np.concatenate((np.zeros((1, 3)), np.cumsum(np.diff(times)[:, None]*(velocity[1:]+velocity[:-1])/2, axis=0)))
  t, p, r = times[first:], positions[first:], rotations[first:]
  # Extrapolate only the final measured velocity for at most 100 milliseconds.
  if t[-1] < 0:
    p = np.concatenate((p, [p[-1]-velocity[-1]*t[-1]]))
    r, t = np.concatenate((r, r[-1:])), np.append(t, 0.)
  wanted = np.arange(-19, 1)*.1
  positions = np.stack([np.interp(wanted, t, p[:, a]) for a in range(3)], axis=-1)
  world_vehicle = Slerp(t, Rotation.from_matrix(r))(wanted).as_matrix() @ Rotation.from_euler('xyz', rpy).as_matrix()
  current_world = AXES @ world_vehicle[-1].T
  xyz = ((positions-positions[-1]) @ current_world.T)[None].astype(np.float32)
  rot = (current_world @ world_vehicle @ AXES)[None].astype(np.float32)
  return xyz, rot, -times[-1]*1000


def ego_history(states, query, rpy):
  from opendbc.car.vehicle_model import VehicleModel
  xyz, rotations, extrapolation_ms = measured_history(states['deviceMotion'], query, rpy)
  cp, _ = required(states['carParams'], query, STATE_LIMITS['carParams'])
  vm = VehicleModel(SimpleNamespace(**cp))
  speed, yaw_rate, ages = [], [], []
  for stamp in query+STATE_SAMPLE_OFFSETS_NS:
    cs, ct = required(states['carState'], stamp, STATE_LIMITS['carState'])
    lp, lt = required(states['vehicleParameters'], stamp, STATE_LIMITS['vehicleParameters'])
    ratio = lp['centerToFrontRatio']
    if 0.31 <= ratio <= 0.69:
      vm.update_geometry(ratio)
    vm.update_params(max(lp['stiffnessFactor'], .1), max(lp['steerRatio'], .1))
    v = max(cs['vEgo'], 0.)
    curvature = vm.calc_curvature(math.radians(cs['steeringAngleDeg']-lp['angleOffsetDeg']), v, lp['roll'])
    speed.append(v)
    yaw_rate.append(v*curvature)
    ages.append([int(stamp)-ct, int(stamp)-lt])
  speed, yaw_rate = np.array(speed), np.array(yaw_rate)
  yaw = np.r_[0., np.cumsum((yaw_rate[:-1]+yaw_rate[1:])*.025)]
  velocity = speed[:, None]*np.stack([np.cos(yaw), np.sin(yaw)], axis=-1)
  xy = np.vstack([np.zeros(2), np.cumsum((velocity[:-1]+velocity[1:])*.025, axis=0)])
  xy = (xy-xy[-1]) @ Rotation.from_euler('z', -yaw[-1]).as_matrix()[:2, :2].T
  xyz[0, :, :2] = xy[::2]
  tilt = Rotation.from_matrix(rotations[0]).as_euler('xyz')
  tilt[:, 2] = yaw[::2]-yaw[-1]
  rotations[0] = Rotation.from_euler('xyz', tilt).as_matrix()
  if not np.isfinite(xyz).all() or not np.isfinite(rotations).all():
    raise Unavailable('Nonfinite ego history')
  return xyz, rotations, {'speed_m_s': float(speed[-1]), 'left_yaw_rate_rad_s': float(yaw_rate[-1]),
                          'max_car_state_age_ms': max(a[0] for a in ages)/1e6,
                          'max_learned_parameters_age_ms': max(a[1] for a in ages)/1e6,
                          'motion_extrapolation_ms': extrapolation_ms}
