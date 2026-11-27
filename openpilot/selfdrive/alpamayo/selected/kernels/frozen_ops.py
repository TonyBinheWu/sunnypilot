"""PROGRAM adapters for the exact selected HIP objects."""
from functools import partial
from tinygrad import Tensor, dtypes
from tinygrad.uop.ops import KernelInfo, UOp
from ..frozen import program as frozen_program


def maximum_program(out, x, final, images=1):
  sink = UOp.sink(out.flatten()[0].store(x.flatten()[0].load().float()),
                 UOp.special(out.numel(), 'gidx0'), UOp.special(256, 'lidx0'), arg=KernelInfo(name='alpamayo_absmax'))
  return frozen_program(sink, 'absmax', (x.numel()//images, x.dtype == dtypes.bfloat16, final))


def maximum(x, images=1):
  assert x.dtype == dtypes.bfloat16 and x.numel() > 0 and images > 0 and x.numel()%images == 0
  values = x.contiguous().realize()
  partial_max = Tensor.empty((images*((x.numel()//images+4095)//4096),), device=x.device, dtype=dtypes.float32)
  partial_max = Tensor.custom_kernel(partial_max, values, fxn=partial(maximum_program, final=False, images=images))[0].realize()
  result = Tensor.empty(() if images == 1 else (images,1,1), device=x.device, dtype=dtypes.float32)
  return Tensor.custom_kernel(result, partial_max, fxn=partial(maximum_program, final=True, images=images))[0].realize()


def quantize(x):
  scale = (maximum(x)/448).clamp(min_=1e-12).realize()
  return (x.float()/scale).clamp(-448,448).cast(dtypes.fp8e4m3).reshape(-1,x.shape[-1]).contiguous(), scale


def grouped_quantize(x, images):
  # The maximum is order-free, so a fused reduction gives the same scale as the frozen absmax objects.
  # x stays lazy: producers such as GELU are recomputed in the reduction and in the packing quantizer
  # instead of being stored, and the quantizer writes the packed layout directly.
  assert images > 0 and x.numel() % (images*x.shape[-1]) == 0
  grouped = x.reshape(images,-1,x.shape[-1])
  scale = (grouped.float().abs().max(axis=(1,2),keepdim=True)/448).clamp(min_=1e-12).realize()
  quantized = (grouped.float()/scale).clamp(-448,448).cast(dtypes.fp8e4m3).reshape(-1,x.shape[-1])
  return quantized, scale.reshape(images,1).expand(images,grouped.shape[1]).reshape(-1).contiguous()


def norm_program(out, x, weight, bias, rms, eps):
  value = x.flatten()[0].load().float()+weight[0].load().float()+bias[0].load().float()
  sink = UOp.sink(out.flatten()[0].store(value.cast(out.dtype)),
                 UOp.special(x.numel()//x.shape[-1], 'gidx0'), UOp.special(256,'lidx0'), arg=KernelInfo(name='alpamayo_norm'))
  return frozen_program(sink, 'norm', (x.shape[-1],rms,eps))


def norm(x, weight, bias=None, rms=False, eps=1e-5):
  assert x.dtype == weight.dtype == dtypes.bfloat16
  out = Tensor.empty(x.shape, device=x.device, dtype=x.dtype)
  return Tensor.custom_kernel(out, x.contiguous().realize(), weight.contiguous().realize(),
                             (weight if bias is None else bias).contiguous().realize(),
                             fxn=partial(norm_program,rms=rms,eps=eps))[0].realize()


def norm_fp8_program(out, x, weight, scale):
  dependency = x.flatten()[0].load().float()+weight.flatten()[0].load().float()+scale.flatten()[0].load()
  sink = UOp.sink(out.flatten()[0].store(dependency.cast(dtypes.fp8e4m3)),
                 UOp.special(x.numel()//x.shape[-1], 'gidx0'), UOp.special(256, 'lidx0'), arg=KernelInfo(name='alpamayo_norm_fp8'))
  return frozen_program(sink, 'norm_fp8', (x.shape[-1], 1e-5))


def norm_quantize(x, weight, scale):
  """Prefill RMS norm (same arithmetic as norm) quantized with a fixed scale and written in amd_gemm.pack layout.

  The BF16 normalized value is rounded exactly as norm stores it; it is never stored itself.
  """
  assert x.dtype == weight.dtype == dtypes.bfloat16 and x.shape[-1] == 2048 and scale.dtype == dtypes.float32 and scale.numel() == 1
  rows = x.numel()//x.shape[-1]
  assert rows % 16 == 0
  out = Tensor.empty(rows, x.shape[-1], device=x.device, dtype=dtypes.fp8e4m3)
  return Tensor.custom_kernel(out, x.contiguous().realize(), weight.contiguous().realize(), scale, fxn=norm_fp8_program)[0]


def attention_program(out, q, k, v, *, shape):
  batch,heads,rows,width = shape
  keys,kv_heads = k.shape[2],k.shape[1]
  dependency = q.flatten()[0].load()+k.flatten()[0].load()+v.flatten()[0].load()
  dependency = dependency+0  # Preserve the original unmasked PROGRAM dependency expression.
  sink = UOp.sink(out.flatten()[0].store(dependency),
                 UOp.special(batch*heads*((rows+127)//128), 'gidx0'), UOp.special(256, 'lidx0'), arg=KernelInfo(name='alpamayo_online'))
  return frozen_program(sink, 'vision_attention', (heads,kv_heads,rows,keys,width))


def attention(q, k, v):
  """Vision encoder attention (non-causal, 72-wide heads)."""
  assert q.dtype == k.dtype == v.dtype == dtypes.bfloat16
  assert q.shape[-1] == k.shape[-1] == v.shape[-1] == 72
  assert q.shape[0] == k.shape[0] == v.shape[0] and k.shape == v.shape
  out = Tensor.empty(q.shape, device=q.device, dtype=q.dtype)
  return Tensor.custom_kernel(out,q.contiguous(),k.contiguous(),v.contiguous(),fxn=partial(attention_program,shape=q.shape))[0]


PREFILL_ATTENTION = (16, 8, 2304, 128)  # query heads, KV heads, cache rows, width
PREFILL_ATTENTION_PARTS = {(576, 0), (192, 576), (1344, 768)}  # (query rows, first query row)


def prefill_attention_program(out, q, kv, *, rows, offset):
  heads,kv_heads,capacity,width = PREFILL_ATTENTION
  dependency = q.flatten()[0].load()+kv.flatten()[0].load()
  sink = UOp.sink(out.flatten()[0].store(dependency), UOp.special(rows//16*kv_heads, 'gidx0'), UOp.special(64, 'lidx0'),
                  arg=KernelInfo(name='agent_prefill_cache_attention'))
  args = (heads,kv_heads,rows,capacity,width) + ((offset,) if offset else ())
  return frozen_program(sink, 'prefill_cache_attention', args)


def prefill_attention(q, kv, offset=0):
  """Causal prefill attention for query rows offset..offset+rows, reading K and V straight from the (2,1,8,2304,128) KV cache.

  Each 64-thread workgroup holds the two query heads of one KV head for one 16-row tile; V loads use the gfx12
  transposing load. The online softmax keeps the original per-row 32-key block order and rounding, so a split
  prefill gives the same bits as the full one.
  """
  heads,kv_heads,capacity,width = PREFILL_ATTENTION
  rows = q.shape[2]
  assert (rows,offset) in PREFILL_ATTENTION_PARTS
  assert q.shape == (1,heads,rows,width) and kv.shape == (2,1,kv_heads,capacity,width)
  assert q.dtype == kv.dtype == dtypes.bfloat16
  out = Tensor.empty(q.shape, device=q.device, dtype=q.dtype)
  return Tensor.custom_kernel(out,q.contiguous(),kv,fxn=partial(prefill_attention_program,rows=rows,offset=offset))[0]


def mlp_program(out, x, weight, xs, ws, output_scale, *, rows):
  columns,width = out.shape[-1],weight.shape[-1]
  dependency = x.flatten()[0].load().float()+weight.flatten()[0].load().float()+xs.flatten()[0].load()+ws.flatten()[0].load()+output_scale.flatten()[0].load()
  # Four waves share each workgroup. Each wave computes one 64 by 64 tile.
  sink = UOp.sink(out.flatten()[0].store(dependency.cast(dtypes.fp8e4m3)),
                 UOp.special(-(-(rows//64)//4)*(columns//64),'gidx0'), UOp.special(128,'lidx0'),
                 arg=KernelInfo(name='agent_packed_epilogue'))
  return frozen_program(sink,'mlp',(rows,columns,width))


def fused_mlp(x, weight, xs, ws, output_scale, rows):
  assert x.dtype == weight.dtype == dtypes.fp8e4m3 and x.shape[-1] == weight.shape[-1]
  assert xs.dtype == ws.dtype == output_scale.dtype == dtypes.float32
  assert xs.numel() == ws.numel() == output_scale.numel() == 1
  out = Tensor.empty((rows+15)//16*16,weight.shape[0],device=x.device,dtype=dtypes.fp8e4m3)
  return Tensor.custom_kernel(out,x,weight,xs,ws,output_scale,fxn=partial(mlp_program,rows=rows))[0]


def hip_program(kind, args, name, grid, local, outputs):
  """PROGRAM for a frozen multi-output HIP object; every output gets a declared store."""
  def program(*buffers):
    dependency = sum(b.flatten()[0].load().float() for i,b in enumerate(buffers) if i not in outputs)
    stores = [buffers[i].flatten()[0].store(dependency.cast(getattr(buffers[i].dtype,'base',buffers[i].dtype))) for i in outputs]
    sink = UOp.sink(*stores, UOp.special(grid,'gidx0'), UOp.special(local,'lidx0'), arg=KernelInfo(name=name))
    return frozen_program(sink, kind, args)
  return program


def hip_call(buffers, outputs, *, kind, args, name, grid, local):
  """buffers in the kernel's argument order; outputs are the written positions."""
  results = Tensor.custom_kernel(*buffers, fxn=hip_program(kind, args, name, grid, local, outputs))
  results = tuple(results[i] for i in outputs)
  Tensor.realize(*results)  # one launch writes every output
  return results


# Two-image (1440-row) FP8 vision layer objects. Inputs use amd_gemm.pack / vision_tiles.pack_images layouts.
PAIR_ROWS, VISION_WIDTH, VISION_MLP = 1440, 1152, 4304


def vision_norm_max(x, weight, bias):
  """alpamayo_norm LayerNorm (eps 1e-6) with one wave per row, plus each row's |output| maximum."""
  assert x.shape == (2,720,VISION_WIDTH) and x.dtype == weight.dtype == bias.dtype == dtypes.bfloat16
  out = Tensor.empty(x.shape, device=x.device, dtype=x.dtype)
  partial = Tensor.empty(PAIR_ROWS, device=x.device, dtype=dtypes.float32)
  return hip_call((out, x.contiguous(), weight, bias, partial), (0, 4), kind='vision_norm_max', args=(PAIR_ROWS, VISION_WIDTH, 1e-6),
                  name='alpamayo_norm_fast', grid=360, local=128)


def vision_qkv(packed_x, weight, scales, bias, row_scales):
  """Merged Q/K/V projection writing (2,16,720,72) heads directly; per-projection weight scales."""
  outs = tuple(Tensor.empty(2,16,720,72, device=packed_x.device, dtype=dtypes.bfloat16) for _ in range(3))
  return hip_call((*outs, packed_x, weight, row_scales, scales, bias), (0, 1, 2), kind='vision_qkv', args=(PAIR_ROWS, 3*VISION_WIDTH, VISION_WIDTH),
                  name='qkv_k', grid=1620, local=32)


def vision_attention_max(q, k, v):
  """The vision online attention with each wave's |output| maximum (2*16*6*8 partials)."""
  assert q.shape == k.shape == v.shape == (2,16,720,72)
  out = Tensor.empty(q.shape, device=q.device, dtype=q.dtype)
  partial = Tensor.empty(2*16*6*8, device=q.device, dtype=dtypes.float32)
  return hip_call((out, q, k, v, partial), (0, 4), kind='vision_attention_max', args=(16,16,720,720,72),
                  name='alpamayo_online', grid=192, local=256)


def vision_gemm(packed_x, weight, row_scales, scale, bias, residual=None, *, kind, name, columns, width, grid, local):
  out = Tensor.empty(2,720,columns, device=packed_x.device, dtype=dtypes.bfloat16)
  buffers = (out, packed_x, weight, row_scales, scale, bias)+(() if residual is None else (residual.contiguous(),))
  return hip_call(buffers, (0,), kind=kind, args=(PAIR_ROWS, columns, width), name=name, grid=grid, local=local)[0]


def vision_fc1_gelu(packed_x, weight, row_scales, scale, bias):
  """FC1 followed by the original GELU (BF16 in and out), plus 1350 per-tile |GELU| maxima as float bits."""
  out = Tensor.empty(2,720,VISION_MLP, device=packed_x.device, dtype=dtypes.bfloat16)
  partial = Tensor.empty(1350, device=packed_x.device, dtype=dtypes.uint32)
  return hip_call((out, packed_x, weight, row_scales, scale, bias, partial), (0, 6), kind='vision_fc1_gelu_max',
                  args=(PAIR_ROWS, VISION_MLP, VISION_WIDTH), name='fc1_k', grid=675, local=64)


def vision_partial_max(partial):
  out = Tensor.empty(2, device=partial.device, dtype=dtypes.uint32)
  return hip_call((out, partial), (0,), kind='vision_partial_max', args=(675,), name='partial_max', grid=2, local=256)[0]


PROJECTOR = {'vlm.model.projector.linear_fc1': (11520, 4608, 1440), 'vlm.model.projector.linear_fc2': (2048, 11520, 176)}


def projector_gemm(name, packed_x, weight, row_scales, scale, bias):
  """Two-image (360-row) projector GEMM with per-row scales."""
  columns, width, grid = PROJECTOR[name]
  out = Tensor.empty(360, columns, device=packed_x.device, dtype=dtypes.bfloat16)
  return hip_call((out, packed_x, weight, row_scales, scale, bias), (0,), kind='projector_gemm', args=(360, columns, width),
                  name='pj_k', grid=grid, local=32)[0]


def expert_attention(q, k_new, v_new, cache, mask):
  """Diffusion expert attention in one launch: BF16 scores, FP32 key mask, softmax and PV with the original rounding.

  Keys are the 2304 prompt rows read directly from the layer's KV cache, then the 64 new action rows.
  The kernel stages probabilities in a scratch buffer that it writes.
  """
  assert q.shape == (1,16,64,128) and k_new.shape == v_new.shape == (1,8,64,128) and cache.shape == (2,1,8,2304,128)
  assert q.dtype == k_new.dtype == v_new.dtype == cache.dtype == dtypes.bfloat16 and mask.shape == (2368,) and mask.dtype == dtypes.float32
  out = Tensor.empty(q.shape, device=q.device, dtype=q.dtype)
  scratch = Tensor.empty(64*148*32*8, device=q.device, dtype=dtypes.uint16)
  return hip_call((out, q.contiguous(), k_new.contiguous(), v_new.contiguous(), cache, mask, scratch), (0, 6),
                  kind='expert_attention', args=(16,8,64,2304,128), name='alpamayo_expert_attention', grid=64, local=256)[0]
