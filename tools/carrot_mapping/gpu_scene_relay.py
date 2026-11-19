"""Single-frame read-only relay. The trusted producer supplies the age since camera capture."""

import time
from dataclasses import dataclass

from aiohttp import web


@dataclass(frozen=True)
class SceneFrame:
  seq: int
  captured: float
  jpeg: bytes
  cells: int
  raised: int
  parking: bool


class GpuSceneRelay:
  def __init__(self, clock=time.monotonic):
    self.clock = clock
    self.frame = None
    self.seq = 0

  def publish(self, jpeg, age_ms, cells, raised, parking=False):
    if not (0 <= age_ms < 900 and 0 <= raised <= cells <= 2304):
      return False
    if not (0 < len(jpeg) <= 1048576 and jpeg.startswith(b"\xff\xd8") and jpeg.endswith(b"\xff\xd9")):
      return False
    captured = self.clock() - age_ms / 1000
    if self.frame and captured <= self.frame.captured:
      return False
    self.seq += 1
    self.frame = SceneFrame(self.seq, captured, jpeg, cells, raised, parking)
    return True

  async def read(self, request):
    headers = {"Cache-Control":"no-store"}
    frame = self.frame
    age = round((self.clock() - frame.captured) * 1000) if frame else None
    if age is None or not 0 <= age < 900:
      return web.Response(status=204, headers=headers)
    if request is not None and request.query.get("after") == str(frame.seq):
      return web.Response(status=304, headers=headers)
    headers.update({"X-Scene-Parking": "1" if frame.parking else "0", "X-Scene-Frame":str(frame.seq), "X-Scene-Age-Ms":str(age),
                    "X-Scene-Cells":str(frame.cells), "X-Scene-Raised":str(frame.raised)})
    return web.Response(body=frame.jpeg, content_type="image/jpeg", headers=headers)
