"""Own the Studio SSH tunnel, probe the actual teacher, and supervise qualification."""
import hashlib
import json
import subprocess
import sys
import time
import urllib.request

from tools.training_studio.engine import TEACHER_REVISION
from tools.training_studio.store import read_json,write_json


def check_health(health):
  p=health.get('provenance',{})
  return bool(health.get('teacher_ready') is True and p.get('revision')==TEACHER_REVISION
    and p.get('weights_verified') is True and p.get('camera_ids')==[1,6]
    and p.get('input_profile')=='experimental_front_only')


def qualified(receipt,health):
  required={'lane_center','red_light','pedestrian','left_turn','right_turn','yield_left','yield_right','left_arrow','right_arrow'}
  return bool(check_health(health) and receipt and receipt.get('passed') is True
    and receipt.get('input_profile')=='experimental_front_only' and receipt.get('provenance')==health['provenance']
    and required <= {case.get('scenario') for case in receipt.get('cases',[]) if case.get('passed') is True}
    and {300,301,302} <= {case.get('seed') for case in receipt.get('cases',[]) if case.get('scenario')=='red_light' and case.get('passed') is True})


def training_ready(store):
  health=read_json(store.root/'teacher-health.json',{})
  return bool(health.get('connected') and health.get('qualified') and 0<=time.time()-health.get('updated',0)<20)


def adaptation_progress(store):
  saved=read_json(store.root/'teacher-training-progress.json',{})
  if saved: return saved  # never compare a DGX wall clock with the supervisor clock
  path=store.root/'teacher-pilot.log'
  if path.is_file():
    with path.open('rb') as stream:
      stream.seek(max(0,path.stat().st_size-131072))
      for line in reversed(stream.read().decode('utf-8',errors='replace').splitlines()):
        try:
          row=json.loads(line)
          if row.get('phase') in ('prefill','training','completed'):
            return {**row,'cycle':1}
        except ValueError: pass
  return saved


def monitor(store,stop):
  tunnel=child=None
  tunnel_command=None
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  try:
    while not stop.is_set():
      config=store.config()
      adapting=config.get('teacher_adaptation',{}).get('enabled') is True
      connection=config.get('teacher_connection',{})
      command=connection.get('tunnel_command')
      if tunnel is not None and command!=tunnel_command:
        tunnel.terminate()
        tunnel.wait(timeout=10)
        tunnel=None
      try:
        with opener.open(config['teacher_url'].rstrip('/')+'/health',timeout=5) as response:
          health=json.loads(response.read(1024*1024))
        if not check_health(health): raise ValueError('teacher checkpoint/camera provenance mismatch')
        fingerprint=hashlib.sha256(json.dumps(health['provenance'],sort_keys=True).encode()).hexdigest()
        path=config.get('teacher_qualification')
        receipt=read_json(path,{}) if path else {}
        attempt=read_json(store.root/'teacher-attempt.json',{})
        ready=qualified(receipt,health)
        if attempt.get('fingerprint')==fingerprint and receipt.get('completed_at',0)<attempt.get('started',0):
          ready=False  # a failed explicit revalidation cannot reuse an older passing receipt
        status={'updated':time.time(),'connected':True,'qualified':ready,'fingerprint':fingerprint,
          'revision':health['provenance']['revision'],'camera_ids':[1,6],'gpu':health['provenance'].get('gpu')}
        write_json(store.root/'teacher-health.json',status)
        retry=store.root/'teacher-retry.json'
        if child and child.poll() is not None: child=None
        if not adapting and config.get('qualification_checkout') and child is None and (retry.exists() or (not ready and attempt.get('fingerprint')!=fingerprint)):
          if retry.exists(): retry.unlink()
          batch=store.root/'teacher-qualification'/f'{fingerprint[:12]}-{int(time.time())}'
          write_json(store.root/'teacher-attempt.json',{'fingerprint':fingerprint,'batch':str(batch),'started':time.time()})
          with (store.root/'teacher-qualification.log').open('a') as log:
            child=subprocess.Popen([sys.executable,'-u','-m','tools.training_studio.qualification','--root',str(store.root),'--batch',str(batch)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
          write_json(store.root/'teacher-health.json',{**status,'qualified':False})
      except Exception as exc:
        write_json(store.root/'teacher-health.json',{'updated':time.time(),'connected':False,'qualified':False,'error':type(exc).__name__})
        if command and (tunnel is None or tunnel.poll() is not None):
          if not isinstance(command,list) or not all(isinstance(x,str) for x in command):
            raise ValueError('tunnel_command must be a trusted local argument array')
          with (store.root/'teacher-tunnel.log').open('a') as log:
            tunnel=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
          tunnel_command=command
      # Offline adaptation loads its bound parent directly and repairs its own
      # teacher sidecar at qualification. A crashed API must not deadlock it.
      if child and child.poll() is not None: child=None
      if adapting and store.enabled() and not training_ready(store) and child is None:
        with (store.root/'teacher-adaptation.log').open('a') as log:
          child=subprocess.Popen([sys.executable,'-u','-m','tools.training_studio.teacher_adapt','--root',str(store.root)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
      stop.wait(3)
  finally:
    for owned in (child,tunnel):
      if owned and owned.poll() is None:
        owned.terminate()
        try: owned.wait(timeout=15)
        except subprocess.TimeoutExpired:
          owned.kill()
          owned.wait()
