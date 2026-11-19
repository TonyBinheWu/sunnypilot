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
