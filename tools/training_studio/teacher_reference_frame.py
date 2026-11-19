"""Explicit rigid-body calibration around the pinned action-space decoder.

Observed inputs and stored futures stay at the measured vehicle center. Only
inverse/forward action dynamics use the configured rear-axle reference; decoded
positions are returned to the measured center before any loss or tracker sees
them. The offset is vehicle geometry, never a fitted lane or signal correction.
"""
import math

PROFILE='observed_center_to_rear_axle_v1'


def validate_offset(value):
  if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=3:
    raise ValueError('rear axle offset must be finite vehicle geometry in [0,3] metres')
  return float(value)


def shift(xyz,rot,current_axis,offset):
  if xyz.shape[-1:]!=(3,) or rot.shape!=(*xyz.shape,3):raise ValueError('position/rotation dimensions disagree')
  return xyz+offset*(rot[...,0]-current_axis)


def install(space,offset_m):
  offset=validate_offset(offset_m)
  if not offset:return
  previous=getattr(space,'_studio_reference_offset_m',None)
  if previous is not None:
    if previous!=offset:raise ValueError('action space already has another reference calibration')
    return
  decode,inverse=space.action_to_traj,space.traj_to_action
  def action_to_traj(action,history_xyz,history_rot,t0_states=None):
    axis=history_rot[...,-1,:,0].unsqueeze(-2)
    history=shift(history_xyz,history_rot,axis,-offset)
    # An optional state supplied in the measured-center frame cannot be reused
    # at the axle. Derive it from the same observed history, with no scorer data.
    states=space.estimate_t0_states(history,history_rot) if t0_states is not None else None
    xyz,rot=decode(action,history,history_rot,t0_states=states)
    return shift(xyz,rot,axis,offset),rot
  def traj_to_action(history_xyz,history_rot,future_xyz,future_rot):
    axis=history_rot[...,-1,:,0].unsqueeze(-2)
    return inverse(shift(history_xyz,history_rot,axis,-offset),history_rot,
      shift(future_xyz,future_rot,axis,-offset),future_rot)
  space.action_to_traj=action_to_traj
  space.traj_to_action=traj_to_action
  space._studio_reference_offset_m=offset
  space._studio_reference_profile=PROFILE
