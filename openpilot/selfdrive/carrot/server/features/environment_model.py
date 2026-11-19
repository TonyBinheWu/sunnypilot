"""Optional, read-only front occupancy model. Downloads never contain camera or vehicle data."""

import asyncio
import hashlib
import os
import time
from pathlib import Path
from tempfile import NamedTemporaryFile

from aiohttp import ClientError, ClientTimeout, web

from ..services.web_settings import read_web_settings

NAME = "formosa-front-occupancy-v1.onnx"
MODEL = Path("/data/media/0/carrot/models") / NAME
URL = f"https://github.com/TonyBinheWu/sunnypilot/releases/download/formosa-front-occupancy-research-v1/{NAME}"
SIZE = 35_939_304
SHA256 = "d477bac0f82ace6c8663b222d2c0c00987906a6939f545a5fdf60ef81138b787"


def verified(path):
  if not path.is_file() or path.stat().st_size != SIZE:
    return False
  with path.open("rb") as f:
    return hashlib.file_digest(f, "sha256").hexdigest() == SHA256


async def fetch_model(session, path):
  path.parent.mkdir(parents=True, exist_ok=True)
  async with session.get(URL, timeout=ClientTimeout(total=70, sock_connect=8, sock_read=20)) as response:
    if response.status != 200 or response.content_length not in (None, SIZE):
      raise ValueError("unavailable model")
    temp = None
    try:
      with NamedTemporaryFile(dir=path.parent, delete=False) as f:
        temp = Path(f.name)
        size, digest = 0, hashlib.sha256()
        async for chunk in response.content.iter_chunked(131072):
          size += len(chunk)
          if size > SIZE:
            raise ValueError("model size")
          digest.update(chunk)
          f.write(chunk)
      if size != SIZE or digest.hexdigest() != SHA256:
        raise ValueError("model integrity")
      os.replace(temp, path)
    finally:
      if temp is not None:
        temp.unlink(missing_ok=True)


def register(app):
  lock = asyncio.Lock()
  cached_stat = None
  retry_at = 0.0

  async def serve(request):
    nonlocal cached_stat, retry_at
    if read_web_settings().get("vision_environment_occupancy") is not True:
      raise web.HTTPForbidden(headers={"Cache-Control": "no-store"})
    try:
      async with lock:
        stat = MODEL.stat() if MODEL.is_file() else None
        if stat is None or cached_stat != (stat.st_mtime_ns, stat.st_ino, stat.st_size):
          if not await asyncio.to_thread(verified, MODEL):
            if time.monotonic() < retry_at:
              raise web.HTTPServiceUnavailable(headers={"Retry-After": "15", "Cache-Control": "no-store"})
            try:
              await fetch_model(request.app["http"], MODEL)
            except (ClientError, OSError, TimeoutError, ValueError):
              retry_at = time.monotonic() + 15
              raise
          stat = MODEL.stat()
          cached_stat = (stat.st_mtime_ns, stat.st_ino, stat.st_size)
      return web.FileResponse(MODEL, headers={"Cache-Control": "private, max-age=86400"})
    except (ClientError, OSError, TimeoutError, ValueError):
      raise web.HTTPServiceUnavailable(text="occupancy model unavailable", headers={"Cache-Control": "no-store"}) from None

  app.router.add_get("/api/vision/occupancy/model", serve)
