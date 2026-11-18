"""Paired stop/proceed updates with PCGrad and a per-example descent guard.

Projection rule: https://arxiv.org/abs/2001.06782 . This changes offline
optimization only; the original closed-loop driving gates remain authoritative.
"""


def paired_indices(items,epoch):
  import numpy as np
  stop=[i for i,item in enumerate(items) if item['row']['stop_required']]
  go=[i for i,item in enumerate(items) if not item['row']['stop_required']]
  if not stop or not go: raise ValueError('paired training needs both stop and proceed references')
  rng=np.random.default_rng(epoch+42)
  stop=rng.permutation(stop).tolist();go=rng.permutation(go).tolist()
  return [(stop[i%len(stop)],go[i%len(go)]) for i in range(max(len(stop),len(go)))]


def project_pair(stop,go):
  import torch
  if stop.ndim!=1 or stop.shape!=go.shape or not stop.numel(): raise ValueError('matching nonempty flat gradients required')
  if not bool(torch.isfinite(stop).all() and torch.isfinite(go).all()): raise ValueError('nonfinite paired gradient')
  dot=torch.dot(stop,go);stop_norm=torch.dot(stop,stop);go_norm=torch.dot(go,go)
  if not bool(torch.isfinite(torch.stack((dot,stop_norm,go_norm))).all()): raise ValueError('nonfinite paired gradient norm')
  conflict=bool(dot<0)
  cosine=float(dot/(stop_norm*go_norm).sqrt()) if bool(stop_norm>0 and go_norm>0) else None
  if conflict:
    # Both projections use the original other-task gradient, not an already
    # modified vector. With two tasks this is exactly the PCGrad update.
    joint=(stop-dot/go_norm*go+go-dot/stop_norm*stop)/2
  else: joint=(stop+go)/2
  return joint,cosine,conflict


def paired_step(parameters,optimizer,objective,stop_item,go_item,max_backtracks=8):
  import torch
  from tools.training_studio.teacher_train import load_prefix,release_prefix_pages
  if not stop_item['row']['stop_required'] or go_item['row']['stop_required']: raise ValueError('one stop and one proceed example required')
  if not parameters: raise ValueError('no trainable expert parameters')
  items=(stop_item,go_item);names=list(parameters);params=list(parameters.values())
  def objective_loss(item,grad):
    result=objective(item,grad)
    return result[0] if isinstance(result,(tuple,list)) else result
  def release_mappings():
    # Keep this pair's clean pages resident until both post-step checks finish.
    # Only one deserialized mmap context remains cached at a time.
    load_prefix.cache_clear()
  try:
    gradients=[];before_losses=[]
    for item in items:
      optimizer.zero_grad(set_to_none=True)
      result=objective(item,True);loss=result[0] if isinstance(result,(tuple,list)) else result
      if loss.numel()!=1 or not bool(torch.isfinite(loss)): raise ValueError('invalid paired rollout loss')
      before_losses.append(float(loss.detach()));loss.backward()
      gradients.append(torch.cat([(p.grad.detach() if p.grad is not None else torch.zeros_like(p)).reshape(-1) for p in params]))
      del result,loss;release_mappings()
    joint,cosine,conflict=project_pair(*gradients)
    optimizer.zero_grad(set_to_none=True);offset=0
    for p in params:
      p.grad=joint[offset:offset+p.numel()].reshape_as(p);offset+=p.numel()
    norm=torch.nn.utils.clip_grad_norm_(params,1.)
    if not bool(torch.isfinite(norm)): raise ValueError('invalid projected gradient norm')
    before={name:p.detach().clone() for name,p in parameters.items()}
    optimizer.step();delta={name:p.detach()-before[name] for name,p in parameters.items()}
    scale=1.;backtracks=0
    def check():
      with torch.no_grad():
        values=[]
        for item in items:
          loss=objective_loss(item,False);values.append(float(loss));del loss;release_mappings()
      if not all(__import__('math').isfinite(value) for value in values): raise ValueError('nonfinite paired post-step loss')
      return values
    observed=check()
    def acceptable(): return all(value<=initial+max(.0001,abs(initial)*.0001) for value,initial in zip(observed,before_losses))
    while not acceptable() and backtracks<max_backtracks:
      scale*=.5;backtracks+=1
      with torch.no_grad():
        for name,p in parameters.items():p.copy_(before[name]+scale*delta[name])
      observed=check()
    if not acceptable():
      with torch.no_grad():
        for name,p in parameters.items():p.copy_(before[name])
      optimizer.state.clear();scale=0.;observed=before_losses.copy()
    change=float(torch.stack([(p.detach()-before[name]).square().sum() for name,p in parameters.items()]).sum().sqrt())
    return {'loss':sum(observed)/2,'loss_before_step':sum(before_losses)/2,'stop_loss':observed[0],'go_loss':observed[1],
      'stop_loss_before_step':before_losses[0],'go_loss_before_step':before_losses[1],'step_scale':scale,'backtracks':backtracks,
      'gradient_cosine':cosine,'gradient_projected':conflict,'parameter_delta_norm':change,'gradient_norm_before_clip':float(norm)}
  finally:
    load_prefix.cache_clear()
    for item in items:
      if item.get('prefix_path'):release_prefix_pages(item['prefix_path'])
    if params[0].device.type=='cuda':torch.cuda.empty_cache()
