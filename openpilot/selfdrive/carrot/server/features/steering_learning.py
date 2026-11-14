from aiohttp import web

from ..services.steering_learning import service


async def status(_request):
  return web.json_response(service.snapshot(), headers={'Cache-Control': 'no-store'})


async def cleanup(_app):
  service.close()


def register(app):
  app.router.add_get('/api/device/steering_learning', status)
  app.on_cleanup.append(cleanup)
