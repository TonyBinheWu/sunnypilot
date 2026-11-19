"""Explicit forward-only decoding for offline teachers, using observed motion only.

Keep the sampled brake commands intact. Project equivalent action-space inputs
only while decoding, so a brake held at rest cannot become a reverse trajectory.
The original pinned decoder still supplies course, positions and body rotations.
"""

PROFILE='forward_only_physical_action_decode_v2'


def forward_states(states,space,history_xyz):
  import torch
  speed=states['v']
  if not bool(torch.isfinite(speed).all()):raise ValueError('nonfinite observed initial speed')
  # This explicitly non-reversing planner uses speed magnitude, as do the
  # original Scene state and trajectory tracker. A short settling rollback
  # must remain an observation rather than turn a valid request into HTTP400.
  # Preserve normal forward estimates and never mutate the caller's states.
  measured=torch.linalg.vector_norm(history_xyz[...,-1,:2]-history_xyz[...,-2,:2],dim=-1)/space.dt
  if not bool(torch.isfinite(measured).all()):raise ValueError('nonfinite observed chord speed')
  return {**states,'v':torch.where(speed<0,measured,speed)}


def project_actions(action,space,history_xyz,history_rot,*,t0_states=None):
  import torch
  states=forward_states(space.estimate_t0_states(history_xyz,history_rot) if t0_states is None else t0_states,space,history_xyz)
  speed=states['v']
  mean=space.accel_mean.to(action.device);std=space.accel_std.to(action.device)
  if not bool(torch.isfinite(std).all() and (std>0).all()):raise ValueError('invalid acceleration scale')
  acceleration=action[...,0]*std+mean;normalized=[]
  for index,value in enumerate(acceleration.unbind(-1)):
    following=speed+value*space.dt
    # Preserve the exact sampled values for every unconstrained step.
    normalized.append(torch.where(following>=0,action[...,index,0],(-speed/space.dt-mean)/std))
    speed=following.clamp_min(0)
  return torch.stack((torch.stack(normalized,dim=-1),action[...,1]),dim=-1),states


def install(space):
  if getattr(space,'_studio_forward_profile',None)==PROFILE:return
  original_observer=space.estimate_t0_states
  def observe(history_xyz,history_rot):
    return forward_states(original_observer(history_xyz,history_rot),space,history_xyz)
  space.estimate_t0_states=observe
  original=space.action_to_traj
  def decode(action,history_xyz,history_rot,t0_states=None):
    effective,states=project_actions(action,space,history_xyz,history_rot,t0_states=t0_states)
    return original(effective,history_xyz,history_rot,t0_states=states)
  space.action_to_traj=decode
  space._studio_forward_profile=PROFILE
