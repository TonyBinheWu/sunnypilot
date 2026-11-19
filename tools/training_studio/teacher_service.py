"""Pinned, offline Alpamayo 2 Edge service with real dual-front-camera timestamp tolerance."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import io
import json
from pathlib import Path
import time


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--model',type=Path,required=True)
  parser.add_argument('--receipt',type=Path,required=True)
  parser.add_argument('--adapter',type=Path,help='Immutable JSON adapter pointer with path and SHA-256')
  parser.add_argument('--forward-only',action='store_true',help='Decode the explicit forward-only teacher profile')
  parser.add_argument('--rear-axle-offset-m',type=float,help='Explicit observed-center to rear-axle vehicle geometry')
  parser.add_argument('--port',type=int,default=8767)
  parser.add_argument('--listen',default='127.0.0.1')
  parser.add_argument('--memory-fraction',type=float,help='Explicit CUDA fraction; default caps this service at 12 GiB')
  args=parser.parse_args()
  import numpy as np
  import torch
  from alpamayo2_edge.checkpoint import load_model
  from alpamayo2_edge.helper import get_processor,to_device
  from alpamayo2_edge.inference import predict,validate_predictions
  from tools.training_studio.edge_inputs import MODEL_REVISION,prepare_front_inputs
  from openpilot.sunnypilot.formosalink.training_protocol import digest_file
  model_path=args.model.resolve()
  receipt=json.loads(args.receipt.read_text())
  if receipt.get('revision')!=MODEL_REVISION or receipt.get('weights_verified') is not True or not receipt.get('weights'):
    raise ValueError('verified pinned Edge weights receipt required')
  for value in receipt['weights']:
    path=(model_path/value['file']).resolve()
    if not path.is_relative_to(model_path) or path.stat().st_size!=value['bytes'] or digest_file(path)!=value['sha256']:
      raise ValueError('teacher weight digest/size mismatch')
  cuda_total=torch.cuda.get_device_properties(0).total_memory
  cuda_fraction=args.memory_fraction if args.memory_fraction is not None else min(.9,12*1024**3/cuda_total)
  if not 0<cuda_fraction<=1: raise ValueError('CUDA memory fraction must be in (0,1]')
  torch.cuda.set_per_process_memory_fraction(cuda_fraction)
  model,_=load_model(str(model_path),device='cuda',dtype='bfloat16',attn_implementation='sdpa')
  model.requires_grad_(False)
  adapter=None
  if args.adapter:
    from tools.training_studio.teacher_lora import load
    adapter=json.loads(args.adapter.read_text())
    path=Path(adapter['path']).resolve()
    if digest_file(path)!=adapter['sha256']: raise ValueError('teacher adapter hash mismatch')
    load(model,path)
    model.requires_grad_(False)
  model.eval()
  from tools.training_studio.teacher_motion import install as install_motion,PROFILE as MOTION_PROFILE
  install_motion(model.expert.action_space)
  if adapter is not None and type(adapter.get('forward_only',False)) is not bool:raise ValueError('invalid adapter motion profile')
  forward_only=args.forward_only or bool(adapter and adapter.get('forward_only',False))
  if forward_only:
    from tools.training_studio.teacher_forward_motion import install as install_forward
    install_forward(model.expert.action_space)
  from tools.training_studio.teacher_reference_frame import validate_offset,install as install_reference,PROFILE as REFERENCE_PROFILE
  pointer_offset=adapter.get('rear_axle_offset_m',0.) if adapter else 0.
  offset=validate_offset(pointer_offset if args.rear_axle_offset_m is None else args.rear_axle_offset_m)
  if args.rear_axle_offset_m is not None and adapter and 'rear_axle_offset_m' in adapter and offset!=validate_offset(pointer_offset):
    raise ValueError('CLI geometry disagrees with immutable teacher pointer')
  if offset and not forward_only:raise ValueError('rear-axle calibration requires the forward-only profile')
  install_reference(model.expert.action_space,offset)
  processor=get_processor(model.tokenizer,model.config)
  space=model.expert.action_space
  captured={}
  decode=space.action_to_traj
  def capture(action,*fields,**kwargs):
    captured['action']=action.detach().clone()
    return decode(action,*fields,**kwargs)
  space.action_to_traj=capture
  settings={'seed':42,'num_traj_sets':1,'num_traj_samples':1,'top_p':.98,'top_k':None,'temperature':.6,
    'max_generation_length':256,'diffusion_kwargs':{'inference_step':10}}
  provenance={**receipt,'input_profile':'experimental_front_only','camera_ids':[1,6],'precision':'BF16',
    'cuda_memory_budget_gib':cuda_fraction*cuda_total/1024**3,
    'gpu':torch.cuda.get_device_name(0),'server_script_sha256':digest_file(Path(__file__)),
    'input_adapter_sha256':digest_file(Path(__file__).with_name('edge_inputs.py')),
    'motion_state_profile':MOTION_PROFILE,'motion_state_adapter_sha256':digest_file(Path(__file__).with_name('teacher_motion.py')),
    'action_expert_adapter':adapter,'adapter_loader_sha256':digest_file(Path(__file__).with_name('teacher_lora.py')),'driving_qualified':False,'amd_benchmarked':False}
  if forward_only:
    from tools.training_studio.teacher_forward_motion import PROFILE as FORWARD_PROFILE
    provenance.update(forward_motion_profile=FORWARD_PROFILE,
      forward_motion_adapter_sha256=digest_file(Path(__file__).with_name('teacher_forward_motion.py')))
  if offset:
    provenance.update(reference_frame_profile=REFERENCE_PROFILE,rear_axle_offset_m=offset,
      reference_frame_adapter_sha256=digest_file(Path(__file__).with_name('teacher_reference_frame.py')))

  class Handler(BaseHTTPRequestHandler):
    def reply(self,value,status=200):
      body=json.dumps(value,allow_nan=False).encode()
      self.send_response(status)
      self.send_header('Content-Type','application/json')
      self.send_header('Content-Length',str(len(body)))
      self.end_headers()
      self.wfile.write(body)

    def do_GET(self):
      self.reply({'teacher_ready':True,'provenance':provenance})

    def do_POST(self):
      try:
        size=int(self.headers.get('Content-Length','0'))
        if not 0<size<=64*1024**2:
          raise ValueError('invalid teacher input size')
        payload=self.rfile.read(size)
        with np.load(io.BytesIO(payload),allow_pickle=False) as packet:
          data={key:packet[key] for key in packet.files}
        data['nav_text']=[str(data['nav_text'].item())]
        started=time.perf_counter()
        prepared=prepare_front_inputs(data,model.config,model.tokenizer,processor=processor,timestamp_tolerance_us=35000)
        prepared=to_device(prepared,device='cuda')
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        inference_start=time.perf_counter()
        with torch.inference_mode():
          xyz,rot,extra=predict(model,prepared,settings,'cuda')
        torch.cuda.synchronize()
        validate_predictions(xyz,rot,1,1)
        action=captured.pop('action').float()
        actions=torch.stack((action[...,0]*space.accel_std+space.accel_mean,
                             action[...,1]*space.curvature_std+space.curvature_mean),dim=-1).cpu().numpy().reshape(64,2)
        self.reply({'ok':True,'backend':'nvidia_alpamayo2_edge','teacher_revision':MODEL_REVISION,
          'input_sha256':hashlib.sha256(payload).hexdigest(),'scripted_fallback':False,
          'xyz':xyz.float().cpu().numpy().reshape(64,3).tolist(),'rot':rot.float().cpu().numpy().reshape(64,3,3).tolist(),
          'actions_accel_curvature':actions.tolist(),'cot':str(np.asarray(extra.get('cot','')).reshape(-1)[0]),
          'camera_ids':[1,6],'processed_image_count':10,'inference_s':time.perf_counter()-inference_start,
          'wall_s':time.perf_counter()-started,'peak_allocated_gib':torch.cuda.max_memory_allocated()/1024**3,
          'peak_reserved_gib':torch.cuda.max_memory_reserved()/1024**3,'benchmark_device':provenance['gpu'],
          'amd_benchmarked':False,'precision':'BF16'})
      except Exception as exc:
        self.reply({'ok':False,'error':str(exc),'scripted_fallback':False},400)
      finally:
        torch.cuda.empty_cache()

    def log_message(self,*unused):
      pass

  print(json.dumps({'ready':True,'provenance':provenance}),flush=True)
  HTTPServer((args.listen,args.port),Handler).serve_forever()


if __name__=='__main__':
  main()
