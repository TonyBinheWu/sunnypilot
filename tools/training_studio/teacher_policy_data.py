"""Replay observed teacher-policy states to create offline-only corrective labels."""
import argparse
import hashlib
import json
from pathlib import Path

from tools.training_studio.edge_inputs import MODEL_REVISION
from tools.training_studio.store import read_json,write_json
from tools.training_studio.teacher_train import observed_inputs
from tools.training_studio.teacher_standstill import (hold_acceleration,in_stop_zone,PROFILE as HOLD_PROFILE,
  gentle_recovery_acceleration,RECOVERY_PROFILE,RECOVERY_INTERIOR_MARGIN_M)

REFERENCE_PROFILE="history_confirmed_red_stop_and_gentle_boundary_v2"


def check_source(result,health,split):
  seed=result.get('seed',-1)
  valid_seed=(1000<=seed<7000) if split=='train' else (8000<=seed<9500) if split=='validation' else False
  provenance=health.get('provenance',{})
  fingerprint=hashlib.sha256(json.dumps(provenance,sort_keys=True).encode()).hexdigest()
  if not valid_seed: raise ValueError('policy supervision must use separate training/validation seeds')
  if (result.get('scenario') not in ('red_light','pedestrian','lane_center','left_turn','right_turn','yield_left','yield_right','left_arrow','right_arrow') or result.get('backend')!='nvidia_alpamayo2_edge' or result.get('revision')!=MODEL_REVISION
      or result.get('scripted_fallback') is not False or result.get('model_inputs_include_signal_ground_truth') is not False
      or result.get('model_provenance_sha256')!=fingerprint or provenance.get('weights_verified') is not True
      or provenance.get('revision')!=MODEL_REVISION or provenance.get('camera_ids')!=[1,6]):
    raise ValueError('policy source is not a bound, observed-only Edge episode')
  return fingerprint


def freeze_observed_permission(scene,scenario):
  """Keep blocked offline futures at the actor/permission actually observed."""
  if not scene.blocked():return False
  import numpy as np
  actor=(scene.pedestrian if scenario=='pedestrian' else scene.opponent if scenario in ('yield_left','yield_right') else None)
  # Changing the clearance clock without freezing the actor would teleport it
  # to an earlier crossing phase. This affects future supervision only.
  if actor is not None:
    position=np.array(actor.position,copy=True)
    heading=float(actor.heading_theta) if scenario in ('yield_left','yield_right') else None
    def hold_actor():
      actor.set_position(position.copy())
      if heading is not None:actor.set_heading_theta(heading)
    scene.update_actors=hold_actor
  scene.green_at=1e6
  # Arrow scenes retain the original light updater; the observed forbidden
  # arrow stays forbidden throughout the label without anticipating its change.
  return actor is not None


def maintain_reference(scenario,blocked,current_stopped,front_distance,source_stop_audit):
  """Retain an earlier original red-stop confirmation while correcting creep.

  A source's past hold violation stays in its audit; future supervision must
  brake back to rest instead of relaunching toward a nearer stopping point.
  Permission release and leaving the legal stop zone never inherit a hold.
  """
  confirmed=source_stop_audit and source_stop_audit.get('red_stop_confirmed_at_s') is not None
  return bool(blocked and 0<=front_distance<5 and (current_stopped or (scenario=='red_light' and confirmed)))


def reference(episode,index,output,split,assets,*,turn_reference_speed_mps=None):
  import numpy as np
  episode,output=Path(episode),Path(output)
  result=read_json(episode/'result.json');health=read_json(episode/'provenance.json')
  fingerprint=check_source(result,health,split)
  if turn_reference_speed_mps is not None and (result.get('scenario') not in ('left_turn','right_turn') or not np.isfinite(turn_reference_speed_mps) or not 1<=turn_reference_speed_mps<=5):
    raise ValueError('turn reference speed must be finite in [1,5] for a simple turn')
  from openpilot.tools.sim.training.capture_teacher import rotation
  from openpilot.tools.sim.training.scene import Scene,DT
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
    source_stop_audit=None
    if result['scenario']=='red_light':
      from openpilot.tools.sim.training.edge_stop_audit import red_wait_audit
      source_stop_audit=red_wait_audit(trace[:steps],result['signal_green_at_s'],scene.stop_s,scene.vehicle.LENGTH)
    current_stopped=in_stop_zone(scene)
    maintain=maintain_reference(result['scenario'],blocked,current_stopped,front,source_stop_audit)
    historical_latch_used=maintain and not current_stopped
    gentle=blocked and result['scenario']=='red_light' and 5<=front<=6 and not maintain
    freeze_actor=freeze_observed_permission(scene,result['scenario'])
    scene.update_actors();xyz=[];rot=[]
    latched_stop=maintain
    for step in range(128):
      ready=in_stop_zone(scene)
      current_front=scene.stop_s-scene.state()[3]-scene.vehicle.LENGTH/2
      if gentle:ready=ready and current_front<=5-RECOVERY_INTERIOR_MARGIN_M
      latched_stop=latched_stop or (scene.blocked() and ready)
      action=scene.expert()
      if gentle and not latched_stop and scene.blocked():
        action[1]=gentle_recovery_acceleration(scene.vehicle.velocity,scene.vehicle.heading,current_front)
      if turn_reference_speed_mps is not None:
        # Offline corrective labels only: retain the original steering policy,
        # and test whether a slower turn is physically recoverable. Observed
        # history, source controls and every original failure flag stay intact.
        speed=scene.state()[-1]
        action[1]=min(action[1],float(np.clip((turn_reference_speed_mps-speed)*1.5,-3.5,1.6)))
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
        'hold_control_profile':HOLD_PROFILE,'label_policy_profile':REFERENCE_PROFILE,
        'source_red_wait_audit':source_stop_audit,'historical_stop_latch_used':historical_latch_used,
        **({'recovery_reference_profile':RECOVERY_PROFILE,'stop_interior_margin_m':RECOVERY_INTERIOR_MARGIN_M} if gentle else {}),
        'turn_reference_speed_mps':turn_reference_speed_mps,
        'reference_terminal_front_distance_m':terminal_front,'reference_terminal_speed_mps':terminal[-1],
        'future_permission_frozen_for_red_supervision':blocked and result['scenario']=='red_light',
        'future_permission_frozen_for_supervision':blocked,
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
  parser.add_argument('--turn-reference-speed-mps',type=float,help='Optional offline speed cap for physically checked simple-turn correction labels')
  args=parser.parse_args()
  row=reference(args.episode,args.index,args.output,args.split,args.assets,turn_reference_speed_mps=args.turn_reference_speed_mps)
  print(json.dumps({key:row[key] for key in ('seed','source_simulation_time_s','rejected','physics_replay_errors') if key in row}))


if __name__=='__main__': main()
