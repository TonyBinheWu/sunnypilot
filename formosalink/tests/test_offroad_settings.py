"""Native offroad semantics and device-authoritative catalog diagnostics."""
import time
from types import SimpleNamespace

import pytest

from openpilot.sunnypilot.formosalink.device_settings import NativeSettingsProvider
from openpilot.sunnypilot.formosalink.settings import disabled_reason


@pytest.mark.parametrize("ignition", [False, True])
@pytest.mark.parametrize("panda_fresh", [False, True])
def test_native_offroad_does_not_require_ignition_off_or_panda(ignition, panda_fresh):
  class Sources(dict):
    def update(self, timeout):
      pass
  sources = Sources(deviceState=SimpleNamespace(started=False), pandaStates=[SimpleNamespace(ignitionCan=ignition, ignitionLine=ignition)])
  sources.seen = {"deviceState": True, "pandaStates": panda_fresh}
  sources.valid = {"deviceState": True, "pandaStates": panda_fresh}
  sources.logMonoTime = {"deviceState": time.monotonic_ns(), "pandaStates": 0}
  provider = NativeSettingsProvider.__new__(NativeSettingsProvider)
  provider.sm = sources
  provider.params = SimpleNamespace(get_bool=lambda key: key == "IsOffroad")
  assert provider.parked()
  from formosalink.tests.test_settings import provider as settings_provider, command
  settings, params, _ = settings_provider()
  settings.guard = provider.parked
  request = command(settings.capture())
  assert settings.apply(request, request['device_id'], time.monotonic() + 5)['status'] == 'applied'
  assert params.values['QuietMode'] is True
  # Both manager transition and actual onroad state remain independently gated.
  sources['deviceState'].started = True
  assert not provider.parked()
  sources['deviceState'].started = False
  provider.params = SimpleNamespace(get_bool=lambda key: False)
  assert not provider.parked()
  provider.params = SimpleNamespace(get_bool=lambda key: True)
  sources.valid['deviceState'] = False
  assert not provider.parked()
  sources.valid['deviceState'] = True
  sources.logMonoTime['deviceState'] = time.monotonic_ns() - 3_000_000_000
  assert not provider.parked()


def test_disabled_reasons_keep_capability_and_dependency_guards():
  capability = {"type": "capability", "field": "supported", "equals": True}
  dependency = {"type": "param", "key": "Enabled", "equals": True}
  assert disabled_reason([], {}, {}, False, True, "toggle") == "offroad_required"
  assert disabled_reason([], {}, {}, True, False, "toggle") == "read_only"
  assert disabled_reason([capability], {}, {}, True, True, "toggle") == "unknown_condition"
  assert disabled_reason([capability], {}, {"supported": False}, True, True, "toggle") == "capability_required"
  assert disabled_reason([dependency], {"Enabled": False}, {}, True, True, "toggle") == "dependency_required"
  assert disabled_reason([capability, dependency], {"Enabled": True}, {"supported": True}, True, True, "toggle") == ""
