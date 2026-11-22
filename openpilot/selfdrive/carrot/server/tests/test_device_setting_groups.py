from openpilot.selfdrive.carrot.server.services import device_info


def test_defaults_are_derived_from_the_groups_not_restated():
  from_groups = {name: default for _group, entries in device_info.DEVICE_SETTING_GROUPS for name, default in entries}
  assert device_info.DEVICE_SETTING_DEFAULTS == from_groups


def test_no_parameter_appears_in_two_groups():
  names = [name for _group, entries in device_info.DEVICE_SETTING_GROUPS for name, _default in entries]
  assert len(names) == len(set(names))


def test_every_default_belongs_to_exactly_one_group():
  grouped = device_info.get_device_setting_group_names()
  flattened = [name for names in grouped.values() for name in names]
  assert sorted(flattened) == sorted(device_info.DEVICE_SETTING_DEFAULTS)


def test_the_group_mapping_keeps_declaration_order():
  grouped = device_info.get_device_setting_group_names()
  assert list(grouped) == [group for group, _entries in device_info.DEVICE_SETTING_GROUPS]
  assert grouped["Device"][0] == "DeviceType"
  assert grouped["Toggles"][0] == "OpenpilotEnabledToggle"


def test_the_groups_the_web_renders_are_all_present():
  grouped = device_info.get_device_setting_group_names()
  # Network is read-only and has no parameters, so it is intentionally absent.
  assert set(grouped) == {"Device", "Software", "Toggles", "Developer"}


def test_parameters_the_ui_depends_on_are_not_dropped():
  grouped = device_info.get_device_setting_group_names()
  # Each of these drives a specific control; losing one silently blanks it.
  assert "LongitudinalPersonality" in grouped["Toggles"]
  assert "ExperimentalModeConfirmed" in grouped["Toggles"]
  assert "SoftwareMenu" in grouped["Device"]
  assert {"GithubUsername", "GithubSshKeys"} <= set(grouped["Developer"])


def test_the_mapping_is_a_copy_callers_cannot_corrupt():
  first = device_info.get_device_setting_group_names()
  first["Device"].append("Injected")
  assert "Injected" not in device_info.get_device_setting_group_names()["Device"]


def test_longitudinal_setup_uses_vehicle_capability_instead_of_saved_toggles():
  from openpilot.cereal import car

  params = {"ExperimentalMode": True, "AlphaLongitudinalEnabled": True}
  assert device_info.get_longitudinal_setup_status(params) == "unknown"
  params["CarParamsPersistent"] = b"bad"
  assert device_info.get_longitudinal_setup_status(params) == "unknown"
  for host, passive, expected in [(False, False, "stock"), (True, False, "openpilot"), (True, True, "observer")]:
    cp = car.CarParams.new_message(brand="hyundai", carFingerprint="KIA_EV6", openpilotLongitudinalControl=host, passive=passive)
    params["CarParamsPersistent"] = cp.to_bytes()
    assert device_info.get_longitudinal_setup_status(params) == expected
  for issue in ("identity", "wiring", "adas"):
    params["AutoExperimentalIssue"] = issue
    assert device_info.get_longitudinal_setup_status(params) == issue


def test_web_longitudinal_request_is_scoped_and_cancellable_after_failed_identification():
  import pytest
  from openpilot.cereal import car
  from openpilot.selfdrive.carrot.server.features.intro.reconfigure import SetupError
  from openpilot.selfdrive.carrot.server.features.settings import _experimental_setup
  from openpilot.selfdrive.carrot.server.services.params import INTERNAL_SESSION_PARAMS

  class Settings(dict):
    put = dict.__setitem__
    remove = dict.__delitem__

    def get_bool(self, name):
      return bool(self.get(name))

    def get_int(self, name):
      return int(self.get(name, 0))

  params = Settings(CarSelected3="Kia EV6 (with HDA II) 2022-24")
  platform = "KIA_EV6"
  params["CarParamsPersistent"] = car.CarParams.new_message(brand="hyundai", carFingerprint=platform).to_bytes()
  assert _experimental_setup(params) == {"platform": platform, "requested": "", "owner": "stock"}
  for key, value in (("IsReleaseBranch", True), ("HyundaiCameraSCC", 3), ("CarSelected3", "different")):
    original = params.copy()
    params[key] = value
    with pytest.raises(SetupError, match="settings_changed"):
      _experimental_setup(params, (True, platform))
    params.clear()
    params.update(original)
  with pytest.raises(SetupError, match="settings_changed"):
    _experimental_setup(params, (True, "KIA_SORENTO"))
  params["CarSelected3"] = "AUTO"
  assert _experimental_setup(params)["platform"] == ""
  params["AutoCarModelResult"] = platform
  assert "AutoCarModelResult" in INTERNAL_SESSION_PARAMS
  assert "AutoExperimentalPlatform" in INTERNAL_SESSION_PARAMS
  assert _experimental_setup(params, (True, platform)) == {"platform": platform, "requested": platform, "owner": "stock"}
  assert "AlphaLongitudinalEnabled" not in params and "ExperimentalMode" not in params
  params["CarParamsPersistent"] = car.CarParams.new_message(brand="mock", carFingerprint="MOCK").to_bytes()
  params["AutoExperimentalIssue"] = "identity"
  assert _experimental_setup(params) == {"platform": "", "requested": platform, "owner": "identity"}
  with pytest.raises(SetupError, match="settings_changed"):
    _experimental_setup(params, (False, "KIA_SORENTO"))
  assert _experimental_setup(params, (False, platform))["requested"] == ""
  params["CarName"] = "MOCK"
  assert _experimental_setup(params, (True, platform))["requested"] == platform
  assert "AlphaLongitudinalEnabled" not in params and "ExperimentalMode" not in params
  assert _experimental_setup(params, (False, platform))["requested"] == ""
  for key, value in (("CarName", platform), ("AutoCarModelResult", "unknown"), ("CarSelected3", "different"),
                     ("IsReleaseBranch", True), ("HyundaiCameraSCC", 3), ("CarParamsPersistent", b"")):
    original = params.copy()
    params[key] = value
    with pytest.raises(SetupError, match="settings_changed"):
      _experimental_setup(params, (True, platform))
    params.clear()
    params.update(original)


def test_web_longitudinal_route_requires_offroad_and_rechecks_live_guard(monkeypatch):
  import asyncio
  from types import SimpleNamespace

  from aiohttp import web
  from aiohttp.test_utils import TestClient, TestServer
  from openpilot.selfdrive.carrot.server.features import settings
  from openpilot.selfdrive.carrot.server.features.intro import reconfigure, routes

  writes = []
  flags = {"IsOnroad": True}
  monkeypatch.setattr(settings, "HAS_PARAMS", True)
  monkeypatch.setattr(settings, "Params", lambda: SimpleNamespace(get_bool=flags.get))
  monkeypatch.setattr(settings, "_experimental_setup", lambda params, change: writes.append(change) or {})
  def blocked(_):
    raise reconfigure.SetupError("vehicle_unavailable")

  async def run():
    app = web.Application()
    settings.register(app)
    async with TestClient(TestServer(app)) as client:
      url = "/api/settings/experimental_setup"
      body = {"platform": "KIA_EV6", "enabled": True}
      monkeypatch.setattr(routes, "_reconfigure_guard", blocked)
      assert (await client.post(url, json=body, headers={"Origin": "https://other.example"})).status == 403
      assert (await client.post(url, json={**body, "enabled": 1})).status == 400
      response = await client.post(url, json=body)
      assert (await response.json())["error"] == "vehicle_unavailable"
      monkeypatch.setattr(routes, "_reconfigure_guard", lambda _: None)
      response = await client.post(url, json=body)
      assert (await response.json())["error"] == "park_required"
      assert writes == []
      flags.update(IsOnroad=False, IsOffroad=True)
      assert (await client.post(url, json=body)).status == 200
      assert writes == [(True, "KIA_EV6")]

  asyncio.run(run())


def test_switch_to_auto_clears_previous_receipt_and_confirms_storage(monkeypatch):
  import pytest
  from openpilot.selfdrive.carrot.server.services import params

  class Store(dict):
    def remove(self, name):
      self.pop(name, None)

  store = Store(CarSelected3="Kia EV6", AutoCarModelResult="KIA_EV6")
  monkeypatch.setattr(params, "HAS_PARAMS", True)
  monkeypatch.setattr(params, "Params", lambda: store)
  monkeypatch.setattr(params, "put_typed", lambda storage, name, value, meta: storage.update({name: value}))
  params.set_param_value("CarSelected3", "AUTO")
  assert store == {"CarSelected3": "AUTO"}
  store["CarSelected3"] = "Kia EV6"
  monkeypatch.setattr(params, "put_typed", lambda *args: None)
  with pytest.raises(RuntimeError, match="not saved"):
    params.set_param_value("CarSelected3", "AUTO")
