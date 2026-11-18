"""Offline visual-decision supervision; only original closed-loop tests grant qualification."""
import argparse
import hashlib
import json
from pathlib import Path
import time


def maneuver_class(row):
  if row['stop_required']: return 'wait'
  if row['scenario'] in ('left_turn','yield_left','left_arrow'): return 'left'
  if row['scenario'] in ('right_turn','yield_right','right_arrow'): return 'right'
  if row['scenario'] in ('lane_center','pedestrian','red_light'): return 'straight'
  raise ValueError('unsupported driving reference')


def balanced_maneuver_weights(rows):
  from collections import Counter
  counts=Counter(maneuver_class(row) for row in rows)
  if set(counts)!={'wait','left','right','straight'}: raise ValueError('all four maneuver classes required')
  return {key:len(rows)/(4*count) for key,count in counts.items()}


def balanced_scene_weights(rows):
  """Keep four decisions equal, then preserve rare visual conditions within each."""
  from collections import Counter
  balanced_maneuver_weights(rows)
  counts=Counter((maneuver_class(row),row['scenario']) for row in rows)
  scenes=Counter(key[0] for key in counts)
  return {key[0]+':'+key[1]:len(rows)/(4*scenes[key[0]]*count) for key,count in counts.items()}


def navigation_order(rows,epoch):
  """Balance actual exposure; scalar single-example weights can vanish at clipping.

  Cycle shuffled members rather than discarding common references. Epoch offsets
  continue those cycles, so later epochs visit the rest of each scene's data.
  """
  import numpy as np
  balanced_maneuver_weights(rows)
  rng=np.random.default_rng(42);groups={key:{} for key in ('wait','straight','left','right')}
  for index,row in enumerate(rows):groups[maneuver_class(row)].setdefault(row['scenario'],[]).append(index)
  prepared={}
  for key,scenes in groups.items():
    names=rng.permutation(sorted(scenes)).tolist()
    prepared[key]=[rng.permutation(scenes[name]).tolist() for name in names]
  per_class=(len(rows)+3)//4;result=[]
  keys=np.random.default_rng(epoch+42).permutation(list(groups)).tolist()
  for step in range(per_class):
    slot=epoch*per_class+step
    for key in keys:
      scenes=prepared[key];members=scenes[slot%len(scenes)]
      result.append(members[(slot//len(scenes))%len(members)])
  return result


def decision_text(row,navigation_balanced=False):
  scenario=row['scenario']
  if row['stop_required']:
    if scenario=='pedestrian': return 'Wait before the crossing until the pedestrian has completely left the roadway.'
    if scenario=='red_light': return 'Wait before the stop line until the traffic signal permits proceeding.'
    if scenario in ('left_arrow','right_arrow'): return 'Wait before the stop line until the turn arrow permits the requested turn.'
    if scenario in ('yield_left','yield_right'): return 'Wait before the intersection until the crossing traffic has cleared.'
    raise ValueError('unsupported stopped reference')
  if scenario in ('left_turn','yield_left','left_arrow'): return 'Left turn along the requested route while staying in the lane.' if navigation_balanced else 'Proceed with the requested left turn while staying in the lane.'
  if scenario in ('right_turn','yield_right','right_arrow'): return 'Right turn along the requested route while staying in the lane.' if navigation_balanced else 'Proceed with the requested right turn while staying in the lane.'
  if scenario in ('lane_center','pedestrian','red_light'): return 'Proceed straight along the current lane because the roadway ahead is clear.'
  raise ValueError('unsupported driving reference')


def decision_objective(logits,target):
  import torch.nn.functional as F
  ce=F.cross_entropy(logits.float().reshape(-1,logits.shape[-1]),target.reshape(-1))
  decision=F.cross_entropy(logits[:,0].float(),target[:,0])
  return ce+4*decision,ce,decision


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--data',type=Path,required=True)
  parser.add_argument('--output',type=Path,required=True)
  parser.add_argument('--parent',type=Path,required=True)
  parser.add_argument('--parent-sha256',required=True)
  parser.add_argument('--epochs',type=int,default=12)
  parser.add_argument('--learning-rate',type=float,default=1e-5)
  parser.add_argument('--navigation-balanced',action='store_true',help='Balance Wait/Proceed/Left/Right with distinct first decision tokens')
  parser.add_argument('--balanced-sampling',action='store_true',help='Balance actual maneuver/scene exposure, not single-example gradient magnitudes')
  args=parser.parse_args()
  if args.balanced_sampling and not args.navigation_balanced: raise ValueError('balanced sampling requires the four-class navigation profile')
  import numpy as np
  import torch
  from torch import nn
  from safetensors.torch import save_file
  from alpamayo2_edge.checkpoint import load_model
  from alpamayo2_edge.helper import get_processor,to_device
  from alpamayo2_edge.models.alpamayo2_edge import fuse_traj_tokens
  from alpamayo2_edge.inference import predict,validate_predictions
  from tools.training_studio.edge_inputs import prepare_front_inputs
  from tools.training_studio.teacher_train import observed_inputs
  from tools.training_studio.teacher_lora import DeltaLinear,load,reasoning_path,adapter_parameters
  from tools.training_studio.teacher_motion import install as install_motion
  from tools.training_studio.store import write_json
  if not 1<=args.epochs<=100 or not 0<args.learning_rate<=1e-3: raise ValueError('invalid training settings')
  if hashlib.sha256(args.parent.read_bytes()).hexdigest()!=args.parent_sha256: raise ValueError('parent adapter hash mismatch')
  args.output.mkdir(exist_ok=False)
  manifest=json.loads((args.data/'manifest.json').read_text());rows=manifest['samples']
  if manifest.get('data_source')!='simulation_only': raise ValueError('decision labels require verified offline simulation references')
  if {r['seed'] for r in rows}&{300,301,302,303}: raise ValueError('qualification observations must remain held out')
  train=[r for r in rows if r['split']=='train'];validation=[r for r in rows if r['split']=='validation']
  if not train or not validation or {r['seed'] for r in train}&{r['seed'] for r in validation}: raise ValueError('independent train and validation seeds required')
  train_weights=balanced_scene_weights(train) if args.navigation_balanced else {}
  validation_weights=balanced_scene_weights(validation) if args.navigation_balanced else {}
  objective_name='balanced_Wait_Proceed_Left_Right_first_decision_CE_v2' if args.navigation_balanced else 'token_CE_plus_4x_first_decision_CE_v1'
  if args.balanced_sampling:
    train_weights={};objective_name='balanced_scene_sampled_Wait_Proceed_Left_Right_CE_v3'
  sampling_profile='four_maneuver_scene_round_robin_v1' if args.balanced_sampling else 'single_pass_shuffle_v1'
  if {r['pixel_sha256'] for r in train}&{r['pixel_sha256'] for r in validation}: raise ValueError('duplicate images across splits')
  for row in rows:
    path=(args.data/row['file']).resolve()
    if not path.is_relative_to(args.data.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']: raise ValueError('packet path/hash mismatch')
    decision_text(row,args.navigation_balanced)
  torch.cuda.set_per_process_memory_fraction(min(.9,16*1024**3/torch.cuda.get_device_properties(0).total_memory));torch.manual_seed(42)
  model,_=load_model('/teacher/model',device='cuda',dtype='bfloat16',attn_implementation='sdpa')
  load(model,args.parent);model.requires_grad_(False);model.eval();install_motion(model.expert.action_space)
  paths=[]
  for name,module in list(model.named_modules()):
    if not reasoning_path(model,name): continue
    if isinstance(module,nn.Linear):
      parent,_,leaf=name.rpartition('.');module=DeltaLinear(module);setattr(model.get_submodule(parent),leaf,module)
    if not isinstance(module,DeltaLinear): raise ValueError('unsupported reasoning adapter topology')
    module.a.requires_grad_(True);module.b.requires_grad_(True);paths.append(name)
  if len(paths)!=8: raise ValueError('expected eight final-four query/value projections')
  params={name:p for name,p in model.named_parameters() if p.requires_grad}
  if not params or any(not name.startswith('vlm.') for name in params): raise ValueError('only visual decision deltas may be optimized')
  processor=get_processor(model.tokenizer,model.config);history=[]
  def emit(phase,**fields):
    value={'phase':phase,'updated':time.time(),'epochs':args.epochs,'history':history,'experiment_only':True,'qualified':False,
      'objective':objective_name,'sampling_profile':sampling_profile,'maneuver_class_weights':train_weights,'trainable_parameters':sum(p.numel() for p in params.values()),
      'cuda_peak_gib':torch.cuda.max_memory_allocated()/1024**3,**fields}
    write_json(args.output/'progress.json',value)
    print(json.dumps({k:v for k,v in value.items() if k!='history'}),flush=True)
  def sample(row):
    with np.load(args.data/row['file'],allow_pickle=False) as packet: s={k:np.array(v,copy=True) for k,v in observed_inputs(packet).items()}
    s['nav_text']=[str(s['nav_text'].item())];return s
  if args.navigation_balanced:
    first={key:model.tokenizer.encode(decision_text(next(row for row in train if maneuver_class(row)==key),True),add_special_tokens=False)[0] for key in ('wait','straight','left','right')}
    if len(set(first.values()))!=4: raise ValueError('four distinct first decision tokens required')
  def objective(row,weights):
    prepared=to_device(prepare_front_inputs(sample(row),model.config,model.tokenizer,processor=processor),device='cuda');inputs=dict(prepared['tokenized_data'])
    with torch.no_grad(): inputs['input_ids']=fuse_traj_tokens(model.history_traj_tokenizer,model.future_traj_tokenizer,inputs['input_ids'],{k:prepared[k] for k in ('ego_history_xyz','ego_history_rot')},model.config.traj_ids)
    target=torch.tensor([model.tokenizer.encode(decision_text(row,args.navigation_balanced),add_special_tokens=False)+[model.config.traj_ids['future_start']]],device='cuda')
    inputs['input_ids']=torch.cat((inputs['input_ids'],target),dim=1)
    for key in ('attention_mask','mm_token_type_ids'):
      if key in inputs: inputs[key]=torch.cat((inputs[key],torch.ones_like(target) if key=='attention_mask' else torch.zeros_like(target)),dim=1)
    model.vlm.model.rope_deltas=None
    with torch.autocast('cuda',dtype=torch.bfloat16):
      hidden=model.vlm.model(**inputs,use_cache=False,return_dict=True).last_hidden_state[:,-target.shape[1]-1:-1]
      logits=model.vlm.get_output_embeddings()(hidden)
      loss,ce,decision=decision_objective(logits,target)
    correct=int(logits[:,0].argmax(-1).eq(target[:,0]).all())
    return loss*weights.get(maneuver_class(row)+':'+row['scenario'],1.),ce,decision,correct
  def validate(epoch):
    losses=[];ces=[];decisions=[];correct=0;classes={};maneuvers={}
    with torch.no_grad():
      for index,row in enumerate(validation):
        loss,ce,decision,right=objective(row,validation_weights)
        values=[float(loss),float(ce),float(decision)]
        if not np.isfinite(values).all(): raise ValueError('nonfinite validation loss')
        losses.append(values[0]);ces.append(values[1]);decisions.append(values[2]);correct+=right
        key=row['scenario']+('_stop' if row['stop_required'] else '_go');c=classes.setdefault(key,{'correct':0,'samples':0,'decision_ce_sum':0.});c['correct']+=right;c['samples']+=1;c['decision_ce_sum']+=values[2]
        group=maneuvers.setdefault(maneuver_class(row),{'correct':0,'samples':0});group['correct']+=right;group['samples']+=1
        del loss,ce,decision;torch.cuda.empty_cache();emit('validation',epoch=epoch,sample=index+1,samples=len(validation))
    return {'validation_loss':float(np.mean(losses)),'ce':float(np.mean(ces)),'decision_ce':float(np.mean(decisions)),'decision_correct':correct,'decision_samples':len(validation),'decision_metric':'exact_first_target_token_v1','maneuver_classes':maneuvers,'balanced_first_token_accuracy':float(np.mean([v['correct']/v['samples'] for v in maneuvers.values()])),'classes':{k:{'correct':v['correct'],'samples':v['samples'],'decision_ce':v['decision_ce_sum']/v['samples']} for k,v in classes.items()}}
  def generation(epoch):
    selected=[]
    for key in sorted({(r['scenario'],r['stop_required']) for r in validation}): selected.extend([r for r in validation if (r['scenario'],r['stop_required'])==key][:2])
    results=[];settings={'seed':42,'num_traj_sets':1,'num_traj_samples':1,'top_p':.98,'top_k':None,'temperature':.6,'max_generation_length':256,'diffusion_kwargs':{'inference_step':10}}
    with torch.inference_mode():
      for index,row in enumerate(selected):
        inputs=to_device(prepare_front_inputs(sample(row),model.config,model.tokenizer,processor=processor),device='cuda')
        try:
          xyz,rot,extra=predict(model,inputs,settings,'cuda');validate_predictions(xyz,rot,1,1)
          result={'success':True,'cot':str(np.asarray(extra.get('cot','')).reshape(-1)[0]),'forward_2s_m':float(xyz.reshape(64,3)[19,0])}
        except ValueError as error: result={'success':False,'error':str(error)}
        results.append({**result,'seed':row['seed'],'scenario':row['scenario'],'stop_required':row['stop_required'],'source_sha256':row['sha256']});emit('generation',epoch=epoch,sample=index+1,samples=len(selected));torch.cuda.empty_cache()
    write_json(args.output/f'generation-{epoch:03d}.json',results)
  emit('initializing',epoch=0);baseline=validate(0);history.append({'epoch':0,**baseline});generation(0)
  def score(metrics):return (metrics['balanced_first_token_accuracy'] if args.navigation_balanced else metrics['decision_correct'],-metrics['validation_loss'])
  best=score(baseline);best_epoch=0
  def save(): save_file({k:p.detach().float().cpu().contiguous() for k,p in adapter_parameters(model).items()},str(args.output/'best.safetensors'))
  save();optimizer=torch.optim.AdamW(params.values(),lr=args.learning_rate,weight_decay=0)
  for epoch in range(1,args.epochs+1):
    values=[];ces=[]
    order=navigation_order(train,epoch-1) if args.balanced_sampling else np.random.default_rng(42+epoch).permutation(len(train))
    for batch,index in enumerate(order,1):
      optimizer.zero_grad(set_to_none=True);loss,ce,decision,_=objective(train[index],train_weights);value=float(loss.detach());ce_value=float(ce.detach())
      if not np.isfinite(value): raise ValueError('nonfinite decision loss')
      loss.backward();norm=torch.nn.utils.clip_grad_norm_(params.values(),1.)
      if not torch.isfinite(norm) or norm<=0: raise ValueError('invalid visual decision gradient')
      optimizer.step();values.append(value);ces.append(ce_value);del loss,ce,decision;torch.cuda.empty_cache();emit('training',epoch=epoch,batch=batch,batches=len(order),loss=value,ce=ce_value)
    metrics=validate(epoch);history.append({'epoch':epoch,'train_loss':float(np.mean(values)),'train_ce':float(np.mean(ces)),**metrics})
    candidate_score=score(metrics)
    if candidate_score>best: best,best_epoch=candidate_score,epoch;save()
    generation(epoch);emit('training',epoch=epoch)
  write_json(args.output/'result.json',{'history':history,'best_epoch':best_epoch,'adapter_sha256':hashlib.sha256((args.output/'best.safetensors').read_bytes()).hexdigest(),
    'parent_sha256':args.parent_sha256,'dataset_sha256':hashlib.sha256((args.data/'manifest.json').read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'objective':objective_name,'sampling_profile':sampling_profile,'maneuver_class_weights':train_weights,'qualification_granted':False,'live_service_changed':False,'paths':paths})
  emit('completed',epoch=args.epochs)


if __name__=='__main__': main()
