"""Read both planes of the canonical KV allocation after the selected serial store."""
from functools import partial
from tinygrad import Tensor,dtypes
from tinygrad.uop.ops import Ops
from openpilot.selfdrive.alpamayo import amd_attention as att

SHAPE=(2,1,8,2304,128)

def direct_scores(out,q,cache,mask):
  return att._scores(out,q,cache[0],mask)

def direct_values(out,probs,cache):
  return att._values(out,probs,cache[1])

def direct(q,assigned,mask):
  assert assigned.shape==SHAPE and q.shape==(1,16,1,128) and q.dtype==assigned.dtype==dtypes.bfloat16
  assert mask.numel()==2304 and assigned.uop.op is Ops.AFTER and assigned.uop.src[1].op is Ops.STORE
  scores=Tensor.empty(1,16,1,2304,dtype=q.dtype,device=q.device)
  scores=Tensor.custom_kernel(scores,q.contiguous(),assigned,mask.float().contiguous(),fxn=direct_scores)[0]
  probs=Tensor.empty(scores.shape,dtype=q.dtype,device=q.device)
  probs=Tensor.custom_kernel(probs,scores,fxn=partial(att._softmax,packed=False))[0]
  partials=Tensor.empty(1,16,18,128,dtype=dtypes.float32,device=q.device)
  partials=Tensor.custom_kernel(partials,probs,assigned,fxn=direct_values)[0]
  return partials.sum(2,keepdim=True).cast(q.dtype)
