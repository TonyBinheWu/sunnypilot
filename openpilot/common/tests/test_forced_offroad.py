import ast
import asyncio
import json
import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS
import time

import pytest

from openpilot.common.forced_offroad import (ACTIVE_KEY, OBSERVER_KEY, REQUEST_KEY, OffroadPolicy,
                                           OffroadService, observer_failed, parked_reason, release_observer, toggle_reason)

ROOT = Path(__file__).resolve().parents[3]


class Params:
  def __init__(self):
    self.values = {}
    self.writes = []

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def put_bool(self, key, value):
    self.values[key] = value
    self.writes.append((key, value))


class Vehicle(dict):
  def __init__(self):
    super().__init__(carState=NS(gearShifter="park", standstill=True, vEgo=0., vEgoRaw=0., canValid=True),
                     carControl=NS(enabled=False, latActive=False, longActive=False),
                     selfdriveState=NS(enabled=False), deviceState=NS(started=True))
    self.seen = dict.fromkeys(self, True)
    self.valid = dict.fromkeys(self, True)
    self.logMonoTime = dict.fromkeys(self, time.monotonic_ns())

  def update(self, _timeout):
    pass


@pytest.mark.parametrize("gear", ["drive", "reverse", "neutral", "sport", "low", "unknown", ""])
def test_only_park_allows_both_directions(gear):
  params, sm = Params(), Vehicle()
  sm["carState"].gearShifter = gear
  service = OffroadService(params, sm)
  for active in (False, True):
    params.values.update({REQUEST_KEY: active, ACTIVE_KEY: active})
    sm["deviceState"].started = not active
    assert not service.status()["can_toggle"]
    with pytest.raises(PermissionError, match="park_required"):
      service.request(not active)
  assert not params.writes


@pytest.mark.parametrize("field,value", [("vEgo", 0.051), ("vEgoRaw", -0.051), ("vEgo", float("nan")),
                                        ("vEgoRaw", float("inf")), ("standstill", False), ("canValid", False)])
def test_park_does_not_hide_motion_or_bad_can(field, value):
  sm = Vehicle()
  setattr(sm["carState"], field, value)
  assert parked_reason(sm)
  policy = OffroadPolicy()
  policy.active = True
  assert not policy.update(True, sm)


@pytest.mark.parametrize("fault", ["stale", "future", "unseen", "invalid"])
def test_vehicle_data_fails_closed(fault):
  sm = Vehicle()
  if fault in ("stale", "future"):
    sm.logMonoTime["carState"] += int((-1 if fault == "stale" else 1) * 1e9)
  elif fault == "unseen":
    sm.seen["carState"] = False
  else:
    sm.valid["carState"] = False
  assert toggle_reason(sm) == "vehicle_unavailable"


@pytest.mark.parametrize("service,field", [("carControl", "enabled"), ("carControl", "latActive"),
                                           ("carControl", "longActive"), ("selfdriveState", "enabled")])
def test_all_control_authorities_must_be_disengaged(service, field):
  sm = Vehicle()
  setattr(sm[service], field, True)
  assert toggle_reason(sm) == "controls_active"


def test_request_runtime_activation_stop_publishers_and_parked_release():
  params, sm, policy = Params(), Vehicle(), OffroadPolicy()
  service = OffroadService(params, sm)
  assert service.status()["can_toggle"]
  result = service.request(True)
  assert result["pending"] and not result["can_toggle"]
  assert policy.update(params.get_bool(REQUEST_KEY), sm)
  params.put_bool(ACTIVE_KEY, True)
  sm["deviceState"].started = False
  sm.seen["carControl"] = sm.seen["selfdriveState"] = False
  assert policy.update(True, sm)  # Retention uses current carState, not stopped publishers.
  assert service.status()["can_toggle"]
  assert service.request(False)["pending"]
  assert not policy.update(False, sm)


@pytest.mark.parametrize("cause", ["gear", "motion", "stale", "ignition"])
def test_runtime_rechecks_after_request_and_cancels_active_mode(cause):
  sm, policy = Vehicle(), OffroadPolicy()
  assert policy.update(True, sm)
  if cause == "gear": sm["carState"].gearShifter = "drive"
  if cause == "motion": sm["carState"].vEgoRaw = 1.
  if cause == "stale": sm.logMonoTime["carState"] -= 1_000_000_000
  assert not policy.update(True, sm, ignition=cause != "ignition")
  fresh_policy = OffroadPolicy()
  assert not fresh_policy.update(True, sm, ignition=cause != "ignition")


def test_stale_controls_cannot_enable_or_release_an_unconfirmed_session():
  sm = Vehicle()
  sm.seen["carControl"] = False
  sm["deviceState"].started = False
  assert toggle_reason(sm) == "controls_unavailable"
  assert toggle_reason(sm, active=True) == ""
  sm.valid["deviceState"] = False
  assert toggle_reason(sm, active=True) == "controls_unavailable"


def test_each_write_rechecks_vehicle_after_the_display_was_enabled():
  params, sm = Params(), Vehicle()
  service = OffroadService(params, sm)
  assert service.status()["can_toggle"]
  sm["carState"].gearShifter = "drive"
  with pytest.raises(PermissionError):
    service.request(True)
  assert not params.writes


def test_native_callback_uses_the_same_live_guard_even_with_cached_ui_status():
  path = ROOT / "openpilot/selfdrive/ui/widgets/forced_offroad.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  view_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "OffroadView")
  params, sm = Params(), Vehicle()
  service = OffroadService(params, sm)
  namespace = {"time": time, "get_service": lambda: service}
  exec(compile(ast.Module(body=[view_class], type_ignores=[]), str(path), "exec"), namespace)
  view = namespace["OffroadView"]()
  assert view.refresh()["can_toggle"]
  sm["carState"].gearShifter = "drive"
  view.change(True)
  assert not params.writes and not view.state["can_toggle"]


@pytest.mark.parametrize("value", [0, 1, "true", "false", None, {}, []])
def test_only_actual_booleans_are_requests(value):
  params = Params()
  with pytest.raises(ValueError):
    OffroadService(params, Vehicle()).request(value)
  assert not params.writes


def test_observer_restarts_even_when_request_was_cancelled_between_manager_ticks():
  params = Params()
  params.put_bool(OBSERVER_KEY, True)
  calls = []
  process = NS(stop=lambda: calls.append(params.get_bool(OBSERVER_KEY)))
  assert release_observer(params, process)
  assert calls == [True] and not params.get_bool(OBSERVER_KEY)
  assert not release_observer(params, process)
  params.values.update({OBSERVER_KEY: True, ACTIVE_KEY: True})
  assert not release_observer(params, process)


def test_manager_records_a_stalled_observer_before_card_can_acknowledge():
  params, calls = Params(), []
  params.put_bool(REQUEST_KEY, True)
  process = NS(stop=lambda: calls.append("stop"))
  assert not release_observer(params, process)
  assert params.get_bool(OBSERVER_KEY)
  params.put_bool(REQUEST_KEY, False)
  assert release_observer(params, process) and calls == ["stop"]


@pytest.mark.parametrize("proc", [None, NS(is_alive=lambda: False)])
def test_dead_observer_is_cancelled_without_starting_an_offroad_fingerprint(proc):
  params = Params()
  params.values.update({REQUEST_KEY: True, ACTIVE_KEY: True})
  assert observer_failed(params, NS(proc=proc))
  assert not params.get_bool(REQUEST_KEY)
  assert params.get_bool(ACTIVE_KEY)  # hardwared retains ownership of actual mode.
  assert not observer_failed(params, NS(proc=NS(is_alive=lambda: True)))


def test_actual_card_step_is_read_only_and_latches_until_process_restart():
  path = ROOT / "openpilot/selfdrive/car/card.py"
  cls = next(node for node in ast.parse(path.read_text(encoding="utf-8")).body if isinstance(node, ast.ClassDef) and node.name == "Car")
  step = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "step")
  namespace = {"time": time, "CAN_BACKEND": "test", "EventName": NS(selfdriveInitializing=99),
               "car": NS(CarControl=NS(Actuators=NS(new_message=lambda: NS(torque=0, accel=0))))}
  exec(compile(ast.Module(body=[step], type_ignores=[]), str(path), "exec"), namespace)
  calls, params = [], Params()
  sm = Vehicle()
  sm["onroadEvents"] = []
  sm.seen["onroadEvents"] = True
  obj = NS(params=params, forced_offroad_observer=False, initialized_prev=True,
           state_update=lambda: NS(buttonEvents=[]), sm=sm, CP=NS(passive=False),
           cruise_main_toggle=NS(update=lambda *a: False),
           state_publish=lambda cs: calls.append("publish"), controls_update=lambda *a: calls.append("control"),
           card_diag_recv_ns=time.monotonic_ns(), card_diag_stage_current={},
           runtime_diagnostics=NS(record=lambda **kwargs: None), v_cruise_helper=NS(cruise_stage_ms={}))
  params.put_bool(REQUEST_KEY, True)
  namespace["step"](obj)
  assert calls == ["publish"] and not obj.initialized_prev
  assert obj.last_actuators_output.torque == obj.last_actuators_output.accel == 0
  assert params.get_bool(OBSERVER_KEY)
  params.put_bool(REQUEST_KEY, False)
  params.put_bool("IsOnroad", True)
  namespace["step"](obj)
  assert calls == ["publish", "publish"]  # Even queued controls cannot escape the observer latch.
  assert release_observer(params, NS(stop=lambda: None))
  obj.forced_offroad_observer = False  # A fresh process starts with an empty latch.
  namespace["step"](obj)
  assert calls[-1] == "control"


def test_http_uses_the_same_park_gate(monkeypatch):
  spec = importlib.util.spec_from_file_location("forced_offroad_api", ROOT / "openpilot/selfdrive/carrot/server/features/forced_offroad.py")
  api = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(api)
  params, sm = Params(), Vehicle()
  service = OffroadService(params, sm)
  monkeypatch.setattr(api, "get_service", lambda: service)
  async def body(): return {"enabled": True}
  request = NS(json=body)
  sm["carState"].gearShifter = "reverse"
  response = asyncio.run(api.change(request))
  assert response.status == 409 and json.loads(response.body)["error"] == "park_required"
  assert not params.writes
  sm["carState"].gearShifter = "park"
  response = asyncio.run(api.change(request))
  assert response.status == 200 and params.get_bool(REQUEST_KEY)


def test_native_registry_resets_every_offroad_flag_at_manager_start(tmp_path):
  try:
    from openpilot.common.params import Params as NativeParams, ParamKeyFlag, ParamKeyType
  except ImportError:
    pytest.skip("native Params registry is checked after the production build")
  params = NativeParams(str(tmp_path))
  for key in (REQUEST_KEY, ACTIVE_KEY, OBSERVER_KEY):
    assert params.get_type(key) == ParamKeyType.BOOL
    assert not params.get_bool(key)
    params.put_bool(key, True)
  params.clear_all(ParamKeyFlag.CLEAR_ON_MANAGER_START)
  assert not any(params.get_bool(key) for key in (REQUEST_KEY, ACTIVE_KEY, OBSERVER_KEY))
