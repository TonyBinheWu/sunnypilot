"""Runtime queue construction from sunnypilot. See LICENSE.md."""
import math
import numpy as np
from tinygrad.tensor import Tensor


def nv12_copy_size(stride: int, y_height: int, uv_height: int) -> int:
  return stride * (y_height + uv_height)


def _detect_desire_key(shapes: dict) -> str | None:
  return next((key for key in shapes if key.startswith('desire')), None)


def _detect_vision_keys(shapes: dict) -> tuple[str | None, str | None]:
  img_keys = sorted(key for key in shapes if 'img' in key)
  return (next((key for key in img_keys if 'big' not in key), None),
          next((key for key in img_keys if 'big' in key), None))


def get_policy_npy_shapes(input_shapes):
  shapes = {}
  desire_key = _detect_desire_key(input_shapes)
  if desire_key:
    shapes['desire'] = (input_shapes[desire_key][2],)
  for key, shape in input_shapes.items():
    if key not in (desire_key, 'features_buffer') and 'img' not in key:
      shapes[key] = tuple(shape)
  if 'features_buffer' in input_shapes:
    fb = input_shapes['features_buffer']
    shapes['prev_feat'] = (fb[0], math.prod(fb[2:]))

  sizes = [int(np.prod(size)) for size in shapes.values()]
  return shapes, sizes


def make_input_queues(input_shapes, frame_skip, device, frame_copy_size):
  road_key, _ = _detect_vision_keys(input_shapes)
  img = input_shapes[road_key]
  fb = input_shapes['features_buffer']
  feat_dim = math.prod(fb[2:])
  dp = input_shapes[_detect_desire_key(input_shapes)]
  n_frames = img[1] // 6
  img_buf_shape = (frame_skip * (n_frames - 1) + 1, 6, img[2], img[3])

  policy_shapes, _ = get_policy_npy_shapes(input_shapes)
  shapes = {'tfm': (3, 3), 'big_tfm': (3, 3)} | policy_shapes
  sizes = [math.prod(s) for s in shapes.values()]
  packed_npy_size = sum(sizes) * np.dtype(np.float32).itemsize
  packed_input = np.zeros(packed_npy_size + 2 * frame_copy_size, dtype=np.uint8)
  packed_npy_inputs = packed_input[:packed_npy_size].view(np.float32)
  frames = packed_input[packed_npy_size:]
  frame_views = {'img': frames[:frame_copy_size], 'big_img': frames[frame_copy_size:]}
  npy = {k: v.reshape(s) for (k, s), v in zip(shapes.items(), np.split(packed_npy_inputs, np.cumsum(sizes[:-1])), strict=True)}
  input_queues = {
    'img_q': Tensor(np.zeros(img_buf_shape, dtype=np.uint8), device=device).contiguous().realize(),
    'big_img_q': Tensor(np.zeros(img_buf_shape, dtype=np.uint8), device=device).contiguous().realize(),
    'feat_q': Tensor(np.zeros((frame_skip * fb[1], fb[0], feat_dim), dtype=np.float32), device=device).contiguous().realize(),
    'desire_q': Tensor(np.zeros((frame_skip * dp[1], dp[0], dp[2]), dtype=np.float32), device=device).contiguous().realize(),
    'packed_npy_inputs': Tensor(packed_input, device='NPY').realize(),
  }
  return input_queues, npy, frame_views
