"""NVIDIA CPU input preparation, retained from comma's prototype (MIT)."""
from functools import partial
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from safetensors import safe_open
from transformers.models.cosmos3_edge.modeling_cosmos3_edge import Cosmos3EdgeModel, Cosmos3EdgeVisionEmbeddings
from alpamayo2_edge.chat_template import build_conversation
from alpamayo2_edge.config import Alpamayo2EdgeConfig, build_alpamayo2_edge_tokenizer
from alpamayo2_edge.helper import _tokenize_messages, get_processor
from alpamayo2_edge.models.delta_tokenizer import DeltaTrajectoryTokenizer
from alpamayo2_edge.sample import CAMERA_PIXEL_BOUNDS


class InputAdapter:
  def __init__(self, checkpoint):
    root = Path(checkpoint)
    self.config = Alpamayo2EdgeConfig(**json.loads((root/'config.json').read_text()))
    self.config._name_or_path = str(root.resolve())
    self.tokenizer = build_alpamayo2_edge_tokenizer(self.config._name_or_path)
    self.processor = get_processor(self.tokenizer, self.config)
    name = 'vlm.model.visual.embeddings.position_embedding.weight'
    index = json.loads((root/'model.safetensors.index.json').read_text())['weight_map']
    with safe_open(root/index[name], framework='pt', device='cpu') as source:
      self.position_weight = source.get_tensor(name).reshape(16, 16, -1)

  def prepare(self, arrays):
    data = {k: v if k == 'nav_text' else torch.from_numpy(np.array(v, copy=True)) for k, v in arrays.items()}
    if (data['camera_indices'].tolist() != [1]*5+[6]*5 or data['image_frames'].dtype != torch.uint8 or
        data['image_frames'].shape != (10, 1, 3, 432, 768) or data['ego_history_xyz'].shape != (1, 20, 3) or
        data['ego_history_rot'].shape != (1, 20, 3, 3)):
      raise ValueError('Require the complete calibrated two-front input')
    canonical = dict(data, camera_pixel_bounds=CAMERA_PIXEL_BOUNDS)
    tokenized = _tokenize_messages(build_conversation(canonical), self.processor, include_closed_thinking=True)
    prepared = {'tokenized_data': tokenized, 'ego_history_xyz': data['ego_history_xyz'].unsqueeze(0),
                'ego_history_rot': data['ego_history_rot'].unsqueeze(0)}
    ids = tokenized['input_ids'].clone()
    xyz, rot = prepared['ego_history_xyz'][:, 0], prepared['ego_history_rot'][:, 0]
    history = DeltaTrajectoryTokenizer(pad_origin_at_beginning=False).encode(None, None, xyz, rot)
    ids[ids == self.config.traj_ids['history_pad']] = (history+self.config.traj_ids['history_id0']).flatten()
    rope_model = SimpleNamespace(config=self.config.vlm_config)
    rope_model.get_vision_position_ids = partial(Cosmos3EdgeModel.get_vision_position_ids, rope_model)
    positions, delta = Cosmos3EdgeModel.get_rope_index(rope_model, ids, tokenized['mm_token_type_ids'],
                                                     image_grid_thw=tokenized['image_grid_thw'])
    vision_positions = Cosmos3EdgeVisionEmbeddings.resize_positional_embeddings(self.position_weight, tokenized['image_grid_thw'], 2)
    return prepared, (ids.numpy(), positions.numpy(), int(delta.item()), vision_positions.float().numpy())


def rotary(positions):
  frequencies = 1/(1e8**(np.arange(0, 128, 2, dtype=np.float32)/128))
  angles = positions[..., None].astype(np.float32)*frequencies
  combined = angles[0].copy()
  for axis in (1, 2):
    combined[..., axis:60:3] = angles[axis, ..., axis:60:3]
  combined = np.concatenate((combined, combined), axis=-1)[:, None]
  return np.cos(combined), np.sin(combined)
