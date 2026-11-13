from types import SimpleNamespace
import asyncio
import importlib.util
import json
from pathlib import Path
import re

import pytest

from openpilot.selfdrive.carrot.sound_volume import NAVIGATION_VOICE_FILES, read_voice_volume


@pytest.mark.parametrize(('stored', 'gain'), [(None, 1.), ('bad', 1.), ('100', 1.), (b'200', 2.),
                                            ('300', 3.), ('9999', 3.), ('-10', .05), ('0', .05), ('5', .05)])
def test_voice_volume_validates_persisted_values(stored, gain):
  def get(key, return_default=False):
    assert key == 'SoundLanguageVolume' and return_default
    return stored
  assert read_voice_volume(SimpleNamespace(get=get)) == gain


def test_voice_volume_default_and_warning_exclusions():
  assert len(NAVIGATION_VOICE_FILES) == 12
  assert {'prompt.wav', 'warning_immediate.wav', 'prompt_distracted.wav', 'engage.wav'}.isdisjoint(NAVIGATION_VOICE_FILES)


def test_catalog_range_and_persistent_default_agree():
  root = Path(__file__).resolve().parents[4]
  catalog = json.loads((root/'openpilot/selfdrive/carrot_settings.json').read_text(encoding='utf-8'))
  setting = next(item for item in catalog['params'] if item['name'] == 'SoundLanguageVolume')
  assert (setting['min'], setting['max'], setting['unit']) == (5, 300, 5)
  assert read_voice_volume(SimpleNamespace(get=lambda *args, **kwargs: setting['default'])) == 1.
  keys = (root/'openpilot/common/params_keys.h').read_text(encoding='utf-8')
  assert re.search(r'"SoundLanguageVolume",\s*\{PERSISTENT,\s*INT,\s*"'+str(setting['default'])+r'"\}', keys)


def test_web_sound_state_reports_gain_changes_without_a_new_alert(monkeypatch):
  path = Path(__file__).resolve().parents[1]/'server/features/web_sound.py'
  spec = importlib.util.spec_from_file_location('voice_volume_web_sound', path)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  clock, stored, sent = [100.], ['100'], []
  class Socket:
    closed = False
    async def send_json(self, payload): sent.append(payload)
  socket = Socket()
  class SubMaster:
    updated = {'selfdriveState':False, 'carrotMan':False}
    valid = {'selfdriveState':True, 'carrotMan':True, 'carState':True}
    recv_time = {'selfdriveState':100.}
    def __getitem__(self, service):
      return {'selfdriveState':SimpleNamespace(enabled=False,alertSound=0),
              'carrotMan':SimpleNamespace(leftSec=100), 'carState':SimpleNamespace(buttonEvents=[])}[service]
    def update(self, _): pass
  class Params:
    def get_int(self, _): return 100
    def get(self, key, **kwargs): return stored[0] if key == 'SoundLanguageVolume' else 'en'
  async def sleep(_):
    if len(sent) >= 2:
      socket.closed = True
    clock[0] += 1.1
    stored[0] = '200'
  monkeypatch.setattr(module, 'Params', Params)
  monkeypatch.setattr(module, '_is_tizi', lambda: False)
  monkeypatch.setattr(module.messaging, 'SubMaster', lambda _: SubMaster())
  monkeypatch.setattr(module.time, 'monotonic', lambda: clock[0])
  monkeypatch.setattr(module.asyncio, 'sleep', sleep)
  asyncio.run(module._send_sound_states(socket))
  assert [state['voiceVolume'] for state in sent] == [1., 2.]
  assert [state['alert'] for state in sent] == [0, 0]
