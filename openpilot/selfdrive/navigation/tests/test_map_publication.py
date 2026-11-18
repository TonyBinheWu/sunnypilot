import sys
import types
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.selfdrive.navigation import mapsd


@pytest.mark.parametrize('failure', ['position', 'tiles', 'slow'])
def test_map_producer_revokes_route_on_failed_frame_then_recovers(monkeypatch, failure):
  """Run the production loop with isolated IPC and valid/failed/valid renders."""
  phase = {'frame': 0, 'rendered': False}
  sent = []
  def clock():
    return 10. + phase['frame'] * 2 + (.6 if failure == 'slow' and phase['frame'] == 1 and phase['rendered'] else 0.)
  monkeypatch.setattr(mapsd.time, 'monotonic', clock)
  for name in ('sched_setscheduler', 'sched_setaffinity', 'nice'):
    monkeypatch.setattr(mapsd.os, name, lambda *args: None, raising=False)
  monkeypatch.setattr(mapsd.os, 'sched_getaffinity', lambda _: {0}, raising=False)
  monkeypatch.setattr(mapsd.os, 'SCHED_OTHER', 0, raising=False)
  monkeypatch.setattr(mapsd.os, 'sched_param', lambda _: None, raising=False)
  monkeypatch.delenv('MAPBOX_TOKEN', raising=False)

  class SM(dict):
    def update(self, _):
      self.updated = {'navRoute': phase['frame'] == 0}
      self.recv_time = {'navInstructionCarrot': clock()}

  sm = SM(navRoute=NS(carrotRouteId=42), navInstructionCarrot=NS())
  sm.valid = {'navRoute': True, 'navInstructionCarrot': True}
  sm.update(0)

  class Server:
    def __init__(self, name):
      assert name == 'mapsd'

    def create_buffers_with_sizes(self, *args):
      pass

    def start_listener(self):
      pass

    def send(self, stream, data, frame, route_id, timestamp):
      sent.append((route_id, np.frombuffer(data, np.uint8).copy()))

  class Ratekeeper:
    def __init__(self, *args, **kwargs):
      self.frame = 0

    def keep_time(self):
      self.frame += 1
      phase.update(frame=self.frame, rendered=False)
      if self.frame == 3:
        raise StopIteration

  def module(name, **attrs):
    value = types.ModuleType(name)
    value.__dict__.update(attrs)
    monkeypatch.setitem(sys.modules, name, value)
    return value

  messaging = module('openpilot.cereal.messaging', SubMaster=lambda _: sm)
  module('openpilot.cereal', messaging=messaging)
  import openpilot
  monkeypatch.setattr(openpilot, 'cereal', sys.modules['openpilot.cereal'], raising=False)
  visionipc = module('msgq.visionipc', VisionIpcServer=Server, VisionStreamType=NS(VISION_STREAM_MAP=0))
  module('msgq', visionipc=visionipc)
  module('openpilot.common.params', Params=lambda: NS(get_bool=lambda _: True, get_int=lambda _: 0, get=lambda _: ''))
  module('openpilot.common.realtime', Ratekeeper=Ratekeeper)
  module('openpilot.common.runtime_diagnostics', RuntimeDiagnostics=lambda *a, **k: NS(record=lambda **kw: None))
  module('openpilot.common.swaglog', cloudlog=NS(event=lambda *a, **k: None, warning=lambda *a: None))
  module('openpilot.selfdrive.navigation.tiles', RemoteTiles=lambda: NS())
  module('openpilot.selfdrive.navigation.mapbox_tiles', MapboxTiles=lambda _: NS(close=lambda: None))
  monkeypatch.setattr(mapsd, 'ParkedPosition', lambda: NS(
    held=False, update=lambda _: None if failure == 'position' and phase['frame'] == 1 else NS(
      latitude=25., longitude=121., speed=0., time=clock())))
  monkeypatch.setattr(mapsd, 'route_coordinates', lambda _: np.array([[121., 25.], [121., 25.001]]))
  monkeypatch.setattr(mapsd, 'RouteTracker', lambda _: NS(update_pose=lambda *a: (121., 25., 0.)))
  monkeypatch.setattr(mapsd, 'PMTiles', lambda _: NS(close=lambda: None))

  def render(*args):
    phase['rendered'] = True
    return NS(valid=not (failure == 'tiles' and phase['frame'] == 1), image=np.full((256, 256), 128, np.uint8))

  monkeypatch.setattr(mapsd, 'MapRenderer', lambda _: NS(render=render))
  monkeypatch.setattr(mapsd, 'write_preview', lambda *a, **k: None)
  monkeypatch.setattr(mapsd, 'write_navigation_view', lambda *a, **k: None)
  with pytest.raises(StopIteration):
    mapsd.main()
  assert [route_id for route_id, _ in sent] == [42, 0, 42]
  assert sent[0][1].any() and not sent[1][1].any() and sent[2][1].any()
