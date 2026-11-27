"""Bind the two mixed-precision block schedules to the selected model's verified weights."""

import hashlib
import json
from tinygrad import Device, Tensor, dtypes
from tinygrad.engine.realize import capturing
from tinygrad.uop.ops import Ops, UOp
from ..frozen import ASSETS
from ..model import SelectedModel
from .programs import PairPrograms, require

PAIR = ((1, 720, 768), (1, 720, 1152)) * 2
PREFIX = 'vlm.model.visual.encoder.layers.'
PROJECTIONS = ('self_attn.q_proj', 'self_attn.k_proj', 'self_attn.v_proj', 'self_attn.out_proj', 'mlp.fc1', 'mlp.fc2')
BULK_LAYOUT = 'f052598ec86566ec63f98908ecf412b6e20e3f5cb4f5de5d47137dc02ade9fb0'
CHECKPOINT = 'f0471a81f8a1b191eb92c12639660a7bbcf831ff379d1b0d724fba23c533785d'
ORDERED_PROGRAMS = 'b6da5dc02b203ef34b55b7961c67a6c0058d2dc848fbee019cbecee5104fbfa3'


def root(t):
  b = t.uop.storage_base
  require(b.op is Ops.BUFFER, 'Vision tensor has no storage')
  return b


class VisionWeights:
  def __init__(self, model):
    # Runtime constructs the cache immediately after verifying and packing the checkpoint. Keep those exact named owners.
    self.model = model
    self.roles = [
      (field, name, t, t.uop)
      for field in ('weights', 'weight_scales', 'bf16_weights', 'projector_weights', 'vision_qkv')
      for name, t in getattr(model, field).items()
      if name.startswith(('vlm.model.visual.', 'vlm.model.projector.'))
    ]

  def check(self):
    for field, name, t, view in self.roles:
      if getattr(self.model, field).get(name) is not t or t.uop is not view:
        raise ValueError(f'Vision weight binding changed: {name}')

  def check_layout(self):
    self.check()
    artifacts = json.loads((ASSETS / 'artifacts.json').read_bytes())
    logical = {k: artifacts[k] for k in ('checkpoint_config_sha256', 'checkpoint_shards', 'fp8_index_sha256', 'fp8_weights_sha256')}
    # Reviewed fine-tunes change only expert layers, so the vision plan of the base checkpoint stays valid for them.
    weights = {logical['fp8_weights_sha256']} | {pin['fp8_weights_sha256'] for pin in artifacts.get('fp8_finetunes', {}).values()}
    require(hashlib.sha256(json.dumps(logical, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == CHECKPOINT
            and self.model.weight_digest in weights, 'Vision checkpoint differs')
    require(self.model.config['vlm_config']['vision_config']['num_hidden_layers'] == 27, 'Unexpected vision depth')
    require(
      tuple(self.model.projector_weights) == ('vlm.model.projector.linear_fc1', 'vlm.model.projector.linear_fc2'),
      'Unexpected vision projector order',
    )
    # Same-shaped packed matrices, biases and scales must retain their correct named ranges in the verified bulk upload.
    rows = []
    for field, name, t, _ in self.roles:
      if field in ('weights', 'weight_scales') and (b := root(t).buffer).base is self.model._bulk_storage:
        rows.append((field, name, b.offset, b.nbytes, t.shape, t.dtype.name))
    require(
      hashlib.sha256(json.dumps(sorted(rows), separators=(',', ':')).encode()).hexdigest() == BULK_LAYOUT,
      'Vision weight or scale has the wrong bulk storage range',
    )


def layer_inputs(model, x, i):
  p = PREFIX + str(i) + '.'
  args = {'activation': x}
  args.update({s + '.' + k: model.weights[p + s + '.' + k] for s in ('layer_norm1', 'layer_norm2') for k in ('weight', 'bias')})
  if i >= 2:
    # The fused pair layer reads the merged Q/K/V projection instead of the three separate ones.
    args.update({'self_attn.qkv.' + k: model.vision_qkv[p + 'self_attn.qkv.' + k] for k in ('matrix', 'scale', 'bias')})
  for s in PROJECTIONS:
    if i >= 2 and s in ('self_attn.q_proj', 'self_attn.k_proj', 'self_attn.v_proj'):
      continue
    n = p + s + '.weight'
    if i < 2:
      require(n not in model.weight_scales and model.weights[n].dtype == dtypes.bfloat16, 'Expected restored BF16 vision weight')
      args[s + '.matrix'] = model.bf16_weights[p + s]
    else:
      require(
        model.weights[n].dtype == dtypes.fp8e4m3 and model.weight_scales[n].dtype == dtypes.float32, 'Expected scaled FP8 vision weight'
      )
      args[s + '.matrix'], args[s + '.scale'] = model.weights[n], model.weight_scales[n]
    args[s + '.bias'] = model.weights[p + s + '.bias']
  return args


class CompileAtRealize:
  def __init__(self, sink, compiler):
    self.sink, self.compiler = sink, compiler

  def add_linear(self, linear):
    self.sink.add_linear(self.compiler(linear))


class LayerTemplate:
  def __init__(self, build, args, compiler):
    self.signature = self.layout(args)
    self.calls, self.scratch, calls = [], [], []

    class Collect:
      def add_linear(self, linear):
        calls.extend(linear.src)

    require(len(capturing) == 1, 'Require one vision pair capture')
    parent = capturing[0]
    capturing[0] = CompileAtRealize(Collect(), compiler)
    try:
      result = build()
    finally:
      capturing[0] = parent
    ids = {root(t): i for i, t in enumerate(args.values())}
    require(len(ids) == len(args), 'Aliased vision layer inputs')
    read = set()
    for c in calls:
      require(c.op is Ops.CALL and c.body.op is Ops.PROGRAM, 'Expected compiled vision operation')
      slots = []
      for n, a in enumerate(c.src[1:]):
        require(a.op is Ops.BUFFER, 'Unexpected vision argument')
        if a not in ids:
          require(n in c.body.arg.outs and n not in c.body.arg.ins and not a.buffer.is_allocated(), 'Undeclared vision layer input')
          ids[a] = len(ids)
          self.scratch.append((a.device, a.max_numel(), a.dtype))
        k = ids[a]
        if k < len(args):
          require(n not in c.body.arg.outs, 'Vision layer writes an input')
          if n in c.body.arg.ins:
            read.add(k)
        slots.append(k)
      self.calls.append((c.body, c.arg, slots))
    require(read == set(range(len(args))), 'Unused vision layer input')
    self.output, self.shape = ids[root(result)], result.shape
    require(self.output >= len(args) and result.uop is root(result).reshape(self.shape), 'Unexpected vision output layout')

  @staticmethod
  def layout(args):
    return tuple((n, b.shape, b.dtype, b.device, t.uop.substitute({b: UOp(Ops.NOOP)})) for n, t in args.items() for b in (root(t),))

  def emit(self, args):
    require(self.layout(args) == self.signature, 'Vision layer ABI differs')
    bufs = [root(t) for t in args.values()]
    require(len(set(bufs)) == len(bufs), 'Duplicate vision layer input')
    bufs.extend(UOp.new_buffer(dev, n, dt) for dev, n, dt in self.scratch)
    calls = tuple(UOp(Ops.CALL, src=(body, *(bufs[k] for k in slots)), arg=arg) for body, arg, slots in self.calls)
    capturing[0].add_linear(UOp(Ops.LINEAR, src=calls))
    return Tensor(bufs[self.output]).reshape(self.shape)


class PairCapture(SelectedModel):
  def __init__(self, model, compiler):
    self.__dict__.update(vars(model))  # share verified tensors; encode_group changes only this capture's image count
    self.compiler, self.templates = compiler, {}

  def vision_layer(self, x, i):
    family, args = i < 2, layer_inputs(self, x, i)
    if family not in self.templates:
      original = super().vision_layer
      self.templates[family] = LayerTemplate(lambda: original(x, i), args, self.compiler)
    return self.templates[family].emit(args)

  def encode_group(self, *pairs):
    require(len(capturing) == 1, 'Require one vision pair capture')
    parent = capturing[0]
    order = hashlib.sha256()

    def compile_group(linear):
      compiled = self.compiler(linear)
      for call in compiled.src:
        order.update(call.body.key)
      return compiled

    capturing[0] = CompileAtRealize(parent, compile_group)
    try:
      result = super().encode_group(*pairs)
    finally:
      capturing[0] = parent
    require(order.hexdigest() == ORDERED_PROGRAMS, 'Vision pair operation order differs')
    return result


class PairEncoder:
  def __init__(self, weights):
    weights.check_layout()
    capture = PairCapture(weights.model, PairPrograms(Device[Device.DEFAULT].renderer))
    from ..graph_cache import CachedJit
    self.jit = CachedJit(capture.encode_group,'vision-pair')
    self.jit.jit.cnt = 1  # capture, link, and execute the first real pair (or load the cached graph)

  def __call__(self, *pairs):
    require(all(t.device == 'AMD' and t.uop.base.realized is not None for t in pairs), 'Require resident AMD camera pair inputs')
    result = self.jit(*pairs)
    if self.jit.jit.cnt == 2:
      self.jit.jit.fxn = None  # warm replay owns the linked graph; release capture-only state
    return result
