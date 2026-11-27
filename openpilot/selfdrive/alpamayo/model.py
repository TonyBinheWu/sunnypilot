"""Alpamayo 2 Edge BF16 core from comma's Alpamayo prototype (MIT)."""
import json
import math
from pathlib import Path

from tinygrad import Device, Tensor, TinyJit, dtypes
from tinygrad.helpers import USE_TC
from tinygrad.nn.state import safe_load
from tinygrad.renderer.llvmir import AMDLLVMRenderer
from tinygrad.uop.ops import UOp


class EdgeModel:
  def __init__(self, checkpoint):
    self.config = json.loads((Path(checkpoint)/'config.json').read_text())
    index = json.loads((Path(checkpoint)/'model.safetensors.index.json').read_text())['weight_map']
    self.weights = {}
    self.dtype = dtypes.bfloat16
    self.amd = getattr(Device[Device.DEFAULT], 'arch', '') in ('gfx1200', 'gfx1201')
    for shard in sorted(set(index.values())):
      for name, weight in safe_load(Path(checkpoint)/shard).items():
        self.weights[name] = weight.to(Device.DEFAULT).cast(self.dtype).contiguous().realize()
        self.synchronize()
      print(f'Loaded {shard}', flush=True)
    self.cache = self.prompt_length = self.greedy_shape = None
    self.encode_jits, self.trajectory_jits = {}, {}
    self.prefill_jit = TinyJit(self._language)
    self.decode_jit = TinyJit(self._greedy_decode)

  def linear(self, x, name):
    shape = x.shape[:-1]
    weight, bias = self.weights[f'{name}.weight'], self.weights.get(f'{name}.bias')
    return x.reshape(-1, x.shape[-1]).linear(weight.T, bias).reshape(*shape, weight.shape[0])

  def norm(self, x, name, rms=False, eps=None):
    eps = eps if eps is not None else 1e-5 if rms else 1e-6
    y = x.float().rmsnorm(eps=eps) if rms else x.float().layernorm(eps=eps)
    if rms:
      return y.cast(x.dtype)*self.weights[f'{name}.weight']
    return (y*self.weights[f'{name}.weight'].float()+self.weights[f'{name}.bias'].float()).cast(x.dtype)

  def attention(self, q, k, v, mask=None, causal=False):
    if (self.amd and q.dtype == dtypes.bfloat16 and q.shape[2:] == (1, 128) and mask is not None and not causal
        and isinstance(k.shape[2], int) and mask.numel() == k.shape[2] and isinstance(Device[q.device].renderer, AMDLLVMRenderer)):
      from openpilot.selfdrive.alpamayo.amd_attention import decode_attention
      return decode_attention(q, k, v, mask)
    if (self.amd and USE_TC.value == 1 and q.dtype == dtypes.bfloat16 and q.shape[2] >= 128 and mask is None
        and isinstance(Device[q.device].renderer, AMDLLVMRenderer)):
      from openpilot.selfdrive.alpamayo.amd_attention import attention
      return attention(q, k, v, causal)
    if q.shape[1] != k.shape[1]:
      k, v = (t.repeat_interleave(q.shape[1]//k.shape[1], dim=1) for t in (k, v))
    scores = (q.matmul(k.transpose(-2, -1))*(q.shape[-1]**-.5)).float()
    if causal:
      mask = (Tensor.arange(k.shape[2]).reshape(1, -1) > Tensor.arange(q.shape[2]).reshape(-1, 1)).where(-math.inf, 0)
    if mask is not None:
      scores = scores+mask
    return scores.softmax(-1).cast(q.dtype).matmul(v)

  def vision_layer(self, x, i):
    prefix = f'vlm.model.visual.encoder.layers.{i}'
    h = self.norm(x, f'{prefix}.layer_norm1')
    q, k, v = (self.linear(h, f'{prefix}.self_attn.{n}_proj').reshape(*h.shape[:2], 16, 72).transpose(1, 2) for n in ('q', 'k', 'v'))
    h = self.attention(q, k, v).transpose(1, 2).reshape(x.shape)
    x = x+self.linear(h, f'{prefix}.self_attn.out_proj')
    h = self.linear(self.norm(x, f'{prefix}.layer_norm2'), f'{prefix}.mlp.fc1').float().gelu().cast(self.dtype)
    return (x+self.linear(h, f'{prefix}.mlp.fc2')).realize()

  def encode(self, pixels, positions, ids, batches, spans):
    key = (pixels.shape, ids.shape, batches, spans)
    if key not in self.encode_jits:
      if len(self.encode_jits) >= 8:
        self.encode_jits.pop(next(iter(self.encode_jits)))
      self.encode_jits[key] = TinyJit(lambda p, v, t: self._encode(p, v, t, batches, spans))
    return self.encode_jits[key](pixels, positions, ids)

  def _encode(self, pixels, positions, ids, batches, spans):
    features = [self._vision(pixels[a:b].reshape(n, -1, pixels.shape[-1]), positions[a:b].reshape(n, -1, positions.shape[-1]))
                for a, b, n in batches]
    return self.embed(ids, Tensor.cat(*features, dim=0), spans)

  def embed(self, ids, features, spans):
    embedding = self.weights['vlm.model.language_model.embed_tokens.weight'][ids]
    chunks, cursor, feature_cursor = [], 0, 0
    for begin, end in spans:
      chunks.extend((embedding[:, cursor:begin], features[feature_cursor:feature_cursor+end-begin].unsqueeze(0)))
      cursor, feature_cursor = end, feature_cursor+end-begin
    chunks.append(embedding[:, cursor:])
    return Tensor.cat(*chunks, dim=1).realize()

  def _vision(self, pixels, positions):
    x = (self.linear(pixels, 'vlm.model.visual.embeddings.patch_embedding')+positions).realize()
    for i in range(self.config['vlm_config']['vision_config']['num_hidden_layers']):
      x = self.vision_layer(x, i)
    x = self.norm(x, 'vlm.model.visual.post_layernorm')
    x = self.norm(x, 'vlm.model.projector.norm').reshape(-1, 4608)
    x = self.linear(x, 'vlm.model.projector.linear_fc1').float().gelu(approximate='none').cast(self.dtype)
    return self.linear(x, 'vlm.model.projector.linear_fc2').realize()

  @staticmethod
  def rope(q, k, cos, sin):
    def rotate(x):
      half = x.shape[-1]//2
      return (-x[..., half:]).cat(x[..., :half], dim=-1)
    return q*cos+rotate(q)*sin, k*cos+rotate(k)*sin

  def text_layer(self, x, cos, sin, prefix, cache=None, mask=None, cache_pos=None):
    h = self.norm(x, f'{prefix}.input_layernorm', rms=True)
    q, k, v = (self.linear(h, f'{prefix}.self_attn.{n}_proj').reshape(1, h.shape[1], heads, 128).transpose(1, 2)
               for n, heads in (('q', 16), ('k', 8), ('v', 8)))
    q, k = self.rope(q, k, cos, sin)
    if cache_pos is not None:
      store = cache[:, :, :, cache_pos:cache_pos+x.shape[1]].uop.store(Tensor.stack(k, v).uop)
      assigned = Tensor(cache.uop.after(store))
      end = cache.shape[3] if self.amd and not isinstance(cache_pos, int) else cache_pos+x.shape[1]
      k, v = (assigned[i, :, :, :end] for i in range(2))
    elif cache is not None:
      k, v = (old.cat(new, dim=2) for old, new in zip(cache, (k, v), strict=True))
    causal = isinstance(cache_pos, int) and cache_pos == 0
    h = self.attention(q, k, v, mask, causal).transpose(1, 2).reshape(1, x.shape[1], 2048)
    x = x+self.linear(h, f'{prefix}.self_attn.o_proj')
    h = self.linear(self.norm(x, f'{prefix}.post_attention_layernorm', rms=True), f'{prefix}.mlp.fc1').relu().square()
    return (x+self.linear(h, f'{prefix}.mlp.fc2')).realize()

  def prefill(self, x, cos, sin, max_tokens):
    capacity = ((x.shape[1]+max_tokens+255)//256)*256
    if self.cache is None or self.cache[0].shape[3] != capacity:
      self.cache = [Tensor.zeros(2, 1, 8, capacity, 128, dtype=self.dtype).realize()
                    for _ in range(self.config['vlm_config']['text_config']['num_hidden_layers'])]
      self.prefill_jit.reset()
      self.decode_jit.reset()
      self.trajectory_jits.clear()
    if self.prompt_length != x.shape[1]:
      self.prefill_jit.reset()
      self.prompt_length = x.shape[1]
    return self.prefill_jit(x, cos, sin, 0)

  def greedy_decode(self, logits, cos, sin, position, step):
    if self.greedy_shape != cos.shape:
      self.decode_jit.reset()
      self.greedy_shape = cos.shape
    position = UOp.variable('position', 0, self.cache[0].shape[3]-1).bind(position)
    step = UOp.variable('step', 0, cos.shape[2]-1).bind(step)
    return self.decode_jit(logits, cos, sin, position, step)

  def _greedy_decode(self, logits, cos, sin, position, step):
    ids, config = Tensor.arange(logits.shape[-1]), self.config
    allowed = (ids < config['traj_ids']['history_id0']) | (ids >= config['traj_ids']['history_id0']+config['history_vocab_size'])
    allowed &= (ids < config['traj_ids']['future_id0']) | (ids >= config['traj_ids']['future_id0']+config['future_vocab_size'])
    allowed &= ids != config['vlm_config']['text_config']['eos_token_id']
    token = allowed.where(logits.reshape(-1), -math.inf).argmax().realize()
    x = self.weights['vlm.model.language_model.embed_tokens.weight'][token].reshape(1, 1, -1)
    logits = self._language(x, cos[:, :, step:step+1], sin[:, :, step:step+1], position)
    return logits, token.float().realize()

  def _language(self, x, cos, sin, past):
    length = x.shape[1]
    if isinstance(past, int) and past == 0:
      mask = None
    elif self.amd:
      mask = (Tensor.arange(self.cache[0].shape[3]) > past).where(-math.inf, 0)
    else:
      mask = (Tensor.arange(past+length).reshape(1, -1) > Tensor.arange(past, past+length).reshape(-1, 1)).where(-math.inf, 0)
    for i in range(self.config['vlm_config']['text_config']['num_hidden_layers']):
      x = self.text_layer(x, cos, sin, f'vlm.model.language_model.layers.{i}', self.cache[i], mask, cache_pos=past)
    x = self.norm(x[:, -1:], 'vlm.model.language_model.norm', rms=True)
    return self.linear(x, 'vlm.lm_head').realize()

  def trajectory(self, actions, cos, sin, length, steps, offset=0):
    key = (steps, cos.shape)
    if key not in self.trajectory_jits:
      from .selected.graph_cache import CachedJit
      self.trajectory_jits[key] = CachedJit(lambda a, c, s, n, p: self._trajectory(a, c, s, n, steps, p),
                                            f'trajectory-{key}-{self.cache[0].shape}')
    length = UOp.variable('cache_length', 1, self.cache[0].shape[3]).bind(length)
    offset = UOp.variable('action_position', 0, cos.shape[2]-64).bind(offset) if cos.shape[2] > 64 else 0
    return self.trajectory_jits[key](actions, cos, sin, length, offset)

  def _trajectory(self, actions, cos, sin, length, steps, offset):
    cos, sin = (t[:, :, offset:offset+64] for t in (cos, sin))
    capacity = self.cache[0].shape[3]
    keys = Tensor.arange(capacity+64)
    mask = ((keys < length) | (keys >= capacity)).where(0, -math.inf)
    flat_cache = [t[i] for t in self.cache for i in range(2)]
    for step in range(steps):
      timestep = Tensor.full((1,), step/steps, dtype=dtypes.float32)
      velocity = self.expert_step(actions, timestep, cos, sin, flat_cache, mask)
      actions = (actions+velocity/steps).realize()
    return actions.realize()

  def action_projection(self, actions, timestep):
    freqs = (Tensor.arange(10, dtype=dtypes.float32)*(math.log(100)/9)).exp()
    def fourier(x):
      angles = x.unsqueeze(-1)*freqs*(2*math.pi)
      return angles.sin().cat(angles.cos(), dim=-1)*math.sqrt(2)
    x = fourier(actions[..., 0]).cat(fourier(actions[..., 1]), fourier(timestep).reshape(1, 1, 20).expand(1, 64, 20), dim=-1)
    prefix = 'expert.action_in_proj.encoder.trunk'
    x = self.linear(x.cast(self.dtype), f'{prefix}.0').float().silu().cast(self.dtype)
    x = self.linear(self.norm(x, f'{prefix}.2', rms=True), f'{prefix}.3').float().silu().cast(self.dtype)
    x = self.linear(self.norm(x, f'{prefix}.5', rms=True), f'{prefix}.6')
    return self.norm(x, 'expert.action_in_proj.norm', eps=1e-5)

  def expert_step(self, actions, timestep, cos, sin, flat_cache, mask):
    x = self.action_projection(actions, timestep)
    for i in range(self.config['expert_config']['llm_config']['num_hidden_layers']):
      x = self.text_layer(x, cos, sin, f'expert.expert.layers.{i}', flat_cache[2*i:2*i+2], mask)
    return self.linear(self.norm(x, 'expert.expert.norm', rms=True), 'expert.action_out_proj').float().realize()

  def synchronize(self):
    Device[Device.DEFAULT].synchronize()
    dev = Device[Device.DEFAULT]
    if hasattr(dev, 'error_state') and dev.error_state.host.view(fmt='q')[0]:
      raise RuntimeError('eGPU reported an execution error')
