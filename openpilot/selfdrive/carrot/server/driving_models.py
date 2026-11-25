import asyncio
from pathlib import Path
from threading import Event

from aiohttp import web

from openpilot.common import big_model_catalog, internal_models, sunny_models
from openpilot.selfdrive.modeld import vla_status
from .services.params import HAS_PARAMS, Params, UnknownKeyName


def device_params():
  return Params() if HAS_PARAMS and Params is not None else None


def is_c4():
  if not Path('/TICI').is_file():
    return False
  from openpilot.system.hardware import HARDWARE
  return HARDWARE.get_device_type() == 'mici'


def offroad(params):
  try:
    return params is not None and params.get_bool('IsOffroad') and not params.get_bool('IsOnroad') and not params.get_bool('IsEngaged')
  except OSError:
    return False


def selection_status(params):
  observer = None
  try:
    raw_scene = params.get('DrivingSceneView', return_default=True) if params is not None else None
  except Exception as exc:
    if UnknownKeyName is None or not isinstance(exc, UnknownKeyName):
      raise
    raw_scene = None
  if params is not None and is_c4():
    try:
      observer = {'enabled': params.get_bool('C4VlaObserve'), **vla_status.read_status()}
    except Exception as exc:
      if UnknownKeyName is None or not isinstance(exc, UnknownKeyName):
        raise

  def selection(boot):
    return {
      'small': sunny_models.key_for(False, boot) or (internal_models.active() if boot else internal_models.pending()),
      'large': sunny_models.key_for(True, boot) or (big_model_catalog.effective_id() if boot else big_model_catalog.preferences()['selected']),
      'primary': 'internal' if sunny_models.internal_primary(boot) else 'auto',
    }
  return {'boot': selection(True), 'next': selection(False), 'offroad': offroad(params),
          'vla_observer': observer,
          'scene': raw_scene if raw_scene in (-1, 0, 1, 2) else None,
          'failed': [key for big in (False, True) if (key := sunny_models.failed_key(big))],
          'internal_build_failed': bool(internal_models.state().get('failed'))}


class ModelPreparation:
  def __init__(self):
    self.task = None
    self.job = {}
    self.closing = Event()

  async def prepare(self, params, field, key):
    try:
      await asyncio.to_thread(sunny_models.choose_model, field == 'large', key,
                              lambda: not self.closing.is_set() and offroad(params))
      self.job = {'state': 'saved', 'model': key}
    except Exception:
      self.job = {'state': 'failed', 'model': key}

  async def prepare_vla(self, params):
    def parked():
      return not self.closing.is_set() and vla_status.parked(params)
    try:
      await asyncio.to_thread(vla_status.prepare_weights, parked)
      if not parked():
        raise ValueError('Offroad preparation interrupted')
      params.put_bool('C4VlaObserve', True)
      self.job = {'state': 'saved', 'model': 'PhysicalAI-reason-VLA 4B'}
    except Exception:
      self.job = {'state': 'failed', 'model': 'PhysicalAI-reason-VLA 4B'}


PREPARATION = web.AppKey('driving_model_preparation', ModelPreparation)


async def catalog(_request):
  rows = [{'id': key, 'name': name, 'size': 'large' if big else 'small',
           'source': 'sunnypilot' if key in sunny_models.catalog() else 'carrot-wip'}
          for big, key, name in sunny_models.model_items()]
  return web.json_response({'models': rows})


async def change(request):
  if request.content_type != 'application/json' or request.headers.get('Sec-Fetch-Site') == 'cross-site':
    raise web.HTTPForbidden()
  job = request.app[PREPARATION]
  params = device_params()
  try:
    body = await request.json()
    if not isinstance(body, dict) or set(body) != {'field', 'value'}:
      raise ValueError('Invalid selection')
    field, value = body['field'], body['value']
    if not offroad(params):
      raise ValueError('Park and turn the ignition off before changing this setting')
    if job.task is not None and not job.task.done():
      raise ValueError('Another model selection is in progress')
    if field == 'primary':
      await asyncio.to_thread(sunny_models.set_primary, value, lambda: offroad(params))
    elif field == 'vla_observer' and is_c4() and value in ('on', 'off'):
      if not vla_status.parked(params):
        raise ValueError('Turn the ignition off and leave forced offroad mode')
      if value == 'on':
        job.job = {'state': 'preparing', 'model': 'PhysicalAI-reason-VLA 4B'}
        job.task = asyncio.create_task(job.prepare_vla(params))
        return web.json_response({'ok': True, 'job': job.job}, status=202)
      params.put_bool('C4VlaObserve', False)
    elif field == 'scene':
      if type(value) is not int or value not in (-1, 0, 1, 2):
        raise ValueError('Unknown driving view')
      await asyncio.to_thread(params.put, 'DrivingSceneView', value)
    elif field in ('small', 'large') and isinstance(value, str) and any(
        big == (field == 'large') and key == value for big, key, _ in sunny_models.model_items()):
      job.job = {'state': 'preparing', 'model': value}
      job.task = asyncio.create_task(job.prepare(params, field, value))
      return web.json_response({'ok': True, 'job': job.job}, status=202)
    else:
      raise ValueError('Unknown model selection')
    return web.json_response({'ok': True})
  except (ValueError, OSError, TypeError) as exc:
    return web.json_response({'ok': False, 'error': str(exc)}, status=409)


def register(app):
  app[PREPARATION] = ModelPreparation()
  async def lifecycle(app):
    yield
    job = app[PREPARATION]
    job.closing.set()
    if job.task is not None:
      await job.task
  app.cleanup_ctx.append(lifecycle)
  app.router.add_get('/api/driving-models/catalog', catalog)
  app.router.add_post('/api/driving-models/selection', change)
