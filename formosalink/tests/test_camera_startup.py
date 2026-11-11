"""Execute the actual camerad condition expression without host-native imports."""
import ast
import itertools
import operator
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


def test_actual_camera_start_condition_all_modes():
  path = Path(__file__).resolve().parents[2]/'openpilot/system/manager/process_config.py'
  tree = ast.parse(path.read_text(encoding='utf-8'))
  names = {'or_', 'driverview', 'livestream', 'formosalink_cameras'}
  functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
  scope = {'operator':operator, 'Params':object, 'car':SimpleNamespace(CarParams=object)}
  exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec'), scope)
  camera = next(node for node in ast.walk(tree) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name) and node.func.id == 'NativeProcess'
                and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 'camerad')
  predicate = eval(compile(ast.Expression(body=camera.args[3]), str(path), 'eval'), scope)
  for started, driver, livestream, enabled, leased in itertools.product((False, True), repeat=5):
    flags = {'IsDriverViewEnabled':driver, 'IsLiveStreaming':livestream, 'FormosaLinkEnabled':enabled}
    params = SimpleNamespace(get_bool=lambda key:flags.get(key, False))
    with patch('openpilot.sunnypilot.formosalink.cameras.camera_requested', return_value=leased):
      assert predicate(started, params, None) == (started or driver or livestream or enabled and leased)
