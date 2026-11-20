"""Durable, local teacher training/qualification loop. No hosted LLM is used."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time
import urllib.request
from urllib.parse import urlparse

from tools.training_studio.remote import Remote
from tools.training_studio.store import Store, read_json, write_json
from tools.training_studio.teacher_control import qualified, finish_adaptation
from tools.training_studio.teacher_quality import checkpoint_quality


class IntegrityError(RuntimeError):
  pass


def validate_manifest(manifest, reference_sha):
  rows = manifest.get('samples', [])
  validation = {r['sha256'] for r in rows if r['split'] == 'validation'}
  guard = set(manifest.get('validation_guard_sha256s', []))
  parent = set(manifest.get('parent_validation_sha256s', []))
  if (len(guard) != 6 or len(parent) != 154 or not guard <= parent <= validation
      or manifest.get('parent_validation_reference_checkpoint_sha256') != reference_sha
      or not manifest.get('validation_guard_reference')
      or not manifest.get('parent_validation_reference', {}).get('validation_guard')):
    raise IntegrityError('immutable validation references are missing or changed')
  if any(r['seed'] in (300, 301, 302, 303) for r in rows):
    raise IntegrityError('qualification observations must never enter training')
  if ({r['seed'] for r in rows if r['split'] == 'train'} &
      {r['seed'] for r in rows if r['split'] == 'validation'}):
    raise IntegrityError('training and validation seeds overlap')
  if ({r['pixel_sha256'] for r in rows if r['split'] == 'train'} &
      {r['pixel_sha256'] for r in rows if r['split'] == 'validation'}):
    raise IntegrityError('training and validation observations overlap')


def audit_script(anchor, checkpoint, checksum, destination):
  """The detached CPU job always records whether a failure is structural."""
  return f'''from pathlib import Path
import hashlib,json,numpy as np
from safetensors.numpy import load_file
p=Path({anchor['path']!r});e=Path({checkpoint!r});out=Path({destination!r})
try:
 assert hashlib.sha256(p.read_bytes()).hexdigest()=={anchor['sha256']!r}
 m=json.loads(e.with_suffix('.json').read_text());assert hashlib.sha256(e.read_bytes()).hexdigest()==m['sha256']=={checksum!r}
 head=m.get('mlp_output_residual',False)
 assert m['fp32_expert'] is True and m['objective_revision']=='ten_step_executed_peak_hold_and_steering_v10'
 assert (m['mlp_only'] is True and not head) or (m['mlp_only'] is False and head and m['optimization_profile']=='grouped_twelve_task_separate_stop_lateral_safety_fp64_projection_sgd_v13')
 old=load_file(str(p));new=load_file(str(e));assert len(old)==242
 assert all(n in new and np.array_equal(v,new[n]) for n,v in old.items())
 added=set(new)-set(old);extra={{'expert.action_out_proj.output_residual_weight','expert.action_out_proj.output_residual_bias'}} if head else set()
 assert len(added)==112+len(extra) and extra<=added
 assert all('.mlp.fc1.' in n or '.mlp.fc2.' in n for n in added-extra)
 assert all(np.isfinite(new[n]).all() for n in added)
 result={{'passed':True,'all_original_adapter_tensors_bitwise_unchanged':True,'original_adapter_tensor_count':242,'new_mlp_adapter_tensors':112,'new_output_residual_tensors':len(extra),'epoch_sha256':m['sha256'],'metrics':m['metrics'],'qualification_granted':False}}
except AssertionError as exc:result={{'passed':False,'kind':'tensor_integrity','error':str(exc)}}
except Exception as exc:result={{'passed':False,'kind':'runtime','error':str(exc)}}
tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result));tmp.replace(out)
'''


class Loop:
  def __init__(self, store):
    self.s = store
    self.config = store.config()
    if urlparse(self.config['teacher_url']).hostname not in ('127.0.0.1', 'localhost', '::1'):
      raise IntegrityError('teacher inference must use the local Alpamayo endpoint')
    self.r = Remote(self.config['remote'])
    self.options = self.config['closed_loop']
    self.path = store.root/'closed-loop-state.json'
    self.state = read_json(self.path, {'attempts': {}, 'audit_jobs': {}})
    self.native = self.qualifier = None
    self.qual_key = None
    self.program = None
    names=('teacher_service.py','teacher_lora.py','teacher_motion.py','teacher_forward_motion.py','teacher_reference_frame.py','teacher_precision.py','edge_inputs.py')
    self.runtime_key=hashlib.sha256(b''.join((Path(__file__).parent/n).read_bytes() for n in names)).hexdigest()[:12]
    self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

  def save(self, phase, **fields):
    self.state.update(fields)
    write_json(self.path, self.state)
    write_json(self.s.root/'closed-loop-progress.json', {
      'updated': time.time(), 'active': True, 'phase': phase,
      'uses_hosted_llm': False, 'cycle': self.state.get('cycle'),
      'qualification_running': self.qualifier is not None,
      'attempted_checkpoints': len(self.state['attempts']),
      'last_error': self.state.get('last_error'), **fields})

  def gates(self):
    state = read_json(self.s.root/'teacher-adaptation/state.json')
    gates = Path(self.s.config()['qualification_checkout'])/'openpilot/tools/sim/training'
    if state['acceptance'] != self.options['original_acceptance'] or not all(hashlib.sha256((gates/name).read_bytes()).hexdigest() == digest
               for name, digest in self.options['original_acceptance'].items()):
      raise IntegrityError('original simulation acceptance code changed')

  def dataset(self, cycle):
    folder = self.s.root/f'teacher-cycles/cycle-{cycle:03d}'
    manifest = read_json(folder/'data/manifest.json')
    validate_manifest(manifest, self.options['reference_checkpoint_sha256'])
    if hashlib.sha256(json.dumps(manifest['parent_validation_reference'],sort_keys=True).encode()).hexdigest() != self.options['reference_metrics_sha256']:
      raise IntegrityError('immutable reference metrics changed')
    digest = hashlib.sha256((folder/'data/manifest.json').read_bytes()).hexdigest()
    origin = read_json(folder/'dataset-origin.json')
    if origin['dataset_sha256'] != digest:
      raise IntegrityError('sealed training manifest changed')
    return folder, manifest, origin

  def prepare(self, source_cycle, target_cycle):
    source, manifest, origin = self.dataset(source_cycle)
    target = self.s.root/f'teacher-cycles/cycle-{target_cycle:03d}'
    target.mkdir(parents=True, exist_ok=True)
    if not (target/'data/manifest.json').exists():
      data = target/'data'
      data.mkdir(exist_ok=True)
      for row in manifest['samples']:
        src = source/'data'/row['file']; dst = data/row['file']
        if hashlib.sha256(src.read_bytes()).hexdigest() != row['sha256']:
          raise IntegrityError('training packet changed')
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists(): os.link(src, dst)
      (data/'manifest.json').write_bytes((source/'data/manifest.json').read_bytes())
      write_json(target/'dataset-origin.json', {**origin, 'cycle': target_cycle,
        'prepared_before_training': True, 'prepared_from_cycle': source_cycle})
    self.dataset(target_cycle)
    return target

  def descriptor(self, cycle, row):
    folder = self.s.root/f'teacher-cycles/cycle-{cycle:03d}'
    path = folder/f'completed-metadata-epoch{row["epoch"]:03d}.json'
    if not path.exists():
      self.r.download(self.r.root+f'/teacher/cycle-{cycle:03d}/output/epoch-{row["epoch"]:03d}.json', path)
    value = read_json(path)
    if value['metrics'] != row or value['epoch'] != row['epoch'] or value.get('file') != f'epoch-{row["epoch"]:03d}.safetensors':
      raise IntegrityError('checkpoint metrics disagree with the recorded epoch')
    return value

  def audit(self, cycle, descriptor):
    epoch = descriptor['epoch']; checksum = descriptor['sha256']
    folder = self.s.root/f'teacher-cycles/cycle-{cycle:03d}'
    local = folder/f'frozen-parent-audit-epoch{epoch:03d}.json'
    proof = read_json(local, {})
    if proof:
      if not (proof.get('all_original_adapter_tensors_bitwise_unchanged') and
          proof.get('original_adapter_tensor_count') == 242 and
          proof.get('epoch_sha256') == checksum and proof.get('metrics') == descriptor['metrics']):
        raise IntegrityError('saved frozen-tensor proof is inconsistent')
      return True
    key = f'{cycle}:{epoch}:{checksum}'
    remote = self.r.root+f'/teacher/cycle-{cycle:03d}/output/closed-loop-frozen-{epoch:03d}.json'
    payload = self.r.call('if test -f '+shlex.quote(remote)+'; then cat '+shlex.quote(remote)+'; fi',
                          capture_output=True, text=True, timeout=20).stdout.strip()
    if payload:
      proof = json.loads(payload)
      if not proof.get('passed'):
        if proof.get('kind') == 'tensor_integrity':raise IntegrityError('frozen tensor verification failed')
        archive=remote+'.runtime-error-'+str(time.time_ns())
        self.r.call(shlex.join(['python3','-c','from pathlib import Path;Path('+repr(remote)+').rename('+repr(archive)+')']),timeout=20)
        raise RuntimeError('CPU audit environment failed; preserved report and will retry: '+proof.get('error', 'unknown'))
      if proof['epoch_sha256'] != checksum or proof['metrics'] != descriptor['metrics']:
        raise IntegrityError('detached tensor proof belongs to a different checkpoint')
      write_json(local, proof)
      return True
    name = f'studio-loop-audit-{cycle}-{epoch}-{checksum[:8]}'
    existing = self.r.call('docker ps -a --filter '+shlex.quote('name=^/'+name+'$')+
      ' --format '+shlex.quote('{{.Names}}'), capture_output=True, text=True, timeout=20).stdout.strip()
    if not existing:
      checkpoint = f'/studio/teacher/cycle-{cycle:03d}/output/epoch-{epoch:03d}.safetensors'
      output = f'/studio/teacher/cycle-{cycle:03d}/output/closed-loop-frozen-{epoch:03d}.json'
      code = audit_script(self.options['frozen_anchor'], checkpoint, checksum, output)
      command = ['docker','run','-d','--rm','--name',name,'--label','formosapilot.owner=training-studio',
        '--network','none','--memory','4g','--user','1000:1000','-v',self.r.root+':/studio',
        '--entrypoint','python',self.r.image,'-c',code]
      self.r.call(shlex.join(command), capture_output=True, text=True, timeout=30)
      self.state['audit_jobs'][key] = time.time()
    return False

  def stop(self, child):
    if child and child.poll() is None:
      os.killpg(child.pid, signal.SIGTERM)
      try: child.wait(timeout=20)
      except subprocess.TimeoutExpired: os.killpg(child.pid, signal.SIGKILL); child.wait()

  def latch(self):
    config = self.s.config()
    q = read_json(self.s.root/'teacher-qualification-progress.json', {})
    if q.get('state') != 'passed':return False
    with self.opener.open(config['teacher_url']+'/health', timeout=10) as response:health = json.load(response)
    receipt = read_json(config['teacher_qualification'], {})
    if not qualified(receipt, health) or len(receipt['cases']) != 11 or not all(c['passed'] for c in receipt['cases']):
      raise IntegrityError('qualification receipt is not bound to the exact live teacher')
    self.gates()
    report = read_json(Path(q['batch'])/'qualification.json')
    fingerprint = hashlib.sha256(json.dumps(health['provenance'], sort_keys=True).encode()).hexdigest()
    if (len(report['results']) != 11 or not report['passed'] or
        any(r['status'] != 'pass' or r['failures'] or r['model_provenance_sha256'] != fingerprint for r in report['results'])):
      raise IntegrityError('all eleven original cases must pass on one fixed teacher')
    adapter = health['provenance']['action_expert_adapter']
    proof = read_json(self.s.root/'teacher-quality'/f'{adapter["sha256"]}.json', {})
    if not proof.get('passed') or proof.get('candidate_sha256') != adapter['sha256']:
      raise IntegrityError('qualified teacher lacks its strict offline quality proof')
    finish_adaptation(self.s, health)
    self.stop(self.native); self.native = None
    progress = read_json(self.s.root/'teacher-training-progress.json', {})
    folder = self.s.root/f'teacher-cycles/cycle-{progress["cycle"]:03d}'
    if not (folder/'result.json').exists() and not (folder/'interrupted.json').exists():
      write_json(folder/'interrupted.json', {**progress, 'completed':False,
        'completed_epochs':len(progress.get('history', [])), 'reason':'exact teacher passed all original eleven cases'})
    write_json(self.s.root/'teacher-training-progress.json', {**progress, 'phase':'qualified',
      'updated':time.time(), 'qualified_candidate':adapter, 'qualified_cases':11,
      'optimizer_completed_epochs':len(progress.get('history', []))})
    write_json(self.s.root/'closed-loop-qualification-adoption.json', {'teacher':adapter,
      'provenance_sha256':fingerprint, 'simulation_cases':11, 'original_gates_unchanged':True,
      'real_road_qualified':False, 'amd_benchmarked':False, 'continuous_enabled':self.s.enabled()})
    self.state['qualified_sha256'] = adapter['sha256']
    return True

  def advance(self, progress):
    old_cycle = progress['cycle']; folder, manifest, origin = self.dataset(old_cycle)
    name=f'studio-teacher-train-{old_cycle:03d}'
    existing=self.r.call('docker ps --filter '+shlex.quote('name=^/'+name+'$')+' --filter label=formosapilot.owner=training-studio --format '+shlex.quote('{{.Names}}'),capture_output=True,text=True,timeout=20).stdout.strip()
    if existing:self.r.call(shlex.join(['docker','stop','--time','3',name]),timeout=20)
    state_path = self.s.root/'teacher-adaptation/state.json'; state = read_json(state_path)
    rows = progress.get('history', [])
    if rows:
      descriptor = self.descriptor(old_cycle, rows[-1])
      if not self.audit(old_cycle, descriptor):return False
      state['parent'] = {'path':f'/studio/teacher/cycle-{old_cycle:03d}/output/'+descriptor['file'],
        'sha256':descriptor['sha256'], 'cycle':old_cycle, 'training_epoch':descriptor['epoch'],
        'selection':'training_continuation_not_qualified', 'scope':progress['adapter_scope'],
        **{k:descriptor.get(k, False if k != 'rear_axle_offset_m' else 0.) for k in
           ('fp32_expert','forward_only','signed_hold_controls','rear_axle_offset_m','mlp_only','mlp_output_residual')},
        'objective_revision':descriptor['objective_revision'], 'driving_qualified':False}
    if not (folder/'result.json').exists() and not (folder/'interrupted.json').exists():
      write_json(folder/'interrupted.json', {**progress, 'completed':False,
        'completed_epochs':len(rows), 'reason':'autonomous continuation; partial unsaved updates are not claimed as resumed'})
    next_cycle = max(old_cycle+1, state['cycle'])
    self.prepare(old_cycle, next_cycle)
    state.update(cycle=next_cycle, best_closed_loop=(-1,)*11, ranking_version=5, rehearsal_version=1)
    state.pop('pending_container', None); write_json(state_path, state)
    write_json(self.s.root/'teacher-training-progress.json', {'cycle':next_cycle, 'phase':'scheduled',
      'updated':time.time(), 'history':[], 'previous_cycle':old_cycle})
    self.s.event(f'自治閉環接續第{next_cycle}輪：沿用一份完整已存權重；原154筆及固定6筆門檻保留，不使用原資格觀測訓練。')
    return True

  def tick(self):
    if self.state.get('blocked_integrity'):
      self.save('blocked_integrity'); return
    if not self.s.enabled():
      self.stop(self.native); self.native = None
      self.stop(self.qualifier); self.qualifier = None
      self.save('paused'); return
    if self.latch():
      with self.s.db() as db:counts = {r['split']:r['n'] for r in db.execute('SELECT split,COUNT(*) n FROM datasets GROUP BY split')}
      missing = [n for n in ('train','validation','test') if not counts.get(n)]
      self.save('waiting_real_data' if missing else 'student_pipeline', missing_splits=missing,
                data_splits=counts, qualified_sha256=self.state['qualified_sha256']); return
    config = self.s.config()
    if not config['teacher_adaptation']['enabled']:
      self.save('teacher_disabled'); return
    self.gates()
    if self.qualifier and self.qualifier.poll() is not None:
      q = read_json(self.s.root/'teacher-qualification-progress.json', {})
      if q.get('state') == 'failed':self.state['attempts'][self.qual_key] = 'failed_original_cases'
      elif q.get('state') != 'passed':
        self.qualifier = None
        raise RuntimeError('qualification interrupted; retry the same fixed checkpoint')
      self.qualifier = None
    progress = read_json(self.s.root/'teacher-training-progress.json', {})
    cycle = progress.get('cycle')
    if cycle:
      self.state['cycle'] = cycle
      folder, manifest, origin = self.dataset(cycle)
      for row in progress.get('history', []):
        descriptor = self.descriptor(cycle, row)
        key = f'{cycle}:{row["epoch"]}:{descriptor["sha256"]}:{self.runtime_key}'
        if key in self.state['attempts']:continue
        if not self.audit(cycle, descriptor):self.save('auditing_frozen_tensors'); return
        decision = checkpoint_quality(row, progress['baseline'], manifest['validation_guard_reference'])
        write_json(folder/f'checkpoint-quality-epoch{row["epoch"]:03d}.json', {
          'epoch':row['epoch'], 'metrics':row, 'baseline':progress['baseline'], **decision})
        if not decision['passed']:
          self.state['attempts'][key] = 'rejected_offline'
          self.s.event(f'自治閉環拒收第{cycle}輪Epoch{row["epoch"]}：離線原驗證條件未同時通過，接續訓練，不降低門檻。')
          continue
        if self.qualifier is None:
          self.qual_key = key
          log = (folder/f'autonomous-qualification-epoch{row["epoch"]:03d}.log').open('a')
          self.qualifier = subprocess.Popen([sys.executable,'-u','-m','tools.training_studio.teacher_checkpoint',
            '--root',str(self.s.root),'--cycle',str(cycle),'--selection','completed','--epoch',str(row['epoch'])],
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
          log.close()
          self.save('qualifying_original_cases'); return
    if self.native and self.native.poll() is not None:self.native = None
    if self.native is not None:
      phase={'generating':'preparing_data','transfer':'transferring_data','prefill':'building_context','training':'training'}.get(progress.get('phase'),'starting_training')
      self.save('qualifying_original_cases' if self.qualifier else phase); return
    if self.qualifier is not None:self.save('qualifying_original_cases'); return
    if cycle and progress.get('phase') != 'scheduled':
      if not self.advance(progress):self.save('auditing_continuation'); return
    state = read_json(self.s.root/'teacher-adaptation/state.json'); cycle = state['cycle']
    folder, manifest, origin = self.dataset(cycle)
    self.prepare(cycle, cycle+1)
    if self.program is None:self.program = self.r.program(snapshot=True)
    write_json(folder/'dataset-origin.before-autonomous-launch.json', origin)
    write_json(folder/'dataset-origin.json', {**origin, 'source_program':self.program,
      'source_commit':self.options.get('source_revision','snapshot'), 'parent':state['parent'],
      'autonomous_supervisor':True, 'prepared_before_training':True})
    log = (self.s.root/'autonomous-teacher.log').open('a')
    self.native = subprocess.Popen([sys.executable,'-u','-m','tools.training_studio.teacher_adapt',
      '--root',str(self.s.root)], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    log.close()
    self.save('starting_training', cycle=cycle, native_pid=self.native.pid, last_error=None)


def main():
  parser = argparse.ArgumentParser(); parser.add_argument('--root', required=True); args = parser.parse_args()
  store = Store(args.root)
  with (store.root/'closed-loop.lock').open('a+') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    loop = Loop(store); stopping = False; failures = 0
    def stop(*unused):
      nonlocal stopping
      stopping = True
    for sig in (signal.SIGTERM, signal.SIGINT):signal.signal(sig, stop)
    try:
      while not stopping:
        try:loop.tick(); failures = 0; loop.state['last_error'] = None; delay = 5
        except IntegrityError as exc:
          loop.stop(loop.native); loop.native = None
          loop.stop(loop.qualifier); loop.qualifier = None
          config = store.config(); config['teacher_adaptation']['enabled'] = False
          write_json(store.root/'config.json', config)
          loop.save('blocked_integrity', blocked_integrity=True, last_error=str(exc))
          store.event('自治閉環完整性保護停止：'+str(exc)); delay = 5
        except Exception as exc:
          failures += 1; delay = min(60, 5*2**min(failures, 4))
          loop.save('retrying', last_error=type(exc).__name__+': '+str(exc)[:800], retry_in_s=delay)
        for _ in range(delay):
          if stopping:break
          time.sleep(1)
    finally:
      loop.stop(loop.native); loop.stop(loop.qualifier)
      loop.save('stopped', active=False)


if __name__ == '__main__':main()
