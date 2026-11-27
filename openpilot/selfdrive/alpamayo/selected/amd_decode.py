from functools import partial, reduce

from tinygrad import Tensor, dtypes
from tinygrad.dtype import AddrSpace
from tinygrad.uop.ops import AxisType, KernelInfo, Ops, UOp
from openpilot.selfdrive.alpamayo.amd_attention import _warp_reduce
from .amd_gemm import pack


def _relu_squared_scale(out, raw):
  wave = UOp.range(8, 0, AxisType.LOCAL)
  lane = UOp.range(32, -1, AxisType.WARP)
  tid = wave*32+lane

  def positive_word(i):
    bits = raw.flatten().index(i).bitcast(dtypes.uint16).cast(dtypes.uint32)
    return (bits <= 0x7f80).where(bits, 0)

  # Positive BF16 words sort by magnitude. Square and round the maximum once, after reducing all 9,216 activations.
  peak = reduce(UOp.maximum, (positive_word(base+tid*4+j) for base in range(0,9216,1024) for j in range(4)))
  swizzle = UOp.custom_function('llvm.amdgcn.ds.swizzle', dtype=dtypes.int32)
  for shift in (16,8,4,2,1):
    other = swizzle.call(peak.bitcast(dtypes.int32), UOp.const(0x1f | (shift << 10), dtypes.int32))
    peak = peak.maximum(other.bitcast(dtypes.uint32))
  partials = UOp.alloc((8,), dtypes.uint32, addrspace=AddrSpace.LOCAL)
  stored = partials.index(wave.valid(lane.eq(0))).store(peak)
  peak = reduce(UOp.maximum, (partials.after(stored).index(i) for i in range(8)))
  value = (peak << 16).bitcast(dtypes.float32)
  scale = ((value*value).cast(dtypes.bfloat16).cast(dtypes.float32)*(1.0/448.0)).maximum(1e-12)
  store = out.flatten().index(UOp.const(0,dtypes.int32).valid(tid.eq(0))).store(scale)
  return store.end(wave,lane).sink(arg=KernelInfo(name='alpamayo_serial_fc2_scale', opts_to_apply=()))


def quantize_relu_squared(raw):
  assert raw.shape == (1,1,9216) and raw.dtype == dtypes.bfloat16
  scale = Tensor.custom_kernel(Tensor.empty((),dtype=dtypes.float32,device=raw.device),raw.flatten(),fxn=_relu_squared_scale)[0]
  values = (raw.relu().square().float()/scale).clamp(-448,448).cast(dtypes.fp8e4m3)
  return values.reshape(1,9216).contiguous(),scale


def _gemv(out, x, weight, x_scale, w_scale, *bias, packed=True):
  rows, width = weight.shape
  group = UOp.range(rows//(16 if packed else 4), 0, AxisType.GLOBAL)
  wave, lane = UOp.range(4, 1, AxisType.LOCAL), UOp.range(32, -1, AxisType.WARP)
  if packed:
    row, k = group*16+lane%16, UOp.range(width//64, 2, AxisType.LOOP)
    cols = [(k*4+wave)*16+(lane//16)*4+j%4+(j//4)*8 for j in range(8)]
    indices = [(group*(width//16)+c//16)*256+(c%16//4)*64+(row%16)*4+c%4 for c in cols]
  else:
    row, k = group*4+wave, UOp.range(width//128, 2, AxisType.LOOP)
    cols = [k*128+lane*4+j for j in range(4)]
    indices = [row*width+c for c in cols]
  value = sum(x.flatten().index(c).cast(dtypes.float32) * weight.flatten().index(i).cast(dtypes.float32)
              for c, i in zip(cols, indices, strict=True)).reduce(k, arg=Ops.ADD)
  if packed:
    shuffle = UOp.custom_function('llvm.amdgcn.ds.swizzle', dtype=dtypes.int32)
    value = value + shuffle.call(value.bitcast(dtypes.int32), UOp.const(0x1f | (16 << 10), dtypes.int32)).bitcast(dtypes.float32)
    partials = UOp.alloc((64,), dtypes.float32, addrspace=AddrSpace.LOCAL)
    stored = partials.index((wave*16+lane%16).valid(lane < 16)).store(value)
    value = sum(partials.after(stored).index(i*16+lane%16) for i in range(4))
    valid = wave.eq(0) & (lane < 16)
  else:
    value, valid = _warp_reduce(value), lane.eq(0)
  value = value * (x_scale.flatten().index(0) * w_scale.flatten().index(0))
  if bias:
    value = value + bias[0].flatten().index(row).cast(dtypes.float32)
  store = out.flatten().index(row.valid(valid)).store(value.cast(out.dtype))
  return store.end(group, wave, lane).sink(arg=KernelInfo(name='alpamayo_fp8_gemv', opts_to_apply=()))


def gemv(x, weight, scales, bias=None, packed=True, dtype=dtypes.bfloat16):
  out = Tensor.empty(weight.shape[0], dtype=dtype, device=x.device)
  return Tensor.custom_kernel(out, x, pack(weight) if packed else weight, *scales, *(() if bias is None else (bias,)),
                              fxn=partial(_gemv, packed=packed))[0]
