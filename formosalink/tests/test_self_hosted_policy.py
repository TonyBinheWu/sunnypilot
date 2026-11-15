import json
import os
import signal
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from openpilot.sunnypilot.formosalink.service_policy import disable_legacy, self_hosted_origin, stop_legacy_daemon
from openpilot.sunnypilot.formosalink.identity import create, read
from openpilot.sunnypilot.formosalink.connection_status import acknowledge, is_online


def test_disable_legacy_preserves_existing_formosa_pairing_and_consent():
  values = {"SunnylinkEnabled":True, "EnableSunnylinkUploader":True, "SunnylinkDongleId":"old-id",
            "FormosaLinkEnabled":True, "FormosaLinkRemoteSettings":True}
  before = dict(values)
  params = SimpleNamespace(get_bool=lambda key:values.get(key, False), put_bool=lambda key,value,block:values.update({key:value}))
  disable_legacy(params)
  assert values == {**before, "SunnylinkEnabled":False, "EnableSunnylinkUploader":False}


@pytest.mark.parametrize('origin', ['https://sunnylink.ai', 'https://api.sunnylink.ai', 'https://api.sunnypilot.ai', 'https://API.SUNNYLINK.AI.'])
def test_legacy_origins_are_refused_before_creating_identity_or_connecting(tmp_path,origin):
  from openpilot.sunnypilot.formosalink.agent import connect_http, connect_once
  for action in (lambda:create(tmp_path/'new',origin), lambda:connect_http({'origin':origin},None,None),
                 lambda:connect_once({'origin':origin},None,None)):
    with pytest.raises(ValueError, match='self-hosted'):
      action()
  assert not (tmp_path/'new'/'identity.json').exists()


def test_existing_identity_is_preserved_and_custom_self_hosting_remains_supported(tmp_path):
  create(tmp_path, 'https://custom-formosalink.example')
  path = tmp_path/'identity.json'
  before = path.read_bytes()
  assert read(tmp_path)[0]['origin'] == 'https://custom-formosalink.example'
  assert path.read_bytes() == before
  value = json.loads(before)
  value['origin'] = 'https://api.sunnylink.ai'
  path.write_text(json.dumps(value))
  invalid = path.read_bytes()
  with pytest.raises(ValueError): read(tmp_path)
  assert path.read_bytes() == invalid


@pytest.mark.parametrize('module,group,stopped', [
  ('openpilot.sunnypilot.sunnylink.athena.manage_sunnylinkd',12345,True),
  ('openpilot.system.athena.manage_athenad',12345,False),
  ('openpilot.sunnypilot.sunnylink.athena.manage_sunnylinkd',777,False),
])
def test_retirement_only_signals_verified_dedicated_legacy_group(tmp_path,module,group,stopped):
  proc = tmp_path/'12345';proc.mkdir()
  (proc/'cmdline').write_bytes(b'python\0-m\0'+module.encode()+b'\0')
  with patch.object(os,'getpgid',return_value=group,create=True), patch.object(os,'killpg',create=True) as kill:
    assert stop_legacy_daemon(SimpleNamespace(get=lambda _:12345),tmp_path) is stopped
    if stopped: kill.assert_called_once_with(12345,signal.SIGTERM)
    else: kill.assert_not_called()


def test_only_fresh_ack_for_same_server_is_online(tmp_path,monkeypatch):
  monkeypatch.setenv('FORMOSALINK_STATUS_PATH', str(tmp_path/'status.json'))
  origin = 'https://formosapilot.dinglu-t.com'
  with patch('openpilot.sunnypilot.formosalink.connection_status.time.monotonic',return_value=100):
    acknowledge(origin)
  assert is_online(origin,101)
  assert not is_online('https://other.example',101)
  assert not is_online(origin,121)
  assert not is_online(origin,99)
  assert set(json.loads((tmp_path/'status.json').read_text())) == {'origin','last_ack'}


def test_legacy_service_settings_are_unavailable_remotely():
  from openpilot.sunnypilot.formosalink.settings import catalog, validate_setting
  key = 'SunnylinkEnabled'
  schema = {'panels':[{'remote_configurable':True, 'items':[{'key':key,'widget':'toggle'}]}]}
  assert catalog(schema,{key:True},{key:'BOOL'},{},True) == []
  with pytest.raises(ValueError): validate_setting({'key':key,'type':'BOOL','enabled':True},True)
