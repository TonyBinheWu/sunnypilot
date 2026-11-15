from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.selfdrive.ui.onroad import rainbow_path


def test_gradient_has_complete_spectrum_fade_and_reuses_current_phase():
  path = rainbow_path.RainbowPath()
  gradient = path.gradient(100)
  assert gradient.stops == [i / 7 for i in range(8)]
  assert len({(c.r, c.g, c.b) for c in gradient.colors}) >= 7
  assert gradient.colors[0].a > gradient.colors[-1].a > 0
  assert path.gradient(100.001) is gradient
  assert path.gradient(101) is not gradient


def test_rainbow_draw_reuses_geometry_and_never_draws_empty_paths(monkeypatch):
  path = rainbow_path.RainbowPath()
  calls = []
  monkeypatch.setattr(rainbow_path, 'draw_polygon', lambda rect, points, **kwargs: calls.append((rect, points, kwargs)))
  points = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], dtype=np.float32)
  path.draw(None, np.empty((0, 2)), 1)
  assert not calls
  path.draw(None, points, 1)
  assert calls[0][1] is points
  assert calls[0][2]['gradient'] is path.gradient(1)


@pytest.mark.parametrize('enabled,lateral', [(False, False), (False, True), (True, False), (True, True)])
def test_both_device_renderers_only_override_path_fill_when_enabled_and_lateral_active(monkeypatch, enabled, lateral):
  from openpilot.selfdrive.ui.onroad import model_renderer
  from openpilot.selfdrive.ui.mici.onroad import model_renderer as mici_renderer
  ui = model_renderer.ui_state
  monkeypatch.setattr(ui, 'rainbow_path', enabled)
  monkeypatch.setattr(ui, 'lat_active', lateral)
  points = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], dtype=np.float32)
  rainbow = []
  default = []
  custom = object.__new__(model_renderer.ModelRenderer)
  custom._rect = None
  custom._path = SimpleNamespace(projected_points=points)
  custom._rainbow_path = SimpleNamespace(draw=lambda *args: rainbow.append('c3x'))
  custom._refresh_carrot_params = lambda *_: None
  custom._make_path_data_carrot = lambda *_: True
  custom._render_diagnostics = SimpleNamespace(call=lambda name, fn, *args: fn(*args))
  custom._update_path_end_carrot = lambda *_: None
  custom._carrot_use_lane_line_speed_apply = 0
  custom._carrot_show_path_color = 3
  custom._carrot_show_path_mode = 0
  custom._carrot_colors = [None] * 10
  custom._draw_path_end_overlay_carrot = lambda: None
  custom._draw_tire_trajectory_carrot = lambda *_: None
  monkeypatch.setattr(model_renderer, 'draw_polygon_solid', lambda *args: default.append('c3x'))
  sm = {'carState': SimpleNamespace(useLaneLineSpeed=0, brakeLights=False), 'longitudinalPlan': SimpleNamespace(accels=[])}
  sm = type('Messages', (dict,), {'valid': {'radarState': False}})(sm)
  custom._draw_path_carrot(sm)
  assert rainbow == (['c3x'] if enabled and lateral else [])
  assert default == ([] if enabled and lateral else ['c3x'])
  assert custom._path.projected_points is points

  compact = object.__new__(mici_renderer.ModelRenderer)
  compact._rect = None
  compact._path = SimpleNamespace(projected_points=points)
  compact._rainbow_path = SimpleNamespace(draw=lambda *args: rainbow.append('c4'))
  compact._longitudinal_control = False
  compact._experimental_mode = True
  compact._exp_gradient = SimpleNamespace(colors=[])
  compact._blend_filter = None
  compact._display_clock = SimpleNamespace(update_filter=lambda *_: None)
  monkeypatch.setattr(mici_renderer, 'draw_polygon', lambda *args, **kwargs: default.append('c4'))
  compact._draw_path({'longitudinalPlan': SimpleNamespace(allowThrottle=True)})
  assert ('c4' in rainbow) == (enabled and lateral)
  assert ('c4' in default) != (enabled and lateral)
  assert compact._path.projected_points is points
