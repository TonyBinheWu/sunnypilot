"""Experimental two-front-camera Edge input adapter; not the official six-camera profile.

No images are synthesized for absent cameras. Model driving qualification and
AMD/Chestnut deployment remain separate requirements.
"""
import numpy as np

CAMERA_IDS = (1,6)  # NVIDIA front wide and front telephoto semantics.
FRAME_OFFSETS_US = np.array([-2000000,-1000000,-500000,-100000,0],np.int64)
HISTORY_OFFSETS_US = np.arange(-19,1,dtype=np.int64)*100000
SOURCE_COMMIT = '02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e'
MODEL_REVISION = 'b92b6aa326bd3e2235db28f248ad5a30b5890e64'


def validate_front_sample(data, timestamp_tolerance_us=0):
  """Require measured front RGB, capture times, ego poses and manual route intent."""
  frames = np.asarray(data['image_frames'])
  if frames.dtype!=np.uint8 or frames.ndim!=5 or frames.shape[:3]!=(10,1,3) or min(frames.shape[-2:])<=0:
    raise ValueError('Two actual cameras must supply ten uint8 RGB frames [10,1,3,H,W]')
  ids = np.asarray(data['camera_indices'])
  times = np.asarray(data['absolute_timestamps'])
  history_times = np.asarray(data['ego_history_timestamps'])
  if ids.dtype!=np.int64 or ids.shape!=(10,) or not np.array_equal(ids,np.repeat(CAMERA_IDS,5)):
    raise ValueError('Only five front-wide frames (ID 1), then five telephoto frames (ID 6), are supported')
  if times.dtype!=np.int64 or times.shape!=(10,) or history_times.dtype!=np.int64 or history_times.shape!=(20,):
    raise ValueError('Actual image and ego timestamps must be int64 microseconds')
  now = history_times[-1]
  if np.any(np.abs(times.reshape(2,5)-now-np.tile(FRAME_OFFSETS_US,(2,1))) > timestamp_tolerance_us):
    raise ValueError('Capture times must match the two-second front-camera schedule; do not repeat missing frames')
  if np.any(np.abs(history_times-now-HISTORY_OFFSETS_US) > timestamp_tolerance_us):
    raise ValueError('Twenty measured ego poses at 10 Hz are required')
  xyz,rot = np.asarray(data['ego_history_xyz']),np.asarray(data['ego_history_rot'])
  if xyz.shape!=(1,1,20,3) or rot.shape!=(1,1,20,3,3) or not np.isfinite(xyz).all() or not np.isfinite(rot).all():
    raise ValueError('Invalid measured ego poses')
  if not np.allclose(xyz[0,0,-1],0,atol=1e-4) or not np.allclose(rot[0,0,-1],np.eye(3),atol=1e-4):
    raise ValueError('Ego history must be expressed in the current ego frame')
  if not np.allclose(rot.swapaxes(-1,-2)@rot,np.eye(3),atol=1e-3) or not np.allclose(np.linalg.det(rot),1,atol=1e-3):
    raise ValueError('Ego rotations must be proper rotation matrices')
  nav = data.get('nav_text')
  if not isinstance(nav,(list,tuple)) or len(nav)!=1 or not isinstance(nav[0],str) or not nav[0].strip():
    raise ValueError('A nonempty lane-follow or navigation driving instruction is required')


def prepare_front_inputs(data,model_config,tokenizer,*,processor=None,timestamp_tolerance_us=0):
  """Use official Edge image normalization and prompt building for ten real images.

  This explicitly bypasses the official six-camera sample validator, replacing
  it with the stricter front-only contract above. It does not qualify weights
  trained with surround cameras for driving with this reduced observation.
  """
  import torch
  from alpamayo2_edge import helper
  from alpamayo2_edge.chat_template import build_conversation

  validate_front_sample(data,timestamp_tolerance_us=timestamp_tolerance_us)
  helper._check_image_layout(model_config)
  if model_config.history_num_steps!=20 or model_config.tokens_per_history_traj!=57:
    raise ValueError('Unsupported Edge ego-history configuration')
  canonical = dict(data)
  for key in ('image_frames','camera_indices','absolute_timestamps','ego_history_xyz','ego_history_rot'):
    canonical[key] = torch.from_numpy(np.ascontiguousarray(data[key]))
  canonical['camera_pixel_bounds'] = dict.fromkeys(CAMERA_IDS,(163840,196608))
  canonical['system_prompt'] = ('You are a driving assistant. Only front wide and front telephoto cameras are available. '
                                + 'Side and rear camera observations are unavailable; do not claim they are clear.')
  messages = build_conversation(canonical,num_tokens_per_history_traj=57,
                                include_camera_ids=True,system_prompt=canonical['system_prompt'])
  if processor is None:
    processor = helper.get_processor(tokenizer,model_config)
  tokens = helper._tokenize_messages(messages,processor,include_closed_thinking=True)
  if tokens['image_grid_thw'].shape[0]!=10:
    raise RuntimeError('All ten measured front images must reach the model processor')
  return {'tokenized_data':tokens,'ego_history_xyz':canonical['ego_history_xyz'].float(),
          'ego_history_rot':canonical['ego_history_rot'].float()}


def oem_blindspot_veto(direction,*,left,right,available,fresh):
  """Return blocked/unknown/no_warning; no_warning never grants a lane change."""
  if direction not in ('left','right'):
    raise ValueError('A lane-change direction is required')
  if not available or not fresh or type(left) is not bool or type(right) is not bool:
    return 'unknown'
  return 'blocked' if (left if direction=='left' else right) else 'no_warning'
