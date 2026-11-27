"""Exact image features with group-two encoding and a 144-image LRU."""
from collections import OrderedDict
import hashlib
import numpy as np
from tinygrad import Device, Tensor, dtypes
from tinygrad.uop.ops import Ops, UOp
from openpilot.selfdrive.alpamayo.segments import PatchRows


class VisionCache:
  capacity = 144
  group_limit = 2

  def __init__(self, model):
    self.model = model
    self.pair_weights = None
    if getattr(model,'amd',False) and Device.DEFAULT == 'AMD':
      from .model import SelectedModel
      if type(model) is SelectedModel and model.dtype == dtypes.bfloat16 and model.config['vlm_config']['vision_config']['num_hidden_layers'] == 27:
        from .vision_pair import VisionWeights
        self.pair_weights = VisionWeights(model)
    self.cache,self.encoders,self.stitchers = OrderedDict(),{},OrderedDict()
    # The frozen pair encoder writes both features into one reused base buffer. A captured copy into fresh storage
    # costs ~3 ms; a scheduled clone() costs 30-60 ms of host work on the Dragon.
    def copy_pair(first, second, src):
      flat = src.reshape(2, -1)
      return first.assign(flat[0]).realize(), second.assign(flat[1]).realize()
    from .graph_cache import CachedJit
    self.copy_jit = CachedJit(copy_pair,'vision-copy')
    self.keys = ()
    self.hits = self.misses = 0

  def reset(self):
    self.cache.clear()
    self.encoders.clear()
    self.stitchers.clear()
    self.keys = ()
    self.hits = self.misses = 0

  @staticmethod
  def patch_keys(pixels, grids):
    if type(pixels) is PatchRows:
      if any(np.prod(grid) != 720 for grid in grids):
        raise ValueError('Wrong grid for immutable byte patches')
      return tuple((tuple(grid),p[1]) for p,grid in zip(pixels,grids,strict=True))
    offsets = np.concatenate(([0],np.cumsum(grids.prod(axis=1))))
    return tuple((tuple(grid),hashlib.sha256(np.ascontiguousarray(pixels[a:b])).digest())
                 for grid,a,b in zip(grids,offsets[:-1],offsets[1:],strict=True))

  def prepare(self, prepared):
    tokens = prepared['tokenized_data']
    pixels = tokens['pixel_values']
    self.keys = self.patch_keys(pixels if type(pixels) is PatchRows else pixels.numpy(),tokens['image_grid_thw'].numpy())
    if len(self.keys) != 10 or any(np.prod(grid) != 720 for grid,_ in self.keys):
      raise ValueError('Require all ten full-resolution images')

  @staticmethod
  def image_view(tensor, begin, end):
    assert tensor.ndim == 2
    stride = tensor.shape[-1]*tensor.dtype.itemsize
    buffer = tensor._buffer().view((end-begin)*stride,begin*stride).ensure_allocated()
    return Tensor(UOp.from_buffer(buffer,tensor.dtype)).reshape(1,end-begin,tensor.shape[-1])

  def missing_indices(self, keys):
    missing = {}
    for i,key in enumerate(keys):
      if key not in self.cache:
        missing.setdefault(key, i)
    return tuple(missing.values())

  def encoder(self, pairs):
    shape = tuple(t.shape for t in pairs)
    if self.pair_weights is not None:
      from .vision_pair import PAIR, PairEncoder
      if shape == PAIR and all(t.dtype == dtypes.bfloat16 and b.max_numel() == t.numel() and t.uop is b.reshape(t.shape)
                               for t in pairs for b in (t.uop.storage_base,)):
        key = (PairEncoder,shape)
        if key not in self.encoders:
          self.encoders[key] = PairEncoder(self.pair_weights)
        return self.encoders[key]
    if shape not in self.encoders:
      from .graph_cache import CachedJit
      self.encoders[shape] = CachedJit(self.model.encode_group,f'vision-{shape}')
    return self.encoders[shape]

  def encode_missing(self, keys, pixels, positions, batches, missing):
    if self.pair_weights is not None:
      self.pair_weights.check()
    assert len(batches) == len(keys) and all(count == 1 for _,_,count in batches)
    groups,encoded = {},{}
    offset = 0
    for i in missing:
      key = keys[i]
      begin,end,_ = batches[i]
      groups.setdefault(key[0],[]).append((key,offset,begin,end))
      offset += end-begin
    for group in groups.values():
      for start in range(0,len(group),self.group_limit):
        chunk = group[start:start+self.group_limit]
        pairs = [view for _,p,a,b in chunk for view in (self.image_view(pixels,p,p+b-a),self.image_view(positions,a,b))]
        Tensor.realize(*pairs)
        outputs = self.encoder(pairs)(*pairs)
        values = self.own(outputs)
        encoded.update(zip((item[0] for item in chunk),values,strict=True))
    return encoded

  def own(self, outputs):
    """Copy encoder outputs out of the encoder's reused storage."""
    base = outputs[0].uop.base
    views = [t.uop.buffer for t in outputs]
    width = outputs[0].numel()
    if (len(outputs) == 2 and all(t.uop.base is base and t.shape == outputs[0].shape for t in outputs) and base.op is Ops.BUFFER
        and base.buffer.nbytes == 2*width*outputs[0].dtype.itemsize and [b.offset for b in views] == [0, width*outputs[0].dtype.itemsize]):
      # Separate storage per image: a later stitch graph may take both features as distinct inputs.
      targets = [Tensor(UOp.new_buffer(base.device, width, base.dtype)) for _ in outputs]
      for t in targets:
        t.uop.buffer.ensure_allocated()
      # A replayed graph returns its captured buffers; the results live in the per-call targets.
      self.copy_jit(*targets, Tensor(base))
      return [t.reshape(outputs[0].shape) for t in targets]
    values = [t.clone() for t in outputs]
    Tensor.realize(*values)
    return values

  def retain(self, keys, encoded):
    self.cache.update(encoded)
    for key in keys:
      self.cache.move_to_end(key)
    while len(self.cache) > self.capacity:
      self.cache.popitem(last=False)

  def encode(self, pixels, positions, ids, batches, spans, missing):
    self.hits = sum(key in self.cache for key in self.keys)
    self.misses = len(missing)
    self.retain(self.keys,self.encode_missing(self.keys,pixels,positions,batches,missing))
    unique,indices,layout = [],{},[]
    for key in self.keys:
      if key not in indices:
        indices[key] = len(unique)
        unique.append(self.cache[key])
      layout.append(indices[key])
    layout = tuple(layout)
    grids = tuple(key[0] for key in self.keys)
    shape = (ids.shape,spans,layout,grids,grids)
    if shape not in self.stitchers:
      def stitch(tokens, *images):
        merged = Tensor.cat(*(images[i] for i in layout),dim=0)
        return self.model.embed(tokens,merged,spans)
      from .graph_cache import CachedJit
      self.stitchers[shape] = CachedJit(stitch,f'stitch-{shape}')
    self.stitchers.move_to_end(shape)
    while len(self.stitchers) > 8:
      self.stitchers.popitem(last=False)
    return self.stitchers[shape](ids,*unique)
