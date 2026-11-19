"""Offline reference controls for the unchanged simulator's signed motion."""
import math

PROFILE='signed_velocity_stop_reference_v1'


def hold_acceleration(velocity,heading):
  speed=sum(float(velocity[index])*float(heading[index]) for index in range(2))
  if not math.isfinite(speed):raise ValueError('nonfinite observed reference velocity')
  return max(-3.5,min(1.6,-1.5*speed))


def in_stop_zone(scene):
  state=scene.state()
  front=scene.stop_s-state[3]-scene.vehicle.LENGTH/2
  return 0<=front<5 and state[-1]<.15


RECOVERY_PROFILE='gentle_near_boundary_stop_recovery_v1'
RECOVERY_INTERIOR_MARGIN_M=.15
RECOVERY_TARGET_FRONT_M=4.8


def gentle_recovery_acceleration(velocity,heading,front_distance):
  """Offline labels only: recover a near-boundary early stop without a launch."""
  speed=sum(float(velocity[i])*float(heading[i]) for i in range(2))
  if not math.isfinite(speed) or not math.isfinite(front_distance):raise ValueError('finite recovery reference state required')
  target=min(.2,math.sqrt(2*.3*max(0.,front_distance-RECOVERY_TARGET_FRONT_M)))
  return max(-3.5,min(.15,1.5*(target-speed)))


def stop_training_margin(row,balanced_stop_modes):
  """Match the documented recovery reference while keeping the driving gate fixed."""
  profile=row.get('recovery_reference_profile')
  if profile is not None:
    if (profile!=RECOVERY_PROFILE or not row.get('stop_required') or row.get('maintain_stop_reference')
        or row.get('scenario')!='red_light' or not 5<=row.get('front_distance_m',-1)<=6
        or row.get('stop_interior_margin_m')!=RECOVERY_INTERIOR_MARGIN_M):
      raise ValueError('invalid gentle recovery reference metadata')
    return RECOVERY_INTERIOR_MARGIN_M
  return .5 if balanced_stop_modes and not row.get('maintain_stop_reference') else 0.
