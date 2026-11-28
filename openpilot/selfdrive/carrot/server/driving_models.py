import asyncio
from threading import Event

from aiohttp import web

from openpilot.common import big_model_catalog, internal_models, sunny_models
from .services.params import HAS_PARAMS, Params, UnknownKeyName


def device_params():
  return Params() if HAS_PARAMS and Params is not None else None


def offroad(params):
  try:
    return params is not None and params.get_bool('IsOffroad') and not params.get_bool('IsOnroad') and not params.get_bool('IsEngaged')
  except OSError:
    return False


def selection_status(params):
  try:
    raw_scene = params.get('DrivingSceneView', return_default=True) if params is not None else None
  except Exception as exc:
    if UnknownKeyName is None or not isinstance(exc, UnknownKeyName):
      raise
    raw_scene = None

  def selection(boot):
    return {
      'small': sunny_models.key_for(False, boot) or (internal_models.active() if boot else internal_models.pending()),
      'large': sunny_models.key_for(True, boot) or (big_model_catalog.effective_id() if boot else big_model_catalog.preferences()['selected']),
      'primary': 'internal' if sunny_models.internal_primary(boot) else 'auto',
    }
  park_block = sunny_models.lat2v_park_block(params)
  return {'boot': selection(True), 'next': selection(False), 'offroad': offroad(params),
          'lat2v_park_block': park_block, 'lat2v_supported': sunny_models.lat2v_supported(),
          'lat2v_install': sunny_models.lat2v_install_status(park_block),
          'scene': raw_scene if raw_scene in (-1, 0, 1, 2) else None,
          'failed': [key for big in (False, True) if (key := sunny_models.failed_key(big))],
          'internal_build_failed': bool(internal_models.state().get('failed'))}


class ModelPreparation:
  def __init__(self):
    self.task = None
    self.job = {}
    self.closing = Event()

  def progress(self, phase, name, received, total):
    self.job = {**self.job, 'progress': {'phase': phase, 'file': name, 'received': received, 'total': total}}

  async def prepare(self, params, field, key):
    try:
      await asyncio.to_thread(sunny_models.choose_model, field == 'large', key,
                              lambda: not self.closing.is_set() and offroad(params), self.progress, params=params)
      self.job = {'state': 'saved', 'model': key}
    except Exception as exc:
      self.job = {'state': 'failed', 'model': key}
      if isinstance(exc, sunny_models.Lat2vParkedError):
        self.job['park_block'] = exc.reason
      elif key == sunny_models.LAT2V and isinstance(exc, ValueError):
        self.job['detail'] = str(exc)


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
    is_lat2v = field == 'large' and value == sunny_models.LAT2V
    if not offroad(params):
      if is_lat2v:
        reason = sunny_models.lat2v_park_block(params) or 'offroad'
        return web.json_response({'ok': False, 'error': sunny_models.LAT2V_PARK_MESSAGES[reason], 'park_block': reason}, status=409)
      raise ValueError('Park and turn the ignition off before changing this setting')
    if job.task is not None and not job.task.done():
      raise ValueError('Another model selection is in progress')
    if is_lat2v:
      await asyncio.to_thread(sunny_models.choose_model, True, value, lambda: offroad(params), params=params)
      job.job = {}
      return web.json_response({'ok': True, 'lat2v_install': sunny_models.lat2v_install_status(sunny_models.lat2v_park_block(params))},
                               status=202)
    if field == 'primary':
      await asyncio.to_thread(sunny_models.set_primary, value, lambda: offroad(params))
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
