"""Selected mixed-precision specialization of the shared BF16 core."""
from contextlib import contextmanager
from functools import partial
import json
import math
from pathlib import Path
from tinygrad import Device, Tensor, TinyJit, dtypes
from tinygrad.helpers import USE_TC, TC_OPT, round_up
from tinygrad.renderer.llvmir import AMDLLVMRenderer
from tinygrad.uop.ops import UOp
from openpilot.selfdrive.alpamayo.model import EdgeModel
from openpilot.selfdrive.alpamayo.amd_attention import _pack, _matmul, _softmax

PREFILL_ROWS = 2112  # Padded prompt rows: 2025 base tokens, compact navigation text and the 31-token verified draft (33 x 64).
# The prefill runs in parts that start at these rows; each part writes its own KV rows and attends to the earlier ones.
# Rows 0-575 hold the system prompt and the three older front images; rows 576-767 continue with the -0.1 s front image.
# Neither depends on the current exposures, so both can run before the current images arrive.
PREFILL_SPLITS = (0,576,768)
PREFILL_PARTS = {(end-start,start) for start,end in zip(PREFILL_SPLITS,(*PREFILL_SPLITS[1:],PREFILL_ROWS))}  # (rows, first row)
from . import amd_gemm, amd_decode, weights
EXPERT_LAYERS = 28
DIFFUSION_STEPS = range(1,11)  # NVIDIA uses 10 Euler steps (5 on its car)
from .serial_attention import direct as serial_cache_attention
from .kernels import bf16_linear, frozen_ops, serial_mlp, tiled_gemm, vision_tiles


class PackedActivation:
  def __init__(self, value, rows, width):
    self.value,self.rows,self.width = value,rows,width


class SelectedModel(EdgeModel):
  def __init__(self, checkpoint, fp8_cache, fixed_scales):
    # Initialize shared state without loading the full BF16 weights first.
    self.config = json.loads((Path(checkpoint)/'config.json').read_text())
    self.weights,self.weight_scales = {},{}
    self.dtype,self.amd = dtypes.bfloat16,True
    self.cache = self.prompt_length = self.greedy_shape = None
    self.encode_jits,self.trajectory_jits = {},{}
    self.prefill_jit = TinyJit(self._language)
    self.decode_jit = TinyJit(self._greedy_decode)
    self.images,self.verifying,self.trajectory_active = 0,False,False
    self.prefill_prefix,self.quantizer_slot = None,0
    self.trace_counts = {'expert_attention':0,'fused_mlp':0}
    import time
    marks = [('start',time.monotonic())]
    def mark(name):
      Device[Device.DEFAULT].synchronize(); marks.append((name,time.monotonic()))
    self.weight_digest = weights.load_bulk(self,checkpoint,fp8_cache)
    mark('bulk')
    self.restored = weights.restore_bf16(self,checkpoint)
    mark('restore_bf16')
    self.bf16_weights = {name[:-7]:bf16_linear.pack_weight(value) for name,value in self.weights.items()
                        if name.startswith(('vlm.model.visual.embeddings.','vlm.model.visual.encoder.layers.'))
                        and name.endswith('.weight') and value.ndim == 2 and value.dtype == dtypes.bfloat16}
    mark('bf16_pack')
    self.vocabulary_size = weights.reduce_head(self)
    mark('reduce_head')
    # One schedule for all packs: per-tensor realizes cost ~20 ms of host scheduling each on the Dragon.
    expert = {name:amd_gemm.pack(value) for name,value in self.weights.items()
              if name.startswith('expert.') and value.dtype == dtypes.fp8e4m3}
    self.packed_weights = {name[:-7]:amd_gemm.pack(value) for name,value in self.weights.items()
                           if name.startswith('vlm.model.language_model.layers.') and name.endswith('.weight')
                           and ('.mlp.' in name or '.self_attn.' in name) and value.dtype == dtypes.fp8e4m3}
    Tensor.realize(*expert.values(),*self.packed_weights.values())
    self.expert_weights = set()
    for name,packed in expert.items():
      self.weights[name] = amd_gemm.unpack(packed)
      self.expert_weights.add(name.removesuffix('.weight'))
    mark('expert_and_language_pack')
    expected = {f'vlm.model.language_model.layers.{i}/{j}' for i in range(28) for j in range(4)}
    if set(fixed_scales) != expected or not all(math.isfinite(v) and v > 0 for v in fixed_scales.values()):
      raise ValueError('Require all 112 positive finite fixed language scales')
    if self.config['vlm_config']['text_config']['num_hidden_layers'] != 28:
      raise ValueError('Unsupported selected model depth')
    # One upload for the 112 fixed scales; each scale is an independent 4-byte view of it.
    keys = sorted(fixed_scales)
    scales = Tensor([float(fixed_scales[k]) for k in keys],dtype=dtypes.float32).realize()
    base = scales.uop.base.buffer
    self.fixed = {key:Tensor(UOp.from_buffer(base.view(4,4*i,).ensure_allocated(),dtypes.float32)).reshape(())
                  for i,key in enumerate(keys)}
    self._fixed_storage = scales
    projector = {name:amd_gemm.pack(self.weights[name+'.weight']) for name in ('vlm.model.projector.linear_fc1','vlm.model.projector.linear_fc2')}
    Tensor.realize(*projector.values())
    self.projector_weights = {name:amd_gemm.unpack(packed) for name,packed in projector.items()}
    mark('projector')
    self.w4_weights = serial_mlp.pack_weights(self)
    mark('w4_pack')
    self.vision_qkv = self.merge_vision_qkv()
    mark('vision_qkv')
    self.load_ms = {b[0]:round((b[1]-a[1])*1e3) for a,b in zip(marks,marks[1:])}

  def merge_vision_qkv(self):
    # Packed Q/K/V matrices, scales and biases of the FP8 vision layers side by side for the merged pair projection.
    merged = {}
    for i in range(2,self.config['vlm_config']['vision_config']['num_hidden_layers']):
      prefix = f'vlm.model.visual.encoder.layers.{i}.self_attn'
      names = [f'{prefix}.{n}_proj' for n in 'qkv']
      merged[f'{prefix}.qkv.matrix'] = Tensor.cat(*[amd_gemm.pack(self.weights[n+'.weight']) for n in names]).contiguous()
      merged[f'{prefix}.qkv.scale'] = Tensor.cat(*[self.weight_scales[n+'.weight'].reshape(1) for n in names]).contiguous()
      merged[f'{prefix}.qkv.bias'] = Tensor.cat(*[self.weights[n+'.bias'] for n in names]).contiguous()
    Tensor.realize(*merged.values())
    return merged

  def reset(self):
    self.cache = self.prompt_length = self.greedy_shape = None
    self.encode_jits.clear()
    self.trajectory_jits.clear()
    self.prefill_jit.reset()
    self.decode_jit.reset()
    self.images,self.verifying,self.trajectory_active = 0,False,False
    self.prefill_prefix,self.quantizer_slot = None,0

  @contextmanager
  def verification(self):
    if self.verifying or self.trajectory_active or self.images:
      raise RuntimeError('Nested verification is unsupported')
    self.verifying = True
    try:
      yield
    finally:
      self.verifying = False

  def quantize(self, x):
    if self.verifying:
      value = x.reshape(-1,x.shape[-1]).float()
      scale = (value.abs().max(axis=1,keepdim=True)/448).clamp(min_=1e-12)
      return (value/scale).clamp(-448,448).cast(dtypes.fp8e4m3).contiguous(),scale
    if self.images:
      return frozen_ops.grouped_quantize(x,self.images)
    rows,width = x.numel()//x.shape[-1],x.shape[-1]
    if self.prefill_prefix is not None and x.dtype == dtypes.bfloat16 and rows >= 128:
      scale = self.fixed[f'{self.prefill_prefix}/{self.quantizer_slot}']
      self.quantizer_slot += 1
      value = (x.float()/scale).clamp(-448,448).cast(dtypes.fp8e4m3).reshape(-1,width)
      return PackedActivation(amd_gemm.pack(value).realize(),rows,width),scale
    if x.dtype == dtypes.bfloat16 and x.numel() >= 131072:
      return frozen_ops.quantize(x)
    scale = (x.float().abs().max()/448).clamp(min_=1e-12)
    return (x.float()/scale).clamp(-448,448).cast(dtypes.fp8e4m3).reshape(-1,x.shape[-1]).contiguous(),scale

  def norm_quantize(self, x, name):
    # Prefill: RMS norm straight to packed FP8 with the layer's next fixed scale. The BF16 norm output is never stored.
    assert self.prefill_prefix is not None and x.shape[0] == 1 and x.shape[2] == 2048
    assert any(x.shape[1] == rows for rows,_ in PREFILL_PARTS)
    scale = self.fixed[f'{self.prefill_prefix}/{self.quantizer_slot}']
    self.quantizer_slot += 1
    packed = frozen_ops.norm_quantize(x,self.weights[name+'.weight'],scale).realize()
    return PackedActivation(packed,x.shape[1],2048),scale

  def packed_linear(self, packed, scale, name, shape):
    weight = self.weights[name+'.weight']
    bias = self.weights.get(name+'.bias')
    out = Tensor.empty(packed.rows,weight.shape[0],device=packed.value.device,dtype=dtypes.bfloat16)
    value = Tensor.custom_kernel(out,packed.value,self.packed_weights[name],scale,self.weight_scales[name+'.weight'],
                                *(() if bias is None else (bias,)),fxn=partial(amd_gemm._gemm,packed_input=True))[0]
    return value.reshape(*shape,weight.shape[0])

  def base_linear(self, x, name, quantized_input=None, heads=None):
    shape = x.shape[:-1]
    x = x.reshape(-1,x.shape[-1])
    single = x.numel() == x.shape[-1]
    weight,bias = self.weights[name+'.weight'],self.weights.get(name+'.bias')
    if (scale := self.weight_scales.get(name+'.weight')) is not None:
      quantized,x_scale = self.quantize(x) if quantized_input is None else quantized_input
      if single and weight.shape[1]%128 == 0 and isinstance(Device[x.device].renderer,AMDLLVMRenderer):
        packed = name.startswith('vlm.') and ('.mlp.' in name or '.self_attn.' in name)
        return amd_decode.gemv(quantized,weight,(x_scale,scale),bias,packed=packed,dtype=x.dtype).reshape(*shape,weight.shape[0])
      if not single and USE_TC.value == 1 and (x.shape[0]%16 == 0 or TC_OPT >= 2):
        if x.shape[0] >= 128 and name.startswith('vlm.') and ('.mlp.' in name or '.self_attn.' in name):
          return amd_gemm.gemm(quantized,weight,(x_scale,scale),bias,dtype=x.dtype).reshape(*shape,weight.shape[0])
        y = quantized.dot(weight.T,dtype=dtypes.float32)
      else:
        y = quantized.float().dot(weight.float().T)
      y = y*(x_scale*scale)
      if bias is not None:
        y = y+bias.float()
      return y.cast(x.dtype).reshape(*shape,weight.shape[0])
    return super().linear(x,name).reshape(*shape,weight.shape[0])

  def linear(self, x, name, quantized_input=None, heads=None, residual=None):
    shape = x.shape[:-1]
    weight,bias = self.weights[name+'.weight'],self.weights.get(name+'.bias')
    scale = self.weight_scales.get(name+'.weight')
    if self.verifying and scale is not None:
      quantized,x_scale = self.quantize(x) if quantized_input is None else quantized_input
      return tiled_gemm.gemm(quantized,weight,(x_scale,scale),tile=(1,4),row_scale=True,bias=bias).reshape(*shape,-1)
    match = vision_tiles.NAME.fullmatch(name)
    if (match is not None and int(match[1]) >= 2 and x.ndim == 3 and x.shape[0] in (1,2) and x.shape[1] == 720
        and x.dtype == dtypes.bfloat16 and heads is None and scale is not None and weight.dtype == dtypes.fp8e4m3):
      fc,images = match[2],x.shape[0]
      assert (x.shape[1],weight.shape[0],x.shape[-1]) == vision_tiles.SHAPES[fc]
      assert bias is not None and bias.dtype == dtypes.bfloat16
      quantized,x_scale = self.quantize(x) if quantized_input is None else quantized_input
      return vision_tiles.gemm(quantized.reshape(images,720,x.shape[-1]),weight,(x_scale,scale),bias,vision_tiles.TILES[fc],
                               residual=residual).reshape(*shape,weight.shape[0])
    if residual is not None:
      # Only FP8 vision projections add the residual in their epilogue.
      assert self.images and scale is not None and name.endswith('.self_attn.out_proj') and x.dtype == residual.dtype == dtypes.bfloat16
      quantized,x_scale = self.quantize(x) if quantized_input is None else quantized_input
      return tiled_gemm.gemm(quantized,weight,(x_scale,scale),tile=(3,3),row_scale=True,bias=bias,residual=residual).reshape(*shape,weight.shape[0])
    if self.images and scale is not None:
      if name.startswith(('vlm.model.visual.embeddings.','vlm.model.projector.')):
        count = self.images
        grouped = x.reshape(count,-1,x.shape[-1])
        self.images = 0
        try:
          parts = [self.linear(grouped[i:i+1],name,heads=heads).realize() for i in range(count)]
          return Tensor.cat(*parts,dim=0).reshape(*shape,parts[0].shape[-1])
        finally:
          self.images = count
      quantized,x_scale = self.quantize(x) if quantized_input is None else quantized_input
      # 3x3 output tiles are 12% faster than 4x4 for the 1440-row projections; reduction order is unchanged.
      tile = (3,3) if (x.numel()//x.shape[-1]) % 48 == 0 and weight.shape[0] % 48 == 0 else (4,4)
      return tiled_gemm.gemm(quantized,weight,(x_scale,scale),tile=tile,row_scale=True,bias=bias).reshape(*shape,weight.shape[0])
    rows = x.numel()//x.shape[-1]
    if (name in self.w4_weights and x.shape == (1,1,weight.shape[1]) and x.dtype == dtypes.bfloat16 and heads is None
        and not (self.images or self.verifying or self.trajectory_active) and self.prefill_prefix is None):
      q,x_scale = self.quantize(x.reshape(1,-1)) if quantized_input is None else quantized_input
      return serial_mlp.gemv(q,self.w4_weights[name],x_scale,scale,weight.shape)
    if self.prefill_prefix is not None and name in self.packed_weights and rows >= 128:
      packed,x_scale = self.quantize(x) if quantized_input is None else quantized_input
      assert isinstance(packed,PackedActivation) and (packed.rows,packed.width) == (rows,x.shape[-1])
      return self.packed_linear(packed,x_scale,name,shape)
    if name in self.expert_weights and rows == 64:
      quantized,x_scale = self.quantize(x) if quantized_input is None else quantized_input
      # 64 rows give a 64x64 tile too few waves to stream the weights. Smaller output tiles keep each output's
      # reduction order (bit-identical) and take 36 instead of 79 us per expert layer.
      assert x.dtype == dtypes.bfloat16
      tile = (1,2) if weight.shape[0] <= 512 else (2,2)
      return tiled_gemm.gemm(quantized,weight,(x_scale,scale),tile=tile,bias=bias).reshape(*shape,weight.shape[0])
    if name in self.bf16_weights and rows >= 128:
      assert quantized_input is None and x.dtype == dtypes.bfloat16
      if x.ndim == 3 and x.shape[0] > 1 and x.shape[1]%16 and weight.shape[0]%64:
        parts = [bf16_linear.linear(x[i],self.bf16_weights[name],weight.shape[0],bias).unsqueeze(0) for i in range(x.shape[0])]
        return parts[0].cat(*parts[1:],dim=0)
      return bf16_linear.linear(x.reshape(-1,x.shape[-1]),self.bf16_weights[name],weight.shape[0],bias).reshape(*shape,weight.shape[0])
    return self.base_linear(x,name,quantized_input,heads)

  def norm(self, x, name, rms=False, eps=None):
    if x.dtype != dtypes.bfloat16 or x.numel()//x.shape[-1] < 64:
      return super().norm(x,name,rms,eps)
    return frozen_ops.norm(x,self.weights[name+'.weight'],None if rms else self.weights[name+'.bias'],
                           rms,eps if eps is not None else 1e-5 if rms else 1e-6)

  def masked_attention(self, q, k, v, mask):
    batch,heads,queries,width = q.shape
    kv_heads,keys = k.shape[1:3]
    assert queries in (16,32,48,64) and mask.shape in ((keys,),(queries,keys))
    packed_k = _pack(k)
    scores = Tensor.empty(batch,heads,queries,keys,device=q.device,dtype=q.dtype)
    scores = Tensor.custom_kernel(scores,_pack(q),packed_k,fxn=partial(_matmul,shape=(batch,heads,kv_heads,queries,keys,width),scaled=True,
                                                                       tile=(queries//16,2)))[0]
    scores = (scores.float()+mask).cast(q.dtype).contiguous()
    probs = Tensor.empty(batch,heads,round_up(queries,16),round_up(keys,16),device=q.device,dtype=q.dtype)
    probs = Tensor.custom_kernel(probs,scores,fxn=_softmax)[0]
    out = Tensor.empty(q.shape,device=q.device,dtype=q.dtype)
    packed_v = _pack(v.transpose(-2,-1))
    return Tensor.custom_kernel(out,probs,packed_v,fxn=partial(_matmul,shape=(batch,heads,kv_heads,queries,width,keys),tile=(queries//16,2)))[0]

  def attention(self, q, k, v, mask=None, causal=False):
    if self.verifying:
      return self.masked_attention(q,k,v,mask)
    if mask is None and q.shape[2] >= 128 and q.shape[-1] == 72 and not causal:
      return frozen_ops.attention(q,k,v)
    if q.dtype == dtypes.bfloat16 and q.shape[2] == 64 and mask is not None and mask.numel() == k.shape[2] and not causal:
      return self.masked_attention(q,k,v,mask)
    return super().attention(q,k,v,mask,causal)

  def vision_pair_layer(self, x, prefix):
    """FP8 vision layer for two images with fused frozen objects; same arithmetic as the general path.

    Norms, attention and FC1 also emit |output| maxima; each image's FP8 scale uses grouped_quantize's expressions.
    """
    def scales(maximum):
      scale = (maximum.reshape(2,1,1)/448).clamp(min_=1e-12).realize()
      return scale,scale.reshape(2,1).expand(2,720).reshape(-1).contiguous()
    def fp8(value, scale):
      return (value.reshape(2,-1,value.shape[-1]).float()/scale).clamp(-448,448).cast(dtypes.fp8e4m3).reshape(-1,value.shape[-1])
    def gemm_args(name):
      return amd_gemm.pack(self.weights[name+'.weight']),self.weight_scales[name+'.weight'],self.weights[name+'.bias']
    h,partial = frozen_ops.vision_norm_max(x,self.weights[prefix+'.layer_norm1.weight'],self.weights[prefix+'.layer_norm1.bias'])
    scale,rows = scales(partial.reshape(2,720).max(axis=1))
    q,k,v = frozen_ops.vision_qkv(amd_gemm.pack(fp8(h,scale)),*(self.vision_qkv[f'{prefix}.self_attn.qkv.{n}'] for n in ('matrix','scale','bias')),rows)
    h,partial = frozen_ops.vision_attention_max(q,k,v)
    scale,rows = scales(partial.reshape(2,-1).max(axis=1))
    w,ws,b = gemm_args(prefix+'.self_attn.out_proj')
    x = frozen_ops.vision_gemm(amd_gemm.pack(fp8(h.transpose(1,2).reshape(x.shape),scale)),w,rows,ws,b,x,kind='vision_o_residual',name='o_k',
                               columns=1152,width=1152,grid=540,local=32)
    h,partial = frozen_ops.vision_norm_max(x,self.weights[prefix+'.layer_norm2.weight'],self.weights[prefix+'.layer_norm2.bias'])
    scale,rows = scales(partial.reshape(2,720).max(axis=1))
    w,ws,b = gemm_args(prefix+'.mlp.fc1')
    g,partial = frozen_ops.vision_fc1_gelu(vision_tiles.pack_images(fp8(h,scale).reshape(2,720,1152)),w,rows,ws,b)
    scale,rows = scales(frozen_ops.vision_partial_max(partial).bitcast(dtypes.float32))
    w,ws,b = gemm_args(prefix+'.mlp.fc2')
    return frozen_ops.vision_gemm(vision_tiles.pack_images(fp8(g,scale).reshape(2,720,4304)),w,rows,ws,b,x,kind='vision_fc2_residual',name='fc2_k',
                                  columns=1152,width=4304,grid=360,local=32).realize()

  def vision_layer(self, x, i):
    prefix = f'vlm.model.visual.encoder.layers.{i}'
    if x.shape == (2,720,1152) and self.images == 2 and f'{prefix}.self_attn.q_proj.weight' in self.weight_scales:
      return self.vision_pair_layer(x,prefix)
    h = self.norm(x,f'{prefix}.layer_norm1')
    quantized = self.quantize(h) if f'{prefix}.self_attn.q_proj.weight' in self.weight_scales else None
    q,k,v = (self.linear(h,f'{prefix}.self_attn.{n}_proj',quantized,heads=16).reshape(*h.shape[:2],16,72).transpose(1,2) for n in ('q','k','v'))
    h = self.attention(q,k,v).transpose(1,2).reshape(x.shape)
    if quantized is None:
      x = x+self.linear(h,f'{prefix}.self_attn.out_proj')
      h = self.linear(self.norm(x,f'{prefix}.layer_norm2'),f'{prefix}.mlp.fc1').float().gelu().cast(self.dtype)
      return (x+self.linear(h,f'{prefix}.mlp.fc2')).realize()
    # FP8 layers add each residual in the projection epilogue, with the same BF16 rounding.
    x = self.linear(h,f'{prefix}.self_attn.out_proj',residual=x)
    h = self.linear(self.norm(x,f'{prefix}.layer_norm2'),f'{prefix}.mlp.fc1').float().gelu().cast(self.dtype)
    return self.linear(h,f'{prefix}.mlp.fc2',residual=x).realize()

  def text_layer(self, x, cos, sin, prefix, cache=None, mask=None, cache_pos=None):
    previous = self.prefill_prefix,self.quantizer_slot
    prefill = x.shape[1] >= 128
    self.prefill_prefix,self.quantizer_slot = (prefix if prefill else None),0
    try:
      if prefill:
        h,quantized = x,self.norm_quantize(x,f'{prefix}.input_layernorm')  # h only provides the row shape
      else:
        h = self.norm(x,f'{prefix}.input_layernorm',rms=True)
        quantized = self.quantize(h) if f'{prefix}.self_attn.q_proj.weight' in self.weight_scales else None
      q,k,v = (self.linear(h,f'{prefix}.self_attn.{n}_proj',quantized,heads=heads).reshape(1,h.shape[1],heads,128).transpose(1,2)
               for n,heads in (('q',16),('k',8),('v',8)))
      q,k = self.rope(q,k,cos,sin)
      if cache_pos is not None:
        store = cache[:,:,:,cache_pos:cache_pos+x.shape[1]].uop.store(Tensor.stack(k,v).uop)
        assigned = Tensor(cache.uop.after(store))
        end = cache.shape[3] if not isinstance(cache_pos,int) else cache_pos+x.shape[1]
        k,v = (assigned[i,:,:,:end] for i in range(2))
      elif cache is not None:
        assert not self.trajectory_active, 'The diffusion expert runs expert_block'
        k,v = (old.cat(new,dim=2) for old,new in zip(cache,(k,v),strict=True))
      causal = isinstance(cache_pos,int) and cache_pos == 0
      if (not self.verifying and not self.trajectory_active and cache_pos is not None and not isinstance(cache_pos,int)
          and q.shape == (1,16,1,128) and cache.shape == (2,1,8,2304,128) and mask is not None and mask.numel() == 2304):
        h = serial_cache_attention(q,assigned,mask)
      elif prefill and isinstance(cache_pos,int) and mask is None:
        assert (x.shape[1],cache_pos) in PREFILL_PARTS
        h = frozen_ops.prefill_attention(q,assigned,cache_pos)
      else:
        h = self.attention(q,k,v,mask,causal)
      h = h.transpose(1,2).reshape(1,x.shape[1],2048)
      if prefill:
        o_proj = f'{prefix}.self_attn.o_proj'
        assert o_proj+'.bias' not in self.weights and self.quantizer_slot == 1
        packed,scale = self.quantize(h)
        residual = x.reshape(x.shape[1],2048).contiguous()
        x = Tensor.custom_kernel(Tensor.empty(residual.shape,dtype=x.dtype,device=x.device),packed.value,self.packed_weights[o_proj],
                                 scale,self.weight_scales[o_proj+'.weight'],residual,fxn=amd_gemm.prefill_residual)[0].reshape(x.shape)
      else:
        x = x+self.linear(h,f'{prefix}.self_attn.o_proj')
      if prefill:
        rows = x.shape[1]
        assert type(cache_pos) is int and (rows,cache_pos) in PREFILL_PARTS
        fc1,fc2 = prefix+'.mlp.fc1',prefix+'.mlp.fc2'
        assert self.quantizer_slot == 2 and fc1+'.bias' not in self.weights and fc2+'.bias' not in self.weights
        packed,scale = self.norm_quantize(x,f'{prefix}.post_attention_layernorm')
        assert self.quantizer_slot == 3
        output_scale = self.fixed[prefix+'/3']
        output = frozen_ops.fused_mlp(packed.value,self.packed_weights[fc1],scale,self.weight_scales[fc1+'.weight'],output_scale,rows)
        # The fused kernel already performed original BF16/ReLU/square/slot-3 conversion.
        self.quantizer_slot += 1
        residual = x.reshape(rows,2048).contiguous()
        result = Tensor.custom_kernel(Tensor.empty(residual.shape,dtype=x.dtype,device=x.device),output,self.packed_weights[fc2],
                                      output_scale,self.weight_scales[fc2+'.weight'],residual,fxn=amd_gemm.prefill_residual)[0]
        self.trace_counts['fused_mlp'] += 1
        return result.reshape(x.shape).realize()
      else:
        h = self.norm(x,f'{prefix}.post_attention_layernorm',rms=True)
        raw = self.linear(h,f'{prefix}.mlp.fc1')
        quantized = amd_decode.quantize_relu_squared(raw) if not self.verifying and raw.shape == (1,1,9216) else None
        h = self.linear(raw.relu().square(),f'{prefix}.mlp.fc2',quantized_input=quantized)
      return (x+h).realize()
    finally:
      self.prefill_prefix,self.quantizer_slot = previous

  def _greedy_decode(self, logits, cos, sin, position, step):
    token = self.output_token_mapping[logits.reshape(-1).argmax()].realize()
    x = self.weights['vlm.model.language_model.embed_tokens.weight'][token].reshape(1,1,-1)
    logits = self._language(x,cos[:,:,step:step+1],sin[:,:,step:step+1],position)
    return logits,token.float().realize()

  def trajectory(self, actions, cos, sin, length, steps, offset=0):
    self.pack_expert()  # outside the captured graph: the merged weights are persistent buffers
    return super().trajectory(actions, cos, sin, length, steps, offset)

  def pack_expert(self):
    """Merged Q/K/V weights (packed layout, rows q|k|v) and per-column weight scales of each expert layer."""
    if getattr(self, 'expert_qkv', None) is not None:
      return
    names = [[f'expert.expert.layers.{i}.self_attn.{n}_proj' for n in 'qkv'] for i in range(EXPERT_LAYERS)]
    if any(n+'.bias' in self.weights for layer in names for n in layer):
      raise ValueError('Unsupported expert projection bias')
    qkv = [Tensor.cat(*[amd_gemm.pack(self.weights[n+'.weight']) for n in layer]).contiguous() for layer in names]
    scales = [Tensor.cat(*[self.weight_scales[n+'.weight'].reshape(1).expand(self.weights[n+'.weight'].shape[0]) for n in layer]).contiguous()
              for layer in names]
    Tensor.realize(*qkv,*scales)
    self.expert_qkv = [amd_gemm.unpack(w) for w in qkv]
    self.expert_qkv_scales = scales

  def expert_step(self, actions, timestep, cos, sin, flat_cache, mask):
    x = self.action_projection(actions, timestep)
    mask = mask.float().contiguous()
    for i in range(EXPERT_LAYERS):
      x = self.expert_block(x, cos, sin, i, mask)
    return self.linear(self.norm(x, 'expert.expert.norm', rms=True), 'expert.action_out_proj').float().realize()

  def expert_block(self, x, cos, sin, i, mask):
    """One expert layer with the arithmetic of text_layer and fewer launches.

    Q/K/V share one GEMM (per-column weight scales), FP8 casts are fused into the GEMM input packing, the O and FC2
    projections add the residual in their epilogue, and scales stay unmaterialized. Every value keeps its original rounding.
    """
    assert self.trajectory_active and not self.verifying and x.shape == (1,64,512) and x.dtype == dtypes.bfloat16
    prefix = f'expert.expert.layers.{i}'
    def scale_of(maximum):
      return (maximum/448).clamp(min_=1e-12)
    def fp8(value, scale):
      return (value.float()/scale).clamp(-448,448).cast(dtypes.fp8e4m3)
    def projection(value, scale, name, tile, residual=None):
      return tiled_gemm.gemm(value, self.weights[name+'.weight'], (scale, self.weight_scales[name+'.weight']), tile=tile, residual=residual)
    h = self.norm(x, f'{prefix}.input_layernorm', rms=True).reshape(64,512)
    scale = scale_of(h.float().abs().max())
    qkv = tiled_gemm.gemm(fp8(h, scale), self.expert_qkv[i], (scale, self.expert_qkv_scales[i]), tile=(2,2), column_scale=True)
    q,k,v = (qkv[:,a:b].reshape(1,64,heads,128).transpose(1,2) for a,b,heads in ((0,2048,16),(2048,3072,8),(3072,4096,8)))
    q,k = self.rope(q,k,cos,sin)
    self.trace_counts['expert_attention'] += 1
    attention = frozen_ops.expert_attention(q,k,v,self.cache[i],mask)
    # The FP8 scale is order-free: the attention output's maximum equals that of its transposed copy.
    scale = scale_of(frozen_ops.maximum(attention))
    x = projection(fp8(attention.transpose(1,2).reshape(64,2048), scale), scale, f'{prefix}.self_attn.o_proj', (1,2), x.reshape(64,512))
    h = self.norm(x.reshape(1,64,512), f'{prefix}.post_attention_layernorm', rms=True).reshape(64,512)
    scale = scale_of(h.float().abs().max())
    raw = projection(fp8(h, scale), scale, f'{prefix}.mlp.fc1', (2,2))
    hidden = raw.relu().square()
    # ReLU and the rounded BF16 square are monotonic: the maximum of ReLU^2 equals ReLU^2 of the signed maximum, with the
    # same rounding. The reduction then reads the FC1 output only (about 0.2 ms less per Euler step).
    scale = scale_of(raw.float().max().cast(dtypes.bfloat16).relu().square().float().abs())
    return projection(fp8(hidden, scale), scale, f'{prefix}.mlp.fc2', (1,2), x).reshape(1,64,512).realize()

  def _trajectory(self, actions, cos, sin, length, steps, offset):
    if steps not in DIFFUSION_STEPS or self.cache[0].shape[3] != 2304 or self.trajectory_active or self.verifying:
      raise ValueError('Selected expert requires one to ten Euler steps and 2304 KV rows')
    before = self.trace_counts['expert_attention']
    self.trajectory_active = True
    try:
      result = super()._trajectory(actions,cos,sin,length,steps,offset)
    finally:
      self.trajectory_active = False
    if self.trace_counts['expert_attention']-before != 28*steps:
      raise ValueError('Selected expert attention coverage changed')
    return result

  def encode_group(self, *pairs):
    count = len(pairs)//2
    assert count in (1,2) and not self.images
    self.images = count
    try:
      pixels,positions = Tensor.cat(*pairs[::2],dim=0),Tensor.cat(*pairs[1::2],dim=0)
      assert pixels.shape[1] == 720
      value = (self.linear(pixels,'vlm.model.visual.embeddings.patch_embedding')+positions).realize()
      for layer in range(self.config['vlm_config']['vision_config']['num_hidden_layers']):
        value = self.vision_layer(value,layer)
      self.images = 0
      parts = []
      for i in range(count):
        x = self.norm(value[i:i+1],'vlm.model.visual.post_layernorm')
        parts.append(self.norm(x,'vlm.model.projector.norm').reshape(-1,4608).realize())
      x = Tensor.cat(*parts,dim=0)
      for index,name in enumerate(self.projector_weights):
        quantized,scale = self.quantize(x) if count == 1 else frozen_ops.grouped_quantize(x,count)
        if count == 2:
          x = frozen_ops.projector_gemm(name,amd_gemm.pack(quantized),amd_gemm.pack(self.projector_weights[name]),scale,
                                        self.weight_scales[name+'.weight'],self.weights[name+'.bias'])
        else:
          x = tiled_gemm.gemm(quantized,self.projector_weights[name],(scale,self.weight_scales[name+'.weight']),
                              row_scale=count > 1,bias=self.weights.get(name+'.bias'))
        if index == 0:
          x = x.float().gelu(approximate='none').cast(self.dtype)
      x = x.realize().reshape(count,-1,x.shape[-1])
      return tuple(x[i].realize() for i in range(count))
    finally:
      self.images = 0
