"""One GPU-resident pair of coordinates per serial block. Unchanged greedy decisions every six tokens."""
from functools import partial
from tinygrad import Tensor,dtypes
from tinygrad.uop.ops import UOp,KernelInfo
from openpilot.selfdrive.alpamayo import amd_attention as att


def coords_kernel(out,pos,step):
  return UOp.group(out.index(0).store(pos.cast(dtypes.int32)),out.index(1).store(step.cast(dtypes.int32))).sink(arg=KernelInfo(name='serial_block_coordinates',opts_to_apply=()))


def fused_layer(m,x,cache,ctrl,coss,sins,j,mask,layer):
  """One serial language layer in eleven launches with the original arithmetic (same tokens, logits and KV rows).

  Norm+quantize, Q/K/V GEMV+RoPE+KV store, scores, softmax, values, output quantize, o_proj, residual+norm,
  W4 FC1, ReLU^2 quantize, and W4 FC2 with the residual add.
  """
  from .kernels import frozen_ops,serial_mlp
  from . import amd_gemm
  hc=frozen_ops.hip_call;dev=x.device;prefix=f'vlm.model.language_model.layers.{layer}'
  empty=lambda *shape,dtype: Tensor.empty(*shape,dtype=dtype,device=dev)
  weight=lambda n: amd_gemm.pack(m.weights[f'{prefix}.self_attn.{n}_proj.weight'])
  scale=lambda n: m.weight_scales[f'{prefix}.self_attn.{n}_proj.weight']
  x=x.reshape(2048)
  q8,s1=hc((empty(2048,dtype=dtypes.fp8e4m3),empty(dtype=dtypes.float32),x,m.weights[prefix+'.input_layernorm.weight']),(0,1),
           kind='serial_norm_fp8',args=(2048,),name='prep_norm_fp8',grid=1,local=256)
  q,stored=hc((empty(1,16,1,128,dtype=dtypes.bfloat16),cache,q8,weight('q'),weight('k'),weight('v'),s1,scale('q'),scale('k'),scale('v'),coss,sins,ctrl),
              (0,1),kind='serial_qkv_rope_store',args=(2048,j),name='qkv_rope_store',grid=32,local=256)
  scores,=hc((empty(1,16,1,2304,dtype=dtypes.bfloat16),q,stored,mask),(0,),kind='serial_scores',args=(16,8,2304,128),name='attn_scores',grid=144,local=128)
  probs=Tensor.custom_kernel(empty(1,16,1,2304,dtype=dtypes.bfloat16),scores,fxn=partial(att._softmax,packed=False))[0]
  parts,=hc((empty(1,16,18,128,dtype=dtypes.float32),probs,stored),(0,),kind='serial_values',args=(16,8,2304,128),name='attn_values',grid=72,local=128)
  q8o,s2=hc((empty(2048,dtype=dtypes.fp8e4m3),empty(dtype=dtypes.float32),parts),(0,1),kind='serial_attn_out_fp8',args=(2048,),name='prep_attn_out_fp8',
            grid=1,local=256)
  o,=hc((empty(2048,dtype=dtypes.bfloat16),q8o,weight('o'),s2,scale('o')),(0,),kind='serial_o_gemv',args=(2048,2048),name='fp8_gemv',grid=32,local=128)
  q16,s3=hc((empty(2048,dtype=dtypes.float16),empty(dtype=dtypes.float32),x,o,m.weights[prefix+'.post_attention_layernorm.weight']),(0,1),
            kind='serial_residual_norm_f16',args=(2048,),name='prep_resid_norm_f16',grid=1,local=256)
  fc1,fc2=prefix+'.mlp.fc1',prefix+'.mlp.fc2'
  f1=Tensor.custom_kernel(empty(9216,dtype=dtypes.bfloat16),q16,m.w4_weights[fc1],s3,m.weight_scales[fc1+'.weight'],
                          fxn=partial(serial_mlp._program,kind='gemv',n=9216,k=2048))[0]
  q16b,s4=hc((empty(9216,dtype=dtypes.float16),empty(dtype=dtypes.float32),f1),(0,1),kind='serial_relu2_f16',args=(9216,),name='prep_relu2_f16',
             grid=1,local=384)
  out,=hc((empty(2048,dtype=dtypes.bfloat16),q16b,m.w4_weights[fc2],s4,m.weight_scales[fc2+'.weight'],x,o),(0,),kind='projection_w4_gemv_residual',
          args=(2048,9216),name='projection_w4_gemv_residual',grid=512,local=128)
  return out.reshape(1,1,2048).realize()


def block_six(m,logits,cos,sin,pos,step):
  assert m.amd and not m.images and not m.verifying and not m.trajectory_active and m.prefill_prefix is None
  assert logits.shape==(1,1,2112) and cos.shape==sin.shape==(1,1,64,128) and len(m.cache)==28
  ctrl=Tensor.custom_kernel(Tensor.empty(2,device=logits.device,dtype=dtypes.int32),Tensor(pos),Tensor(step),fxn=coords_kernel)[0].realize()
  idx=ctrl[1]+Tensor.arange(6);coss=cos.reshape(64,128)[idx].contiguous().realize();sins=sin.reshape(64,128)[idx].contiguous().realize();tokens=[]
  for j in range(6):
    # Exactly the original selected head and first-on-tie argmax.
    token=m.output_token_mapping[logits.reshape(-1).argmax()].realize();tokens.append(token.float().reshape(1).realize())
    x=m.weights['vlm.model.language_model.embed_tokens.weight'][token].reshape(1,1,-1)
    mask=(Tensor.arange(2304)>ctrl[0]+j).where(-float('inf'),0.).float().contiguous().realize()
    for i,cache in enumerate(m.cache):
      x=fused_layer(m,x,cache,ctrl,coss,sins,j,mask,i)
    logits=m.linear(m.norm(x,'vlm.model.language_model.norm',rms=True),'vlm.lm_head').realize()
  return logits,Tensor.cat(*tokens).realize()
