"""Group-32 W4 weights for the two single-token language projections on gfx1200."""
from functools import partial
from tinygrad import Tensor, dtypes
from tinygrad.uop.ops import KernelInfo, UOp
from ..frozen import program


def _words(n, k):
  # Eight offset-binary nibbles per word, followed by two FP16 group scales per word.
  return n*k//8 + n*k//64


def _program(out, *inputs, kind, n, k):
  # Declare every buffer read by the frozen object and its exact dispatch geometry.
  dep = sum((x.flatten()[0].load().float() for x in inputs[1:]), inputs[0].flatten()[0].load().float())
  groups = n*k//(64*128) if kind == 'pack' else n//4
  symbol = 'projection_w4_'+kind
  sink = UOp.sink(out.flatten()[0].store(dep.cast(out.dtype)), UOp.special(groups,'gidx0'), UOp.special(128,'lidx0'), arg=KernelInfo(name=symbol))
  return program(sink,symbol,(n,k))


def pack_weights(model):
  result = {}
  for layer in range(28):
    for fc,n,k in (('fc1',9216,2048),('fc2',2048,9216)):
      name = f'vlm.model.language_model.layers.{layer}.mlp.{fc}'
      w = model.packed_weights[name]  # Same packed 16x16 FP8 tiles used by prefill.
      scale = model.weight_scales[name+'.weight']
      if (w.shape != (n,k) or w.dtype != dtypes.fp8e4m3 or model.weights[name+'.weight'].shape != (n,k)
          or scale.dtype != dtypes.float32 or scale.numel() != 1 or scale.device != w.device or name+'.bias' in model.weights):
        raise ValueError(f'Unsupported W4 projection: {name}')
      out = Tensor.empty(_words(n,k),device=w.device,dtype=dtypes.uint32)
      result[name] = Tensor.custom_kernel(out,w,fxn=partial(_program,kind='pack',n=n,k=k))[0]
  Tensor.realize(*result.values())
  model.synchronize()
  return result


def gemv(q, packed, x_scale, w_scale, shape):
  n,k = shape
  assert shape in ((9216,2048),(2048,9216)) and q.shape == (1,k) and q.dtype == dtypes.fp8e4m3
  assert packed.shape == (_words(n,k),) and packed.dtype == dtypes.uint32
  assert x_scale.dtype == w_scale.dtype == dtypes.float32 and x_scale.numel() == w_scale.numel() == 1
  assert q.device == packed.device == x_scale.device == w_scale.device
  out = Tensor.empty(n,device=q.device,dtype=dtypes.bfloat16)
  # FP16 exactly represents every finite E4M3 activation. Keep the weight matrix packed.
  y = Tensor.custom_kernel(out,q.cast(dtypes.float16).contiguous(),packed,x_scale,w_scale,fxn=partial(_program,kind='gemv',n=n,k=k))[0]
  return y.reshape(1,1,n)
