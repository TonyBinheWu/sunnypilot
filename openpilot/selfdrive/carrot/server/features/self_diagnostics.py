import asyncio
import json
from urllib.parse import urlsplit

from aiohttp import web

from ..services.native_diagnostics import service
from .intro.reconfigure import SetupError


async def status(_request):
  report = await asyncio.to_thread(service.snapshot)
  return web.json_response(report, headers={'Cache-Control': 'no-store'})


async def repair(request):
  origin = request.headers.get('Origin')
  if (origin and urlsplit(origin).netloc != request.host) or request.headers.get('Sec-Fetch-Site') == 'cross-site':
    return web.json_response({'ok': False, 'error': 'same_origin_required'}, status=403)
  if request.content_type != 'application/json':
    return web.json_response({'ok': False, 'error': 'invalid_action'}, status=415)
  raw = bytearray()
  async for chunk in request.content.iter_chunked(2049):
    raw.extend(chunk)
    if len(raw) > 2048:
      return web.json_response({'ok': False, 'error': 'invalid_action'}, status=413)
  try:
    body = json.loads(raw)
    if not isinstance(body, dict) or set(body) != {'ticket', 'action'} or body['action'] not in ('enable_vision', 'reboot'):
      raise ValueError('invalid_action')
    # Reuse the reviewed native P/offroad interlock, not the compact web broker.
    from .intro.routes import _check_setup_state
    from ..services.params import Params
    def apply():
      with service.lock:
        service.tickets.consume(body['ticket'], body['action'])
        service.cached = None
        p = Params()
        if service.sm is None:
          raise SetupError('vehicle_unavailable')
        service.sm.update(0)
        _check_setup_state(p, service.sm)
        if body['action'] == 'enable_vision':
          # Re-read eligibility at the write. Never change any driving tuning.
          changed = not p.get_bool('CarrotVisionEnabled')
          if changed:
            p.put_bool('CarrotVisionEnabled', True)
          if not p.get_bool('CarrotVisionEnabled'):
            raise OSError('write_failed')
          if changed:
            from ..services.param_changes import append_param_change
            append_param_change('CarrotVisionEnabled', False, True, source='web_ui', engaged=False)
          result = 'vision_enabled'
        else:
          p.put_bool('DoReboot', True)
          result = 'reboot_requested'
        service.cached = None
        return result
    result = await asyncio.to_thread(apply)
    return web.json_response({'ok': True, 'result': result}, headers={'Cache-Control': 'no-store'})
  except (ValueError, TypeError, KeyError) as exc:
    code = str(exc) if str(exc) in ('report_expired', 'invalid_action') else 'invalid_action'
    return web.json_response({'ok': False, 'error': code}, status=409)
  except SetupError as exc:
    return web.json_response({'ok': False, 'error': exc.code}, status=409)
  except Exception:
    return web.json_response({'ok': False, 'error': 'repair_unconfirmed'}, status=503)


def register(app):
  app.router.add_get('/api/device/diagnostics', status)
  app.router.add_post('/api/device/diagnostics/repair', repair)
