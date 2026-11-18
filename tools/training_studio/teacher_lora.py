"""Small FP32 LoRA deltas on the real Edge action expert; frozen official base weights."""
import torch
from torch import nn
from torch.nn import functional as F


class DeltaLinear(nn.Module):
  def __init__(self,base,rank=8):
    super().__init__()
    self.base = base
    self.a = nn.Parameter(torch.randn(rank,base.in_features,device=base.weight.device,dtype=torch.float32)*.02)
    self.b = nn.Parameter(torch.zeros(base.out_features,rank,device=base.weight.device,dtype=torch.float32))
    self.scale = 2.

  def forward(self,x):
    result = self.base(x)
    with torch.autocast(x.device.type,enabled=False):
      delta = F.linear(F.linear(x.float(),self.a),self.b)*self.scale
    return (result.float()+delta).to(result.dtype)


class DenseActionDelta(nn.Module):
  """Direct, zero-initialized action-head residual; the pretrained head stays frozen."""
  def __init__(self,base):
    super().__init__()
    self.base=base
    self.delta_weight=nn.Parameter(torch.zeros_like(base.weight,dtype=torch.float32))
    self.delta_bias=nn.Parameter(torch.zeros(base.out_features,device=base.weight.device,dtype=torch.float32))

  def forward(self,x):
    result=self.base(x)
    with torch.autocast(x.device.type,enabled=False):
      delta=F.linear(x.float(),self.delta_weight,self.delta_bias)
    return (result.float()+delta).to(result.dtype)

  @classmethod
  def from_low_rank(cls,source):
    result=cls(source.base)
    with torch.no_grad(): result.delta_weight.copy_(source.scale*(source.b@source.a))
    return result


def install(model):
  model.requires_grad_(False)
  paths = []
  for name,module in list(model.expert.expert.named_modules()):
    if isinstance(module,nn.Linear) and name.endswith(('.q_proj','.v_proj')):
      parent_name,_,leaf = name.rpartition('.')
      parent = model.expert.expert.get_submodule(parent_name)
      setattr(parent,leaf,DeltaLinear(module))
      paths.append('expert.expert.'+name)
  if not paths:
    raise RuntimeError('No supported real action-expert attention projections found')
  return {name:p for name,p in model.named_parameters() if p.requires_grad},paths


def load(model,path):
  from safetensors.torch import load_file
  saved = load_file(str(path),device='cpu')
  model.requires_grad_(False)
  paths=[]
  for key,value in saved.items():
    if not key.endswith('.a'): continue
    name=key[:-2]
    if not (name.startswith('expert.expert.') or name=='expert.action_out_proj'):
      raise ValueError('Adapter must stay inside the actual action expert')
    parent_name,_,leaf=name.rpartition('.')
    parent=model.get_submodule(parent_name)
    base=getattr(parent,leaf)
    if not isinstance(base,nn.Linear): raise ValueError('Unsupported expert adapter topology')
    setattr(parent,leaf,DeltaLinear(base,rank=value.shape[0]))
    paths.append(name)
  if 'expert.action_out_proj.delta_weight' in saved:
    base=model.expert.action_out_proj
    if not isinstance(base,nn.Linear): raise ValueError('Unsupported dense action residual')
    model.expert.action_out_proj=DenseActionDelta(base)
    paths.append('expert.action_out_proj')
  parameters={name:p for name,p in model.named_parameters() if p.requires_grad}
  if set(parameters)!=set(saved):
    raise RuntimeError('Edge adapter topology mismatch')
  with torch.no_grad():
    for name,p in parameters.items():
      p.copy_(saved[name].to(p.device))
  return paths


def expand(model):
  """Increase conditional expert capacity; keep the VLM and all base weights frozen."""
  paths=[]
  suffixes=('.q_proj','.k_proj','.v_proj','.o_proj','.gate_proj','.up_proj','.down_proj')
  for name,module in list(model.expert.expert.named_modules()):
    if '.base' in name or not isinstance(module,nn.Linear) or not name.endswith(suffixes): continue
    parent_name,_,leaf=name.rpartition('.')
    parent=model.expert.expert.get_submodule(parent_name)
    setattr(parent,leaf,DeltaLinear(module))
    paths.append('expert.expert.'+name)
  if isinstance(model.expert.action_out_proj,DeltaLinear):
    model.expert.action_out_proj=DenseActionDelta.from_low_rank(model.expert.action_out_proj)
    paths.append('expert.action_out_proj')
  elif isinstance(model.expert.action_out_proj,nn.Linear):
    model.expert.action_out_proj=DenseActionDelta(model.expert.action_out_proj)
    paths.append('expert.action_out_proj')
  return paths
