"""Nonblocking model map input. Unsupported driving models do no map work."""
import time

import numpy as np

from openpilot.selfdrive.navigation.helpers import VALHALLA_SIDED_TYPES, navigation_input
from openpilot.selfdrive.navigation.map_geometry import FORWARD_VIEW_METERS


RAMP_AND_FORK_COMMANDS = frozenset(command for kind in ('on ramp', 'off ramp', 'fork') for command in VALHALLA_SIDED_TYPES[kind])


def distant_branch(navigation):
  return navigation[-1] > np.float32(FORWARD_VIEW_METERS / 100) and any(navigation[i] for i in RAMP_AND_FORK_COMMANDS)


class MapInput:
  def __init__(self):
    self.client = None
    self.retry_at = 0.
    self.image = None
    self.image_time = 0.
    self.image_time_ns = 0
    self.route_time = 0

  def update(self, model, sm, speed):
    if 'nav_map' not in getattr(model, 'views', {}):
      self.image = None
      return {}
    note_map = getattr(model, "set_nav_metadata", None)
    if note_map is not None:
      note_map(None)
    now = time.monotonic()
    if self.client is None:
      from msgq.visionipc import VisionIpcClient, VisionStreamType
      self.client = VisionIpcClient('mapsd', VisionStreamType.VISION_STREAM_MAP, True)
    if not self.client.is_connected() and now >= self.retry_at:
      self.client.connect(False)
      self.retry_at = now + 1.
    if self.client.is_connected():
      buf = self.client.recv(0)
      if buf is not None:
        self.image = None
        if (buf.width, buf.height) == (256, 256) and len(buf.data) >= 65536:
          image = np.frombuffer(buf.data, np.uint8, count=65536).reshape(256, 256)
          # Older mapsd versions stamp invalid black frames with a live route ID.
          # Also reject that sentinel during a rolling producer/consumer update.
          # A rendered map always contains at least the ego/route strokes.
          self.image = image.copy() if image.any() else None
          self.image_time_ns = int(self.client.timestamp_eof)
          self.image_time = self.image_time_ns * 1e-9
          self.route_time = self.client.timestamp_sof
    result = {}
    if sm.valid['navInstructionCarrot'] and 0 <= now - sm.recv_time['navInstructionCarrot'] < 2:
      command = navigation_input(sm['navInstructionCarrot'].allManeuvers,
                                 max(0., speed) * (now - sm.recv_time['navInstructionCarrot']))
      # A road-level route cannot identify the current lane. Keep remote ramp/fork
      # preparation on the display until the branch can enter the model raster.
      if distant_branch(command):
        return {}
      result['navigation'] = command
      if (self.image is not None and 0 <= now - self.image_time < .5
          and self.route_time != 0 and self.route_time == sm['navRoute'].carrotRouteId and sm.valid['navRoute']):
        result['nav_map'] = self.image
        if note_map is not None:
          note_map((int(self.route_time), self.image_time_ns,
                    min(self.image_time_ns + 500_000_000, int((sm.recv_time['navInstructionCarrot'] + 2.) * 1e9))))
    return result
