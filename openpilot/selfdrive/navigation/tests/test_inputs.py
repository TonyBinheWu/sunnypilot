import json
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.selfdrive.modeld.generic_model_runtime import host_input_layout, model_metadata
from openpilot.selfdrive.navigation.helpers import navigation_input
from openpilot.selfdrive.navigation.map_client import MapInput
from openpilot.selfdrive.navigation.source import RouteSource, coordinates


@pytest.mark.parametrize('filename,dtype,command_shape,count,states,suffix', [
  ('nav_metadata.json', np.uint8, (47,), 18452, {'state_map_q', 'state_nav_q'}, '56320'),
  ('nav_rl_metadata.json', np.float32, (1, 47), 18580,
   {'state_map_features_q', 'state_navigation_features_q'}, '80eedcdd-f97b-46d0-9b94-780685292acf/12864'),
])
def test_real_nav_artifact_mixed_width_inputs_and_feedback(filename, dtype, command_shape, count, states, suffix):
  from openpilot.selfdrive.modeld.parse_model_outputs import Parser
  artifact = json.loads((Path(__file__).parents[2] / 'modeld/tests/fixtures' / filename).read_text())
  checkpoint, slices, pairs, output_count = model_metadata(artifact)
  assert checkpoint.endswith(suffix)
  assert output_count == count
  assert states <= pairs.keys()
  raw = np.zeros((1, count), np.float32)
  parsed = Parser().parse_outputs({name: raw[:, section].copy() for name, section in slices.items()})
  assert parsed['plan'].shape == (1, 33, 15) and np.isfinite(parsed['action']).all()
  packed, views, offset = host_input_layout(artifact['input_specs'], 1234, pairs)
  assert views['nav_map'].shape == (1, 1, 256, 256)
  assert views['nav_map'].dtype == dtype
  assert views['navigation'].shape == command_shape
  assert views['navigation'].dtype == np.float32
  views['nav_map'][:] = 255
  views['navigation'].flat[-1] = 1.25
  assert np.all(views['nav_map'] == 255) and views['navigation'].flat[-1] == 1.25
  assert np.all(views['img'] == 0) and packed.size == offset + 2468
  for name, view in views.items():
    if name not in ('tfm', 'big_tfm', 'img', 'big_img'):
      assert (view.ctypes.data - packed.ctypes.data) % 128 == 0


@pytest.mark.parametrize('dtype,shape', [('float16', [1, 47]), ('float32', [47]), ('uint8', [1, 47])])
def test_unrecognized_nav_layout_is_rejected(dtype, shape):
  artifact = json.loads((Path(__file__).parents[2] / 'modeld/tests/fixtures/nav_rl_metadata.json').read_text())
  artifact['input_specs']['nav_map'][1] = dtype
  artifact['input_specs']['navigation'][0] = shape
  with pytest.raises(ValueError, match='navigation input contract'):
    model_metadata(artifact)


def test_unknown_tbt_does_not_become_straight_and_distance_is_finite():
  maneuvers = [NS(type='invalid', modifier='', distance=50), NS(type='turn', modifier='left', distance=120)]
  result = navigation_input(maneuvers, 20)
  assert result[15] == 1 and result[-1] == 1.
  for distance in (float('nan'), float('inf'), -1):
    assert not navigation_input([NS(type='turn', modifier='right', distance=distance)], 0).any()


def test_source_priority_no_route_mixing_and_disconnect_resumes_saved_mapbox():
  source = RouteSource()
  source.mapbox = ((37., 127.), (37.1, 127.1))
  source.legacy = ((38., 128.), (38.1, 128.1))
  assert source.select(False)[0]['latitude'] == 37.
  assert source.select(True)[0]['latitude'] == 38.
  assert source.select(True) is None
  v2 = NS(route=NS(present=False, polyline=()), off_route=False)
  assert source.select(True, v2) == []
  assert source.select(False)[0]['latitude'] == 37.
  assert source.legacy == ()
  assert source.select(True) == []  # reconnect cannot revive an old route


@pytest.mark.parametrize('lat,lon', [(float('nan'), 0), (0, float('inf')), (90, 0), (0, 181)])
def test_reject_bad_route_coordinates(lat, lon):
  assert not coordinates([{'latitude': lat, 'longitude': lon}])


def nav_streams():
  class SM(dict):
    pass
  sm = SM(navInstructionCarrot=NS(allManeuvers=[NS(type='turn', modifier='right', distance=100)]),
          navRoute=NS(carrotRouteId=123, coordinates=[0, 1]),
          mapRenderState=NS(routeMatch='matched', carrotRouteId=123, locationMonoTime=9_800_000_000,
                            matchedSinceMonoTime=9_700_000_000, approachManeuver=''))
  sm.valid = dict.fromkeys(sm, True)
  sm.logMonoTime = dict.fromkeys(sm, 9_900_000_000)
  return sm


@pytest.mark.parametrize('issue', ['offRoute', 'ambiguous', 'headingConflict', 'instructionConflict', 'unavailable',
                                   'old_fix', 'future_fix', 'stale_route', 'old_report', 'future_report', 'replaced', 'new_turn'])
def test_route_authority_expires_and_cannot_transfer_to_another_step_or_route(monkeypatch, issue):
  from openpilot.selfdrive.navigation import map_client
  monkeypatch.setattr(map_client.time, 'monotonic', lambda: 10.)
  client = MapInput()
  client.client = NS(is_connected=lambda: True, recv=lambda _: None)
  sm = nav_streams()
  model = NS(views={'nav_map': None})
  client.image, client.image_time, client.route_time = np.ones((256, 256)), 9.9, 123
  client.image_time_ns = 9_900_000_000
  assert set(client.update(model, sm, 10.)) == {'navigation', 'nav_map'}
  report = sm['mapRenderState']
  if issue in ('old_fix', 'future_fix'):
    report.locationMonoTime = 8_000_000_000 if issue == 'old_fix' else 10_000_000_001
  elif issue == 'stale_route':
    sm.logMonoTime['navRoute'] = 5_000_000_000
  elif issue in ('old_report', 'future_report'):
    sm.logMonoTime['mapRenderState'] = 8_500_000_000 if issue == 'old_report' else 10_000_000_001
  elif issue == 'replaced':
    report.carrotRouteId = sm['navRoute'].carrotRouteId = 9_950_000_000
  elif issue == 'new_turn':
    sm['navInstructionCarrot'].allManeuvers[0].distance = 20.
  else:
    report.routeMatch = issue
  assert client.update(model, sm, 10.) == {}


def test_verified_instruction_without_tiles_and_legacy_tbt_only(monkeypatch):
  from openpilot.selfdrive.navigation import map_client
  monkeypatch.setattr(map_client.time, 'monotonic', lambda: 10.)
  client = MapInput()
  client.client = NS(is_connected=lambda: True, recv=lambda _: None)
  sm, model = nav_streams(), NS(views={'nav_map': None})
  assert set(client.update(model, sm, 10.)) == {'navigation'}
  sm['navRoute'].coordinates = []
  sm.valid['mapRenderState'] = False
  command = client.update(model, sm, 10.)['navigation']
  assert command[10] and command[-1] == pytest.approx(.99)
  sm.logMonoTime['navInstructionCarrot'] = 8_000_000_000
  assert client.update(model, sm, 10.) == {}


def test_logged_route_report_round_trips_into_the_model_input_gate():
  from openpilot.cereal import log, messaging
  from openpilot.selfdrive.navigation.helpers import nearby_maneuver
  sm = nav_streams()
  sm['navInstructionCarrot'].allManeuvers[0].distance = 20.
  msg = messaging.new_message('mapRenderState', valid=True)
  msg.mapRenderState.carrotRouteId = 123
  msg.mapRenderState.routeMatch = 'matched'
  msg.mapRenderState.approachManeuver = 'turn right'
  msg.mapRenderState.matchedSinceMonoTime = 9_700_000_000
  msg.mapRenderState.locationMonoTime = 9_800_000_000
  with log.Event.from_bytes(msg.to_bytes()) as event:
    sm['mapRenderState'] = event.mapRenderState
    assert nearby_maneuver(sm, 10_000_000_000, 10.) == 'turn right'
    assert event.mapRenderState.matchedSinceMonoTime == 9_700_000_000


def test_map_input_rejects_stale_image_wrong_route_and_invalid_tbt(monkeypatch):
  from openpilot.selfdrive.navigation import map_client
  monkeypatch.setattr(map_client.time, 'monotonic', lambda: 10.)
  client = MapInput()
  client.client = NS(is_connected=lambda: True, recv=lambda _: None)
  client.image, client.image_time, client.route_time = np.ones((256, 256), np.uint8), 9.8, 123
  sm = nav_streams()
  client.image_time_ns = 9_800_000_000
  model = NS(views={'nav_map': None})
  assert 'nav_map' in client.update(model, sm, 10)
  sm['mapRenderState'].matchedSinceMonoTime = 9_850_000_000
  assert set(client.update(model, sm, 10)) == {'navigation'}  # still-fresh bitmap from before reacquisition
  client.image_time, client.image_time_ns = 9.9, 9_900_000_000
  assert 'nav_map' in client.update(model, sm, 10)
  client.route_time = 122
  assert 'nav_map' not in client.update(model, sm, 10)
  client.route_time, client.image_time = 123, 9.5
  assert 'nav_map' not in client.update(model, sm, 10)
  sm.valid['navInstructionCarrot'] = False
  assert client.update(model, sm, 10) == {}
  assert client.update(NS(views={}), sm, 10) == {}


@pytest.mark.parametrize('pixels,route_id,admitted', [(0, 123, False), (128, 0, False), (128, 123, True)])
def test_received_invalid_map_revokes_cached_valid_map(monkeypatch, pixels, route_id, admitted):
  from openpilot.selfdrive.navigation import map_client
  monkeypatch.setattr(map_client.time, 'monotonic', lambda: 10.)
  client = MapInput()
  frame = NS(width=256, height=256, data=np.full(65536, pixels, np.uint8).tobytes())
  client.client = NS(is_connected=lambda: True, recv=lambda _: frame,
                     timestamp_eof=9_900_000_000, timestamp_sof=route_id)
  client.image, client.image_time, client.route_time = np.ones((256, 256), np.uint8), 9.8, 123
  sm = nav_streams()
  metadata = []
  result = client.update(NS(views={'nav_map': None}, set_nav_metadata=metadata.append), sm, 10)
  assert ('nav_map' in result) == admitted
  assert metadata[0] is None
  if not admitted:
    assert len(metadata) == 1  # Never revive the previous valid map provenance.
