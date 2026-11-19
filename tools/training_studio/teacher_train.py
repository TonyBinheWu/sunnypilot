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
OBJECTIVE_REVISION='ten_step_immediate_stop_and_restart_v2'
EXECUTED_OBJECTIVE_REVISION='ten_step_executed_accel_curvature_hold_margin_v3'
RECOVERY_OBJECTIVE_REVISION='ten_step_balanced_recovery_interior_stop_margin_v4'


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
  release_prefix_pages(path)
  return {**{key:value for key,value in item.items() if key not in ('cache','positions','mask')},'prefix_path':str(path)}


def release_prefix_pages(path):
  """Evict only this generated file's clean pages from shared CPU/GPU RAM."""
  if not hasattr(os,'posix_fadvise'): return
  with open(path,'r+b') as stream:
    os.fsync(stream.fileno())
    os.posix_fadvise(stream.fileno(),0,0,os.POSIX_FADV_DONTNEED)


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


def stop_zone_loss(xyz,target,held,front_distance,*,interior_margin_m=0.):
  """Penalize stopping short only where the reference has reached the valid zone."""
  import torch
  if not 0<=interior_margin_m<5:raise ValueError('invalid training stop margin')
  reference_front=front_distance-target[...,0]
  valid_reference=held*((reference_front>=0)&(reference_front<5)).to(held.dtype)
  shortfall=torch.relu(front_distance-xyz[...,0]-(5-interior_margin_m))
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


def immediate_command_loss(accel_error):
  """Match the next executed commands, including moving stop approaches.

  Rollout position error alone can defer braking until a later replan. These
  offline inverse-dynamics targets preserve acceleration on distant approaches
  and teach braking where safe reference trajectories actually brake.
  """
  return 50*accel_error[:,:3].square().mean()+20*accel_error[:,:10].square().mean()+10*accel_error[:,:20].square().mean()


def restart_command_loss(accel_error):
  """Compatibility name for the same immediate permitted-restart supervision."""
  return immediate_command_loss(accel_error)


def immediate_steering_loss(action,target_action,space,history_xyz):
  """Supervise the curvature commands that execute before the next replan.

  Course/rotation losses over a long horizon can hide an incorrect first turn
  command. Scale curvature to lateral acceleration using observed ego speed,
  without giving route geometry or future signal state to model inference.
  """
  import torch
  speed=torch.linalg.vector_norm(history_xyz[...,-1,:2]-history_xyz[...,-2,:2],dim=-1)/space.dt
  scale=speed.clamp(1,5).square().unsqueeze(-1)
  error=(action[...,1]-target_action[...,1])*space.curvature_std.to(action.device)*scale
  return immediate_command_loss(error)


def held_brake_margin_loss(action,space):
  """Learn a small brake margin on stationary, prohibited-motion references.

  A zero-acceleration target has no margin against small positive command
  errors accumulating into creep. This label-only term applies after an
  observed completed stop, and never supplies a stop flag at inference.
  """
  import torch
  acceleration=action[...,0]*space.accel_std.to(action.device)+space.accel_mean.to(action.device)
  return 50*torch.relu(acceleration[:,:10]+.1).square().mean()


def save_epoch_checkpoint(model,output,epoch,metrics,*,dataset_sha256,parent_sha256,objective_revision):
  """Keep every completed epoch available for the authoritative driving suite.

  Validation ranking may reject a model without testing it in closed loop.
  Keep its exact weights without promoting it or overwriting another epoch.
  """
  from safetensors.torch import save_file
  from tools.training_studio.teacher_lora import adapter_parameters
  from tools.training_studio.store import write_json
  path=Path(output)/f'epoch-{epoch:03d}.safetensors'
  if path.exists():raise FileExistsError('completed epoch checkpoints are immutable')
  save_file({name:p.detach().float().cpu().contiguous() for name,p in adapter_parameters(model).items()},str(path))
  pointer={'file':path.name,'epoch':epoch,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'metrics':metrics,
    'dataset_sha256':dataset_sha256,'parent_sha256':parent_sha256,'objective_revision':objective_revision,
    'script_sha256':IMPLEMENTATION_SHA256,'driving_qualified':False}
  write_json(path.with_suffix('.json'),pointer)
  return pointer


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
  parser.add_argument('--learning-rate',type=float)
  parser.add_argument('--paired-stop-go',action='store_true',help='Pair stop/proceed gradients with PCGrad and guarded SGD')
  parser.add_argument('--unit-task-gradients',action='store_true',help='Balance stop/proceed gradient norms before paired projection')
  parser.add_argument('--expanded-expert',action='store_true')
  parser.add_argument('--executed-commands',action='store_true',help='Supervise immediate steering and all permitted acceleration commands, with stationary hold margin')
  parser.add_argument('--balanced-stop-modes',action='store_true',help='Balance held, approaching and early-stopped recovery references; train non-held stops inside the legal zone')
  parser.add_argument('--lease',type=Path)
  args=parser.parse_args()
  if args.balanced_stop_modes and not (args.executed_commands and args.paired_stop_go and args.unit_task_gradients):raise ValueError('balanced recovery requires executed commands and paired unit gradients')
  objective_revision=RECOVERY_OBJECTIVE_REVISION if args.balanced_stop_modes else EXECUTED_OBJECTIVE_REVISION if args.executed_commands else OBJECTIVE_REVISION
  if args.unit_task_gradients and not args.paired_stop_go: raise ValueError('task gradient balancing requires paired stop/go training')
  optimization_profile=('paired_unit_gradient_pcgrad_sgd_v2' if args.unit_task_gradients else 'paired_stop_go_pcgrad_sgd_v1') if args.paired_stop_go else 'single_sample_adamw_backtracking_v1'
  if args.balanced_stop_modes:optimization_profile='paired_balanced_stop_modes_pcgrad_sgd_v3'
  if args.learning_rate is None: args.learning_rate=.01 if args.paired_stop_go else 3e-5
  if not 0<args.learning_rate<=(.1 if args.paired_stop_go else .001): raise ValueError('invalid optimizer learning rate')
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
  from tools.training_studio.teacher_lora import install,load,expand,adapter_parameters
  from tools.training_studio.store import write_json
  args.output.mkdir(parents=True,exist_ok=False)
  prefix_directory=tempfile.TemporaryDirectory(prefix='prefix-',dir=args.output)
  prefix_root=Path(prefix_directory.name)
  cuda_total=torch.cuda.get_device_properties(0).total_memory
  cuda_budget=min(24*1024**3,int(.9*cuda_total))
  torch.cuda.set_per_process_memory_fraction(cuda_budget/cuda_total)
  torch.manual_seed(42)
  model,_=load_model('/teacher/model',device='cuda',dtype='bfloat16',attn_implementation='sdpa')
  if args.parent:
    if args.parent_sha256 and hashlib.sha256(args.parent.read_bytes()).hexdigest()!=args.parent_sha256:
      raise ValueError('teacher parent hash changed')
    load(model,args.parent)
  else: install(model)
  if args.expanded_expert: expand(model)
  # A saved visual-decision adapter is part of the parent, but this stage
  # optimizes the expert against its newly generated, frozen contexts only.
  model.vlm.requires_grad_(False)
  from tools.training_studio.teacher_motion import install as install_motion
  install_motion(model.expert.action_space)
  model.eval()
  parameters={name:p for name,p in model.named_parameters() if p.requires_grad}
  adapter_scope='actual_Edge_expert_and_VLM_LoRA' if any(name.startswith('vlm.') for name in adapter_parameters(model)) else 'actual_Edge_expert_expanded_LoRA'
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
  history=[];checkpoints=[]
  def emit(phase,**fields):
    value={'phase':phase,'optimization_profile':optimization_profile,'learning_rate':args.learning_rate,'adapter_scope':adapter_scope,'stage':None,'objective_revision':objective_revision,'epochs':args.epochs,'history':history,'latest_checkpoint':checkpoints[-1] if checkpoints else None,'updated':time.time(),
      'cuda_budget_gib':cuda_budget/1024**3,'cuda_allocated_gib':torch.cuda.memory_allocated()/1024**3,
      'cuda_reserved_gib':torch.cuda.memory_reserved()/1024**3,'cuda_peak_allocated_gib':torch.cuda.max_memory_allocated()/1024**3,**fields}
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
    item['observed_speed_mps']=float(torch.linalg.vector_norm(item['ego_history_xyz'][...,-1,:2]-item['ego_history_xyz'][...,-2,:2],dim=-1).max()/model.expert.action_space.dt)
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
    load_prefix.cache_clear()
    release_prefix_pages(spilled['prefix_path'])
    torch.cuda.empty_cache()
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
    if not item['row']['stop_required'] or not item['row'].get('maintain_stop_reference',False):
      loss=loss+proceed_velocity_loss(velocity,ref_velocity)
    if item['row'].get('restart_required') or (args.executed_commands and not item['row']['stop_required']):
      accel_std=model.expert.action_space.accel_std.to(action.device)
      restart_error=(action[...,0]-item['target_action'].to(action.device)[...,0])*accel_std
      loss=loss+restart_command_loss(restart_error)
    if args.executed_commands:
      loss=loss+immediate_steering_loss(action,item['target_action'].to(action.device),model.expert.action_space,item['ego_history_xyz'].to(action.device))
    if item['row']['stop_required']:
      held=(torch.linalg.vector_norm(ref_velocity,dim=-1)<.15).float()
      margin=.5 if args.balanced_stop_modes and not item['row'].get('maintain_stop_reference') else 0.
      loss=loss+stop_zone_loss(xyz,target,held,item['row']['front_distance_m'],interior_margin_m=margin)
      loss=loss+50*(velocity.square().sum(-1)*held).sum()/held.sum().clamp_min(1)
      loss=loss+200*(velocity.square().sum(-1)*held).amax()
      accel_std=model.expert.action_space.accel_std.to(action.device)
      accel_error=(action[...,0]-item['target_action'].to(action.device)[...,0])*accel_std
      # Use the same acceleration scale as restart supervision, including
      # parked holds: a speed-only hold penalty can underweight small
      # positive command pulses compared with direct restart acceleration.
      loss=loss+immediate_command_loss(accel_error)
      loss=loss+50*(accel_error[:,:20].square()*held[:,:20]).sum()/held[:,:20].sum().clamp_min(1)
      if item['row'].get('maintain_stop_reference'):
        loss=loss+held_command_loss(action,model.expert.action_space,item['ego_history_xyz'].to(action.device))
        if args.executed_commands:loss=loss+held_brake_margin_loss(action,model.expert.action_space)
      loss=loss+30*torch.relu(xyz[...,0]-item['row']['front_distance_m']+.2).square().mean()
    if not torch.isfinite(loss): raise ValueError('nonfinite actual rollout loss')
    return loss,xyz,velocity
  def validate(epoch=None):
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
        del loss,xyz,velocity
        load_prefix.cache_clear()
        release_prefix_pages(item['prefix_path'])
        torch.cuda.empty_cache()
        emit('prefill' if epoch is None else 'training',epoch=epoch or 0,
          stage='validation',validation_sample=len(values),validation_samples=len(validation),
          **({'baseline':baseline} if epoch is not None else {}))
    return {'validation_loss':float(np.mean(values)),'red_safe_count':red,'red_samples':len(hold),'red_hold_speed_mse':float(np.mean(hold)) if hold else 0.,'lateral_trajectory_mse':float(np.mean(lateral)),'stop_metric':'valid_stop_zone_v2','go_velocity_mse':float(np.mean(proceed)) if proceed else None,'go_samples':len(proceed)}
  baseline=validate()
  best_metrics,best_epoch=baseline,0
  balanced_metrics,balanced_epoch=baseline,0
  best_score=(baseline['red_safe_count'],-baseline['red_hold_speed_mse'],-baseline['validation_loss'])
  from tools.training_studio.teacher_optim import paired_indices,paired_step
  optimizer=(torch.optim.SGD if args.paired_stop_go else torch.optim.AdamW)(parameters.values(),lr=args.learning_rate,weight_decay=0)
  emit('training',epoch=0,baseline=baseline,trainable_parameters=sum(p.numel() for p in parameters.values()))
  for epoch in range(args.epochs):
    values=[]
    if args.paired_stop_go:
      pairs=paired_indices(train,epoch,balanced_stop_modes=args.balanced_stop_modes)
      for batch,(stop_index,go_index) in enumerate(pairs,1):
        outcome=paired_step(parameters,optimizer,objective,train[stop_index],train[go_index],unit_gradients=args.unit_task_gradients)
        values.append(outcome['loss'])
        emit('training',epoch=epoch+1,batch=batch,batches=len(pairs),batch_examples=2,baseline=baseline,**outcome)
    else:
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
        del loss,_
        load_prefix.cache_clear()
        release_prefix_pages(train[index]['prefix_path'])
        torch.cuda.empty_cache()
        emit('training',epoch=epoch+1,batch=batch+1,batches=len(train),loss=values[-1],loss_before_step=initial_loss,step_scale=scale,baseline=baseline)
    metrics=validate(epoch+1)
    history.append({'epoch':epoch+1,'train_loss':float(np.mean(values)),**metrics})
    checkpoints.append(save_epoch_checkpoint(model,args.output,epoch+1,history[-1],
      dataset_sha256=hashlib.sha256((args.data/'manifest.json').read_bytes()).hexdigest(),
      parent_sha256=hashlib.sha256(args.parent.read_bytes()).hexdigest() if args.parent else None,objective_revision=objective_revision))
    score=(metrics['red_safe_count'],-metrics['red_hold_speed_mse'],-metrics['validation_loss'])
    if score>best_score:
      best_score=score
      best_metrics,best_epoch=metrics,epoch+1
      save_file({name:p.detach().float().cpu().contiguous() for name,p in adapter_parameters(model).items()},str(args.output/'best.safetensors'))
    if metrics['validation_loss']<balanced_metrics['validation_loss']:
      balanced_metrics,balanced_epoch=metrics,epoch+1
      save_file({name:p.detach().float().cpu().contiguous() for name,p in adapter_parameters(model).items()},str(args.output/'balanced.safetensors'))
    emit('training',epoch=epoch+1,baseline=baseline,**metrics)
  write_json(args.output/'result.json',{'revision':MODEL_REVISION,'baseline':baseline,'best':best_metrics,'best_epoch':best_epoch,
    'balanced_best':balanced_metrics,'balanced_epoch':balanced_epoch,'balanced_adapter_saved':(args.output/'balanced.safetensors').is_file(),
    'history':history,'checkpoints':checkpoints,'adapter_saved':(args.output/'best.safetensors').is_file(),'qualified':False,'objective':'actual_ten_step_Euler_rollout',
    'objective_revision':objective_revision,'adapter_scope':adapter_scope,'optimization_profile':optimization_profile,'learning_rate':args.learning_rate,
    'script_sha256':IMPLEMENTATION_SHA256,'dataset_sha256':hashlib.sha256((args.data/'manifest.json').read_bytes()).hexdigest(),
    'parent_sha256':hashlib.sha256(args.parent.read_bytes()).hexdigest() if args.parent else None,'official_sampling_max_error':sampling_error,
    'disk_sampling_max_error':disk_difference})
  emit('completed',epoch=args.epochs,baseline=baseline)
  load_prefix.cache_clear()
  prefix_directory.cleanup()


if __name__=='__main__': main()
