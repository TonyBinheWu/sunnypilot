"""Explicit FP32 action-expert arithmetic; the visual-language model stays frozen BF16."""
import copy

PROFILE='fp32_action_expert_v1'


def resolve(cli_value,pointer):
  pointer=pointer or {};value=pointer.get('fp32_expert',False)
  if type(value) is not bool or (cli_value is not None and type(cli_value) is not bool):
    raise ValueError('expert precision must be boolean')
  if cli_value is not None and 'fp32_expert' in pointer and cli_value!=value:
    raise ValueError('CLI expert precision disagrees with immutable teacher pointer')
  return value if cli_value is None else cli_value


def fp32_cache(source,device):
  import torch
  result=copy.copy(source);result.layers=[copy.copy(layer) for layer in source.layers]
  for layer in result.layers:
    for name in ('keys','values'):
      value=getattr(layer,name,None)
      if value is not None:setattr(layer,name,value.detach().to(device=device,dtype=torch.float32,copy=True))
  return result


def install(model,enabled):
  import torch
  if type(enabled) is not bool:raise ValueError('expert precision must be boolean')
  active=getattr(model.expert,'_studio_fp32_expert',False)
  if active:
    if not enabled:raise ValueError('cannot silently revert an installed FP32 expert profile')
    return
  if not enabled:return
  model.expert.float();sample=model._sample_actions
  def precise_sample(cache,prefix_length,position_ids,attention_mask,expert_batch,device,diffusion_kwargs):
    with torch.autocast(torch.device(device).type,enabled=False):
      return sample(fp32_cache(cache,device),prefix_length,position_ids,attention_mask,expert_batch,device,diffusion_kwargs)
  model._sample_actions=precise_sample;model.expert._studio_fp32_expert=True
