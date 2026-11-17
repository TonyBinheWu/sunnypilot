"""Explicit Carrot-web consent for the existing FormosaLink driving-data uploader."""
import asyncio
import json
import time
from pathlib import Path

from aiohttp import web

from openpilot.sunnypilot.formosalink.identity import default_directory, read
from openpilot.sunnypilot.formosalink.training_protocol import NOTICE, POLICY
from openpilot.sunnypilot.formosalink.training_upload import choose, consent_revision, local_state


def directory(app):
  return Path(app.get('training_data_directory') or default_directory())


def parked(app):
  try:
    return app['params'].get_bool('IsOffroad') is True
  except (KeyError,AttributeError,ValueError):
    return False


def snapshot(app):
  root=directory(app)
  state=local_state(root)
  configured=False
  origin=None
  try:
    identity,_,_=read(root)
    configured=True
    origin=identity['origin']
  except (OSError,ValueError,KeyError,TypeError):
    pass
  try:
    completed=json.loads((root/'training-uploads.json').read_text())
    count=len(completed) if isinstance(completed,dict) else 0
  except (OSError,ValueError):
    count=0
  pending=state.get('pending')
  try:
    progress=json.loads((root/'training-upload-status.json').read_text())
    progress={key:value for key,value in progress.items() if key in ('state','updated','filename','bytes','total','counts','error_type','http_status')}
    progress['fresh']=0<=time.time()-progress.get('updated',0)<100
  except (OSError,ValueError,TypeError,AttributeError):
    progress={'state':'unknown','fresh':False}
  return {'ok':True,'policy':POLICY,'notice':NOTICE,'configured':configured,'receiver':origin,
    'offroad':parked(app),'can_enable':configured and parked(app),'enabled':state.get('enabled') is True,
    'pending_enabled':pending.get('enabled') if isinstance(pending,dict) else None,
    'revision':consent_revision(state),'uploaded_segments':count,'upload':progress}


async def status(request):
  return web.json_response(await asyncio.to_thread(snapshot,request.app),headers={'Cache-Control':'no-store'})


async def change(request):
  if request.headers.get('Origin')!=f'{request.scheme}://{request.host}' or request.headers.get('Sec-Fetch-Site')=='cross-site':
    raise web.HTTPForbidden(text='Same-origin requests only')
  if request.content_type!='application/json':
    raise web.HTTPUnsupportedMediaType(text='JSON required')
  raw=await request.content.read(4097)
  if len(raw)>4096:
    raise web.HTTPRequestEntityTooLarge(max_size=4096,actual_size=len(raw))
  try:
    body=json.loads(raw)
    if not isinstance(body,dict) or set(body)!={'policy','enabled','revision'} or type(body['enabled']) is not bool:
      raise ValueError('invalid_consent')
    if body['policy']!=POLICY:
      raise ValueError('policy_changed')
    current=await asyncio.to_thread(snapshot,request.app)
    if body['enabled'] and not current['offroad']:
      return web.json_response({'ok':False,'error':'offroad_required'},status=409)
    if body['enabled'] and not current['configured']:
      return web.json_response({'ok':False,'error':'pairing_required'},status=409)
    await asyncio.to_thread(choose,body['enabled'],directory(request.app),expected_revision=body['revision'])
    return web.json_response(await asyncio.to_thread(snapshot,request.app),headers={'Cache-Control':'no-store'})
  except (ValueError,KeyError,TypeError) as exc:
    return web.json_response({'ok':False,'error':str(exc)},status=409)


def register(app):
  app.router.add_get('/api/device/training_data',status)
  app.router.add_post('/api/device/training_data',change)
