"""Bounded, signed diagnostic uploads. Kept outside the website tree."""
import asyncio
import base64
import hashlib
import json
import re
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from fastapi import HTTPException, Request
from fastapi.responses import FileResponse
from openpilot.sunnypilot.formosalink.protocol import verify

RETENTION = 30 * 86400
MAX_FILE = 64 * 1024 * 1024
MAX_DEVICE = 1024 * 1024 * 1024
MAX_TOTAL = 10 * MAX_DEVICE


class SupportStore:
  def __init__(self, root):
    self.root = Path(root) / 'support'
    self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
    self.path = self.root / 'index.sqlite3'
    with self.db() as db:
      db.executescript('''
        CREATE TABLE IF NOT EXISTS consent(device TEXT PRIMARY KEY, owner TEXT NOT NULL, enabled INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, device TEXT NOT NULL, owner TEXT NOT NULL, created REAL NOT NULL, expires REAL NOT NULL, state TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS files(id TEXT PRIMARY KEY, device TEXT NOT NULL, owner TEXT NOT NULL, kind TEXT NOT NULL, name TEXT NOT NULL, job TEXT, created REAL NOT NULL, expires REAL NOT NULL, size INTEGER NOT NULL, sha TEXT NOT NULL, offset INTEGER NOT NULL, complete INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS support_device ON files(device,created);
      ''')

  @contextmanager
  def db(self):
    db = sqlite3.connect(self.path, timeout=10)
    db.row_factory = sqlite3.Row
    try:
      with db:yield db
    finally:db.close()

  def purge(self):
    now = time.time()
    with self.db() as db:
      rows = db.execute('SELECT id FROM files WHERE expires<=? OR (complete=0 AND created<?)', (now, now-86400)).fetchall()
      for row in rows:
        (self.root / row['id']).unlink(missing_ok=True)
        db.execute('DELETE FROM files WHERE id=?', (row['id'],))
      db.execute("UPDATE jobs SET state='expired' WHERE state='pending' AND expires<=?", (now,))
      db.execute('DELETE FROM jobs WHERE created<?', (now-RETENTION,))
      # Crash between file creation and transaction commit may leave an orphan.
      known={x[0] for x in db.execute('SELECT id FROM files')}
      for path in self.root.iterdir():
        if re.fullmatch('[a-f0-9-]{36}',path.name) and path.name not in known and path.is_file() and path.stat().st_mtime<now-86400:
          path.unlink(missing_ok=True)

  def allowed(self, db, device, owner):
    return bool(db.execute('SELECT 1 FROM consent WHERE device=? AND owner=? AND enabled=1', (device, owner)).fetchone())

  def policy(self, device, owner):
    self.purge()
    with self.db() as db:
      enabled = self.allowed(db, device, owner)
      job = db.execute("SELECT id FROM jobs WHERE device=? AND owner=? AND state='pending' AND expires>? ORDER BY created LIMIT 1", (device, owner, time.time())).fetchone()
      latest=db.execute('SELECT id,state,created,expires FROM jobs WHERE device=? AND owner=? ORDER BY created DESC LIMIT 1',(device,owner)).fetchone()
      return {'diagnostics': enabled, 'route_job': job['id'] if job else None, 'latest_job':dict(latest) if latest else None,'retention_days': 30}

  def consent(self, device, owner, enabled):
    with self.db() as db:
      db.execute('INSERT INTO consent VALUES(?,?,?) ON CONFLICT(device) DO UPDATE SET owner=excluded.owner,enabled=excluded.enabled', (device, owner, int(enabled)))

  def route_job(self, device, owner):
    with self.db() as db:
      if db.execute("SELECT 1 FROM jobs WHERE device=? AND state='pending' AND expires>?", (device, time.time())).fetchone():
        raise ValueError('request_pending')
      identifier = str(uuid.uuid4())
      db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?)', (identifier, device, owner, time.time(), time.time()+86400, 'pending'))
      return identifier

  def list(self, device=None, owner=None, query=''):
    self.purge()
    with self.db() as db:
      rows = db.execute('SELECT f.id,f.device,f.owner,f.kind,f.name,f.job,f.created,f.expires,f.size,f.complete,j.state AS job_state FROM files f LEFT JOIN jobs j ON j.id=f.job ORDER BY f.created DESC LIMIT 2000').fetchall()
      return [dict(x) for x in rows if (device is None or x['device']==device) and (owner is None or x['owner']==owner) and query.lower() in (x['name']+' '+x['kind']+' '+x['device']).lower()][:200]

  def start(self, device, owner, p):
    if set(p) != {'action','kind','name','size','sha256','job'} or p['kind'] not in ('diagnostic','rlog'):
      raise ValueError('invalid_metadata')
    if not isinstance(p['name'], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,119}', p['name']):
      raise ValueError('invalid_name')
    if type(p['size']) is not int or not 0 < p['size'] <= (262144 if p['kind']=='diagnostic' else MAX_FILE):
      raise ValueError('file_too_large')
    if not isinstance(p['sha256'], str) or not re.fullmatch('[a-f0-9]{64}',p['sha256']):
      raise ValueError('invalid_digest')
    if p['job'] is not None and (not isinstance(p['job'],str) or not re.fullmatch('[a-f0-9-]{36}',p['job'])):raise ValueError('invalid_job')
    self.purge()
    with self.db() as db:
      db.execute('BEGIN IMMEDIATE')
      if p['kind']=='diagnostic':
        if p['job'] is not None or not self.allowed(db,device,owner):
          raise ValueError('sharing_disabled')
      elif not db.execute("SELECT 1 FROM jobs WHERE id=? AND device=? AND owner=? AND state='pending' AND expires>?", (p['job'],device,owner,time.time())).fetchone():
        raise ValueError('route_consent_required')
      total = db.execute('SELECT COALESCE(SUM(size),0) FROM files').fetchone()[0]
      used = db.execute('SELECT COALESCE(SUM(size),0) FROM files WHERE device=?', (device,)).fetchone()[0]
      if total+p['size']>MAX_TOTAL or used+p['size']>MAX_DEVICE:
        raise ValueError('storage_quota')
      identifier=str(uuid.uuid4());now=time.time()
      # Retention begins at reservation; partial data never lasts more than one day.
      db.execute('INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', (identifier,device,owner,p['kind'],p['name'],p['job'],now,now+RETENTION,p['size'],p['sha256'],0,0))
      (self.root/identifier).touch(mode=0o600,exist_ok=False)
      return {'id':identifier,'offset':0}

  def chunk(self, device, owner, p):
    if set(p) != {'action','id','offset','data'} or type(p['offset']) is not int or not isinstance(p['data'],str) or len(p['data'])>44000:
      raise ValueError('invalid_chunk')
    if not isinstance(p['id'],str) or not re.fullmatch('[a-f0-9-]{36}',p['id']):raise ValueError('invalid_identifier')
    data=base64.b64decode(p['data'],validate=True)
    if not 0<len(data)<=32768:
      raise ValueError('invalid_chunk')
    with self.db() as db:
      db.execute('BEGIN IMMEDIATE')
      row=db.execute('SELECT * FROM files WHERE id=? AND device=? AND owner=? AND expires>?', (p['id'],device,owner,time.time())).fetchone()
      if not row:
        raise ValueError('upload_unavailable')
      if row['kind']=='diagnostic' and not self.allowed(db,device,owner):
        raise ValueError('sharing_disabled')
      if row['kind']=='rlog' and not db.execute("SELECT 1 FROM jobs WHERE id=? AND device=? AND owner=? AND state='pending' AND expires>?", (row['job'],device,owner,time.time())).fetchone():
        raise ValueError('route_consent_required')
      path=self.root/row['id']
      if p['offset']<row['offset']:
        with path.open('rb') as stream:
          stream.seek(p['offset'])
          if p['offset']<0 or p['offset']+len(data)>row['offset'] or stream.read(len(data))!=data:
            raise ValueError('conflicting_chunk')
        return {'id':row['id'],'offset':row['offset'],'complete':bool(row['complete'])}
      if row['complete'] or p['offset']!=row['offset'] or p['offset']+len(data)>row['size']:
        raise ValueError('invalid_offset')
      with path.open('r+b') as stream:
        stream.truncate(row['offset']);stream.seek(row['offset']);stream.write(data);stream.flush()
      offset=p['offset']+len(data);complete=offset==row['size']
      if complete:
        with path.open('rb') as stream:
          digest=hashlib.sha256()
          for block in iter(lambda:stream.read(65536),b''):digest.update(block)
        if digest.hexdigest()!=row['sha']:
          path.unlink(missing_ok=True);db.execute('DELETE FROM files WHERE id=?',(row['id'],))
          # Commit invalid-file deletion before returning the validation error.
          db.commit();raise ValueError('digest_mismatch')
      db.execute('UPDATE files SET offset=?,complete=? WHERE id=?',(offset,int(complete),row['id']))
      return {'id':row['id'],'offset':offset,'complete':complete}

  def delete(self, device, owner):
    with self.db() as db:
      db.execute('BEGIN IMMEDIATE')
      for row in db.execute('SELECT id FROM files WHERE device=? AND owner=?',(device,owner)):
        (self.root/row['id']).unlink(missing_ok=True)
      db.execute('DELETE FROM files WHERE device=? AND owner=?',(device,owner))
      db.execute('DELETE FROM jobs WHERE device=? AND owner=?',(device,owner))
      db.execute('DELETE FROM consent WHERE device=? AND owner=?',(device,owner))


def register(app, directory, store, owner, rate):
  support=SupportStore(directory);app.state.support=support

  def owned(request,device):
    user=owner(request);row=store.get(device)
    if not row or row['owner_id']!=user['id']:
      raise HTTPException(404,'device unavailable')
    return user,row

  @app.get('/api/v1/support/{device}')
  def overview(device: str,request: Request):
    user,row=owned(request,device)
    return {**support.policy(device,user['id']),'files':support.list(device,user['id']), 'installation_coverage':'available_logs_only'}

  @app.post('/api/v1/support/{device}/consent')
  async def consent(device: str,request: Request):
    user,row=owned(request,device);p=await request.json()
    if not isinstance(p,dict) or set(p)!={'diagnostics'} or type(p['diagnostics']) is not bool:
      raise HTTPException(400,'invalid consent')
    support.consent(device,user['id'],p['diagnostics']);return {'ok':True}

  @app.post('/api/v1/support/{device}/route')
  async def route(device: str,request: Request):
    user,row=owned(request,device);rate(request,'support-route',10)
    if row['state']!='paired':raise HTTPException(409,'device unavailable')
    if await request.json()!={'consent':'latest-completed-rlog-with-location-v1'}:
      raise HTTPException(400,'explicit route consent required')
    try:return {'id':support.route_job(device,user['id'])}
    except ValueError as exc:raise HTTPException(409,str(exc)) from exc

  @app.post('/api/v1/support/{device}/delete')
  def delete(device: str,request: Request):
    user,row=owned(request,device);support.delete(device,user['id']);return {'ok':True}

  @app.get('/api/v1/admin/support')
  def admin(request: Request,q: str=''):
    if owner(request)['id']!='local-admin':raise HTTPException(403,'administrator required')
    files=support.list(query=q[:120])
    # Include owners' names only for devices with uploaded reports, not every account.
    for item in files:
      row=store.get(item['device']);item['device_name']=row['name'] if row else 'Unknown'
    return {'files':files,'retention_days':30}

  @app.get('/api/v1/support-files/{identifier}')
  def download(identifier: str,request: Request):
    user=owner(request);support.purge()
    with support.db() as db:row=db.execute('SELECT * FROM files WHERE id=? AND complete=1 AND expires>?',(identifier,time.time())).fetchone()
    if not row or (user['id']!='local-admin' and user['id']!=row['owner']):raise HTTPException(404,'file unavailable')
    return FileResponse(support.root/row['id'],filename=row['name'],media_type='application/octet-stream')

  @app.post('/api/v1/agent/support')
  async def agent(request: Request):
    rate(request,'support-agent',10000)
    try:
      envelope=await request.json();row=store.get(envelope['device_id'])
      if not row or row['state']!='paired':raise ValueError('device unavailable')
      verified=verify(envelope,row['public_key'],'support');store.consume_nonce(row['id'],verified['nonce'])
      p=verified['payload'];action=p.get('action')
      if p=={'action':'poll'}:return support.policy(row['id'],row['owner_id'])
      if action=='start':return support.start(row['id'],row['owner_id'],p)
      if action=='chunk':return support.chunk(row['id'],row['owner_id'],p)
      if action=='finish' and set(p)=={'action','job','outcome'} and isinstance(p['job'],str) and re.fullmatch('[a-f0-9-]{36}',p['job']) and p['outcome'] in ('done','no_completed_route','size_limit','upload_failed'):
        with support.db() as db:
          db.execute('BEGIN IMMEDIATE')
          if p['outcome']=='done':
            counts=db.execute('SELECT COUNT(*),COALESCE(SUM(complete),0) FROM files WHERE job=? AND device=? AND owner=?',(p['job'],row['id'],row['owner_id'])).fetchone()
            if not counts[0] or counts[0]!=counts[1]:raise ValueError('incomplete job')
          db.execute("UPDATE jobs SET state=? WHERE id=? AND device=? AND owner=? AND state='pending'",(p['outcome'],p['job'],row['id'],row['owner_id']))
        return {'ok':True}
      raise ValueError('invalid action')
    except (ValueError,KeyError,TypeError,InvalidSignature) as exc:raise HTTPException(403,'support request rejected') from exc

  task=None
  async def cleanup():
    while True:
      await asyncio.to_thread(support.purge)
      await asyncio.sleep(3600)
  @app.on_event('startup')
  async def start_cleanup():
    nonlocal task
    task=asyncio.create_task(cleanup())
  @app.on_event('shutdown')
  async def stop_cleanup():
    if task:
      task.cancel()
      try:await task
      except asyncio.CancelledError:pass
