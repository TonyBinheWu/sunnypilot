import asyncio
from contextlib import suppress
from urllib.parse import urlsplit

from aiohttp import web, WSMsgType

from openpilot.common.remote_screen import ADDRESS, MAX_FRAME


async def screen_socket(request):
  return await relay_screen(request, lambda: asyncio.open_unix_connection(ADDRESS))


async def relay_screen(request, connect):
  origin = urlsplit(request.headers.get("Origin", ""))
  if origin.scheme != request.scheme or origin.netloc != request.host:
    raise web.HTTPForbidden()
  ws = web.WebSocketResponse(max_msg_size=384, heartbeat=8, compress=False)
  await ws.prepare(request)
  writer = None
  tasks = []
  try:
    first = await asyncio.wait_for(ws.receive_json(), 15)
    pin = first.get("pin") if isinstance(first, dict) else None
    if not isinstance(pin,str) or len(pin) != 6 or not pin.isascii() or not pin.isdigit():
      raise ValueError()
    reader, writer = await connect()
    writer.write(b'{"pin":"' + pin.encode("ascii") + b'"}\n')
    await writer.drain()
    if await asyncio.wait_for(reader.readline(), 3) != b"OK\n":
      raise ValueError()
    await ws.send_str("ready")

    async def frames():
      while True:
        size = int.from_bytes(await asyncio.wait_for(reader.readexactly(4), 6),"big")
        if not 0 < size <= MAX_FRAME:
          return
        await ws.send_bytes(await asyncio.wait_for(reader.readexactly(size), 4))

    async def touches():
      async for event in ws:
        if event.type != WSMsgType.TEXT or "\n" in event.data or "\r" in event.data:
          return
        writer.write(event.data.encode() + b"\n")
        await writer.drain()

    tasks = [asyncio.create_task(frames()), asyncio.create_task(touches())]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
  except (OSError, ValueError, TypeError, TimeoutError, RuntimeError, asyncio.IncompleteReadError):
    pass
  finally:
    for task in tasks:
      task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    if writer is not None:
      writer.close()
      with suppress(OSError):
        await writer.wait_closed()
    await ws.close()
  return ws
