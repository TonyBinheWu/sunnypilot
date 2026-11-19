"""Independent full-route reference packets for approach, turning and turn exit.

Reference controls and route state are offline labels only. These packets never
grant qualification to a neural teacher and never change the original scorer.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

SCENARIOS=('left_turn','right_turn','yield_left','yield_right','left_arrow','right_arrow')


def relative_future(positions,rotations,times,index):
  import numpy as np
  positions=np.asarray(positions);rotations=np.asarray(rotations);times=np.asarray(times)
  if index<0 or len(positions)<index+65 or len(rotations)!=len(positions) or len(times)!=len(positions):
    raise ValueError('64 measured future poses required')
  if not np.array_equal(times[index+1:index+65]-times[index],np.arange(1,65)*100000):
    raise ValueError('reference future must be measured at 10 Hz')
  reference=rotations[index]
  xyz=((positions[index+1:index+65]-positions[index])@reference)[None].astype(np.float32)
  rot=(reference.T@rotations[index+1:index+65])[None].astype(np.float32)
  if not np.isfinite(xyz).all() or not np.isfinite(rot).all():raise ValueError('nonfinite reference future')
  return xyz,rot


def observed_stop_reference(args):
  """Branch labels from measured observations without anticipating a future green."""
  import numpy as np
  from openpilot.tools.sim.training.edge_experiment import EdgeHistory
  from openpilot.tools.sim.training.scene import Scene,DT,CASES
  from openpilot.tools.sim.training.capture_teacher import rotation
  from tools.training_studio.store import write_json
  if args.stop_time<2:raise ValueError('two seconds of observed history required')
  scene=Scene(args.scenario,args.seed,'build/official-sim/full-assets/assets');history=EdgeHistory()
  try:
    scene.vehicle.set_position(scene.first_lane.position(scene.stop_s-20,0));scene.previous_position=np.array(scene.vehicle.position)
    current_step=round(args.stop_time/DT)
    for step in range(current_step+1):
      if step%2==0 and step>=current_step-40:history.record(scene)
      if step==current_step:break
      action=np.zeros(2,np.float32) if step<40 else scene.expert()
      if step>=40 and scene.blocked() and scene.stopped:action[1]=np.clip(-1.5*scene.state()[-1],-3.5,0.)
      scene.step(action)
    if not scene.blocked():raise ValueError('counterfactual hold requires observed blocked state')
    intent=('Turn left' if CASES[args.scenario]>0 else 'Turn right')+' at the upcoming intersection. Obey signals, yield to traffic, and remain in the lane.'
    sample=history.sample(intent);origin=history.positions[-1];reference=history.rotations[-1]
    front=scene.stop_s-scene.state()[3]-scene.vehicle.LENGTH/2;speed=scene.state()[-1]
    actors=[] if scene.opponent is None else [(scene.opponent,np.array(scene.opponent.position).copy(),scene.opponent.heading_theta)]
    def hold_observed_actors():
      for actor,position,heading in actors:
        actor.set_position(position);actor.set_heading_theta(heading);actor.set_velocity(actor.heading,0)
    # Do not update colors/positions to a phase the model has not observed.
    scene.green_at=1e6;scene.update_actors=hold_observed_actors
    xyz=[];rot=[]
    for step in range(128):
      action=scene.expert()
      if scene.stopped:action[1]=np.clip(-1.5*scene.state()[-1],-3.5,0.)
      scene.step(action)
      if step%2==1:
        xyz.append((np.array([*scene.vehicle.position,0])-origin)@reference);rot.append(reference.T@rotation(scene.vehicle.heading_theta))
    terminal_front=scene.stop_s-scene.state()[3]-scene.vehicle.LENGTH/2
    if scene.failures or not 0<=terminal_front<5 or scene.state()[-1]>=.15:raise ValueError('counterfactual stop reference failed original safety bounds')
    sample.update(nav_text=np.array(intent),future_xyz=np.array(xyz,np.float32)[None],future_rot=np.array(rot,np.float32)[None])
    filename=f'{args.split}-{args.seed}-stop-{round(args.stop_time*10):03d}.npz';path=args.output/filename;np.savez_compressed(path,**sample)
    row={'file':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pixel_sha256':hashlib.sha256(sample['image_frames'].tobytes()).hexdigest(),'seed':args.seed,'split':args.split,'scenario':args.scenario,'mode':f'observed_stop_t{args.stop_time:04.1f}','front_distance_m':front,'stop_required':True,'restart_required':False,'maintain_stop_reference':0<front<5 and speed<.15,'reference_phase':'approach','future_permission_frozen':True,'future_actor_motion_frozen':True}
    write_json(args.output/'manifest.json',{'samples':[row],'rejected':[],'data_source':'simulation_only','reference_controls_used_only_for_supervision':True,'ground_truth_given_to_inference':False})
  finally:scene.close()


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--output',type=Path,required=True);parser.add_argument('--cycle',type=int,required=True)
  parser.add_argument('--scenario',choices=SCENARIOS);parser.add_argument('--seed',type=int);parser.add_argument('--split',choices=('train','validation'))
  parser.add_argument('--stop-time',type=float,help='Reproduce observed history and hold labels until actual future permission is observed')
  args=parser.parse_args()
  import numpy as np
  from tools.training_studio.store import read_json,write_json
  from tools.training_studio.teacher_data import training_seeds
  source=Path(__file__).read_bytes();args.output.mkdir(parents=True,exist_ok=False)
  if args.scenario is None:
    snapshot=args.output/'generation-source.py';snapshot.write_bytes(source);rows=[];rejected=[]
    for seed,split in training_seeds(args.cycle):
      for scenario in SCENARIOS:
        folder=args.output/f'{split}-{seed}-{scenario}'
        with (args.output/'renderer.log').open('a') as log:
          subprocess.run([sys.executable,str(snapshot),'--cycle',str(args.cycle),'--scenario',scenario,'--seed',str(seed),'--split',split,'--output',str(folder)],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'DISPLAY':os.environ.get('DISPLAY',':0')},check=True,timeout=600)
        packet=read_json(folder/'manifest.json');rows.extend({**row,'file':folder.name+'/'+row['file']} for row in packet['samples']);rejected.extend(packet['rejected'])
        write_json(args.output/'generation-progress.json',{'samples':len(rows),'rejected':len(rejected),'scenes_done':len(list(args.output.glob('*/manifest.json'))),'scenes_total':18})
    for split in ('train','validation'):
      for scenario in SCENARIOS:
        if not any(row['split']==split and row['scenario']==scenario and row['reference_phase'] in ('turning','post_turn') for row in rows):
          raise ValueError('safe turning/exit observations missing; preserve incomplete references')
    if {r['pixel_sha256'] for r in rows if r['split']=='train'}&{r['pixel_sha256'] for r in rows if r['split']=='validation'}:raise ValueError('image leakage')
    write_json(args.output/'manifest.json',{'samples':rows,'rejected':rejected,'data_source':'simulation_only','camera_ids':[1,6],'generator_sha256':hashlib.sha256(source).hexdigest(),'reference_controls_used_only_for_supervision':True,'ground_truth_given_to_inference':False})
    print(json.dumps({'samples':len(rows),'rejected':len(rejected)}),flush=True);return
  if not ((args.split=='train' and 1000<=args.seed<7000) or (args.split=='validation' and 8000<=args.seed<9500)):raise ValueError('independent seed/split required')
  if args.stop_time is not None:observed_stop_reference(args);return
  from openpilot.tools.sim.training.edge_experiment import EdgeHistory
  from openpilot.tools.sim.training.scene import Scene,DT,CASES
  from openpilot.tools.sim.training.capture_teacher import rotation
  scene=Scene(args.scenario,args.seed,'build/official-sim/full-assets/assets');history=EdgeHistory();positions=[];rotations=[];times=[];selected=[]
  try:
    scene.vehicle.set_position(scene.first_lane.position(scene.stop_s-20,0));scene.previous_position=np.array(scene.vehicle.position)
    requested=(4,6,8,10) if args.scenario in ('left_turn','right_turn') else (4,8,12,14,16)
    intent=('Turn left' if CASES[args.scenario]>0 else 'Turn right')+' at the upcoming intersection. Obey signals, yield to traffic, and remain in the lane.'
    for step in range(round(24/DT)+1):
      if step%2==0:
        history.record(scene);positions.append(np.array([*scene.vehicle.position,0],np.float32));rotations.append(rotation(scene.vehicle.heading_theta));times.append(round(scene.t*1e6))
        if step in {round(value/DT) for value in requested}:
          front=scene.stop_s-scene.state()[3]-scene.vehicle.LENGTH/2;speed=scene.state()[-1];blocked=scene.blocked();angle=abs((scene.vehicle.heading_theta-scene.initial_heading+np.pi)%(2*np.pi)-np.pi)
          selected.append((len(times)-1,history.sample(intent),{'front_distance_m':front,'stop_required':blocked,'restart_required':not blocked and speed<.2,'maintain_stop_reference':blocked and 0<front<5 and speed<.15,'reference_phase':'post_turn' if angle>=np.deg2rad(75) else 'turning' if angle>=np.deg2rad(15) else 'approach','reference_heading_change_rad':float(angle)}))
      if step==round(24/DT):break
      action=np.zeros(2,np.float32) if step<40 else scene.expert()
      if step>=40 and scene.blocked() and scene.stopped:action[1]=np.clip(-1.5*scene.state()[-1],-3.5,0.)
      scene.step(action)
    result=scene.result();write_json(args.output/'reference-result.json',{**result,'scripted_reference_only':True,'neural_teacher_qualification':False})
    rows=[];rejected=[]
    if result['status']!='pass':rejected.append({'scenario':args.scenario,'seed':args.seed,'failures':result['failures']})
    else:
      for index,sample,metadata in selected:
        if metadata['stop_required']:
          branch=args.output/f'observed-stop-{index:03d}'
          subprocess.run([sys.executable,str(Path(__file__).resolve()),'--cycle',str(args.cycle),'--scenario',args.scenario,'--seed',str(args.seed),'--split',args.split,'--stop-time',str(times[index]/1e6),'--output',str(branch)],check=True,timeout=300)
          corrected=read_json(branch/'manifest.json');rows.extend({**row,'file':branch.name+'/'+row['file']} for row in corrected['samples']);continue
        xyz,rot=relative_future(positions,rotations,times,index);sample.update(nav_text=np.array(intent),future_xyz=xyz,future_rot=rot)
        filename=f'{args.split}-{args.seed}-{index:03d}.npz';path=args.output/filename;np.savez_compressed(path,**sample)
        rows.append({'file':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pixel_sha256':hashlib.sha256(sample['image_frames'].tobytes()).hexdigest(),'seed':args.seed,'split':args.split,'scenario':args.scenario,'mode':f'full_route_t{times[index]//1000000:02d}','future_permission_frozen':False,'future_actor_motion_frozen':False,**metadata})
    write_json(args.output/'manifest.json',{'samples':rows,'rejected':rejected})
  finally:scene.close()


if __name__=='__main__':main()
