"""Transfer BF16 inputs and reuse immutable vision positions across snapshots."""
import numpy as np
import torch
from tinygrad import Device, Tensor, TinyJit, dtypes
from openpilot.selfdrive.alpamayo.inputs import rotary
from openpilot.selfdrive.alpamayo.segments import PatchRows


class VisionBuffers:
  """Device inputs shared by anchor encoding and complete predictions for one checkpoint."""
  def __init__(self):
    words = ((torch.arange(256,dtype=torch.float32)-127.5)/127.5).to(torch.bfloat16).view(torch.uint16).numpy()
    self.palette = Tensor(words,device='CPU').to(Device.DEFAULT).bitcast(dtypes.bfloat16).realize()
    self.positions = {}
    self.expanders = {}

  def expand(self, pixels):
    return self.palette[pixels.to(Device.DEFAULT).cast(dtypes.int32)].contiguous().realize()

  def expand_captured(self, raw):
    """expand() through a persistent CPU buffer and a captured graph: ~8 ms instead of ~95 ms of host scheduling."""
    if raw.shape not in self.expanders:
      cpu = Tensor.empty(*raw.shape, dtype=dtypes.uint8, device='CPU').realize()
      view = np.frombuffer(cpu._buffer().as_memoryview(allow_zero_copy=True), dtype=np.uint8).reshape(raw.shape)
      self.expanders[raw.shape] = cpu, view, TinyJit(self.expand)
    cpu, view, jit = self.expanders[raw.shape]
    view[:] = raw
    # The captured output buffer is reused; callers copy encoder outputs, never the expanded pixels.
    return jit(cpu)

  def position_buffer(self, grids, positions):
    key = grids.tobytes()
    if key not in self.positions:
      if len(self.positions) >= 4:
        self.positions.pop(next(iter(self.positions)))
      words = torch.from_numpy(positions).to(torch.bfloat16).view(torch.uint16).numpy()
      self.positions[key] = Tensor(words, device='CPU').to(Device.DEFAULT).bitcast(dtypes.bfloat16).realize()
    return self.positions[key]

  @staticmethod
  def batches(grids, limit):
    offsets = np.concatenate(([0], np.cumsum(grids.prod(axis=1))))
    batches, i = [], 0
    while i < len(grids):
      end = i+1
      while end < len(grids) and np.array_equal(grids[i], grids[end]) and end-i < limit:
        end += 1
      batches.append((int(offsets[i]), int(offsets[end]), end-i))
      i = end
    return tuple(batches)


_ROTARY = {}


def bf16_rotary(key, positions):
  """BF16 cos/sin words for one position layout. Consecutive slots repeat the layout; reuse the exact same arrays."""
  if key not in _ROTARY:
    if len(_ROTARY) >= 16:
      _ROTARY.pop(next(iter(_ROTARY)))
    _ROTARY[key] = tuple(torch.from_numpy(a).to(torch.bfloat16).view(torch.uint16).numpy() for a in rotary(positions()))
  return _ROTARY[key]


# Metadata order after pixels: zeros, ids, prefill cos/sin, two decode cos/sin pairs, noise.
PREFILL_ROTARY = (2, 3)
STATIC_FIELDS = (4, 5, 6, 7)  # decode and action rotary tables; the noise is compared by value
NOISE_FIELD = 8


class CompactInputs:

  @staticmethod
  def arrays(args, prepared, packed):
    ids, positions, delta, vision_positions = packed
    patches = prepared['tokenized_data']['pixel_values']
    arrays = [patches if type(patches) is PatchRows else patches.numpy(), np.zeros(1, dtype=np.uint16), ids.astype(np.int32),
              *bf16_rotary(('prefill', positions.shape, positions.tobytes()), lambda: positions)]
    for length in (args.max_tokens, args.max_tokens+64):
      start = ids.shape[1] + delta
      arrays.extend(bf16_rotary(('decode', length, start), lambda: np.broadcast_to(np.arange(length) + start, (3, 1, length))))
    arrays.append(np.zeros((1, 64, 2), dtype=np.float32))
    if arrays[0].dtype != np.uint8:
      raise ValueError('Expected unnormalized uint8 image patches')
    return arrays

  @staticmethod
  def signature(args, config, prepared, packed):
    return (str(config._name_or_path), prepared['tokenized_data']['image_grid_thw'].numpy().tobytes(),
            args.max_tokens, args.vision_batch,
            tuple(np.flatnonzero(packed[0][0] == config.vlm_config.image_token_id)))

  def update(self, args, config, prepared, packed, arrays=None):
    if self.signature(args, config, prepared, packed) != self._signature:
      return False
    arrays = self.arrays(args, prepared, packed) if arrays is None else arrays
    if arrays[0].shape != self.pixels.shape or any(a.shape != old.shape for a, old in zip(arrays[1:], self.cpu, strict=True)):
      return False
    self.pixels = arrays[0]
    for i, (a, old) in enumerate(zip(arrays[1:], self.cpu, strict=True)):
      if a is self.sources[i] or i == NOISE_FIELD:
        continue  # The same memoized rotary array is already in this CPU buffer; upload() owns the noise.
      destination = np.frombuffer(old._buffer().as_memoryview(allow_zero_copy=True), dtype=a.dtype).reshape(a.shape)
      np.copyto(destination, a, casting='no')
      self.sources[i] = a
      self.rotary_dirty |= i in PREFILL_ROTARY
      self.static_dirty |= i in STATIC_FIELDS
    return True

  def __init__(self, args, config, prepared, packed, arrays=None, vision=None):
    vision = VisionBuffers() if vision is None else vision
    ids, positions, delta, vision_positions = packed
    self._signature = self.signature(args, config, prepared, packed)
    grids = prepared['tokenized_data']['image_grid_thw'].numpy()
    fixed_positions = vision.position_buffer(grids,vision_positions)
    self.pixels, *metadata = self.arrays(args, prepared, packed) if arrays is None else arrays
    # Own copies: a CPU tensor may alias its numpy source, and memoized rotary arrays must never be overwritten.
    self.cpu = [Tensor(np.array(a, copy=True), device='CPU').realize() for a in metadata]
    self.sources = list(metadata)
    self.rotary_dirty, self.rotary_device = True, None
    self.static_dirty, self.static_device = True, None
    self.uploaded_pixel_bytes = 0
    self.noise = np.frombuffer(self.cpu[-1]._buffer().as_memoryview(allow_zero_copy=True), dtype=np.float32).reshape(1, 64, 2)
    self.batches = vision.batches(grids,args.vision_batch)
    image_indices = np.flatnonzero(ids[0] == config.vlm_config.image_token_id)
    self.spans = tuple((int(span[0]), int(span[-1])+1) for span in np.split(image_indices, np.flatnonzero(np.diff(image_indices) != 1)+1))
    self.uploads = {}

    def transfer(pixels, _position_placeholder, ids, *fields):
      normalized = None if pixels is None else vision.expand(pixels)
      angles = [x.to(Device.DEFAULT).bitcast(dtypes.bfloat16).contiguous().realize() for x in fields[:-1]]
      return normalized, fixed_positions, ids.to(Device.DEFAULT).contiguous().realize(), *angles, fields[-1].to(Device.DEFAULT).contiguous().realize()

    def transfer_ids(pixels, _position_placeholder, ids):
      # Each copy is its own trip through the USB staging window; unchanged rotary tables and noise stay on the GPU.
      normalized = None if pixels is None else vision.expand(pixels)
      return normalized, fixed_positions, ids.to(Device.DEFAULT).contiguous().realize()

    self.transfer, self.transfer_ids = transfer, transfer_ids
    # The prefill rotary tables (~1 MB) change only with the prompt layout; upload them only then.
    self.rotary_transfer = TinyJit(lambda cos, sin: tuple(x.to(Device.DEFAULT).bitcast(dtypes.bfloat16).contiguous().realize() for x in (cos, sin)))

  def upload(self, noise, missing):
    ranges = [self.batches[i][:2] for i in missing]
    rows = sum(end-begin for begin,end in ranges)
    if rows not in self.uploads:
      buf = Tensor.empty(rows, self.pixels.shape[1], dtype=dtypes.uint8, device='CPU').realize() if rows else None
      dest = np.frombuffer(buf._buffer().as_memoryview(allow_zero_copy=True), dtype=np.uint8).reshape(buf.shape) if rows else None
      self.uploads[rows] = buf, dest, TinyJit(self.transfer), TinyJit(self.transfer_ids)
    buf, dest, transfer, transfer_ids = self.uploads[rows]
    offset = 0
    for begin,end in ranges:
      dest[offset:offset+end-begin] = self.pixels.rows(begin,end) if type(self.pixels) is PatchRows else self.pixels[begin:end]
      offset += end-begin
    self.uploaded_pixel_bytes = dest.nbytes if rows else 0
    if not np.array_equal(self.noise, noise):
      self.noise[:] = noise
      self.static_dirty = True
    if self.rotary_dirty or self.rotary_device is None:
      self.rotary_device = self.rotary_transfer(*(self.cpu[i] for i in PREFILL_ROTARY))
      self.rotary_dirty = False
    rest = [t for i, t in enumerate(self.cpu) if i not in PREFILL_ROTARY]
    if self.static_dirty or self.static_device is None:
      pixels, positions, ids, *static = transfer(buf, *rest)
      self.static_device, self.static_dirty = tuple(static), False
    else:
      pixels, positions, ids = transfer_ids(buf, *rest[:2])
    return (pixels, positions, ids, *self.rotary_device, *self.static_device)
