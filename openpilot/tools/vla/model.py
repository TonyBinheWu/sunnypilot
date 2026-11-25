"""One-frame, two-axis evaluation of the pinned PhysicalAI driving VLA with tinygrad."""
import math
import struct
from pathlib import Path

import numpy as np
from tinygrad import Tensor
from tinygrad.llm.gguf import _GGML_NATIVE, _GGML_QUANT, ggml_data_to_tensor, read_int32, read_str, read_uint64, readers

QUESTIONS = {
  'longitudinal': 'stop, yield, follow, search (for a gap), pass, adapt (speed to road conditions), track (maintain set speed)',
  'lateral': 'turn, change (lanes), merge, out (nudge out of lane), in (nudge within lane), park (pull over), abort, keep (stay centered)',
  'direction': 'left, right, straight',
}
SYSTEM = 'Predict the driving action from the forward camera and observed past ego motion. Answer with the appropriate English verb or direction.'


def prompts(history):
  if not isinstance(history, list) or len(history) != 9:
    raise ValueError('Expected nine observed poses sampled at 0.25 s ending at the image time')
  for pose in history:
    if not isinstance(pose, list) or len(pose) != 3 or not all(type(v) in (int, float) and math.isfinite(v) for v in pose):
      raise ValueError('Invalid observed x/y/yaw')
  if any(abs(v) > 1e-4 for v in history[-1]):
    raise ValueError('Pose history must be in the current vehicle frame')
  trajectory = '\n'.join(f'<wp>[{x:.2f},{y:.2f},{yaw:.4f}]</wp>' for x, y, yaw in history)
  before = f'<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n'
  after = []
  for axis, choices in QUESTIONS.items():
    after.append('\n[PAST-VEHICLE-MOTION]:\n' + trajectory + f'\nSelect {axis} from: {choices}.'
                 + '<|im_end|>\n<|im_start|>assistant\n{"' + axis + '":"')
  return before, after


class Weights:
  """Keep GGUF blocks packed on the device. Expand only the weights used by the current layer."""
  def __init__(self, path: Path, device):
    self.tensors = {}
    with path.open('rb') as f:
      magic, version, count, keys = struct.unpack('<4sIQQ', f.read(24))
      if (magic, version) != (b'GGUF', 3):
        raise ValueError('Unsupported GGUF')
      self.meta = {}
      for _ in range(keys):
        key = read_str(f)
        self.meta[key] = readers[read_int32(f)](f)
      entries = []
      for _ in range(count):
        name = read_str(f)
        shape = tuple(reversed([read_uint64(f) for _ in range(read_int32(f))]))
        entries.append((name, shape, read_int32(f), read_uint64(f)))
      alignment = self.meta.get('general.alignment', 32)
      start = (f.tell() + alignment - 1) // alignment * alignment
      for name, shape, kind, offset in entries:
        block, size = (1, _GGML_NATIVE[kind].itemsize) if kind in _GGML_NATIVE else _GGML_QUANT[kind]
        f.seek(start + offset)
        length = math.prod(shape) // block * size
        data = bytearray(length)
        if f.readinto(data) != length:
          raise ValueError(f'Truncated tensor {name}')
        packed = Tensor(np.frombuffer(data, np.uint8), device=device).realize()
        self.tensors[name] = packed, shape, kind

  def __getitem__(self, name):
    packed, shape, kind = self.tensors[name]
    return ggml_data_to_tensor(packed, math.prod(shape), kind).reshape(shape).half()

  def embedding(self, indices):
    packed, (rows, width), kind = self.tensors['token_embd.weight']
    blocks = packed.reshape(rows, -1)[indices].contiguous().flatten()
    return ggml_data_to_tensor(blocks, indices.numel() * width, kind).reshape(*indices.shape, width).half()

  def linear(self, x, name):
    out = x @ self[name + '.weight'].T
    return out + self[name + '.bias'] if name + '.bias' in self.tensors else out

  def norm(self, x, name):
    return x.float().layernorm(eps=1e-6).half() * self[name + '.weight'] + self[name + '.bias']


def rotary(x, phases):
  a, b = x.chunk(2, dim=-1)
  cos, sin = phases
  return (a * cos - b * sin).cat(b * cos + a * sin, dim=-1)


def frequencies(angles, device):
  return tuple(Tensor(fn(angles).astype(np.float16), device=device) for fn in (np.cos, np.sin))


def patch_order(x):
  h, w, d = x.shape
  return x.reshape(h//2, 2, w//2, 2, d).transpose(1, 2).reshape(h*w, d)


def encode_image(weights, rgb, checkpoint=None):
  pixels = Tensor(rgb.astype(np.float32) / 127.5 - 1., device=weights.tensors['v.patch_embd.bias'][0].device).half()
  height, width = rgb.shape[0] // 16, rgb.shape[1] // 16
  patches = pixels.reshape(height, 16, width, 16, 3).permute(0, 2, 4, 1, 3).reshape(height, width, -1)
  kernel = weights['v.patch_embd.weight'] + weights['v.patch_embd.weight.1']
  x = patch_order(patches) @ kernel.flatten(1).T + weights['v.patch_embd.bias']
  pos = weights['v.position_embd.weight'].reshape(48, 48, -1).permute(2, 0, 1).unsqueeze(0)
  x = (x + patch_order(pos.float().interpolate((height,width), mode='linear', align_corners=True)[0].permute(1, 2, 0).half())).realize()
  grid = np.indices((height, width)).transpose(1, 2, 0).reshape(height//2, 2, width//2, 2, 2).transpose(0, 2, 1, 3, 4).reshape(-1, 2)
  phase = grid[:, :, None] * 10000. ** (-np.arange(16) / 16)
  phases = frequencies(phase.reshape(1, len(grid), 32), x.device)
  features = []
  for layer in range(24):
    p = f'v.blk.{layer}.'
    qkv = weights.linear(weights.norm(x, p+'ln1'), p+'attn_qkv').reshape(-1, 3, 16, 64).permute(1, 2, 0, 3)
    q, k, v = qkv[0], qkv[1], qkv[2]
    attn = rotary(q, phases).scaled_dot_product_attention(rotary(k, phases), v).transpose(0, 1).reshape(-1, 1024)
    x = x + weights.linear(attn, p+'attn_out')
    x = (x + weights.linear(weights.linear(weights.norm(x, p+'ln2'), p+'ffn_up').gelu(), p+'ffn_down')).realize()
    if layer in (5, 11, 17):
      p = f'v.deepstack.{layer}.'
      merged = weights.norm(x.reshape(-1, 4096), p+'norm')
      features.append(weights.linear(weights.linear(merged, p+'fc1').gelu(), p+'fc2').realize())
    if checkpoint is not None:
      checkpoint()
  x = weights.norm(x, 'v.post_ln').reshape(-1, 4096)
  return weights.linear(weights.linear(x, 'mm.0').gelu(), 'mm.2').realize(), features


def rms(x, w):
  return (x.float() * (x.float().square().mean(axis=-1, keepdim=True) + 1e-6).rsqrt()).half() * w


def classify(weights, tokenizer, rgb, vision, history, checkpoint=None):
  before, suffixes = prompts(history)
  first = tokenizer.encode(before + '<|vision_start|>')
  tails = [tokenizer.encode('<|vision_end|>' + suffix) for suffix in suffixes]
  image, deep = vision
  batch, n = len(tails), len(first)
  h, w = rgb.shape[0]//32, rgb.shape[1]//32
  image_end = n + h*w
  seq_len = ((image_end + max(map(len, tails)) + 63) // 64) * 64
  inputs = [first + [0]*(h*w) + t + [0]*(seq_len-image_end-len(t)) for t in tails]
  x = weights.embedding(Tensor(inputs, device=image.device))
  x = x[:, :n].cat(image.unsqueeze(0).expand(batch,-1,-1), x[:, image_end:], dim=1).realize()
  after_pos = np.arange(seq_len-image_end) + n + max(h,w)
  coords = np.indices((h,w)).reshape(2,-1) + n
  pos = np.stack([np.concatenate((np.arange(n), middle, after_pos)) for middle in (np.full(h*w,n), *coords)], axis=1)
  dims = np.arange(64)
  axis = np.where((dims % 3 == 1) & (dims < 60), 1, np.where((dims % 3 == 2) & (dims < 60), 2, 0))
  phases = frequencies((pos[:,axis] * 5000000. ** (-dims/64))[None, None], x.device)
  for layer in range(36):
    p = f'blk.{layer}.'
    norm = rms(x, weights[p+'attn_norm.weight'])
    q = weights.linear(norm, p+'attn_q').reshape(batch, seq_len, 32, 128).transpose(1, 2)
    k = weights.linear(norm, p+'attn_k').reshape(batch, seq_len, 8, 128).transpose(1, 2)
    v = weights.linear(norm, p+'attn_v').reshape(batch, seq_len, 8, 128).transpose(1, 2)
    q, k = rotary(rms(q, weights[p+'attn_q_norm.weight']), phases), rotary(rms(k, weights[p+'attn_k_norm.weight']), phases)
    attn = q.scaled_dot_product_attention(k, v, is_causal=True, enable_gqa=True).transpose(1, 2).reshape(batch, seq_len, -1)
    x = x + weights.linear(attn, p+'attn_output')
    norm = rms(x, weights[p+'ffn_norm.weight'])
    x = x + weights.linear(weights.linear(norm, p+'ffn_gate').silu() * weights.linear(norm, p+'ffn_up'), p+'ffn_down')
    if layer < len(deep):
      x = x + deep[layer].pad(((n, seq_len-image_end), (0, 0)))
    x = x.realize()
    if checkpoint is not None:
      checkpoint()
  hidden = rms(x[list(range(batch)), [image_end+len(t)-1 for t in tails]], weights['output_norm.weight'])
  # Compare against the entire vocabulary. A non-letter prediction is an abstention.
  best = np.full(batch, -np.inf)
  ids = np.zeros(batch, dtype=int)
  packed, (rows, width), kind = weights.tensors['token_embd.weight']
  for offset in range(0, rows, 8192):
    end = min(offset+8192, rows)
    block = packed.reshape(rows, -1)[offset:end].flatten()
    table = ggml_data_to_tensor(block, (end-offset)*width, kind).reshape(end-offset, width).half()
    scores = (hidden @ table.T).float().numpy()
    if not np.isfinite(scores).all():
      raise ValueError('Nonfinite action scores')
    idx = scores.argmax(axis=1)
    values = scores[np.arange(batch),idx]
    ids = np.where(values > best, idx + offset, ids)
    best = np.maximum(best, values)
    if checkpoint is not None:
      checkpoint()
  return [tokenizer.decode([int(i)]) for i in ids]
