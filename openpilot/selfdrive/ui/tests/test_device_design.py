from types import SimpleNamespace
from unittest.mock import Mock

import pyray as rl
import pytest

from openpilot.selfdrive.ui import device_design as design
from openpilot.selfdrive.ui.layout_profile import device_layout
from openpilot.selfdrive.ui.lib.model_choices import ModelChoices
from openpilot.selfdrive.ui.onroad.reality_scene import EGO_ART, RealityScene, VehicleStamp


@pytest.mark.parametrize("compact,width,height", [(True, 476, 240), (False, 2100, 1020)])
def test_view_switch_tap_drag_alert_and_release(compact, width, height, monkeypatch):
  monkeypatch.setattr(design, "tile", Mock())
  state = SimpleNamespace(params=Mock(), started=True, driving_scene_view=0)
  selector = design.DrivingViewSelector(compact)
  rect = rl.Rectangle(31, 19, width, height)
  for previous in (0, 1, 2):
    target = (previous + 1) % 3
    selector.draw(rect, previous, True)
    box = selector.boxes[0 if compact else target]
    pos = rl.Vector2(box.x + box.width/2, box.y + box.height/2)
    assert rect.x < pos.x < rect.x + rect.width and rect.y < pos.y < rect.y + rect.height
    assert selector.begin(pos) and selector.finish(pos, state, True)
    state.params.put_nonblocking.assert_called_once_with("DrivingSceneView", target)
    state.params.reset_mock()
    assert state.driving_scene_view == target
    assert selector.begin(pos) and selector.finish(rl.Vector2(pos.x-35, pos.y), state, True)
    assert selector.begin(pos)
    selector.draw(rect, previous, False)
    selector.draw(rect, previous, True)
    assert selector.finish(pos, state, True)
    assert selector.begin(pos) and selector.finish(pos, state, False)
    assert not selector.finish(pos, state, True)
    state.params.put_nonblocking.assert_not_called()


@pytest.mark.parametrize("w,h", [(520, 190), (1510, 880)])
def test_display_page_reopens_saved_values_and_checks_vehicle_state_at_release(monkeypatch, w, h):
  monkeypatch.setattr(design, "caption", Mock())
  monkeypatch.setattr(design, "tile", Mock())
  values = {"IsMetric": True, "DrivingSceneView": -1, "DeviceSceneEco": False, "DeviceSceneDim": False}
  params = Mock()
  params.get.side_effect = lambda key, **kwargs: values[key]
  params.get_bool.return_value = False
  params.put_bool.side_effect = params.put.side_effect = values.__setitem__
  state = SimpleNamespace(params=params, is_offroad=Mock(return_value=True))
  page = design.DisplaySettings(state)
  page.show_event()
  page._render(rl.Rectangle(20, 30, w, h))
  assert len(page.targets) == 9
  for key, index in (("DrivingSceneView", 2), ("DeviceSceneEco", 1), ("DeviceSceneDim", 1), ("IsMetric", 0)):
    box = page.targets[key, index]
    pos = rl.Vector2(box.x + box.width/2, box.y + box.height/2)
    page._handle_mouse_press(pos)
    page._handle_mouse_release(pos)
    assert values[key] == index
  box = page.targets["DrivingSceneView", 1]
  pos = rl.Vector2(box.x+6, box.y+6)
  page._handle_mouse_press(pos)
  state.is_offroad.return_value = False
  page._handle_mouse_release(pos)
  assert values["DrivingSceneView"] == 2
  state.is_offroad.return_value = True
  params.get_bool.return_value = True
  page.activate(("IsMetric", 1))
  assert not values["IsMetric"]
  page.hide_event()
  page.show_event()
  assert page.values == values


def test_model_search_filters_real_catalog_and_both_sizes():
  choices = ModelChoices(lambda: False, None)
  original = set(choices.visible_models)
  assert {big for big, _ in original} == {False, True}
  for big, key, name in (choices.items[0], choices.items[-1]):
    choices.set_query("  " + name.upper() + " ")
    assert choices.includes(big, key)
    assert all(choices.query.casefold() in (n+" "+k).casefold() for b, k, n in choices.items if choices.includes(b, k))
  choices.set_query("no such model in the catalog")
  assert not choices.visible_models
  choices.set_query("")
  groups = []
  for _ in range(3):
    choices.next_group()
    groups.append(choices.visible_models.copy())
  assert all(groups) and set.union(*groups) == original
  assert all(not big for big, _ in groups[1]) and all(big for big, _ in groups[2])


def test_lat2v_selector_recovers_after_forced_offroad(monkeypatch, tmp_path):
  from openpilot.common import sunny_models as sunny
  from openpilot.selfdrive.ui.lib import model_choices

  monkeypatch.setenv("CARROT_BIG_MODEL_DIR", str(tmp_path))
  monkeypatch.setattr(model_choices, "tr", lambda text: text)
  flags = {"IsOffroad", "ForceOffroadActive"}
  choices = ModelChoices(lambda: True, SimpleNamespace(get_bool=flags.__contains__))
  assert choices.status(True, sunny.LAT2V) == sunny.LAT2V_PARK_MESSAGES["forced_offroad"]
  assert not choices.can_choose(sunny.LAT2V) and choices.can_choose("n16")
  choices.error, choices.park_error = (True, sunny.LAT2V), True
  flags.remove("ForceOffroadActive")
  choices.next_refresh = 0.
  assert choices.status(True, sunny.LAT2V) == "Select again" and choices.can_choose(sunny.LAT2V)
  assert sunny.key_for(True) is None


@pytest.mark.parametrize("device,w,h", [("c3x", 1600, 1000), ("c4", 476, 240)])
def test_ego_and_traffic_use_distinct_rows_and_perspectives(device, w, h):
  scene = RealityScene(device_layout(device))
  scene.vehicle_texture = SimpleNamespace(id=1)
  scene.ego_art = EGO_ART["KIA_EV6"]
  rect = rl.Rectangle(0, 0, w, h)
  faces = scene.geometry(rect, None, None, car_ok=True, rear=((-9,-6), (-9,6)))
  ego, right, left = [item for item in faces if isinstance(item, VehicleStamp)]
  assert (ego.source.x, ego.source.y) == (256, 200)
  assert {(right.source.x, right.source.y), (left.source.x, left.source.y)} == {(0, 0), (512, 0)}
  assert all(item.destination.width > 0 and item.destination.height > 0 for item in (ego, left, right))
  assert ego.destination.height / ego.destination.width == pytest.approx(200 / 256)
  lit = scene.geometry(rect, None, None, car_ok=True, lamps=(True, True, True))
  assert len(lit) == 5
  for vertices, _ in lit[1:]:
    assert all(rl.check_collision_point_rec(vertex, lit[0].destination) for vertex in vertices)
  assert not scene.geometry(rect, None, None, car_ok=False)


@pytest.mark.parametrize("eco", [False, True])
def test_scene_refresh_rate_and_immediate_source_expiry(eco, monkeypatch):
  from openpilot.selfdrive.ui.onroad import reality_scene

  class Messages(dict):
    pass

  now = [100.]
  monkeypatch.setattr(reality_scene.time, "monotonic", lambda: now[0])
  monkeypatch.setattr(rl, "draw_rectangle_gradient_v", Mock())
  sm = Messages(modelV2=object())
  sm.valid = dict(modelV2=True, carState=False, radarState=False, navInstructionCarrot=False)
  sm.recv_frame = {"modelV2": 1}
  sm.logMonoTime = {"modelV2": 100_000_000_000}
  state = SimpleNamespace(sm=sm, started_frame=1, device_scene_eco=eco)
  scene = RealityScene(device_layout("c4"))
  scene.vehicle_texture = SimpleNamespace(id=1)
  scene.geometry = Mock(return_value=[])
  rect = rl.Rectangle(0, 0, 476, 240)
  scene.draw(rect, state)
  sm.recv_frame["modelV2"] += 1
  now[0] += .055
  scene.draw(rect, state)
  assert scene.geometry.call_count == (1 if eco else 2)
  now[0] += .034
  scene.draw(rect, state)
  assert scene.geometry.call_count == 2
  sm.valid["modelV2"] = False
  scene.draw(rect, state)
  assert scene.geometry.call_count == 3 and scene.geometry.call_args.args[1] is None
