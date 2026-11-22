import ast
import importlib.util
from pathlib import Path
import sys
import time
import types

import pytest

DIRECTORY = Path(__file__).resolve().parents[1] / 'features/intro'
PACKAGE = '_carrot_intro_reconfigure_tests'
pkg = types.ModuleType(PACKAGE)
pkg.__path__ = [str(DIRECTORY)]
sys.modules[PACKAGE] = pkg
spec = importlib.util.spec_from_file_location(PACKAGE + '.reconfigure', DIRECTORY / 'reconfigure.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class Params:
  def __init__(self):
    self.values = {key: str(value) for key, value in setup.get_preset('stock').items()}
    self.values.update(CarSelected3='Kia EV6 (with HDA II) 2022-24', CanfdHDA2='1')
    self.values.update(KeepCustom='409', IsOffroad='1', IsOnroad='0')

  def get(self, name):
    return self.values.get(name)

  def put(self, name, value):
    self.values[name] = str(value)

  def remove(self, name):
    self.values.pop(name, None)

  def get_bool(self, name):
    return self.values.get(name) == '1'


def fixture():
  params, web, events = Params(), {'web_language': 'zh-tw', 'vision_presentation': 'bev'}, []
  current = setup.snapshot(params, lambda: web)
  body = {'revision': current['revision'], 'lang': 'zh-tw', 'car': current['car'], 'hda': None, 'preset': None}
  def apply(body, **kwargs):
    return setup.apply(params, body, read_web=lambda: web, update_web=kwargs.pop('update_web', web.update),
      makers={'Kia': [current['car'], 'Kia Test 2025'], 'Toyota': ['Toyota Test 2025']},
      write=kwargs.pop('write', params.put), guard=kwargs.pop('guard', lambda: None),
      record=lambda *event: events.append(event), **kwargs)
  return params, web, events, body, apply


def test_reading_and_no_change_apply_preserve_custom_values_and_other_preferences():
  p, web, events, body, apply = fixture()
  before = dict(p.values)
  assert apply(body)['applied'] == {}
  assert p.values == before and not events
  assert web == {'web_language': 'zh-tw', 'vision_presentation': 'bev'}


def test_selected_hda_and_preset_apply_only_declared_keys_with_readback_and_history():
  p, web, events, body, apply = fixture()
  result = apply({**body, 'car': 'Kia Test 2025', 'hda': 0, 'preset': 'camera_long', 'lang': 'en'})
  assert result['requiresRestart'] is True
  assert p.values['CanfdHDA2'] == '0' and p.values['CarSelected3'] == 'Kia Test 2025'
  assert p.values['EnableCornerRadar'] == '0' and p.values['HyundaiCameraSCC'] == '1'
  assert p.values['KeepCustom'] == '409' and web['vision_presentation'] == 'bev'
  assert web['web_language'] == 'en'
  assert {e[0] for e in events} == set(result['applied'])


@pytest.mark.parametrize('change', [dict(hda=True), dict(hda=4), dict(preset='unknown'), dict(preset=[]), dict(lang=[]), dict(car='Bad car'), dict(extra=1)])
def test_invalid_choices_write_nothing(change):
  p, web, _, body, apply = fixture()
  before = dict(p.values)
  with pytest.raises(setup.SetupError):
    apply({**body, **change})
  assert p.values == before and web['web_language'] == 'zh-tw'


def test_auto_uses_no_manual_platform_or_wiring_preset():
  p, _, _, body, apply = fixture()
  for extra in (dict(hda=1), dict(preset='radar_long')):
    with pytest.raises(setup.SetupError):
      apply({**body, 'car': 'AUTO', **extra})
  assert apply({**body, 'car': 'AUTO'})['applied'] == {'CarSelected3': 'AUTO'}
  assert p.values['CanfdHDA2'] == '1'


def test_other_client_edits_invalidate_open_draft_without_overwriting_them():
  p, _, _, body, apply = fixture()
  p.values['CanfdHDA2'] = '0'
  with pytest.raises(setup.SetupError, match='settings_changed'):
    apply({**body, 'hda': 1})
  assert p.values['CanfdHDA2'] == '0'


def test_non_hkg_preserves_hda_and_rejects_hkg_override():
  p, _, _, body, apply = fixture()
  with pytest.raises(setup.SetupError, match='invalid_hda'):
    apply({**body, 'car': 'Toyota Test 2025', 'hda': 0})
  apply({**body, 'car': 'Toyota Test 2025'})
  assert p.values['CanfdHDA2'] == '1'


def test_competing_edit_to_unchanged_vehicle_is_detected_before_reporting_success():
  p, _, events, body, apply = fixture()
  def write(name, value):
    p.put(name, value)
    p.put('CarSelected3', 'Other client vehicle')
  with pytest.raises(setup.SetupError, match='settings_changed'):
    apply({**body, 'hda': 0}, write=write)
  assert p.values['CarSelected3'] == 'Other client vehicle'
  assert p.values['CanfdHDA2'] == '1' and not events


def test_failure_after_write_restores_preexisting_values_without_success_history():
  p, web, events, body, apply = fixture()
  before = dict(p.values)
  def write(name, value):
    p.put(name, value)
    if name == 'HyundaiCameraSCC':
      raise OSError('after write')
  with pytest.raises(setup.SetupError, match='write_failed'):
    apply({**body, 'hda': 0, 'preset': 'camera_long', 'lang': 'en'}, write=write)
  assert p.values == before and web['web_language'] == 'zh-tw' and not events


def test_rollback_preserves_concurrent_third_party_value_and_reports_incomplete():
  p, _, _, body, apply = fixture()
  def write(name, value):
    p.put(name, '2')
    raise OSError('concurrent writer')
  with pytest.raises(setup.SetupError, match='rollback_incomplete') as error:
    apply({**body, 'hda': 0}, write=write)
  assert p.values['CanfdHDA2'] == '2' and error.value.rollback_failed == ['CanfdHDA2']


def test_guard_rechecked_during_batch_and_rejects_then_restores_earlier_writes():
  p, _, _, body, apply = fixture()
  before = dict(p.values)
  def guard():
    if p.values['CanfdHDA2'] == '0':
      raise setup.SetupError('park_required')
  with pytest.raises(setup.SetupError, match='park_required'):
    apply({**body, 'hda': 0, 'preset': 'camera_long'}, guard=guard)
  assert p.values == before


def load_guard():
  from openpilot.common.forced_offroad import fresh, toggle_reason
  tree = ast.parse((DIRECTORY / 'routes.py').read_text(encoding='utf-8'))
  fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_check_setup_state')
  fn.body = [n for n in fn.body if not isinstance(n, ast.ImportFrom)]
  scope = {'time': time, 'reconfigure': setup, 'fresh': fresh, 'toggle_reason': toggle_reason}
  exec(compile(ast.Module(body=[fn], type_ignores=[]), 'routes.py', 'exec'), scope)
  return scope['_check_setup_state']


def test_native_runtime_guard_accepts_real_offroad_and_rejects_moving_active_stale_or_unknown():
  p = Params()
  guard = load_guard()
  now = int(time.monotonic() * 1e9)
  values = dict(deviceState=types.SimpleNamespace(started=False), carState=types.SimpleNamespace(canValid=True,gearShifter='park',standstill=True,vEgo=0.,vEgoRaw=0.),
    carControl=types.SimpleNamespace(enabled=False,latActive=False,longActive=False),selfdriveState=types.SimpleNamespace(enabled=False))
  sm = type('SM', (dict,), {})(values)
  sm.seen = dict.fromkeys(values, True);sm.valid = dict.fromkeys(values, True);sm.logMonoTime = dict.fromkeys(values, now)
  guard(p, sm)
  sm['carState'].gearShifter='drive'
  with pytest.raises(setup.SetupError, match='park_required'):guard(p, sm)
  sm['carState'].gearShifter='park';sm['carControl'].latActive=True
  with pytest.raises(setup.SetupError, match='controls_active'):guard(p, sm)
  sm['carControl'].latActive=False;sm.logMonoTime['deviceState']=0
  with pytest.raises(setup.SetupError, match='vehicle_unavailable'):guard(p, sm)
  with pytest.raises(setup.SetupError, match='vehicle_unavailable'):guard(p, None)
  sm.logMonoTime['deviceState']=now;sm['deviceState'].started=True
  p.values.update(IsOffroad='0', IsOnroad='1')
  guard(p, sm)  # Ignition on is allowed only with fresh P and disabled control.
  sm.logMonoTime['carControl']=0
  with pytest.raises(setup.SetupError, match='controls_unavailable'):guard(p, sm)


def test_write_guard_refreshes_native_subscriber_under_lock_without_web_broker():
  tree = ast.parse((DIRECTORY / 'routes.py').read_text(encoding='utf-8'))
  fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_reconfigure_guard')
  fn.body = [n for n in fn.body if not isinstance(n, ast.ImportFrom)]
  calls = []
  class Lock:
    def __enter__(self): calls.append('lock')
    def __exit__(self, *args): calls.append('unlock')
  service = types.SimpleNamespace(lock=Lock(), params=Params(), sm=types.SimpleNamespace(update=lambda timeout: calls.append(('refresh', timeout))))
  scope = {'get_service': lambda: service, 'params': types.SimpleNamespace(HAS_PARAMS=True, Params=Params),
    'reconfigure': setup, '_check_setup_state': lambda p, sm: calls.append(('check', p is service.params, sm is service.sm))}
  exec(compile(ast.Module(body=[fn], type_ignores=[]), 'routes.py', 'exec'), scope)
  scope['_reconfigure_guard']({})
  assert calls == ['lock', ('refresh', 0), ('check', True, True), 'unlock']


def test_language_failure_after_landing_rolls_back_vehicle_and_preserves_other_web_preferences():
  p, web, events, body, apply = fixture()
  before = dict(p.values)
  def update(updates):
    web.update(updates)
    if updates['web_language'] == 'en':
      raise OSError('after language write')
  with pytest.raises(setup.SetupError, match='write_failed'):
    apply({**body, 'hda': 0, 'lang': 'en'}, update_web=update)
  assert p.values == before and web == {'web_language': 'zh-tw', 'vision_presentation': 'bev'} and not events
