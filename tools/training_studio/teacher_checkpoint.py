"""Qualify one immutable checkpoint against unchanged offline and simulation gates."""
"""Qualify an immutable intermediate checkpoint while its optimizer continues."""
from pathlib import Path
import argparse,hashlib,json,os,shlex,subprocess,sys,time,urllib.request
from tools.training_studio.store import Store,read_json,write_json
from tools.training_studio.remote import Remote
p=argparse.ArgumentParser();p.add_argument('--cycle',type=int,required=True);p.add_argument('--selection',choices=('safety','balanced','latest','completed'),default='safety');p.add_argument('--epoch',type=int);p.add_argument('--root',default='build/training-studio');args=p.parse_args()
if args.selection=='completed' and (args.epoch is None or args.epoch<=0):p.error('completed selection requires a positive immutable epoch')
store=Store(args.root);config=store.config();r=Remote(config['remote']);settings=config['teacher_adaptation']
import fcntl
publication_lock=(store.root/'teacher-candidate-publication.lock').open('a+')
fcntl.flock(publication_lock,fcntl.LOCK_EX)
if read_json(store.root/'teacher-qualification-progress.json',{}).get('state')=='passed':raise SystemExit('preserve exact qualified teacher')
if not store.enabled():raise SystemExit('training is paused')
folder=store.root/'teacher-cycles'/f'cycle-{args.cycle:03d}';progress_path=folder/'progress.json'
# The local optimizer progress mirror is teacher-training-progress.json.
def chosen():
 value=read_json(store.root/'teacher-training-progress.json');assert value['cycle']==args.cycle and value['phase'] in ('training','completed','paused','error')
 history=[{'epoch':0,**value['baseline']},*value.get('history',[])]
 if args.selection=='completed':return next(row for row in history if row['epoch']==args.epoch)
 score=(lambda h:h['epoch']) if args.selection=='latest' else (lambda h:(h['red_safe_count'],-h['red_hold_speed_mse'],-h['validation_loss'])) if args.selection=='safety' else (lambda h:-h['validation_loss'])
 row=max(history,key=score);assert row['epoch']>0,'no updated candidate'
 return row
chosen_row=chosen();epoch=chosen_row['epoch'];expected_checksum=None
if args.selection in ('latest','completed'):
 if args.selection=='completed':
  metadata=folder/f'completed-metadata-epoch{epoch:03d}.json';r.download(r.root+f'/teacher/cycle-{args.cycle:03d}/output/epoch-{epoch:03d}.json',metadata);descriptor=read_json(metadata);assert descriptor['metrics']==chosen_row
 else:descriptor=read_json(store.root/'teacher-training-progress.json')['latest_checkpoint']
 assert descriptor['epoch']==epoch
 filename=descriptor['file'];assert Path(filename).name==filename and filename==f'epoch-{epoch:03d}.safetensors';expected_checksum=descriptor['sha256']
else:filename='best.safetensors' if args.selection=='safety' else 'balanced.safetensors'
remote_output=r.root+f'/teacher/cycle-{args.cycle:03d}/output';source=remote_output+'/'+filename
snapshot=remote_output+f'/early-{args.selection}-epoch{epoch:03d}.safetensors'
# Exclusive new path; hash source before/after and the snapshot, reject save races.
code="import pathlib,hashlib,shutil; s=pathlib.Path("+repr(source)+");t=pathlib.Path("+repr(snapshot)+");a=hashlib.sha256(s.read_bytes()).hexdigest();expected="+repr(expected_checksum)+";assert expected is None or a==expected;existed=t.exists();assert not existed or expected is not None,'only checksummed immutable epochs may resume';shutil.copyfile(s,t) if not existed else None;b=hashlib.sha256(s.read_bytes()).hexdigest();c=hashlib.sha256(t.read_bytes()).hexdigest();assert a==b==c,'immutable checkpoint changed during snapshot or resume';print(c)"
checksum=r.call(shlex.join(['python3','-c',code]),capture_output=True,text=True).stdout.strip()
if expected_checksum:assert checksum==expected_checksum,'completed epoch digest changed'
if config.get('teacher_checkpoint_quality_guard_enabled'):
 from tools.training_studio.teacher_quality import checkpoint_quality
 origin=read_json(folder/'dataset-origin.json');current=read_json(store.root/'teacher-training-progress.json');assert descriptor['dataset_sha256']==origin['dataset_sha256'];assert chosen_row.get('validation_guard') and current['baseline'].get('validation_guard')
 decision=checkpoint_quality(chosen_row,current['baseline'],origin['validation_guard_reference']);assert decision['passed'],'full and fixed validation guards must pass before publication'
 assert descriptor['metrics']==chosen_row
 frozen=read_json(folder/f'frozen-parent-audit-epoch{epoch:03d}.json');assert frozen['epoch_sha256']==checksum and frozen['all_original_adapter_tensors_bitwise_unchanged'] and frozen['metrics']==chosen_row
 write_json(store.root/'teacher-quality'/f'{checksum}.json',{'candidate_sha256':checksum,'cycle':args.cycle,'epoch':epoch,'runtime_profile':{k:descriptor.get(k,False if k!='rear_axle_offset_m' else 0.) for k in ('fp32_expert','forward_only','signed_hold_controls','rear_axle_offset_m','mlp_only','mlp_output_residual')},'metrics':chosen_row,'baseline':current['baseline'],'guard_reference':origin['validation_guard_reference'],**decision})
time.sleep(3);assert chosen()['epoch']==epoch,'validation checkpoint changed while snapshotting'
pointer={'path':'/studio/teacher/'+f'cycle-{args.cycle:03d}/output/'+Path(snapshot).name,'sha256':checksum,'cycle':args.cycle,'training_epoch':epoch,'selection':args.selection,'scope':read_json(store.root/'teacher-training-progress.json').get('adapter_scope','actual_Edge_expert_expanded_LoRA'),'forward_only':read_json(store.root/'teacher-training-progress.json').get('forward_only',False),'fp32_expert':read_json(store.root/'teacher-training-progress.json').get('fp32_expert',False),'rear_axle_offset_m':read_json(store.root/'teacher-training-progress.json').get('rear_axle_offset_m',0.),'signed_hold_controls':read_json(store.root/'teacher-training-progress.json').get('signed_hold_controls',False),'objective_revision':read_json(store.root/'teacher-training-progress.json').get('objective_revision'),'mlp_output_residual':read_json(store.root/'teacher-training-progress.json').get('mlp_output_residual',False),'driving_qualified':False}
if expected_checksum:assert descriptor.get('rear_axle_offset_m',0.)==pointer['rear_axle_offset_m'],'checkpoint reference geometry disagrees with optimizer'
if expected_checksum:assert descriptor.get('fp32_expert',False)==pointer['fp32_expert'],'checkpoint expert precision disagrees with optimizer'
relative='teacher/service-'+checksum[:16]+'.json';local=store.root/relative;write_json(local,pointer);r.upload(local,r.root+'/'+relative)
program=r.program(snapshot=True);container_program='/studio/'+Path(program).name
existing=r.call('docker ps -a --filter name=^/studio-teacher$ --format "{{.Names}}"',capture_output=True,text=True).stdout.strip()
if existing:
 label=r.call('docker inspect studio-teacher --format \'{{index .Config.Labels "formosapilot.owner"}}\'',capture_output=True,text=True).stdout.strip()
 if label!='training-studio':raise RuntimeError('foreign teacher sidecar')
 r.call(shlex.join(['docker','rm','-f','studio-teacher']))
command=['docker','run','-d','--restart','unless-stopped','--name','studio-teacher','--label','formosapilot.owner=training-studio','--gpus','all','--network','bridge','--memory','32g','--user','1000:1000','-p','127.0.0.1:8767:8767','-v',r.root+':/studio','-v',settings['model_root']+':/teacher:ro','-v',settings['legacy_deps_root']+':/old:ro','-w','/studio','-e','HF_HUB_OFFLINE=1','-e','PYTHONPATH=/teacher/deps:/old/deps:/teacher/source/src:'+container_program,'--entrypoint','python',r.image,'-u','-m','tools.training_studio.teacher_service','--listen','0.0.0.0','--model','/teacher/model','--receipt','/teacher/model-receipt.json','--adapter','/studio/'+relative]
r.call(shlex.join(command));opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));deadline=time.monotonic()+180
while time.monotonic()<deadline:
 try:
  with opener.open(config['teacher_url']+'/health',timeout=5) as response:health=json.load(response)
  if health['provenance'].get('action_expert_adapter',{}).get('sha256')==checksum:
   if pointer['rear_axle_offset_m']:
    from tools.training_studio.teacher_reference_frame import PROFILE as REFERENCE_PROFILE
    assert health['provenance']['reference_frame_profile']==REFERENCE_PROFILE and health['provenance']['rear_axle_offset_m']==pointer['rear_axle_offset_m']
    assert health['provenance']['reference_frame_adapter_sha256']==hashlib.sha256(Path('tools/training_studio/teacher_reference_frame.py').read_bytes()).hexdigest()
   else:assert not health['provenance'].get('rear_axle_offset_m',0.)
   if pointer['fp32_expert']:
    from tools.training_studio.teacher_precision import PROFILE as PRECISION_PROFILE
    assert health['provenance']['expert_precision_profile']==PRECISION_PROFILE
    assert health['provenance']['expert_precision_adapter_sha256']==hashlib.sha256(Path('tools/training_studio/teacher_precision.py').read_bytes()).hexdigest()
   else:assert not health['provenance'].get('expert_precision_profile')
   break
 except (OSError,ValueError):pass
 time.sleep(2)
else:raise RuntimeError('candidate service did not become ready')
fingerprint=hashlib.sha256(json.dumps(health['provenance'],sort_keys=True).encode()).hexdigest()
batch=folder/f'qualification-{args.selection}-early-epoch{epoch:03d}'
write_json(store.root/'teacher-attempt.json',{'fingerprint':fingerprint,'batch':str(batch),'started':time.time()})
write_json(folder/f'early-{args.selection}-epoch{epoch:03d}.json',{'pointer':pointer,'offline_metrics':chosen_row,'fingerprint':fingerprint,'optimizer_continues':True})
store.event(f'教師中途候選重驗：第{args.cycle}輪epoch{epoch}，權重快照已固定；最佳化持續執行')
with (folder/f'qualification-{args.selection}-early-epoch{epoch:03d}.log').open('w') as log:
 result=subprocess.run([sys.executable,'-u','-m','tools.training_studio.qualification','--root',str(store.root),'--batch',str(batch)],env={**os.environ,'DISPLAY':config.get('qualification_display',':0')},stdout=log,stderr=subprocess.STDOUT)
print(json.dumps({'cycle':args.cycle,'epoch':epoch,'selection':args.selection,'qualification_returncode':result.returncode,'progress':read_json(store.root/'teacher-qualification-progress.json')}),flush=True)
if result.returncode not in (0,2):raise RuntimeError('qualification process failed')

