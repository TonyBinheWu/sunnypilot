"""Resolve fitted-speed artifacts using observed ego chords and a near-rest window.

The least-squares history fit can overshoot below zero immediately after braking
or assign a spurious velocity to a settled sequence of centimetre-scale poses.
No future, signal state, route geometry or scorer information is used here.
"""

PROFILE='observed_chord_and_stationary_window_v2'


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
    if history_xyz.shape[-2]>=6:
      # Five measured chords bound a 0.5s near-rest observation to 2.5cm.
      # A fitted negative tail can otherwise turn a stationary reference into
      # a positive acceleration target. Keep real forward/reverse motion;
      # this observer uses no signal, route, stop label or qualification state.
      recent=torch.linalg.vector_norm(torch.diff(history_xyz[...,-6:,:2],dim=-2),dim=-1)/space.dt
      at_rest=(recent<=.05).all(dim=-1)
      velocity=torch.where(at_rest,torch.zeros_like(velocity),velocity)
    return {**states,'v':velocity}

  space.estimate_t0_states=observed
  space._studio_motion_profile=PROFILE
