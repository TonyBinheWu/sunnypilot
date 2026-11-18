"""Train the actual Edge expert through the same ten Euler steps used at inference."""
import argparse
import copy
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import signal
import threading
import tempfile
import time

IMPLEMENTATION_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def observed_inputs(sample):
  return {key:sample[key] for key in ('image_frames','camera_indices','absolute_timestamps','ego_history_timestamps','ego_history_xyz','ego_history_rot','nav_text')}


def cache_copy(source,device):
  result=copy.copy(source)
  result.layers=[copy.copy(layer) for layer in source.layers]
  for layer in result.layers:
    for name in ('keys','values'):
      value=getattr(layer,name,None)
      if value is not None: setattr(layer,name,value.detach().to(device=device,copy=True))
  return result


def spill_prefix(item,path):
  """Keep generated frozen VLM contexts on disk, not one CPU copy per sample."""
  import torch
  torch.save({key:item[key] for key in ('cache','positions','mask')},path)
  return {**{key:value for key,value in item.items() if key not in ('cache','positions','mask')},'prefix_path':str(path)}


@lru_cache(maxsize=1)
def load_prefix(path):
  import torch
  # These are private artifacts created by spill_prefix in this invocation,
  # never uploaded model/data files. Preserve the pinned HF cache class exactly.
  return torch.load(path,map_location='cpu',mmap=True,weights_only=False)


def held_command_loss(action,space,history_xyz):
  """Penalize forward motion under observed speed and bounded executed commands.

  Signed decoded velocities can cancel small positive acceleration pulses;
  forward-only execution cannot cancel those pulses by reversing the vehicle.
  This is an offline loss for already-completed stop references only.
  """
  import torch
  initial=torch.linalg.vector_norm(history_xyz[...,-1,:2]-history_xyz[...,-2,:2],dim=-1)/space.dt
  acceleration=action[...,0]*space.accel_std.to(action.device)+space.accel_mean.to(action.device)
  speed=initial
  speeds=[]
  for value in acceleration[...,:20].clamp(-3.5,1.6).unbind(-1):
    speed=(speed+value*space.dt).clamp_min(0)
    speeds.append(speed)
  executed=torch.stack(speeds,dim=-1)
  return 200*executed.square().amax()+50*executed.square().mean()


def stop_zone_loss(xyz,target,held,front_distance):
  """Penalize stopping short only where the reference has reached the valid zone."""
  import torch
  reference_front=front_distance-target[...,0]
  valid_reference=held*((reference_front>=0)&(reference_front<5)).to(held.dtype)
  shortfall=torch.relu(front_distance-xyz[...,0]-5)
  return 30*(shortfall.square()*valid_reference).sum()/valid_reference.sum().clamp_min(1)


def valid_stopped_trajectory(xyz,velocity,front_distance):
  """Offline selection must honor the existing zero-to-five-metre stop zone."""
  import torch
  final_front=front_distance-xyz[...,-10:,0]
  speed=torch.linalg.vector_norm(velocity,dim=-1)
  return ((xyz[...,0].amax(dim=-1)<=front_distance)&((final_front>=0)&(final_front<5)).all(dim=-1)&(speed[...,-10:].amax(dim=-1)<.15)).all()


def proceed_velocity_loss(velocity,reference_velocity):
  """Match immediate permitted motion rather than postponing a restart at every replan."""
  error=(velocity[:,:20]-reference_velocity[:,:20]).square().sum(-1)
  return 200*error.amax()+50*error.mean()


def rollout(model,item,*,grad,seed=42):
  import torch
  from torch.utils.checkpoint import checkpoint
  device=item.get('device','cuda')
  context=load_prefix(item['prefix_path']) if 'prefix_path' in item else item
  cache,positions,mask=context['cache'],context['positions'],context['mask']
  positions,mask=positions.to(device),mask.to(device)
  noise=torch.randn((1,64,2),device=device,generator=torch.Generator(device=device).manual_seed(seed))
  times=torch.linspace(0,1,11,device=device)
  x=noise
  def field(actions,moment):
    with torch.autocast(torch.device(device).type,dtype=torch.bfloat16,enabled=torch.device(device).type=='cuda'):
      embeddings=model.expert.action_in_proj(actions,moment).reshape(1,64,-1)
      output=model.expert.expert(inputs_embeds=embeddings,position_ids=positions,
        past_key_values=cache_copy(cache,device),attention_mask=mask,use_cache=True,is_causal=False)
      return model.expert.action_out_proj(output.last_hidden_state).reshape(1,64,2).float()
  for index in range(10):
    moment=times[index].reshape(1,1,1)
    velocity=checkpoint(field,x,moment,use_reentrant=False) if grad else field(x,moment)
    x=x+(times[index+1]-times[index])*velocity
  history={key:item[key].to(device) for key in ('ego_history_xyz','ego_history_rot')}
  xyz,rot=model.expert.action_space.action_to_traj(x,history['ego_history_xyz'],history['ego_history_rot'])
  return x,xyz,rot


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--data',type=Path,required=True)
  parser.add_argument('--output',type=Path,required=True)
  parser.add_argument('--parent',type=Path)
  parser.add_argument('--parent-sha256')
  parser.add_argument('--epochs',type=int,default=12)
  parser.add_argument('--learning-rate',type=float,default=3e-5)
  parser.add_argument('--expanded-expert',action='store_true')
  parser.add_argument('--lease',type=Path)
  args=parser.parse_args()
  if args.lease:
    def watchdog():
      changed,stamp=time.monotonic(),None
      while True:
        try: current=args.lease.stat().st_mtime_ns
        except OSError: current=None
        if current!=stamp: changed,stamp=time.monotonic(),current
        if time.monotonic()-changed>90: os.kill(os.getpid(),signal.SIGTERM)
        time.sleep(3)
    threading.Thread(target=watchdog,daemon=True).start()
  import numpy as np
  import torch
  import torch.nn.functional as F
  from safetensors.torch import save_file
  from alpamayo2_edge.checkpoint import load_model
  from alpamayo2_edge.helper import get_processor,to_device
  from alpamayo2_edge.inference import predict
  from tools.training_studio.edge_inputs import MODEL_REVISION,prepare_front_inputs
  from tools.training_studio.teacher_lora import install,load,expand
  from tools.training_studio.store import write_json
  args.output.mkdir(parents=True,exist_ok=False)
  prefix_directory=tempfile.TemporaryDirectory(prefix='prefix-',dir=args.output)
  prefix_root=Path(prefix_directory.name)
  torch.cuda.set_per_process_memory_fraction(.35)
  torch.manual_seed(42)
  model,_=load_model('/teacher/model',device='cuda',dtype='bfloat16',attn_implementation='sdpa')
  if args.parent:
    if args.parent_sha256 and hashlib.sha256(args.parent.read_bytes()).hexdigest()!=args.parent_sha256:
      raise ValueError('teacher parent hash changed')
    load(model,args.parent)
  else: install(model)
  if args.expanded_expert: expand(model)
  from tools.training_studio.teacher_motion import install as install_motion
  install_motion(model.expert.action_space)
  model.eval()
  parameters={name:p for name,p in model.named_parameters() if p.requires_grad}
  processor=get_processor(model.tokenizer,model.config)
  settings={'seed':42,'num_traj_sets':1,'num_traj_samples':1,'top_p':.98,'top_k':None,'temperature':.6,'max_generation_length':256,'diffusion_kwargs':{'inference_step':10}}
  manifest=json.loads((args.data/'manifest.json').read_text())
  rows=manifest['samples']
  if {r['seed'] for r in rows if r['split']=='train'} & {r['seed'] for r in rows if r['split']=='validation'}: raise ValueError('seed leakage')
  if any(r['seed'] in (300,301,302,303) for r in rows): raise ValueError('qualification seeds must remain held out')
  captured={}
  original=model._sample_actions
  def capture(*fields,**kwargs):
    captured['context']=fields[:6]
    action=original(*fields,**kwargs)
    captured['action']=action.detach().cpu().clone()
    return action
  model._sample_actions=capture
  history=[]
  def emit(phase,**fields):
    value={'phase':phase,'epochs':args.epochs,'history':history,'updated':time.time(),**fields}
    write_json(args.output/'progress.json',value)
    print(json.dumps(value),flush=True)
  prepared=[]
  for index,row in enumerate(rows):
    path=args.data/row['file']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']: raise ValueError('packet hash mismatch')
    with np.load(path,allow_pickle=False) as packet: sample={key:packet[key] for key in packet.files}
    sample['nav_text']=[str(sample['nav_text'].item())]
    inputs=to_device(prepare_front_inputs(observed_inputs(sample),model.config,model.tokenizer,processor=processor),device='cuda')
    predict(model,inputs,settings,'cuda')
    cache,_,positions,mask,_,_=captured.pop('context')
    item={'cache':cache_copy(cache,'cpu'),'positions':positions.detach().cpu().clone(),'mask':mask.detach().cpu().clone(),
      'ego_history_xyz':inputs['ego_history_xyz'][:,-1].detach().cpu().clone(),'ego_history_rot':inputs['ego_history_rot'][:,-1].detach().cpu().clone(),
      'target':torch.from_numpy(sample['future_xyz']),'target_rot':torch.from_numpy(sample['future_rot']),'row':row}
    # Official inverse dynamics supplies acceleration targets from the same
    # observed history and label-only reference future. Average position loss
    # alone can hide a positive first-step acceleration pulse while parked.
    target_action=model.expert.action_space.traj_to_action(item['ego_history_xyz'].cuda(),item['ego_history_rot'].cuda(),
      item['target'].cuda(),item['target_rot'].cuda())
    item['target_action']=target_action.detach().cpu().clone()
    if index==0:
      with torch.no_grad(): action,_,_=rollout(model,item,grad=False)
      difference=float((action.cpu()-captured['action']).abs().max())
      sampling_error=difference
      if difference>.02: raise RuntimeError(f'differentiable sampling disagrees with official inference: {difference}')
      emit('prefill',sample=index+1,samples=len(rows),official_sampling_max_error=difference)
    else: emit('prefill',sample=index+1,samples=len(rows))
    spilled=spill_prefix(item,prefix_root/f'{index:06d}.pt')
    if index==0:
      with torch.no_grad(): disk_action,_,_=rollout(model,spilled,grad=False)
      disk_difference=float((disk_action.cpu()-captured['action']).abs().max())
      if disk_difference>.02: raise RuntimeError(f'disk context sampling disagrees with official inference: {disk_difference}')
      emit('prefill',sample=index+1,samples=len(rows),official_sampling_max_error=difference,disk_sampling_max_error=disk_difference)
    captured.pop('action',None)
    prepared.append(spilled)
    del inputs,cache,item
  train=[r for r in prepared if r['row']['split']=='train']
  validation=[r for r in prepared if r['row']['split']=='validation']
  if not train or not validation: raise ValueError('training and validation samples required')
  def objective(item,grad):
    action,xyz,rot=rollout(model,item,grad=grad)
    target=item['target'].cuda()
    error=xyz-target
    velocity=torch.diff(torch.cat((torch.zeros_like(xyz[:,:1]),xyz),dim=1),dim=1)/.1
    ref_velocity=torch.diff(torch.cat((torch.zeros_like(target[:,:1]),target),dim=1),dim=1)/.1
    # Match near-term execution and body orientation, rather than a one-step flow proxy.
    loss=F.smooth_l1_loss(xyz[...,0],target[...,0])+20*error[...,1].square().mean()+10*error[:,:20].square().mean()
    loss=loss+4*(velocity[:,:20]-ref_velocity[:,:20]).square().mean()+50*(rot-item['target_rot'].cuda()).square().mean()
    if not item['row']['stop_required']:
      loss=loss+proceed_velocity_loss(velocity,ref_velocity)
    if item['row'].get('restart_required'):
      accel_std=model.expert.action_space.accel_std.to(action.device)
      restart_error=(action[...,0]-item['target_action'].to(action.device)[...,0])*accel_std
      loss=loss+10*restart_error[:,:20].square().mean()
    if item['row']['stop_required']:
      held=(torch.linalg.vector_norm(ref_velocity,dim=-1)<.15).float()
      loss=loss+stop_zone_loss(xyz,target,held,item['row']['front_distance_m'])
      loss=loss+50*(velocity.square().sum(-1)*held).sum()/held.sum().clamp_min(1)
      loss=loss+200*(velocity.square().sum(-1)*held).amax()
      accel_std=model.expert.action_space.accel_std.to(action.device)
      accel_error=(action[...,0]-item['target_action'].to(action.device)[...,0])*accel_std
      loss=loss+50*(accel_error[:,:20].square()*held[:,:20]).sum()/held[:,:20].sum().clamp_min(1)
      if item['row'].get('maintain_stop_reference'):
        loss=loss+held_command_loss(action,model.expert.action_space,item['ego_history_xyz'].to(action.device))
      loss=loss+30*torch.relu(xyz[...,0]-item['row']['front_distance_m']+.2).square().mean()
    if not torch.isfinite(loss): raise ValueError('nonfinite actual rollout loss')
    return loss,xyz,velocity
  def validate():
    values=[]; red=0; lateral=[]; hold=[]; proceed=[]
    with torch.no_grad():
      for item in validation:
        loss,xyz,velocity=objective(item,False)
        values.append(float(loss))
        lateral.append(float((xyz-item['target'].cuda())[...,1].square().mean()))
        if item['row']['stop_required']:
          speed=torch.linalg.vector_norm(velocity,dim=-1)
          red+=int(bool(valid_stopped_trajectory(xyz,velocity,item['row']['front_distance_m'])))
          hold.append(float(speed[:,-10:].square().mean()))
        else:
          target=item['target'].cuda()
          reference_velocity=torch.diff(torch.cat((torch.zeros_like(target[:,:1]),target),dim=1),dim=1)/.1
          proceed.append(float((velocity[:,:20]-reference_velocity[:,:20]).square().sum(-1).mean()))
    return {'validation_loss':float(np.mean(values)),'red_safe_count':red,'red_samples':len(hold),'red_hold_speed_mse':float(np.mean(hold)) if hold else 0.,'lateral_trajectory_mse':float(np.mean(lateral)),'stop_metric':'valid_stop_zone_v2','go_velocity_mse':float(np.mean(proceed)) if proceed else None,'go_samples':len(proceed)}
  baseline=validate()
  best_metrics,best_epoch=baseline,0
  balanced_metrics,balanced_epoch=baseline,0
  best_score=(baseline['red_safe_count'],-baseline['red_hold_speed_mse'],-baseline['validation_loss'])
  optimizer=torch.optim.AdamW(parameters.values(),lr=args.learning_rate,weight_decay=0)
  emit('training',epoch=0,baseline=baseline,trainable_parameters=sum(p.numel() for p in parameters.values()))
  for epoch in range(args.epochs):
    values=[]
    for batch,index in enumerate(np.random.default_rng(epoch+42).permutation(len(train))):
      optimizer.zero_grad()
      loss,_,_=objective(train[index],True)
      loss.backward()
      gradients=[p.grad for p in parameters.values() if p.grad is not None]
      if not gradients or not all(torch.isfinite(g).all() for g in gradients): raise ValueError('invalid real expert gradients')
      torch.nn.utils.clip_grad_norm_(parameters.values(),1.)
      before={name:p.detach().clone() for name,p in parameters.items()}
      initial_loss=float(loss.detach())
      optimizer.step()
      delta={name:p.detach()-before[name] for name,p in parameters.items()}
      scale=1.
      with torch.no_grad():
        observed=float(objective(train[index],False)[0])
        for backtrack in range(5):
          if observed<=initial_loss+max(.0001,initial_loss*.0001): break
          scale*=.5
          for name,p in parameters.items(): p.copy_(before[name]+scale*delta[name])
          observed=float(objective(train[index],False)[0])
        if observed>initial_loss+max(.0001,initial_loss*.0001):
          for name,p in parameters.items(): p.copy_(before[name])
          observed=initial_loss
          optimizer.state.clear()
          scale=0.
      values.append(observed)
      emit('training',epoch=epoch+1,batch=batch+1,batches=len(train),loss=values[-1],loss_before_step=initial_loss,step_scale=scale,baseline=baseline)
    metrics=validate()
    history.append({'epoch':epoch+1,'train_loss':float(np.mean(values)),**metrics})
    score=(metrics['red_safe_count'],-metrics['red_hold_speed_mse'],-metrics['validation_loss'])
    if score>best_score:
      best_score=score
      best_metrics,best_epoch=metrics,epoch+1
      save_file({name:p.detach().float().cpu().contiguous() for name,p in parameters.items()},str(args.output/'best.safetensors'))
    if metrics['validation_loss']<balanced_metrics['validation_loss']:
      balanced_metrics,balanced_epoch=metrics,epoch+1
      save_file({name:p.detach().float().cpu().contiguous() for name,p in parameters.items()},str(args.output/'balanced.safetensors'))
    emit('training',epoch=epoch+1,baseline=baseline,**metrics)
  write_json(args.output/'result.json',{'revision':MODEL_REVISION,'baseline':baseline,'best':best_metrics,'best_epoch':best_epoch,
    'balanced_best':balanced_metrics,'balanced_epoch':balanced_epoch,'balanced_adapter_saved':(args.output/'balanced.safetensors').is_file(),
    'history':history,'adapter_saved':(args.output/'best.safetensors').is_file(),'qualified':False,'objective':'actual_ten_step_Euler_rollout',
    'script_sha256':IMPLEMENTATION_SHA256,'dataset_sha256':hashlib.sha256((args.data/'manifest.json').read_bytes()).hexdigest(),
    'parent_sha256':hashlib.sha256(args.parent.read_bytes()).hexdigest() if args.parent else None,'official_sampling_max_error':sampling_error,
    'disk_sampling_max_error':disk_difference})
  emit('completed',epoch=args.epochs,baseline=baseline)
  load_prefix.cache_clear()
  prefix_directory.cleanup()


if __name__=='__main__': main()
