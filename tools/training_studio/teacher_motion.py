"""Resolve a negative fitted speed contradicted by the latest observed ego chord.

The least-squares history fit can overshoot below zero immediately after braking.
No future, signal state, route geometry or scorer information is used here.
"""

PROFILE='observed_chord_on_negative_speed_fit_v1'


def install(space):
  import torch
  if getattr(space,'_studio_motion_profile',None)==PROFILE: return
  original=space.estimate_t0_states

  @torch.no_grad()
  def observed(history_xyz,history_rot):
    states=original(history_xyz,history_rot)
    # History is expressed in the current body frame; +x is forward.
    latest=(history_xyz[...,-1,0]-history_xyz[...,-2,0])/space.dt
    fitted=states['v']
    velocity=torch.where((fitted<0)&(latest>=0),latest,fitted)
    return {**states,'v':velocity}

  space.estimate_t0_states=observed
  space._studio_motion_profile=PROFILE
