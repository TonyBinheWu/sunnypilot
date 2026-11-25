import sys
import types
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.selfdrive.navigation import mapsd


@pytest.mark.parametrize('failure', ['position', 'tiles', 'slow', 'instructionConflict', 'tunnel'])
def test_map_producer_revokes_route_on_failed_frame_then_recovers(monkeypatch, failure):
  """Run the production loop with isolated IPC and valid/failed/valid renders."""
  phase = {'frame': 0, 'rendered': False}
  sent, reports = [], []
  def clock():
    if failure == 'tunnel':
      return (10., 19., 30.)[phase['frame']]
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
      self.logMonoTime = dict.fromkeys(('navInstructionCarrot', 'navRoute'), int(clock() * 1e9))
      if failure == 'instructionConflict':
        self['navInstructionCarrot'].allManeuvers = [NS(type='turn', modifier='left' if phase['frame'] == 1 else 'right', distance=22.)]

  sm = SM(navRoute=NS(carrotRouteId=42), navInstructionCarrot=NS(allManeuvers=[]))
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

  messaging = module('openpilot.cereal.messaging', SubMaster=lambda _: sm,
                     PubMaster=lambda _: NS(send=lambda _, msg: reports.append(msg.mapRenderState)),
                     new_message=lambda _, valid: NS(mapRenderState=NS(), valid=valid))
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
  def position(_):
    if phase['frame'] == 1 and failure in ('position', 'tunnel'):
      return None
    lat = (25.0001, 0., 25.0022)[phase['frame']] if failure == 'tunnel' else 25.0008
    return NS(latitude=lat, longitude=121., speed=10., time=clock(), fix_time=clock(), course=0.)

  route = (np.column_stack((np.full(80, 121.), 25. + np.arange(80) * .0001)) if failure == 'tunnel'
           else np.array([[121., 25.], [121., 25.001], [121.001, 25.001]]))
  monkeypatch.setattr(mapsd, 'ParkedPosition', lambda: NS(held=False, update=position))
  monkeypatch.setattr(mapsd, 'route_coordinates', lambda _: route)
  monkeypatch.setattr(mapsd, 'PMTiles', lambda _: NS(close=lambda: None))

  def render(*args):
    phase['rendered'] = True
    return NS(valid=not (failure == 'tiles' and phase['frame'] == 1), image=np.full((256, 256), 128, np.uint8))

  monkeypatch.setattr(mapsd, 'MapRenderer', lambda _: NS(render=render))
  monkeypatch.setattr(mapsd, 'write_preview', lambda *a, **k: None)
  monkeypatch.setattr(mapsd, 'write_navigation_view', lambda *a, **k: None)
  with pytest.raises(StopIteration):
    mapsd.main()
  assert [route_id for route_id, _ in sent] == [42, 0, 42], [r.routeMatch for r in reports]
  assert sent[0][1].any() and not sent[1][1].any() and sent[2][1].any()
  middle = {'position': 'unavailable', 'tunnel': 'unavailable', 'instructionConflict': 'instructionConflict'}.get(failure, 'matched')
  assert [r.routeMatch for r in reports] == ['matched', middle, 'matched']
  expected_start = reports[0] if middle == 'matched' else reports[2]
  assert reports[2].matchedSinceMonoTime == expected_start.locationMonoTime
