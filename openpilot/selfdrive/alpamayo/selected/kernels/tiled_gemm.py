"""FP8 GEMM tiles derived from Harald's pinned amd_gemm implementation."""
from functools import partial
from tinygrad import Device, Tensor, dtypes
from tinygrad.codegen.opt import Opt, OptOps
from tinygrad.codegen.opt.postrange import Scheduler
from tinygrad.helpers import round_up
from tinygrad.uop.ops import AxisType, KernelInfo, Ops, UOp
from ..amd_gemm import pack


def kernel(out, x, weight, x_scale, w_scale, *extra, tile_m, tile_n, row_scale=False, column_scale=False,
           local_m=1, local_n=1, swap=False, unroll_k=1, group_m=1, residual=False):
  bias, residual_input = (extra[:-1], extra[-1]) if residual else (extra, None)
  rows, columns = out.shape
  width = weight.shape[1]
  m, n, k = UOp.range(round_up(rows, 16*tile_m), 0), UOp.range(round_up(columns, 16*tile_n), 1), UOp.range(width, 2)
  def index(row): return (row//16*(width//16)+k//16)*256 + (k%16//4)*64 + (row%16)*4 + k%4
  a = x.flatten().index(index(m).valid(m < rows))
  b = weight.flatten().index(index(n).valid(n < columns))
  value = (a*b).cast(dtypes.float32).reduce(k, arg=Ops.ADD)
  value = value * (x_scale.flatten().index(m.valid(m < rows) if row_scale else 0) * w_scale.flatten().index(n.valid(n < columns) if column_scale else 0))
  if bias:
    value = value + bias[0].flatten().index(n.valid(n < columns)).cast(dtypes.float32)
  offset = (m*columns+n).valid((m < rows) & (n < columns))
  value = value.cast(out.dtype)
  if residual_input is not None:
    # Same rounding as `residual + linear(x)`: round the projection to BF16, add in FP32, round the sum to BF16.
    value = (residual_input.flatten().index(offset).cast(dtypes.float32) + value.cast(dtypes.float32)).cast(out.dtype)
  store = out.flatten().index(offset).store(value)
  schedule = Scheduler(store.end(m, n).sink(arg=KernelInfo()), Device[Device.DEFAULT].renderer)
  schedule.convert_loop_to_global()
  ranges = schedule.apply_opt(Opt(OptOps.TC, 0, (-1, 0, 1)))
  axes = (ranges[1].axis_id, ranges[0].axis_id)
  # Tensor-core axes are returned in N, M, K order.
  for i, count in ((1, tile_m), (0, tile_n)):
    if count == 1:
      continue
    schedule.apply_opt(Opt(OptOps.SPLIT, schedule.rngs.index(ranges[i]), (count, AxisType.UPCAST)))
  for axis,count in zip(axes,(local_m,local_n),strict=True):
    if count==1:
      continue
    rng=next(r for r in schedule.rngs if r.axis_type is AxisType.GLOBAL and r.axis_id==axis)
    if (rng.vmax+1)%count:
      schedule.apply_opt(Opt(OptOps.PADTO,schedule.rngs.index(rng),count))
      rng=next(r for r in schedule.rngs if r.axis_type is AxisType.GLOBAL and r.axis_id==axis)
    schedule.apply_opt(Opt(OptOps.SPLIT,schedule.rngs.index(rng),(count,AxisType.LOCAL)))
  if unroll_k>1:
    rng=next(r for r in schedule.reduce_ranges if r.axis_type is AxisType.WEAK)
    schedule.apply_opt(Opt(OptOps.SPLIT,schedule.rngs.index(rng),(unroll_k,AxisType.UPCAST)))
  if swap:
    globals_=schedule.axes_of(AxisType.GLOBAL)
    assert len(globals_)==2
    schedule.apply_opt(Opt(OptOps.SWAP,globals_[0],globals_[1]))
  name=f'alpamayo_fp8_gemm_{tile_m}_{tile_n}'+('_residual' if residual else '')
  if (local_m,local_n,swap)!=(1,1,False):
    name+=f'_{local_m}_{local_n}_{int(swap)}'
  if unroll_k!=1:
    name+=f'_k{unroll_k}'
  if group_m!=1:
    name+=f'_order{group_m}'
  ast=schedule.get_optimized_ast(name_override=name)
  if group_m>1:
    assert (local_m,local_n,swap,unroll_k)==(1,1,False,1)
    gm,gn=[next(r for r in schedule.rngs if r.axis_type is AxisType.GLOBAL and r.axis_id==axis) for axis in axes]
    nm,nn=int(gm.vmax+1),int(gn.vmax+1)
    linear=gm+gn*nm
    start=(linear//(group_m*nn))*group_m
    left=nm-start
    count=(left<group_m).where(left,group_m)
    within=linear%(group_m*nn)
    mapping={gm:start+within%count,gn:within//count}
    # Change only memory addresses. Keep the global iteration bounds and every
    # WMMA/reduction instruction in its original order.
    ast=ast.substitute({u:u.substitute(mapping,walk=True) for u in ast.toposort() if u.op is Ops.INDEX},walk=True)
  return ast


def gemm(x, weight, scales, tile=(4, 4), row_scale=False, bias=None, column_scale=False, local=(1,1), swap=False, unroll_k=1, group_m=1,
         residual=None):
  out = Tensor.empty(x.shape[0], weight.shape[0], device=x.device, dtype=dtypes.bfloat16)
  extra = (() if bias is None else (bias,))+(() if residual is None else (residual.reshape(out.shape),))
  return Tensor.custom_kernel(out, pack(x), pack(weight), *scales, *extra,
                              fxn=partial(kernel, tile_m=tile[0], tile_n=tile[1], row_scale=row_scale, column_scale=column_scale,
                                           local_m=local[0],local_n=local[1],swap=swap,unroll_k=unroll_k,group_m=group_m,
                                           **({} if residual is None else {'residual':True})))[0]
