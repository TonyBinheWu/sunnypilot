"""Selected vision MLP tiles with independent image address ranges."""
from functools import partial
import re

from tinygrad import Device, Tensor, dtypes
from tinygrad.codegen.opt import Opt, OptOps
from tinygrad.codegen.opt.postrange import Scheduler
from tinygrad.helpers import round_up
from tinygrad.uop.ops import AxisType, KernelInfo, Ops, UOp
from ..amd_gemm import pack

TILES = {'fc1': (3, 3), 'fc2': (3, 6)}
SHAPES = {'fc1': (720, 4304, 1152), 'fc2': (720, 1152, 4304)}
NAME = re.compile(r'^vlm\.model\.visual\.encoder\.layers\.(\d+)\.mlp\.(fc[12])$')


def kernel(out, x, weight, x_scale, w_scale, *extra, images, rows, tile_m, tile_n, residual=False):
  bias, residual_input = (extra[:-1], extra[-1]) if residual else (extra, None)
  columns, width = weight.shape
  assert images in (1, 2) and out.shape == (images, rows, columns)
  assert x.shape == (images*round_up(rows, 16), width) and x_scale.numel() == images*rows
  assert width % 16 == columns % 16 == 0 and (tile_m, tile_n) in ((4, 4), (3, 3), (3, 6))
  m = UOp.range(round_up(rows, 16*tile_m), 0)
  n, k = UOp.range(round_up(columns, 16*tile_n), 1), UOp.range(width, 2)
  def index(row): return (row//16*(width//16)+k//16)*256+(k%16//4)*64+(row%16)*4+k%4
  a = x.flatten().index(index(m).valid(m < rows))
  b = weight.flatten().index(index(n).valid(n < columns))
  value = (a*b).cast(dtypes.float32).reduce(k, arg=Ops.ADD)
  value = value*(x_scale.flatten().index(m.valid(m < rows))*w_scale.flatten().index(0))
  if bias:
    value = value+bias[0].flatten().index(n.valid(n < columns)).cast(dtypes.float32)
  offset = (m*columns+n).valid((m < rows)&(n < columns))
  value = value.cast(out.dtype)
  if residual_input is not None:
    # Same rounding as `residual + linear(x)`: round the projection to BF16, add in FP32, round the sum to BF16.
    value = (residual_input.flatten().index(offset).cast(dtypes.float32) + value.cast(dtypes.float32)).cast(out.dtype)
  store = out.flatten().index(offset).store(value)
  schedule = Scheduler(store.end(m, n).sink(arg=KernelInfo()), Device[Device.DEFAULT].renderer)
  schedule.convert_loop_to_global()
  ranges = schedule.apply_opt(Opt(OptOps.TC, 0, (-1, 0, 1)))
  row_axis = ranges[1].axis_id
  for axis, count in ((1, tile_m), (0, tile_n)):
    schedule.apply_opt(Opt(OptOps.SPLIT, schedule.rngs.index(ranges[axis]), (count, AxisType.UPCAST)))
  ast = schedule.get_optimized_ast(name_override=f'agent_vision_tiles_{tile_m}x{tile_n}_b{images}'+('_residual' if residual else ''))
  # Extend only the row workgroup dispatch. Each image retains the complete
  # single-image reduction and padding predicates, as in image-gemm.py.
  original = next(r for r in schedule.rngs if r.axis_type is AxisType.GLOBAL and r.axis_id == row_axis)
  blocks = int(original.vmax+1)
  expanded = original.replace(src=(original.src[0].const_like(images*blocks),))
  image, mapping = expanded//blocks, {original: expanded % blocks}
  offsets = {out.base: rows*columns, x.base: round_up(rows, 16)*width, x_scale.base: rows}
  if residual_input is not None:
    offsets[residual_input.base] = rows*columns
  indexes, seen = {}, set()
  for node in ast.toposort():
    if node.op is not Ops.INDEX:
      continue
    updated = node.substitute(mapping, walk=True)
    if node.src[0].base in offsets:
      seen.add(node.src[0].base)
      assert len(updated.src) == 2
      updated = updated.replace(src=(updated.src[0], updated.src[1]+image*offsets[node.src[0].base]))
    indexes[node] = updated
  assert seen == set(offsets)
  return ast.substitute(indexes, walk=True).substitute({original: expanded}, walk=True)


def pack_images(x):
  # uint8 permits a byte-exact CPU layout check. Pinned CPU FP8 padding flushes
  # subnormals; the GPU gate checks the real FP8 packing expression separately.
  assert x.ndim == 3 and x.dtype in (dtypes.fp8e4m3, dtypes.uint8)
  images, rows, width = x.shape
  assert width % 16 == 0
  padded = x.pad(((0, 0), (0, round_up(rows, 16)-rows), (0, 0)))
  return padded.reshape(images, -1, 16, width//16, 4, 4).permute(0, 1, 3, 4, 2, 5).contiguous().reshape(-1, width)


def row_scales(scale, images, rows):
  assert scale.dtype == dtypes.float32
  if scale.numel() == images*rows:
    return scale.reshape(-1)
  assert scale.numel() == images, 'Require separate image scales or existing row scales'
  return scale.reshape(images, 1).expand(images, rows).reshape(-1).contiguous()


def packed(packed_x, packed_weight, scales, bias, images, rows, tile, out=None, residual=None):
  if out is None:
    out = Tensor.empty(images, rows, packed_weight.shape[0], device=packed_x.device, dtype=dtypes.bfloat16)
  extra = () if residual is None else (residual.reshape(out.shape),)
  return Tensor.custom_kernel(out, packed_x, packed_weight, *scales, bias, *extra,
    fxn=partial(kernel, images=images, rows=rows, tile_m=tile[0], tile_n=tile[1], **({} if residual is None else {'residual': True})))[0]


def gemm(x, weight, scales, bias, tile, residual=None):
  images, rows, width = x.shape
  assert x.dtype == weight.dtype == dtypes.fp8e4m3 and bias.dtype == dtypes.bfloat16
  assert weight.shape[1] == width
  scales = (row_scales(scales[0], images, rows), scales[1])
  return packed(pack_images(x), pack(weight), scales, bias, images, rows, tile, residual=residual)
