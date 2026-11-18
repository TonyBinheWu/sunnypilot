"""Run the real front-camera simulation curriculum and bind its evidence to the teacher."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request

from tools.training_studio.qualify_teacher import qualify
from tools.training_studio.store import Store, read_json, write_json

CASES=[('red_light',300,None,24),('red_light',301,13,27),('red_light',302,19,33)]
CASES += [(name,303,None,24) for name in ('lane_center','pedestrian','left_turn','right_turn','yield_left','yield_right','left_arrow','right_arrow')]


def log_progress(path):
  """Expose measured timing/counts, without publishing teacher reasoning text."""
  if not path.is_file(): return {}
  with path.open('rb') as stream:
    stream.seek(max(0,path.stat().st_size-32768))
    lines=stream.read().decode('utf-8',errors='replace').splitlines()
  for line in reversed(lines):
    try:
      row=json.loads(line)
      if 'plan' in row:
        return {key:row[key] for key in ('plan','simulation_time_s','inference_s') if key in row}
    except ValueError:
      pass
  return {}


def run(root,batch):
  store=Store(root)
  config=store.config()
  checkout=Path(config['qualification_checkout']).resolve()
  batch=Path(batch).resolve()
  batch.mkdir(parents=True,exist_ok=True)
  results=[]
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  with opener.open(config['teacher_url'].rstrip('/')+'/health',timeout=10) as response:
    health=json.load(response)
  expected=hashlib.sha256(json.dumps(health['provenance'],sort_keys=True).encode()).hexdigest()
  child=None
  stopped=False
  def stop(*_):
    nonlocal stopped
    stopped=True
  for sig in (signal.SIGTERM,signal.SIGINT): signal.signal(sig,stop)
  def report(**fields):
    write_json(store.root/'teacher-qualification-progress.json',{'batch':str(batch),'updated':time.time(),'done':len(results),'total':len(CASES),**fields})
  try:
    for scenario,seed,hold,seconds in CASES:
      destination=batch/f'{scenario}-{seed}'
      log_path=batch/f'{scenario}-{seed}.log'
      command=[sys.executable,'-u','-m','openpilot.tools.sim.training.edge_experiment','--scenario',scenario,'--seed',str(seed),'--seconds',str(seconds),'--url',config['teacher_url'],'--output',str(destination)]
      if hold is not None: command += ['--red-hold',str(hold)]
      report(state='running',scenario=scenario,seed=seed)
      store.event(f'教師資格驗證：{scenario} / seed {seed}')
      if not (destination/'result.json').exists():
        with log_path.open('w') as log:
          child=subprocess.Popen(command,cwd=checkout,env={**os.environ,'DISPLAY':config.get('qualification_display',':0')},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
          started=time.monotonic()
          while child.poll() is None:
            if stopped: raise InterruptedError('qualification interrupted; no receipt issued')
            if time.monotonic()-started>float(config.get('qualification_case_timeout_s',1800)):
              raise TimeoutError('qualification case exceeded its time limit')
            report(state='running',scenario=scenario,seed=seed,**log_progress(log_path))
            time.sleep(1)
        if child.returncode: raise RuntimeError(f'{scenario} simulator exited {child.returncode}; see {log_path.name}')
      result=read_json(destination/'result.json',{})
      if result.get('model_provenance_sha256')!=expected:
        raise ValueError('teacher changed or stored episode belongs to another checkpoint')
      if result.get('scenario')!=scenario or result.get('seed')!=seed:
        raise ValueError('qualification case identity mismatch')
      results.append(result)
      write_json(batch/'qualification.json',{'results':results,'passed':False})
      if result.get('status')!='pass' or result.get('failures'):
        report(state='failed',scenario=scenario,seed=seed,failures=result.get('failures',[]),red_wait_audit=result.get('red_wait_audit'),**log_progress(log_path))
        store.event('教師資格未通過：'+scenario+' / '+', '.join(result.get('failures',[])))
        return False
    write_json(batch/'qualification.json',{'results':results,'passed':True})
    receipt=qualify(batch,config['teacher_qualification'])
    report(state='passed',cases=len(receipt['cases']))
    store.event('教師完整閉迴路資格通過；資料組收齊後可自動蒸餾')
    return True
  except Exception as exc:
    report(state='interrupted' if stopped else 'error',error=str(exc))
    raise
  finally:
    if child and child.poll() is None:
      os.killpg(child.pid,signal.SIGTERM)
      try: child.wait(timeout=10)
      except subprocess.TimeoutExpired:
        os.killpg(child.pid,signal.SIGKILL)
        child.wait()


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--root',required=True)
  parser.add_argument('--batch',required=True)
  args=parser.parse_args()
  if not run(args.root,args.batch): raise SystemExit(2)


if __name__=='__main__': main()
