"""Simulation supervision with held-out qualification seeds and actual reference futures."""
import argparse
import hashlib
import json
from pathlib import Path
import os
import subprocess
import sys
import time


def training_seeds(cycle):
  return [(1000+(cycle%2000)*3,'train'),(1001+(cycle%2000)*3,'train'),(8000+cycle%1500,'validation')]


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--output',type=Path,required=True)
  parser.add_argument('--cycle',type=int,required=True)
  parser.add_argument('--scenario',default='red_light')
  parser.add_argument('--fixture',type=int)
  parser.add_argument('--seed',type=int)
  parser.add_argument('--split')
  parser.add_argument('--rehearsal',default='')
  args=parser.parse_args()
  import numpy as np
  fixtures=[('red_light','hold',-6.5,0,0,0),('red_light','hold',-5,0,0,0),
    ('red_light','recover_early_stop',-10,0,0,0),('red_light','creep',-6.5,0,.3,0),
    ('red_light','approach',-25,0,4,0),('red_light','approach',-18,0,2,.01),
    ('red_light','go',-6.5,0,0,0),('red_light','go',7,-.4,3,.025),
    ('red_light','go',7,.4,3,-.025),('red_light','go',15,0,4,.04),
    ('red_light','brake_approach',-13,0,3,0),('red_light','brake_hold',-9,0,1.5,0),
    ('red_light','green_transition',-6.5,0,0,0),('red_light','accelerating_go',-6.5,0,0,0),
    ('red_light','drift_go',7,.5,3,0),('red_light','drift_go',7,-.5,3,0)]
  scenarios=sorted(({args.scenario}|set(filter(None,args.rehearsal.split(','))))-{'red_light'})
  for scenario in scenarios:
    fixtures += [(scenario,'hold',-6.5,0,0,0),(scenario,'approach',-25,0,3,0),
      (scenario,'go',-6.5,0,0,0),(scenario,'go',-15,0,3,0)]
  if args.fixture is None:
    from tools.training_studio.store import write_json,read_json
    args.output.mkdir(parents=True,exist_ok=False)
    records,rejected=[],[]
    for seed,split in training_seeds(args.cycle):
      for index in range(len(fixtures)):
        destination=args.output/f'{split}-{seed}-{index}'
        command=[sys.executable,'-m','tools.training_studio.teacher_data','--cycle',str(args.cycle),'--scenario',args.scenario,
          '--output',str(destination),'--fixture',str(index),'--seed',str(seed),'--split',split,'--rehearsal',args.rehearsal]
        # A clean renderer process per packet prevents accumulated D3D12 context loss.
        result=subprocess.run(command,env={**os.environ,'LIBGL_ALWAYS_SOFTWARE':'0'},timeout=300)
        if result.returncode: raise RuntimeError('isolated reference renderer failed; preserve the incomplete dataset')
        row=read_json(destination/'sample.json')
        if row.get('rejected'): rejected.append(row)
        else:
          row['file']=destination.name+'/'+row['file']
          records.append(row)
        write_json(args.output/'generation-progress.json',{'phase':'generating','samples':len(records),'rejected':len(rejected),'total':3*len(fixtures),'updated':time.time()})
    if any(not any(r['split']==split and r['stop_required']==stop for r in records) for split in ('train','validation') for stop in (True,False)):
      raise ValueError('insufficient safe references; do not manufacture missing supervision')
    if any(not any(r['split']==split and r['scenario']==scenario for r in records) for scenario in scenarios for split in ('train','validation')):
      raise ValueError('no safe reference survived for a required failure scenario')
    if {r['pixel_sha256'] for r in records if r['split']=='train'} & {r['pixel_sha256'] for r in records if r['split']=='validation'}:
      raise ValueError('duplicate images across train/validation')
    write_json(args.output/'manifest.json',{'samples':records,'rejected':rejected,'camera_ids':[1,6],'data_source':'simulation_only',
      'reference_controls_used_only_for_supervision':True,'ground_truth_given_to_inference':False,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    return
  from openpilot.tools.sim.training.edge_experiment import EdgeHistory
  from openpilot.tools.sim.training.capture_teacher import rotation
  from openpilot.tools.sim.training.scene import Scene,CASES
  from openpilot.sunnypilot.formosalink.model_navigation import driving_context
  from tools.training_studio.store import write_json
  if args.scenario not in CASES: raise ValueError('unsupported failure scenario')
  args.output.mkdir(parents=True,exist_ok=False)
  records,rejected=[],[]
  for seed,split in [(args.seed,args.split)]:
    for index,(scenario,mode,offset,lateral,speed,yaw_error) in enumerate(fixtures):
      if index!=args.fixture: continue
      scene=Scene(scenario,seed,'build/official-sim/full-assets/assets')
      try:
        scene.vehicle.set_position(scene.first_lane.position(scene.stop_s+offset,lateral))
        scene.vehicle.set_heading_theta(scene.initial_heading+yaw_error)
        scene.vehicle.set_velocity(scene.vehicle.heading,speed)
        scene.previous_position=np.array(scene.vehicle.position)
        is_go=mode in ('go','green_transition','accelerating_go','drift_go')
        # Actor interpolation divides by the clearance time. A small positive
        # time clears actors before any history frame used for a go packet.
        scene.green_at=1.9 if mode=='green_transition' else 1e-6 if is_go else 1e6
        scene.update_actors()
        history=EdgeHistory()
        for step in range(41):
          if step%2==0: history.record(scene)
          if step<40:
            action=np.zeros(2,np.float32)
            if mode.startswith('brake_'): action[1]=-.8
            elif mode=='accelerating_go': action=scene.expert()
            elif mode=='drift_go': action[0]=-np.sign(lateral)*.06
            scene.step(action)
        intent=driving_context()['nav_text']
        if CASES[scenario]: intent=('Turn left' if CASES[scenario]>0 else 'Turn right')+' at the upcoming intersection. Obey signals, yield to traffic, and remain in the lane.'
        sample=history.sample(intent)
        origin,reference=history.positions[-1],history.rotations[-1]
        front_distance=scene.stop_s-scene.state()[3]-scene.vehicle.LENGTH/2
        initial_speed=scene.state()[-1]
        for observation in scene.env.observations.values(): observation.observe=lambda *a,**k:{}
        xyz,rot=[],[]
        for step in range(128):
          scene.step(scene.expert())
          if step%2==1:
            xyz.append((np.array([*scene.vehicle.position,0])-origin)@reference)
            rot.append(reference.T@rotation(scene.vehicle.heading_theta))
        if scene.failures:
          rejected.append({'rejected':True,'scenario':scenario,'mode':mode,'seed':seed,'failures':sorted(scene.failures)})
          continue
        sample.update(nav_text=np.array(intent),future_xyz=np.array(xyz,np.float32)[None],future_rot=np.array(rot,np.float32)[None])
        path=args.output/f'{split}-{seed}-{index}.npz'
        np.savez_compressed(path,**sample)
        records.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'seed':seed,'split':split,'scenario':scenario,'mode':mode,
          'stop_required':not is_go and scenario in ('red_light','pedestrian','yield_left','yield_right','left_arrow','right_arrow'),
          'restart_required':is_go and initial_speed<.2,'front_distance_m':front_distance,
          'pixel_sha256':hashlib.sha256(sample['image_frames'].tobytes()).hexdigest()})
        write_json(args.output/'generation-progress.json',{'phase':'generating','samples':len(records),'rejected':len(rejected),'updated':time.time()})
      finally: scene.close()
  write_json(args.output/'sample.json',(records or rejected)[0])


if __name__=='__main__': main()
