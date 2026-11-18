"""Continuous real-expert adaptation; unchanged closed-loop gates control promotion."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import threading
import time
import urllib.request

from tools.training_studio.remote import Remote
from tools.training_studio.store import Store,exclusive_worker,read_json,write_json


def closed_loop_score(batch):
  rows=[read_json(path) for path in Path(batch).glob('*/result.json')]
  if not rows: return (-1,)*9
  failures={failure for row in rows for failure in row.get('failures',[])}
  red=[row.get('red_wait_audit',{}).get('longest_contiguous_red_stop_s',0.) for row in rows if row.get('scenario')=='red_light']
  # Qualification fails fast. An untested later case is not evidence that an
  # earlier-failing parent is safer. Preserve actual passed-prefix progress.
  return (sum(row.get('status')=='pass' and not row.get('failures') for row in rows),
    int('collision' not in failures),int('crossed_before_permission' not in failures),int('out_of_road' not in failures),
    int('lane_envelope' not in failures),int(not failures.intersection({'red_hold_not_maintained','red_stop_not_sustained'})),
    -len(failures),min(red,default=0.),
    -max((row.get('max_center_error_m',0.) for row in rows),default=0.))


def restore_parent_ranking(store,state):
  """Re-rank recorded candidates after changing the training-parent heuristic.

  This does not issue qualification: only the original complete suite may do so.
  """
  if state.get('ranking_version')==4: return
  best=(-1,)*9
  for batch in sorted((store.root/'teacher-cycles').glob('cycle-*/qualification-*')):
    if not batch.is_dir(): continue
    report=read_json(batch/'qualification.json',{})
    rows=report.get('results',[])
    paths=sorted(batch.glob('*/provenance.json'))
    if not rows or not paths: continue
    provenance=read_json(paths[0]).get('provenance',{})
    fingerprint=hashlib.sha256(json.dumps(provenance,sort_keys=True).encode()).hexdigest()
    adapter=provenance.get('action_expert_adapter') or {}
    if not adapter.get('path','').startswith('/studio/teacher/cycle-') or not adapter.get('sha256'): continue
    if any(row.get('model_provenance_sha256')!=fingerprint for row in rows): continue
    score=closed_loop_score(batch)
    if score>best:
      best=score
      state.update(parent=adapter,scenario=rows[-1]['scenario'])
  state.update(best_closed_loop=best,ranking_version=4)


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--root',required=True)
  args=parser.parse_args()
  store=Store(args.root)
  config=store.config()
  settings=config['teacher_adaptation']
  remote=Remote(config['remote'])
  program_root=remote.program(snapshot=True)
  container_program='/studio/'+Path(program_root).name
  owner='formosapilot.owner=training-studio'
  model_root=settings['model_root']
  if not model_root.startswith('/') or '..' in Path(model_root).parts: raise ValueError('invalid teacher model root')
  stop=threading.Event()
  for sig in (signal.SIGINT,signal.SIGTERM): signal.signal(sig,lambda *_:stop.set())
  child=None
  active_container=None
  current={}
  def authorized():
    return not stop.is_set() and store.enabled() and store.config().get('teacher_adaptation',{}).get('enabled') is True
  def report(phase,**fields):
    current.update(fields)
    current.update(phase=phase,updated=time.time())
    write_json(store.root/'teacher-training-progress.json',current)
  def command(parts): return shlex.join([str(part) for part in parts])
  def call(parts,**kwargs): return remote.call(command(parts),**kwargs)
  def publish_service(pointer):
    nonlocal active_container
    relative=f'teacher/service-{pointer["sha256"][:16]}.json'
    local=store.root/relative
    write_json(local,pointer)
    call(['mkdir','-p',remote.root+'/teacher'])
    remote.upload(local,remote.root+'/'+relative)
    # Mutations are restricted to the explicitly labeled Studio-owned sidecar.
    existing=remote.call('docker ps -a --filter name=^/studio-teacher$ --format "{{.Names}}"',capture_output=True,text=True).stdout.strip()
    if existing:
      label=remote.call('docker inspect studio-teacher --format \'{{index .Config.Labels "formosapilot.owner"}}\'',capture_output=True,text=True).stdout.strip()
      if label!='training-studio': raise RuntimeError('refusing to replace a foreign teacher container')
      call(['docker','rm','-f','studio-teacher'])
    call(['docker','run','-d','--name','studio-teacher','--label',owner,'--gpus','all','--network','bridge','--memory','32g','--user','1000:1000',
      '-p','127.0.0.1:8767:8767','-v',remote.root+':/studio','-v',model_root+':/teacher:ro',
      '-v',settings['legacy_deps_root']+':/old:ro','-w','/studio','-e','HF_HUB_OFFLINE=1',
      '-e','PYTHONPATH=/teacher/deps:/old/deps:/teacher/source/src:'+container_program,'--entrypoint','python',remote.image,
      '-u','-m','tools.training_studio.teacher_service','--listen','0.0.0.0','--model','/teacher/model','--receipt','/teacher/model-receipt.json',
      '--adapter','/studio/'+relative])
    cfg=store.config()
    cfg['teacher_url']='http://127.0.0.1:18767'
    cfg['teacher_connection']['tunnel_command']=[*cfg['remote']['ssh_command'],'-N','-o','ExitOnForwardFailure=yes','-o','ConnectTimeout=10',
      '-o','ServerAliveInterval=15','-o','ServerAliveCountMax=3','-L','127.0.0.1:18767:127.0.0.1:8767',cfg['remote']['host']]
    write_json(store.root/'config.json',cfg)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline=time.monotonic()+180
    while authorized() and time.monotonic()<deadline:
      try:
        with opener.open(cfg['teacher_url']+'/health',timeout=5) as response: health=json.load(response)
        if health['provenance'].get('action_expert_adapter',{}).get('sha256')==pointer['sha256']: return health
      except (OSError,ValueError): pass
      stop.wait(2)
    raise RuntimeError('Studio teacher sidecar did not become ready')
  def run_local(module,arguments,log_path,progress=None,allowed=(0,)):
    nonlocal child
    with log_path.open('w') as log:
      child=subprocess.Popen([sys.executable,'-u','-m',module,*map(str,arguments)],cwd=config['qualification_checkout'],
        env={**os.environ,'DISPLAY':config.get('qualification_display',':0')},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
      while child.poll() is None:
        if not authorized(): raise InterruptedError('teacher adaptation paused')
        if progress and progress.is_file():
          value=read_json(progress)
          value.pop('phase',None)
          report('generating',**value)
        stop.wait(1)
    if child.returncode not in allowed: raise RuntimeError(module+' failed; inspect '+str(log_path))
    child=None
  loop_root=store.root/'teacher-adaptation'
  loop_root.mkdir(exist_ok=True)
  state=read_json(loop_root/'state.json',{'cycle':2,'parent':settings['initial_parent'],'scenario':'red_light'})
  restore_parent_ranking(store,state)
  gate_files=('scene.py','edge_stop_audit.py','edge_experiment.py','nvidia_plan.py')
  gates={name:hashlib.sha256((Path(config['qualification_checkout'])/'openpilot/tools/sim/training'/name).read_bytes()).hexdigest() for name in gate_files}
  if state.get('acceptance') and state['acceptance']!=gates: raise RuntimeError('qualification/tracker implementation changed; refusing silent gate changes')
  state['acceptance']=gates
  write_json(loop_root/'state.json',state)
  with exclusive_worker(loop_root):
    try:
      while authorized():
        if state.get('pending_container'):
          pending=state['pending_container']
          names=remote.call(command(['docker','ps','-a','--filter','name=^/'+pending+'$','--filter','label='+owner,'--format','{{.Names}}']),capture_output=True,text=True).stdout.strip()
          if names: call(['docker','stop','--time','3',pending])
          state.pop('pending_container')
          write_json(loop_root/'state.json',state)
        cycle=state['cycle']
        current.clear()
        report('generating',cycle=cycle)
        folder=store.root/'teacher-cycles'/f'cycle-{cycle:03d}'
        folder.mkdir(parents=True,exist_ok=True)
        data=folder/'data'
        try:
          if not (data/'manifest.json').is_file():
            if data.exists():
              data.rename(folder/f'data-incomplete-{int(time.time())}')
            run_local('tools.training_studio.teacher_data',['--cycle',cycle,'--scenario',state['scenario'],'--rehearsal',','.join(state.get('rehearsal',[])),'--output',data],folder/'data.log',data/'generation-progress.json')
          destination=remote.root+f'/teacher/cycle-{cycle:03d}'
          replay=store.config().get('teacher_adaptation',{}).get('supervision_replay_manifest')
          if replay:
            from tools.training_studio.teacher_replay import append_replay
            added=append_replay(data,replay)
            if added: store.event(f'教師監督重播：第 {cycle} 輪加入 {added} 筆已驗證修正樣本')
          report('transfer',cycle=cycle,samples=len(read_json(data/'manifest.json')['samples']))
          call(['mkdir','-p',destination+'/data'])
          # Use a tar stream, so nested packet paths are preserved without shell interpolation.
          import tarfile,io
          stream=io.BytesIO()
          with tarfile.open(fileobj=stream,mode='w:gz') as archive: archive.add(data,arcname='data')
          remote.call('tar -xzf - -C '+shlex.quote(destination),input=stream.getvalue(),timeout=300)
          report('prefill',cycle=cycle,epoch=0,epochs=settings.get('epochs',12),history=[])
          container=f'studio-teacher-train-{cycle:03d}'
          active_container=container
          lease=destination+'/lease'
          call(['touch',lease])
          lease_done=threading.Event()
          def refresh_lease(done=lease_done,path=lease,owned_container=container):
            while not done.wait(5):
              if not authorized():
                try: call(['docker','stop','--time','3',owned_container],timeout=15)
                except subprocess.SubprocessError: pass
                return
              try: call(['touch',path],timeout=15)
              except subprocess.SubprocessError: pass
          threading.Thread(target=refresh_lease,daemon=True).start()
          args=['docker','run','--rm','--name',container,'--label',owner,'--gpus','all','--network','none','--memory','60g','--user','1000:1000',
            '-v',remote.root+':/studio','-v',model_root+':/teacher:ro','-v',settings['legacy_deps_root']+':/old:ro','-w','/studio','-e','HF_HUB_OFFLINE=1',
            '-e','PYTHONPATH=/teacher/deps:/old/deps:/teacher/source/src:'+container_program,'--entrypoint','python',remote.image,
            '-u','-m','tools.training_studio.teacher_train','--data',f'/studio/teacher/cycle-{cycle:03d}/data',
            '--output',f'/studio/teacher/cycle-{cycle:03d}/output','--parent',state['parent']['path'],'--parent-sha256',state['parent']['sha256'],
            '--epochs',str(settings.get('epochs',12)),'--learning-rate',str(settings.get('learning_rate',1e-5)),
            '--lease',f'/studio/teacher/cycle-{cycle:03d}/lease','--expanded-expert']
          child=subprocess.Popen(remote.command(command(args)),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
          with (folder/'train.log').open('w') as log:
            for line in child.stdout:
              log.write(line); log.flush()
              if not authorized(): raise InterruptedError('teacher adaptation paused')
              try:
                event=json.loads(line)
                if event.get('phase') in ('prefill','training','completed'): report(event.pop('phase'),cycle=cycle,**event)
              except ValueError: pass
          if child.wait(): raise RuntimeError('DGX teacher optimizer failed; inspect train.log')
          lease_done.set()
          child=None; active_container=None
          remote.download(destination+'/output/result.json',folder/'result.json')
          result=read_json(folder/'result.json')
          candidates=[]
          if result['adapter_saved']: candidates.append(('safety','best.safetensors',result.get('best_epoch')))
          if result.get('balanced_adapter_saved'): candidates.append(('balanced','balanced.safetensors',result.get('balanced_epoch')))
          seen=set()
          for selection,filename,epoch in candidates:
            remote.download(destination+'/output/'+filename,folder/filename)
            checksum=hashlib.sha256((folder/filename).read_bytes()).hexdigest()
            if checksum in seen: continue
            seen.add(checksum)
            pointer={'path':f'/studio/teacher/cycle-{cycle:03d}/output/'+filename,'sha256':checksum,
              'cycle':cycle,'training_epoch':epoch,'selection':selection,'scope':'actual_Edge_expert_expanded_LoRA','driving_qualified':False}
            report('qualification',cycle=cycle,selection=selection)
            health=publish_service(pointer)
            fingerprint=hashlib.sha256(json.dumps(health['provenance'],sort_keys=True).encode()).hexdigest()
            batch=folder/('qualification-'+selection)
            write_json(store.root/'teacher-attempt.json',{'fingerprint':fingerprint,'batch':str(batch),'started':time.time()})
            run_local('tools.training_studio.qualification',['--root',store.root,'--batch',batch],folder/('qualification-'+selection+'.log'),allowed=(0,2))
            outcome=read_json(store.root/'teacher-qualification-progress.json',{})
            if outcome.get('state')=='passed':
              state.update(parent=pointer,cycle=cycle+1,qualified_sha256=pointer['sha256'])
              write_json(loop_root/'state.json',state)
              report('qualified',cycle=cycle)
              store.event('教師完整資格通過，已結束教師適配；學生等待完整資料組')
              return
            score=closed_loop_score(batch)
            if score>tuple(state.get('best_closed_loop',(-1,))):
              state['parent']=pointer
              state['best_closed_loop']=score
              state['scenario']=outcome.get('scenario','red_light')
            state['rehearsal']=sorted(set(state.get('rehearsal',[]))|{outcome.get('scenario','red_light')})
          state['cycle']=cycle+1
          write_json(loop_root/'state.json',state)
        except InterruptedError: raise
        except Exception as exc:
          if 'lease_done' in locals(): lease_done.set()
          report('error',cycle=cycle,error=str(exc))
          store.event('教師適配保留失敗：'+str(exc))
          if active_container:
            try: call(['docker','stop','--time','3',active_container],timeout=15)
            except subprocess.SubprocessError: state['pending_container']=active_container
          if child and child.poll() is None:
            child.terminate(); child.wait(timeout=10)
          child=None; active_container=None
          state['cycle']=cycle+1
          write_json(loop_root/'state.json',state)
          stop.wait(10)
    except InterruptedError:
      report('paused',cycle=state['cycle'])
    finally:
      if 'lease_done' in locals(): lease_done.set()
      if not authorized() and current.get('phase')!='qualified': report('paused',cycle=state['cycle'])
      if active_container:
        try: call(['docker','stop','--time','3',active_container])
        except subprocess.SubprocessError: pass
      if child and child.poll() is None:
        os.killpg(child.pid,signal.SIGTERM)
        child.wait(timeout=15)


if __name__=='__main__': main()
