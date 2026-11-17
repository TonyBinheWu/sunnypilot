"""Exercise the real compact panel without a display server or native IPC."""
import ast
import html
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace as NS

import pytest

from openpilot.common.steering_learning import section


def panel_scope():
  path = Path(__file__).parents[1] / 'widgets' / 'steering_learning.py'
  tree = ast.parse(path.read_text())
  names = {'TITLE', 'SOURCE', 'STATUS', 'value', 'learning_html', 'learning_mici_dialog'}
  tree.body = [node for node in tree.body if getattr(node, 'name', None) in names or
               isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets)]
  scope = {'html': html, 'tr': lambda text: text}
  exec(compile(tree, str(path), 'exec'), scope)
  return scope


def test_native_missing_progress_and_stale_source_are_unambiguous():
  scope = panel_scope()
  snapshot = {'delay': section('liveDelay'), 'torque': section('liveTorqueParameters')}
  text = scope['learning_html'](snapshot)
  assert '0%' not in text and '—%' not in text
  snapshot['delay'] = section('liveDelay', {'calPerc': 80, 'status': 'unestimated'}, source='stale')
  text = scope['learning_html'](snapshot)
  assert '80%' in text and 'Data expired (last received)' in text


def test_native_passive_observations_show_commands_rates_and_restrictions():
  snapshot = {'delay': section('liveDelay'), 'torque': section('liveTorqueParameters'),
              'lowSpeed': {'source': 'cached', 'enabled': False,
                           'current': {'reason': 'driver', 'requested': 400, 'command': 100, 'angle': 20,
                                       'targetAngle': 30, 'angleRate': 10, 'base': 270, 'ceiling': 409, 'up': 2, 'down': 3},
                           'stats': {'samples': 50, 'left': dict(command=200, angle=30, angleRate=10),
                                     'right': dict(command=100, angle=20, angleRate=5)}}}
  text = panel_scope()['learning_html'](snapshot)
  assert 'Driver takeover' in text and '2.0 / 3.0' in text and '400.0 / 100.0' in text
  assert 'not hardware limits' in text and 'not live' in text


@pytest.mark.parametrize('width,height', [(536, 240), (536, 220)])
def test_c4_panel_scrolls_and_clips_within_its_small_canvas(monkeypatch, width, height):
  calls = []
  class Rectangle:
    def __init__(self, x, y, w, h):
      self.x, self.y, self.width, self.height = x, y, w, h
  class Scroll:
    def update(self, viewport, content_height):
      calls.append(('scroll', viewport, content_height))
      return -100
  class NavPanel:
    def __init__(self):
      self._scroll_panel = Scroll()
  class Renderer:
    def __init__(self, **kwargs):
      assert kwargs['text_size']['p'] <= 26
    def get_total_height(self, width):
      return 900
    def render(self, rect):
      calls.append(('render', rect))
  def module(name, **attrs):
    result = ModuleType(name)
    result.__dict__.update(attrs)
    monkeypatch.setitem(sys.modules, name, result)
  module('pyray', Rectangle=Rectangle,
         begin_scissor_mode=lambda *args: calls.append(('clip', *args)),
         end_scissor_mode=lambda: calls.append(('end',)))
  module('openpilot.system.ui.widgets.scroller', NavRawScrollPanel=NavPanel)
  module('openpilot.system.ui.widgets.html_render', HtmlRenderer=Renderer, ElementType=NS(P='p'))
  scope = panel_scope()
  scope.update(LearningReader=lambda params: None, Params=lambda: None)
  panel = scope['learning_mici_dialog']()
  panel._render(Rectangle(0, 0, width, height))
  viewport = calls[0][1]
  assert 0 <= viewport.x < width and 0 <= viewport.y < height
  assert viewport.x + viewport.width <= width and viewport.y + viewport.height <= height
  assert calls[0][2] > viewport.height  # long content really needs scrolling
  assert calls[1] == ('clip', int(viewport.x), int(viewport.y), int(viewport.width), int(viewport.height))
  assert calls[2][1].y < viewport.y  # user scroll offset is applied
  assert calls[-1] == ('end',)
