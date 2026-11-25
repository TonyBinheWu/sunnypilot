import ast
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


UI_DIR = Path(__file__).parents[1]
MAIN_LAYOUT_PATH = UI_DIR / "layouts" / "main.py"
ROAD_VIEW_PATH = UI_DIR / "onroad" / "augmented_road_view.py"
MICI_MAIN_LAYOUT_PATH = UI_DIR / "mici" / "layouts" / "main.py"
MICI_ROAD_VIEW_PATH = UI_DIR / "mici" / "onroad" / "augmented_road_view.py"
UI_STATE_PATH = UI_DIR / "ui_state.py"


def _method(path: Path, class_name: str, method_name: str) -> ast.FunctionDef:
  tree = ast.parse(path.read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
  return next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == method_name)


def _calls(node: ast.AST, attr: str) -> bool:
  return any(
    isinstance(child, ast.Call)
    and isinstance(child.func, ast.Attribute)
    and (child.func.attr == attr or
         (child.func.attr == "call" and len(child.args) >= 2 and isinstance(child.args[1], ast.Attribute)
          and child.args[1].attr == attr))
    for child in ast.walk(node)
  )


def _call(node: ast.AST, attr: str) -> ast.Call:
  return next(
    child for child in ast.walk(node)
    if isinstance(child, ast.Call)
    and isinstance(child.func, ast.Attribute)
    and child.func.attr == attr
  )


def _is_attr(node: ast.expr, owner: str, attr: str) -> bool:
  return (
    isinstance(node, ast.Attribute)
    and isinstance(node.value, ast.Name)
    and node.value.id == owner
    and node.attr == attr
  )


def _assert_main_layout_forwards_camera_preference(path: Path, class_name: str, method_name: str) -> None:
  render = _method(path, class_name, method_name)
  connected_guards = [
    node for node in ast.walk(render)
    if isinstance(node, ast.If)
    and isinstance(node.test, ast.Attribute)
    and isinstance(node.test.value, ast.Name)
    and node.test.value.id == "ui_state"
    and node.test.attr == "started"
  ]
  assert connected_guards
  guard = connected_guards[0]
  assert _calls(guard, "get_bool")
  setter = _call(guard, "set_cluster_hud_connected")
  assert len(setter.args) == 2
  assert _is_attr(setter.args[1], "ui_state", "show_camera_with_cluster")


def test_main_layouts_forward_external_hud_connection_and_camera_preference():
  _assert_main_layout_forwards_camera_preference(MAIN_LAYOUT_PATH, "MainLayout", "_render")
  _assert_main_layout_forwards_camera_preference(MICI_MAIN_LAYOUT_PATH, "MiciMainLayout", "_handle_transitions")


def test_ui_state_caches_camera_preference_as_exact_enabled_value():
  update_params = _method(UI_STATE_PATH, "UIState", "update_params")
  assignment = next(
    node for node in ast.walk(update_params)
    if isinstance(node, ast.Assign)
    and any(_is_attr(target, "self", "show_camera_with_cluster") for target in node.targets)
  )
  assert isinstance(assignment.value, ast.Compare)
  assert isinstance(assignment.value.left, ast.Call)
  assert isinstance(assignment.value.left.func, ast.Attribute)
  assert assignment.value.left.func.attr == "get_int"
  assert assignment.value.left.args[0].value == "ShowCameraWithCluster"
  assert isinstance(assignment.value.ops[0], ast.Eq)
  assert assignment.value.comparators[0].value == 1


def test_camera_preference_only_bypasses_connected_render_suppression():
  for path in (ROAD_VIEW_PATH, MICI_ROAD_VIEW_PATH):
    setter = _method(path, "AugmentedRoadView", "set_cluster_hud_connected")
    assignment = next(
      node for node in setter.body
      if isinstance(node, ast.Assign)
      and any(_is_attr(target, "self", "_suppress_camera_for_cluster") for target in node.targets)
    )
    assert isinstance(assignment.value, ast.BoolOp)
    assert isinstance(assignment.value.op, ast.And)
    assert isinstance(assignment.value.values[0], ast.Name)
    assert assignment.value.values[0].id == "connected"
    assert isinstance(assignment.value.values[1], ast.UnaryOp)
    assert isinstance(assignment.value.values[1].op, ast.Not)
    assert isinstance(assignment.value.values[1].operand, ast.Name)
    assert assignment.value.values[1].operand.id == "show_camera"


@pytest.mark.parametrize("view", [-1, 0, 1, 2])
@pytest.mark.parametrize("suppressed", [True, False])
@pytest.mark.parametrize("alert", [None, "takeover"])
def test_c3x_renders_sources_and_preserves_alert_and_cluster_priority(view, suppressed, alert):
  class Camera:
    def _render(self, rect):
      self.camera(rect)

  method = _method(ROAD_VIEW_PATH, "AugmentedRoadView", "_render")
  tree = ast.parse("class AugmentedRoadView(Camera): pass")
  tree.body[0].body = [method]
  state = SimpleNamespace(started=True, driving_scene_view=view, device_scene_dim=False, sm={})
  rl = Mock()
  rl.Rectangle.side_effect = lambda x, y, width, height: SimpleNamespace(x=x, y=y, width=width, height=height)
  ns = dict(Camera=Camera, ui_state=state, UI_BORDER_SIZE=30, gui_app=Mock(), time=time, messaging=Mock(), rl=rl)
  exec(compile(tree, str(ROAD_VIEW_PATH), "exec"), ns)
  screen = ns["AugmentedRoadView"]()
  for key in ("camera", "_refresh_plot_mode", "_switch_stream_if_needed", "_update_calibration", "_overlay_state", "client",
              "model_renderer", "_hud_renderer", "_selector", "alert_renderer", "driver_state_renderer", "_pm",
              "_render_diagnostics", "_draw_border_carrot"):
    setattr(screen, key, Mock())
  screen._suppress_camera_for_cluster = suppressed
  screen.stream_type = screen._plot_mode = 0
  screen._reality = Mock(style={"scene_style": 1})
  screen.alert_renderer.get_alert.return_value = alert
  screen._render_diagnostics.call.side_effect = lambda label, callback, *args: callback(*args)
  screen._render(rl.Rectangle(0, 0, 2160, 1080))
  assert screen.camera.called == (view == 1 and not suppressed)
  assert screen._switch_stream_if_needed.called == screen._update_calibration.called == (not suppressed)
  assert screen._reality.draw.called == (view != 1 and not suppressed)
  screen.model_renderer.render.assert_not_called()
  assert screen._selector.draw.call_args.args[-1] == (not suppressed and alert is None)
  screen._hud_renderer.render.assert_called_once()
  screen.alert_renderer.render.assert_called_once()
  screen.driver_state_renderer.draw_onroad.assert_called_once_with(screen._content_rect, alert is not None)
