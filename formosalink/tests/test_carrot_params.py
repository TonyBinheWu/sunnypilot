"""Exercise actual native actions with the Carrot Params write signatures."""
import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]


class Params:
  def __init__(self, **values):
    self.values = values

  def get_bool(self, key):
    return self.values.get(key, False)

  def put_bool(self, key, value):
    self.values[key] = value


def dialog_actions(params, offroad=True):
  path = ROOT / 'openpilot/sunnypilot/formosalink/ui.py'
  tree = ast.parse(path.read_text(encoding='utf-8'))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'FormosaPairingDialog')
  cls.bases = []
  cls.body = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in ('_toggle_remote', '_disable_monitoring')]
  scope = {'ui_state': SimpleNamespace(params=params, is_offroad=lambda: offroad), 'REMOTE_KEY': 'FormosaLinkRemoteWeb'}
  exec(compile(ast.Module(body=[cls], type_ignores=[]), str(path), 'exec'), scope)
  dialog = scope['FormosaPairingDialog']()
  dialog._generation = 0
  dialog._clear_qr = lambda: None
  return dialog


def test_native_remote_carrot_button_toggles_without_params_typeerror():
  params = Params(FormosaLinkEnabled=True)
  dialog = dialog_actions(params)
  dialog._toggle_remote()
  assert params.get_bool('FormosaLinkRemoteWeb')
  dialog._toggle_remote()
  assert not params.get_bool('FormosaLinkRemoteWeb')
  assert params.get_bool('FormosaLinkEnabled')


def test_native_disable_revokes_web_and_monitoring_without_params_typeerror():
  params = Params(FormosaLinkEnabled=True, FormosaLinkRemoteWeb=True)
  dialog = dialog_actions(params)
  dialog._disable_monitoring()
  assert not params.get_bool('FormosaLinkRemoteWeb')
  assert not params.get_bool('FormosaLinkEnabled')
  assert dialog._state == 'disabled'


@pytest.mark.parametrize('action', ['_toggle_remote', '_disable_monitoring'])
def test_native_consent_actions_do_not_write_onroad(action):
  params = Params(FormosaLinkEnabled=True, FormosaLinkRemoteWeb=False)
  getattr(dialog_actions(params, offroad=False), action)()
  assert params.values == {'FormosaLinkEnabled': True, 'FormosaLinkRemoteWeb': False}
