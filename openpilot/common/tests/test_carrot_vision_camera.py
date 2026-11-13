import json
import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from openpilot.common import carrot_vision_camera as camera


def test_request_expires_and_releases_without_persistent_params(monkeypatch, tmp_path):
  path = tmp_path / 'camera.json'
  monkeypatch.setenv('CARROT_VISION_CAMERA_LEASE', str(path))
  now = [100.0]
  monkeypatch.setattr(camera, 'clock', lambda: now[0])
  assert not camera.camera_requested()
  camera.update_camera_request(True)
  assert camera.camera_requested()
  assert camera.enabled_camera_requested(SimpleNamespace(get_bool=lambda key: True))
  assert not camera.enabled_camera_requested(SimpleNamespace(get_bool=lambda key: False))
  now[0] += 4
  camera.update_camera_request(True)
  now[0] += 4
  assert camera.camera_requested()
  now[0] += 2
  assert not camera.camera_requested()
  camera.update_camera_request(False)
  assert not path.exists()


def test_real_manager_predicates_keep_idle_capture_off(monkeypatch, tmp_path):
  root = Path(__file__).resolve().parents[3]
  source = root / 'openpilot/system/manager/process_config.py'
  names = {'carrot_vision_camera', 'carrot_vision_service', 'carrot_vision_encoder'}
  tree = ast.parse(source.read_text(encoding='utf-8'))
  scope = {'Params': object, 'car': SimpleNamespace(CarParams=object)}
  exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names],
                          type_ignores=[]), str(source), 'exec'), scope)
  monkeypatch.setenv('CARROT_VISION_CAMERA_LEASE', str(tmp_path / 'camera.json'))
  monkeypatch.setattr(camera, 'clock', lambda: 100.0)
  enabled = [True]
  params = SimpleNamespace(get_bool=lambda key: enabled[0])
  cp = SimpleNamespace(notCar=False)
  service, capture, encoder = (scope[name] for name in ('carrot_vision_service', 'carrot_vision_camera', 'carrot_vision_encoder'))
  assert service(False, params, cp)
  assert not capture(False, params, cp)
  assert not encoder(False, params, cp)
  assert encoder(True, params, cp)
  camera.update_camera_request(True)
  assert capture(False, params, cp) and encoder(False, params, cp)
  enabled[0] = False
  assert not service(False, params, cp)
  assert not capture(False, params, cp)
  assert not encoder(False, params, cp)
  camera.update_camera_request(False)
  assert not camera.camera_requested()


@pytest.mark.parametrize('value', [None, {}, {'until': True}, {'until': '101'}, {'until': 120}, {'until': float('nan')}])
def test_invalid_or_future_leases_never_start_capture(monkeypatch, tmp_path, value):
  path = tmp_path / 'camera.json'
  monkeypatch.setenv('CARROT_VISION_CAMERA_LEASE', str(path))
  monkeypatch.setattr(camera, 'clock', lambda: 100)
  path.write_text(json.dumps(value))
  assert not camera.camera_requested()
