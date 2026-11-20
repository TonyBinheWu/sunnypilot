"""Paired stop/proceed updates with PCGrad and a per-example descent guard.

Projection rule: https://arxiv.org/abs/2001.06782 . This changes offline
optimization only; the original closed-loop driving gates remain authoritative.
"""


def stop_mode(item):
  row=item['row']
  if not row['stop_required']:raise ValueError('stop reference required')
  if row.get('maintain_stop_reference'):return 'hold'
  speed=item.get('observed_speed_mps')
  if speed is None or not __import__('math').isfinite(speed):raise ValueError('observed stop speed required for balanced sampling')
  return 'recover' if speed<.2 and row['front_distance_m']>=5 else 'approach'


def _balanced_order(groups,epoch,count):
  import numpy as np
  rng=np.random.default_rng(42);prepared={}
  for key,scenes in sorted(groups.items()):
    names=rng.permutation(sorted(scenes)).tolist();prepared[key]=[rng.permutation(scenes[name]).tolist() for name in names]
  keys=np.random.default_rng(epoch+42).permutation(sorted(groups)).tolist();per_class=count//len(keys);result=[]
  for step in range(per_class):
    slot=epoch*per_class+step
    for key in keys:
      scenes=prepared[key];members=scenes[slot%len(scenes)]
      result.append(members[(slot//len(scenes))%len(members)])
  return result


def paired_indices(items,epoch,*,balanced_stop_modes=False):
  import numpy as np
  stop=[i for i,item in enumerate(items) if item['row']['stop_required']]
  go=[i for i,item in enumerate(items) if not item['row']['stop_required']]
  if not stop or not go: raise ValueError('paired training needs both stop and proceed references')
  if balanced_stop_modes:
    from tools.training_studio.teacher_reasoning_train import maneuver_class
    groups=[{},{}]
    for side,indices in enumerate((stop,go)):
      for index in indices:
        item=items[index];key=stop_mode(item) if side==0 else maneuver_class(item['row'])
        groups[side].setdefault(key,{}).setdefault(item['row']['scenario'],[]).append(index)
    if set(groups[0])!={'hold','recover','approach'} or set(groups[1])!={'straight','left','right'}:
      raise ValueError('balanced recovery requires three stop modes and three permitted directions')
    multiple=__import__('math').lcm(*(len(group) for group in groups));count=((max(len(stop),len(go))+multiple-1)//multiple)*multiple
    stop_order,go_order=(_balanced_order(group,epoch,count) for group in groups)
    # Independent class marginals are insufficient: identical class shuffles
    # permanently tie hold/recover/approach to particular directions. Rotate
    # each balanced direction round so all cross-task combinations are used.
    crossed_go=[]
    for start in range(0,count,3):
      stop_order[start:start+3]=sorted(stop_order[start:start+3],key=lambda index:stop_mode(items[index]))
      directions=sorted(go_order[start:start+3],key=lambda index:maneuver_class(items[index]['row']));rotation=(epoch+start//3)%3
      crossed_go.extend(directions[rotation:]+directions[:rotation])
    return list(zip(stop_order,crossed_go))
  rng=np.random.default_rng(epoch+42)
  stop=rng.permutation(stop).tolist();go=rng.permutation(go).tolist()
  return [(stop[i%len(stop)],go[i%len(go)]) for i in range(max(len(stop),len(go)))]


def paired_groups(items,epoch,*,correction_warmup=False):
  pairs=paired_indices(items,epoch,balanced_stop_modes=True)
  groups=[tuple(index for pair in pairs[start:start+3] for index in pair) for start in range(0,len(pairs),3)]
  if correction_warmup:
    from tools.training_studio.teacher_reasoning_train import maneuver_class
    corrections={};stop_corrections={}
    for index,item in enumerate(items):
      if not item['row']['stop_required'] and (item['row'].get('turn_reference_speed_mps') is not None or item['row'].get('correction_priority') is True):
        corrections.setdefault(maneuver_class(item['row']),[]).append(index)
      if item['row']['stop_required'] and item['row'].get('correction_priority') is True:
        stop_corrections.setdefault(stop_mode(item),[]).append(index)
    if corrections or stop_corrections:
      # New data are appended to the manifest. Rehearse a bounded window
      # newest-first every epoch, plus a rotating older rehearsal group.
      # Retain every ordinary group and every six-task post-step guard.
      width=min(5,max(len(members) for members in (*corrections.values(),*stop_corrections.values())))
      warmups=[]
      replay=any(len(members)>width for members in (*corrections.values(),*stop_corrections.values()))
      for offset in range(width+int(replay)):
        warmup=list(groups[offset%len(groups)])
        for direction,members in sorted(corrections.items()):
          slot=next(slot for slot in (1,3,5) if maneuver_class(items[warmup[slot]]['row'])==direction)
          warmup[slot]=members[epoch%len(members)] if offset==width else members[-1-(epoch+offset)%min(width,len(members))]
        for mode,members in sorted(stop_corrections.items()):
          slot=next(slot for slot in (0,2,4) if stop_mode(items[warmup[slot]])==mode)
          warmup[slot]=members[epoch%len(members)] if offset==width else members[-1-(epoch+offset)%min(width,len(members))]
        warmups.append(tuple(warmup))
      groups=warmups+groups
  return groups


def project_pair(stop,go,*,unit_gradients=False):
  import torch
  if stop.ndim!=1 or stop.shape!=go.shape or not stop.numel(): raise ValueError('matching nonempty flat gradients required')
  if not bool(torch.isfinite(stop).all() and torch.isfinite(go).all()): raise ValueError('nonfinite paired gradient')
  dot=torch.dot(stop,go);stop_norm=torch.dot(stop,stop);go_norm=torch.dot(go,go)
  if not bool(torch.isfinite(torch.stack((dot,stop_norm,go_norm))).all()): raise ValueError('nonfinite paired gradient norm')
  conflict=bool(dot<0)
  cosine=float(dot/(stop_norm*go_norm).sqrt()) if bool(stop_norm>0 and go_norm>0) else None
  if unit_gradients:
    # Normalize tasks before projection, so small held-stop gradients have the
    # same directional influence as much larger moving/restart losses.
    if bool(stop_norm>0):stop=stop/stop_norm.sqrt()
    if bool(go_norm>0):go=go/go_norm.sqrt()
    dot=torch.dot(stop,go);stop_norm=torch.dot(stop,stop);go_norm=torch.dot(go,go)
    conflict=bool(dot<0)
  if conflict:
    # Both projections use the original other-task gradient, not an already
    # modified vector. With two tasks this is exactly the PCGrad update.
    joint=(stop-dot/go_norm*go+go-dot/stop_norm*stop)/2
  else: joint=(stop+go)/2
  return joint,cosine,conflict


def project_group(gradients):
  """Minimum-norm convex combination of up to nine unit task gradients.

  Small-task exact active-set solve of the MGDA subproblem described in
  https://proceedings.neurips.cc/paper/2018/hash/432aca3a1e345e339f35a30c8f65edce-Abstract.html
  A common descent direction protects hold/approach/recovery and all three
  permitted directions together, rather than protecting only the current pair.
  """
  import itertools
  import numpy as np
  import torch
  if not 2<=len(gradients)<=9 or any(g.ndim!=1 or g.shape!=gradients[0].shape or not g.numel() for g in gradients):
    raise ValueError('two to nine matching flat task gradients required')
  matrix=torch.stack(gradients)
  if not bool(torch.isfinite(matrix).all()):raise ValueError('nonfinite grouped gradient')
  # Near-opposed tasks can cancel below FP32 Gram/cross-sum precision. Compute
  # their geometry before casting back, so unit normalization cannot amplify
  # an accepted tiny negative gain into a genuine ascent direction.
  precise=matrix.double();norms=precise.norm(dim=1)
  if not bool(torch.isfinite(norms).all()):raise ValueError('nonfinite grouped gradient norm')
  unit=precise/norms.clamp_min(1e-12).unsqueeze(1)
  active=(norms>1e-12).nonzero().flatten().tolist()
  gram=(unit@unit.T).cpu().numpy();best=None
  for size in range(1,len(active)+1):
    for subset in itertools.combinations(active,size):
      block=gram[np.ix_(subset,subset)]
      kkt=np.block([[block,np.ones((size,1))],[np.ones((1,size)),np.zeros((1,1))]])
      rhs=np.r_[np.zeros(size),1.];solution=np.linalg.lstsq(kkt,rhs,rcond=1e-12)[0]
      if np.max(np.abs(kkt@solution-rhs))>1e-7 or solution[:-1].min()<-1e-7:continue
      weights=np.zeros(len(gradients));weights[list(subset)]=np.maximum(solution[:-1],0);weights/=weights.sum()
      squared=float(weights@gram@weights)
      if best is None or squared<best[0]:best=(squared,weights)
  weights=np.zeros(len(gradients)) if best is None else best[1]
  joint=(torch.as_tensor(weights,device=matrix.device,dtype=precise.dtype)@unit).to(matrix.dtype)
  gains=unit@joint.double()
  length=joint.double().norm()
  if bool(length>1e-6) and bool(((unit@(joint.double()/length))<-1e-8).any()):
    raise ValueError('normalized grouped direction is not common descent')
  return joint,weights.tolist(),float(gains.min()),bool((gram<-1e-6).any())


def paired_step(parameters,optimizer,objective,stop_item,go_item,max_backtracks=8,*,unit_gradients=False,extra_items=(),progress=None,safety_objective=None):
  import torch
  from tools.training_studio.teacher_train import load_prefix,release_prefix_pages
  if not stop_item['row']['stop_required'] or go_item['row']['stop_required']: raise ValueError('one stop and one proceed example required')
  if not parameters: raise ValueError('no trainable expert parameters')
  items=(stop_item,go_item,*extra_items);names=list(parameters);params=list(parameters.values())
  if extra_items and (len(items)!=6 or not unit_gradients or any(bool(item['row']['stop_required'])!=(i%2==0) for i,item in enumerate(items))):
    raise ValueError('grouped update requires three alternating stop/proceed pairs and unit gradients')
  original_count=len(items)
  if safety_objective is not None and not extra_items:raise ValueError("separate safety tasks require a six-task group")
  objectives=[objective]*original_count
  if safety_objective is not None:
    items=(*items,*items[::2]);objectives.extend([safety_objective]*3)
  def objective_loss(item,grad,fn):
    result=fn(item,grad)
    return result[0] if isinstance(result,(tuple,list)) else result
  def release_mappings():
    # Keep this pair's clean pages resident until both post-step checks finish.
    # Only one deserialized mmap context remains cached at a time.
    load_prefix.cache_clear()
  try:
    gradients=[];before_losses=[]
    for task,(item,fn) in enumerate(zip(items,objectives),1):
      if progress:progress(group_stage='gradient',group_task=task,group_tasks=len(items))
      optimizer.zero_grad(set_to_none=True)
      result=fn(item,True);loss=result[0] if isinstance(result,(tuple,list)) else result
      if loss.numel()!=1 or not bool(torch.isfinite(loss)): raise ValueError('invalid paired rollout loss')
      before_losses.append(float(loss.detach()));loss.backward()
      gradients.append(torch.cat([(p.grad.detach() if p.grad is not None else torch.zeros_like(p)).reshape(-1) for p in params]))
      del result,loss;release_mappings()
    task_norms=[float(gradient.norm()) for gradient in gradients]
    grouped={}
    if extra_items:
      joint,weights,gain,conflict=project_group(gradients);cosine=None
      common_norm=joint.norm()
      if bool(common_norm>1e-6):joint=joint/common_norm
      else:joint=torch.zeros_like(joint)
      grouped={'task_gradient_weights':weights,'minimum_task_gradient_gain':gain,'common_gradient_norm':float(common_norm),'task_count':len(items)}
    else:joint,cosine,conflict=project_pair(*gradients,unit_gradients=unit_gradients)
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
        for task,(item,fn) in enumerate(zip(items,objectives),1):
          if progress:progress(group_stage='verify',group_task=task,group_tasks=len(items),backtracks=backtracks)
          loss=objective_loss(item,False,fn);values.append(float(loss));del loss;release_mappings()
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
    count=original_count//2
    if extra_items:grouped.update(task_losses_before=before_losses.copy(),task_losses_after=observed.copy())
    if safety_objective is not None:grouped.update(safety_losses_before=before_losses[original_count:],safety_losses_after=observed[original_count:])
    observed=observed[:original_count];before_losses=before_losses[:original_count];task_norms=task_norms[:original_count]
    return {'loss':sum(observed)/len(items),'loss_before_step':sum(before_losses)/len(items),'stop_loss':sum(observed[::2])/count,'go_loss':sum(observed[1::2])/count,
      'stop_loss_before_step':sum(before_losses[::2])/count,'go_loss_before_step':sum(before_losses[1::2])/count,'step_scale':scale,'backtracks':backtracks,
      'gradient_cosine':cosine,'gradient_projected':conflict,'parameter_delta_norm':change,'gradient_norm_before_clip':float(norm),
      'task_gradients_normalized':unit_gradients,'stop_gradient_norm':sum(task_norms[::2])/count,'go_gradient_norm':sum(task_norms[1::2])/count,**grouped}
  finally:
    load_prefix.cache_clear()
    for item in items:
      if item.get('prefix_path'):release_prefix_pages(item['prefix_path'])
    if params[0].device.type=='cuda':torch.cuda.empty_cache()
