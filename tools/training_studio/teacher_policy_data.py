"""Replay observed teacher-policy states to create offline-only corrective labels."""
import argparse
import hashlib
import json
from pathlib import Path

from tools.training_studio.edge_inputs import MODEL_REVISION
from tools.training_studio.store import read_json,write_json
from tools.training_studio.teacher_train import observed_inputs
from tools.training_studio.teacher_standstill import hold_acceleration,in_stop_zone,PROFILE as HOLD_PROFILE


def check_source(result,health,split):
  seed=result.get('seed',-1)
  valid_seed=(1000<=seed<7000) if split=='train' else (8000<=seed<9500) if split=='validation' else False
  provenance=health.get('provenance',{})
  fingerprint=hashlib.sha256(json.dumps(provenance,sort_keys=True).encode()).hexdigest()
  if not valid_seed: raise ValueError('policy supervision must use separate training/validation seeds')
  # Simple turns have no moving permission/actor state to anticipate. Yield and
  # arrow cases still require their own observed-actor freezing implementation.
  if (result.get('scenario') not in ('red_light','pedestrian','lane_center','left_turn','right_turn') or result.get('backend')!='nvidia_alpamayo2_edge' or result.get('revision')!=MODEL_REVISION
      or result.get('scripted_fallback') is not False or result.get('model_inputs_include_signal_ground_truth') is not False
      or result.get('model_provenance_sha256')!=fingerprint or provenance.get('weights_verified') is not True
      or provenance.get('revision')!=MODEL_REVISION or provenance.get('camera_ids')!=[1,6]):
    raise ValueError('policy source is not a bound, observed-only Edge episode')
  return fingerprint


def reference(episode,index,output,split,assets):
  import numpy as np
  from openpilot.tools.sim.training.capture_teacher import rotation
  from openpilot.tools.sim.training.scene import Scene,DT
  episode,output=Path(episode),Path(output)
  result=read_json(episode/'result.json');health=read_json(episode/'provenance.json')
  fingerprint=check_source(result,health,split)
  source=episode/f'input-{index:03d}.npz'
  prediction=read_json(episode/f'prediction-{index:03d}.json')
  source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
  if prediction.get('input_sha256')!=source_hash or prediction.get('scripted_fallback') is not False:
    raise ValueError('policy prediction is not bound to the actual observed packet')
  with np.load(source,allow_pickle=False) as packet: sample=observed_inputs(packet)
  sample={key:np.array(value,copy=True) for key,value in sample.items()}
  moment=result['plans'][index]['time'];steps=round(moment/DT)
  trace=[json.loads(line) for line in (episode/'trace.jsonl').read_text().splitlines()]
  if not 0<steps<=len(trace): raise ValueError('policy trace does not cover the selected packet')
  scene=Scene(result['scenario'],result['seed'],str(assets))
  try:
    scene.vehicle.set_position(scene.first_lane.position(scene.stop_s-20,0))
    scene.previous_position=np.array(scene.vehicle.position)
    scene.green_at=result['signal_green_at_s'];scene.update_actors()
    for observation in scene.env.observations.values(): observation.observe=lambda *args,**kwargs:{}
    positions=[np.array([*scene.vehicle.position,0])];rotations=[rotation(scene.vehicle.heading_theta)]
    for step,row in enumerate(trace[:steps],1):
      scene.step(np.array(row['action'],np.float32))
      if step%2==0:
        positions.append(np.array([*scene.vehicle.position,0]));rotations.append(rotation(scene.vehicle.heading_theta))
    expected=trace[steps-1];_,_,lateral,progress,speed=scene.state()
    origin=np.array([*scene.vehicle.position,0]);orientation=rotation(scene.vehicle.heading_theta)
    xyz_history=np.array([(p-origin)@orientation for p in positions[-20:]])
    rot_history=np.array([orientation.T@r for r in rotations[-20:]])
    errors={'speed_mps':abs(speed-expected['speed_mps']),'progress_m':abs(progress-expected['progress_m']),
      'lateral_m':abs(lateral-expected['lane_offset_m']),
      'history_position_m':float(np.max(np.abs(xyz_history-sample['ego_history_xyz'][0,0]))),
      'history_rotation':float(np.max(np.abs(rot_history-sample['ego_history_rot'][0,0])))}
    if max(errors.values())>.002: raise ValueError('physics replay differs from observed policy history: '+str(errors))
    front=scene.stop_s-progress-scene.vehicle.LENGTH/2
    heading_change=abs((scene.vehicle.heading_theta-scene.initial_heading+np.pi)%(2*np.pi)-np.pi)
    blocked=scene.blocked()
    maintain=blocked and in_stop_zone(scene)
    # Freeze a still-crossing actor at its observed position for offline labels.
    # Moving its clearance clock alone would teleport it back across the road.
    # Neither the future permission nor these label-only flags enter inference.
    freeze_actor=blocked and result['scenario']=='pedestrian'
    if freeze_actor:
      actor_position=np.array(scene.pedestrian.position)
      scene.green_at=1e6
      scene.update_actors=lambda:scene.pedestrian.set_position(actor_position)
    elif blocked: scene.green_at=1e6
    scene.update_actors();xyz=[];rot=[]
    latched_stop=maintain
    for step in range(128):
      latched_stop=latched_stop or (scene.blocked() and in_stop_zone(scene))
      action=scene.expert()
      if latched_stop and scene.blocked(): action[1]=hold_acceleration(scene.vehicle.velocity,scene.vehicle.heading)
      scene.step(action)
      if step%2==1:
        xyz.append((np.array([*scene.vehicle.position,0])-origin)@orientation)
        rot.append(orientation.T@rotation(scene.vehicle.heading_theta))
    output.mkdir(parents=True,exist_ok=False)
    terminal=scene.state();terminal_front=scene.stop_s-terminal[3]-scene.vehicle.LENGTH/2
    if scene.failures:
      row={'rejected':True,'seed':result['seed'],'source_simulation_time_s':moment,'failures':sorted(scene.failures)}
    else:
      sample.update(future_xyz=np.array(xyz,np.float32)[None],future_rot=np.array(rot,np.float32)[None])
      path=output/'sample.npz';np.savez_compressed(path,**sample)
      row={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'seed':result['seed'],'split':split,
        'scenario':result['scenario'],'mode':'on_policy','stop_required':blocked,'restart_required':not blocked and speed<.2,
        'front_distance_m':front,'maintain_stop_reference':maintain,
        'pixel_sha256':hashlib.sha256(sample['image_frames'].tobytes()).hexdigest(),'source_input_sha256':source_hash,
        'source_teacher_provenance_sha256':fingerprint,'source_simulation_time_s':moment,'physics_replay_errors':errors,
        'source_lateral_error_m':lateral,'source_heading_change_rad':float(heading_change),
        'hold_control_profile':HOLD_PROFILE,
        'reference_terminal_front_distance_m':terminal_front,'reference_terminal_speed_mps':terminal[-1],
        'future_permission_frozen_for_red_supervision':blocked and result['scenario']=='red_light',
        'future_actor_motion_frozen':freeze_actor,'source_episode_status':result['status'],
        'reference_generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    write_json(output/'sample.json',row)
    return row
  finally: scene.close()


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--episode',type=Path,required=True)
  parser.add_argument('--index',type=int,required=True)
  parser.add_argument('--output',type=Path,required=True)
  parser.add_argument('--split',choices=('train','validation'),required=True)
  parser.add_argument('--assets',type=Path,default=Path('build/official-sim/full-assets/assets'))
  args=parser.parse_args()
  row=reference(args.episode,args.index,args.output,args.split,args.assets)
  print(json.dumps({key:row[key] for key in ('seed','source_simulation_time_s','rejected','physics_replay_errors') if key in row}))


if __name__=='__main__': main()
