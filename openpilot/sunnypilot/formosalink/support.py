"""Opt-in text diagnostics and separately requested parked rlog uploads."""
import base64
import hashlib
import io
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import threading
import time

from openpilot.sunnypilot.formosalink.identity import read
from openpilot.sunnypilot.formosalink.protocol import sign
from openpilot.sunnypilot.formosalink.service_policy import self_hosted_origin

SOURCES={
  'startup':'/tmp/carrot_startup_failure.log',
  'agnos':'/data/agnos-updater-ui.log',
  'installer':'/data/carrot-installer.log',
  'installer_error':'/data/carrot-installer-error.txt',
  'console':'/tmp/tmux.log',
}


def sanitize(text):
  text=re.sub(r'-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----','[REDACTED KEY]',text,flags=re.S)
  text=re.sub(r'https?://[^\s]+','[REDACTED URL]',text)
  text=re.sub(r'(?im)^.*(?:authorization|cookie|token|password|secret|private_key|pair_code|latitude|longitude|gpsLocation|api_key|access_key|mapbox|destination).*$','[REDACTED LINE]',text)
  text=re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b','[REDACTED IP]',text)
  text=re.sub(r'\b[0-9a-fA-F]{64,}\b','[REDACTED LONG HEX]',text)
  return text


def diagnostic_report():
  result={'version':1,'captured_at':time.time(),'coverage':'available_logs_only','logs':{},'missing':[]}
  for label,name in SOURCES.items():
    path=Path(name)
    try:
      if path.is_symlink() or not path.is_file():raise OSError('unavailable')
      with path.open('rb') as stream:
        stream.seek(max(0,path.stat().st_size-8192));data=stream.read(8192)
      result['logs'][label]=sanitize(data.decode('utf-8','replace'))
    except OSError:result['missing'].append(label)
  try:
    root=Path(__file__).resolve().parents[3]
    result['commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,timeout=2,text=True).strip()
  except (OSError,subprocess.SubprocessError):result['commit']='unknown'
  return json.dumps(result,ensure_ascii=True).encode()


def latest_route(root=Path('/data/media/0/realdata'), now=None):
  now=time.time() if now is None else now;root=Path(root);groups={}
  # Closed segments only. No recursive arbitrary-file collection or videos.
  if not root.is_dir():return []
  for directory in sorted(root.iterdir(),reverse=True)[:2000]:
    if directory.is_symlink() or not directory.is_dir():continue
    for name in ('rlog.zst','rlog.bz2'):
      path=directory/name
      if path.is_symlink() or not path.is_file():continue
      route=directory.name.rsplit('--',1)[0]
      groups.setdefault(route,[]).append(path)
  for route,paths in sorted(groups.items(),reverse=True):
    # Do not silently omit a still-open last segment from a "complete" route.
    if any(now-path.stat().st_mtime<120 for path in paths):continue
    return sorted(paths)
  return []


def call(session, identity, private, payload):
  response=session.post(identity['origin']+'/api/v1/agent/support',json=sign(private,identity['device_id'],'support',payload),timeout=15,stream=True)
  try:
    response.raise_for_status();raw=bytearray()
    for part in response.iter_content(4096):
      raw.extend(part)
      if len(raw)>16384:raise ValueError('oversized support acknowledgement')
    return json.loads(raw)
  finally:response.close()


def upload(session, identity, private, stream, name, kind, job, parked, stop):
  digest=hashlib.sha256();size=0
  for block in iter(lambda:stream.read(65536),b''):
    if stop.is_set() or not parked():raise ValueError('upload deferred')
    digest.update(block);size+=len(block)
  stream.seek(0)
  result=call(session,identity,private,{'action':'start','kind':kind,'name':name,'size':size,'sha256':digest.hexdigest(),'job':job})
  offset=0
  while offset<size:
    if stop.is_set() or not parked():raise ValueError('upload deferred')
    data=stream.read(32768)
    result=call(session,identity,private,{'action':'chunk','id':result['id'],'offset':offset,'data':base64.b64encode(data).decode()})
    offset+=len(data)
    if result.get('offset')!=offset:raise ValueError('invalid support acknowledgement')
    stop.wait(.08)
  if not result.get('complete'):raise ValueError('incomplete upload')


def run(directory,stop):
  import requests
  from openpilot.common.params import Params
  params=Params();last_digest=None;last_sent=0
  parked=lambda:params.get_bool('IsOffroad')
  while not stop.is_set():
    try:
      identity,private,_=read(directory);self_hosted_origin(identity['origin'])
      with requests.Session() as session:
        policy=call(session,identity,private,{'action':'poll'})
        if parked() and policy.get('diagnostics') is True and time.monotonic()-last_sent>900:
          data=diagnostic_report()
          # Timestamp is excluded from deduplication; one initial report per boot.
          parsed=json.loads(data);parsed.pop('captured_at',None)
          digest=hashlib.sha256(json.dumps(parsed,sort_keys=True).encode()).hexdigest()
          if digest!=last_digest:
            upload(session,identity,private,io.BytesIO(data),'diagnostic-'+str(int(time.time()))+'.json','diagnostic',None,parked,stop)
            last_digest=digest
          last_sent=time.monotonic()
        job=policy.get('route_job')
        if parked() and isinstance(job,str):
          outcome='done'
          try:
            paths=latest_route()
            if not paths:outcome='no_completed_route'
            elif len(paths)>128 or any(p.stat().st_size>64*1024*1024 for p in paths) or sum(p.stat().st_size for p in paths)>512*1024*1024:outcome='size_limit'
            else:
              for path in paths:
                name=re.sub('[^A-Za-z0-9_.-]','_',path.parent.name+'-'+path.name)[-120:]
                with path.open('rb') as stream:upload(session,identity,private,stream,name,'rlog',job,parked,stop)
          except Exception:outcome='upload_failed'
          call(session,identity,private,{'action':'finish','job':job,'outcome':outcome})
    except Exception as exc:
      # Never include request data or credentials in local logs.
      logging.getLogger('formosalink').info('Support sync unavailable (%s)',type(exc).__name__)
    stop.wait(60)


def start(directory,stop):
  thread=threading.Thread(target=run,args=(directory,stop),name='formosalink-support',daemon=True)
  thread.start();return thread
