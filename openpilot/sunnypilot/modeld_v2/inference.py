"""Adapted from sunnypilot ModelState.run (see LICENSE.md)."""
import os

import numpy as np

from openpilot.sunnypilot.modeld_v2.parse_model_outputs import Parser


class Inference:
  def __init__(self, adapter, entry):
    self.adapter = adapter
    self.numpy_inputs = adapter.numpy_inputs
    self.chestnut = entry['big']
    self.mlsim = entry['generation'] >= 11
    self.prev_desire = np.zeros(8, np.float32)
    self.parser = Parser()

  def reset(self):
    self.prev_desire.fill(0)
    self.adapter.reset_warmup_buffers()
    if not self.adapter.is_native:
      for name, queue in self.adapter.input_queues.items():
        if name.endswith('_q'):
          queue.assign(0).realize()

  def run(self, frames, transforms, inputs):
    self.adapter.copy_frames(frames)

    desire_key = self.adapter._desire_key
    inputs = dict(inputs, **{desire_key: inputs["desire_pulse"].copy()})
    inputs[desire_key][0] = 0
    (self.numpy_inputs[desire_key].flat if self.adapter.is_native else self.numpy_inputs[desire_key])[:] = \
      np.where(inputs[desire_key] - self.prev_desire > .99, inputs[desire_key], 0)
    self.prev_desire[:] = inputs[desire_key]

    for key in ('nav_map', 'navigation'):
      if key in self.numpy_inputs:
        self.numpy_inputs[key][:] = inputs.get(key, 0)
    for key in ('traffic_convention', 'lateral_control_params', 'action_t'):
      if key in self.numpy_inputs and key in inputs:
        self.numpy_inputs[key][:] = inputs[key]

    transforms = {self.adapter._road_key: transforms['img'], self.adapter._wide_key: transforms['big_img']}
    if self.adapter.is_native:
      for i, key in enumerate(self.adapter._vision_input_names):
        if key in transforms:
          self.numpy_inputs['tfm'][i] = transforms[key].reshape(3, 3)
    else:
      self.numpy_inputs['tfm'][:, :] = transforms[self.adapter._road_key].reshape(3, 3)
      self.numpy_inputs['big_tfm'][:, :] = transforms[self.adapter._wide_key].reshape(3, 3)

    raw_outputs = self.adapter.run()
    if self.adapter._combined_model_type == 'supercombo':
      if isinstance(raw_outputs, (list, tuple)):
        raw_outputs, = raw_outputs
      model_output = raw_outputs.numpy().flatten()
      if self.chestnut and not np.all(np.isfinite(model_output)):
        raise RuntimeError("model output not finite")
      sliced = {k: model_output[np.newaxis, v] for k, v in self.adapter.vision_output_slices.items()}
      outputs = self.parser.parse_outputs(sliced)
      if 'prev_feat' in self.numpy_inputs and 'hidden_state' in self.adapter.vision_output_slices:
        (self.numpy_inputs['prev_feat'].flat if self.adapter.is_native else self.numpy_inputs['prev_feat'])[:] = \
          model_output[self.adapter.vision_output_slices['hidden_state']]
    else:
      vision_output = raw_outputs[0].numpy().flatten()
      vision_sliced = {k: vision_output[np.newaxis, v] for k, v in self.adapter.vision_output_slices.items()}
      outputs = self.parser.parse_vision_outputs(vision_sliced)

      if 'prev_feat' in self.numpy_inputs and 'hidden_state' in self.adapter.vision_output_slices:
        (self.numpy_inputs['prev_feat'].flat if self.adapter.is_native else self.numpy_inputs['prev_feat'])[:] = \
          vision_output[self.adapter.vision_output_slices['hidden_state']]

      policies = []
      for i, policy_slices in enumerate(self.adapter._policy_slices_list):
        policy_output = raw_outputs[i + 1].numpy().flatten()
        policies.append(policy_output)
        policy_sliced = {k: policy_output[np.newaxis, v] for k, v in policy_slices.items()}
        parsed = self.parser.parse_policy_outputs(policy_sliced)
        if 'off' in self.adapter._policy_keys[i] and self.adapter._has_on_policy:
          for key in ('plan', 'planplus', 'action'):
            if any(key in self.adapter._policy_slices_list[j] for j, k in enumerate(self.adapter._policy_keys) if 'on' in k.lower()):
              parsed.pop(key, None)

        outputs.update(parsed)

      if 'planplus' in outputs and 'plan' in outputs:
        outputs['plan'] = outputs['plan'] + outputs['planplus']

    if 'desired_curvature' in outputs and 'prev_desired_curv' in self.numpy_inputs:
      buf = self.numpy_inputs['prev_desired_curv']
      buf[0, :-1] = buf[0, 1:]
      buf[0, -1, :] = outputs['desired_curvature'][0, :] if not self.mlsim else 0

    required = {'plan': (1, 33, 15), 'lane_lines': (1, 4, 33, 2), 'road_edges': (1, 2, 33, 2), 'lead': (1, 3, 6, 4),
                'road_transform': (1, 6), 'wide_from_device_euler': (1, 3), 'pose': (1, 6), 'desire_state': (1, 8)}
    for name, shape in required.items():
      if name not in outputs or outputs[name].shape != shape:
        raise ValueError(f'Incompatible {name} output')
    keys = set(required) | {k + '_stds' for k in required if k != 'desire_state'} | {
      'lane_lines_prob', 'lead_prob', 'meta', 'desire_pred', 'action', 'desired_curvature'}
    result = {k: v for k, v in outputs.items() if k in keys}
    if not all(np.isfinite(v).all() for v in result.values()) or not {'lane_lines_prob','lead_prob','meta','desire_pred'} <= result.keys():
      raise ValueError('Invalid driving model output')
    if os.getenv('SEND_RAW_PRED'):
      result['raw_pred'] = model_output.copy() if self.adapter._combined_model_type == 'supercombo' else np.concatenate([vision_output, *policies])
    if result['meta'].shape[-1] in (48, 53):
      result['_sunny_legacy_meta'] = True
    if not self.mlsim and 'desired_curvature' in result:
      result['_sunny_curvature'] = result['desired_curvature'][0, 0]
    return result
