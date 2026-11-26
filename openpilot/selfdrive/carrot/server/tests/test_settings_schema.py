"""Guards the fields the settings UI now reads straight from the catalogue.

Display units and control kinds used to live in hardcoded tables inside
web/js/pages/setting.js, so adding a parameter meant editing two places and
forgetting one was silent. They are declared per parameter now; these tests
keep the declarations well formed.
"""
import json
from pathlib import Path

import pytest

from openpilot.selfdrive.carrot.server.services.settings import (
  build_menu_categories,
  current_vehicle_brand,
  current_vehicle_settings_context,
  filter_settings_catalog_for_brand,
  group_index,
)

SETTINGS_PATH = Path(__file__).resolve().parents[3] / "carrot_settings.json"
PARAMS_KEYS_PATH = Path(__file__).resolve().parents[4] / "common" / "params_keys.h"

# Mirrors SETTING_DISPLAY_UNIT_TYPES / SETTING_CONTROL_KINDS in setting.js.
KNOWN_DISPLAY_UNITS = {"raw", "speedKph", "distanceCm", "timeSec", "timeMs", "timeMin", "percent", "degree"}
KNOWN_CONTROL_KINDS = {"toggle", "segmented", "select", "slider"}
KNOWN_RISK_LEVELS = {"high", "medium"}


@pytest.fixture(scope="module")
def settings():
  with SETTINGS_PATH.open(encoding="utf-8") as f:
    return json.load(f)


@pytest.fixture(scope="module")
def params(settings):
  return settings["params"]


def test_the_catalogue_is_readable_and_populated(params):
  assert len(params) > 100
  assert all(isinstance(p.get("name"), str) and p["name"] for p in params)


def test_tesla_switches_have_a_dedicated_browser_group(settings):
  _, by_name, _ = group_index(settings)
  categories = build_menu_categories(settings, by_name)
  driving = next(category for category in categories if category["id"] == "DRIVING")
  tesla = next(group for group in driving["groups"] if group["id"] == "TESLA")
  expected = ["TeslaAutoTurnSignals", "TeslaCanTrafficStop", "TeslaManualLaneSignals",
              "TeslaModelDesireSignals", "TeslaModelPathSignals", "TeslaAutoSpeedLimit"]
  assert tesla["count"] == 6
  assert tesla["sections"][0]["items"] == expected
  for category in categories:
    for group in category["groups"]:
      if group["id"] != "TESLA":
        assert not set(expected).intersection(name for section in group["sections"] for name in section["items"])
  wheel = by_name["TeslaAutoSpeedLimit"]
  assert (wheel["control"], wheel["default"], wheel["min"], wheel["max"]) == ("toggle", 0, 0, 1)
  assert '{"TeslaAutoSpeedLimit", {PERSISTENT, BOOL, "0"}}' in PARAMS_KEYS_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("maximum,stored,expected", ((3, 4, 3), (4, 4, 4), (3, 2, 2), (4, 3, 3), (3, 0, 3)))
def test_gap_cycle_read_matches_vehicle_limit(monkeypatch, maximum, stored, expected):
  from openpilot.selfdrive.carrot.server.services import params as service
  class FakeParams:
    def get_int(self, key):
      return maximum
  monkeypatch.setattr(service, "HAS_PARAMS", True)
  monkeypatch.setattr(service, "Params", FakeParams)
  monkeypatch.setattr(service, "_read_param_value", lambda params, name, default: stored)
  assert service.get_param_values(["CruiseGapLevels"], {"CruiseGapLevels": maximum}) == {"CruiseGapLevels": expected}


def test_cruise_and_gap_tuning_is_removed(settings):
  _, by_name, _ = group_index(settings)
  assert not {"CruiseGapLevels", "TFollowGap1", "DrivingPlannerMode"}.intersection(by_name)
  categories = build_menu_categories(settings, by_name)
  assert all(group["id"] != "CRUISE" for category in categories for group in category["groups"])
  assert "SunnyAutoLongitudinal" in by_name
  daily = next(section for category in categories for group in category["groups"]
               for section in group["sections"] if "SunnyAutoLongitudinal" in section["items"])
  assert "DynamicExperimentalControl" in daily["items"]
  dec = by_name["DynamicExperimentalControl"]
  assert (dec["default"], dec["control"]) == (0, "toggle")
  assert '{"DynamicExperimentalControl", {PERSISTENT, BOOL, "0"}}' in PARAMS_KEYS_PATH.read_text(encoding="utf8")


def test_removed_speed_and_longitudinal_panels(settings, params):
  names = {p['name'] for p in params}
  retired = {'ApplyModelSpeed', 'LongTuningKpV', 'LongTuningKiV', 'LongTuningKf', 'LongActuatorDelay',
             'AutoNaviRearCameraHoldDistance', 'VehicleNaviCanControl', 'VehicleNaviDecelCancel', 'VehicleNaviSchoolZoneControl',
             'AutoNaviSpeedBumpEndDistance', 'VehicleNaviSectionAvgControl', 'TrafficStopDistanceAdjust'}
  registry = PARAMS_KEYS_PATH.read_text(encoding='utf8')
  assert retired.isdisjoint(names)
  assert all(f'{{"{name}", {{CLEAR_ON_MANAGER_START,' in registry for name in retired)
  assert not {'SPEED', 'VEH_LONGTUNE'} & {g['id'] for cat in settings['menu'] for g in cat['groups']}
  for key in ('SunnyLaneTurn', 'SunnyLaneCenter'):
    item = next(p for p in params if p['name'] == key)
    assert (item['default'], item['min'], item['max']) == (0, 0, 1)


def test_onnx_vision_toggle_uses_existing_runtime_flag_and_first_steering_section(settings, params):
  by_name = {p["name"]: p for p in params}
  vision = by_name["ShareData"]
  assert (vision["control"], vision["min"], vision["max"], vision["default"]) == ("toggle", 0, 1, 0)
  assert vision["risk"] == "high"
  assert '{"ShareData", {PERSISTENT, INT, "0"}}' in PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  driving = next(category for category in settings["menu"] if category["id"] == "DRIVING")
  steering = next(group for group in driving["groups"] if group["id"] == "STEER")
  onnx = steering["groups"][0]
  lane_change = next(group for group in steering["groups"] if group["id"] == "STEER_LANECHANGE")
  assert onnx["id"] == "STEER_ONNX"
  detail_names = [
    "OnnxBsdEnabled",
    "OnnxLaneThreshold", "OnnxLaneIntervalMs", "OnnxBsdThreshold",
    "OnnxBsdSmoothingMs", "OnnxBsdIntervalMs",
  ]
  assert onnx["params"] == ["ShareData", *detail_names]
  assert "ShareData" not in lane_change["params"]
  for name in detail_names:
    assert by_name[name]["detail_parent"] == "ShareData"
    assert by_name[name]["detail_section"] in ("lane", "bsd")
    assert f'{{"{name}", {{PERSISTENT, INT,' in PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  bsd_enabled = by_name["OnnxBsdEnabled"]
  assert (bsd_enabled["control"], bsd_enabled["min"], bsd_enabled["max"], bsd_enabled["default"]) == ("toggle", 0, 1, 0)
  for title in ("title", "etitle", "ctitle"):
    assert "ONNX" in vision[title]


def test_obsolete_lead_response_settings_are_removed(settings, params):
  removed = {"JLeadFactor3", "RadarReactionFactor"}
  by_name = {p["name"] for p in params}
  assert removed.isdisjoint(by_name)
  assert all(
    removed.isdisjoint(group.get("params", []))
    for category in settings["menu"]
    for section in category.get("groups", [])
    for group in section.get("groups", [])
  )
  params_keys = PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  assert all(name not in params_keys for name in removed)


def test_retired_carrot_following_settings_are_absent(params):
  names = {setting["name"] for setting in params}
  assert names.isdisjoint({"MyDrivingModeAuto", "DynamicTFollow", "LeadAccelResponse",
                           "TFollowDecelBoost", "DynamicTFollowLC"})


@pytest.mark.parametrize("brand", ["hyundai", "toyota"])
def test_fixed_tuning_catalog_hides_longitudinal_pid_settings(settings, brand):
  groups, by_name, groups_list = group_index(settings)
  categories = build_menu_categories(settings, by_name)
  hidden = {"LongTuningKpV", "LongTuningKiV", "LongTuningKf"}

  filtered_groups, filtered_groups_list, filtered_categories, hidden_names = filter_settings_catalog_for_brand(
    groups, groups_list, categories, brand,
  )
  visible_names = {item["name"] for items in filtered_groups.values() for item in items}
  menu_names = {
    name
    for category in filtered_categories
    for group in category["groups"]
    for section in group["sections"]
    for name in section["items"]
  }

  assert hidden_names.isdisjoint(hidden)
  assert hidden.isdisjoint(visible_names)
  assert hidden.isdisjoint(menu_names)
  assert all(
    group["count"] == sum(1 for item in filtered_groups[group["group"]]
                          if not item.get("detail_parent") and not item.get("search_only"))
    for group in filtered_groups_list
  )


@pytest.mark.parametrize("car_name", [
  b"HYUNDAI_IONIQ_5_PE",
  "KIA_EV6",
  "GENESIS_G80_2ND_GEN_FL",
])
def test_vehicle_brand_falls_back_to_hkg_car_name(car_name):
  class FakeParams:
    def get(self, name):
      return {"CarParamsPersistent": None, "CarName": car_name}.get(name)

  assert current_vehicle_brand(FakeParams()) == "hyundai"


def test_vehicle_brand_does_not_hide_settings_for_other_car_name():
  class FakeParams:
    def get(self, name):
      return {"CarParamsPersistent": None, "CarName": "TOYOTA_RAV4"}.get(name)

  assert current_vehicle_brand(FakeParams()) == ""


@pytest.mark.parametrize("fingerprint,pedal,longitudinal,expected", [
  ("KIA_RAY_EV", True, True, True),
  ("KIA_RAY_EV", False, True, False),
  ("KIA_RAY_EV", True, False, False),
  ("HYUNDAI_CASPER_EV", True, True, False),
])
def test_ray_pedal_catalog_uses_identified_capability(settings, fingerprint, pedal, longitudinal, expected):
  from openpilot.cereal import car
  from opendbc.car.hyundai.values import HyundaiFlags
  cp = car.CarParams.new_message(brand="hyundai", carFingerprint=fingerprint,
                                openpilotLongitudinalControl=longitudinal)
  cp.flags = int(HyundaiFlags.CC_ONLY_CAR | (HyundaiFlags.PEDAL_INTERCEPTOR if pedal else 0))
  class FakeParams:
    def get(self, name):
      return {"CarParamsPersistent": cp.to_bytes(), "CarName": fingerprint,
              "CommaPedalEnabled": b"1"}.get(name)
  brand, active_pedal = current_vehicle_settings_context(FakeParams())
  assert (brand, active_pedal) == ("hyundai", expected)
  groups, by_name, groups_list = group_index(settings)
  categories = build_menu_categories(settings, by_name)
  filtered, counts, menu, hidden = filter_settings_catalog_for_brand(
    groups, groups_list, categories, brand, ray_pedal_control=active_pedal)
  tuning = {"LongTuningKpV", "LongTuningKiV", "LongTuningKf"}
  visible = {item["name"] for items in filtered.values() for item in items}
  menu_names = {name for category in menu for group in category["groups"]
                for section in group["sections"] for name in section["items"]}
  assert tuning.isdisjoint(visible)
  assert tuning.isdisjoint(menu_names)
  assert tuning.isdisjoint(item["name"] for items in groups.values() for item in items)
  assert all(group["count"] == sum(not item.get("detail_parent") and not item.get("search_only")
                                  for item in filtered[group["group"]]) for group in counts)
  assert tuning.isdisjoint(hidden)


@pytest.mark.parametrize("car_params", [None, b"invalid"])
def test_pending_pedal_toggle_alone_keeps_fixed_brand_catalog(car_params):
  class FakeParams:
    def get(self, name):
      return {"CarParamsPersistent": car_params, "CarName": "KIA_RAY_EV", "CommaPedalEnabled": b"1"}.get(name)
  assert current_vehicle_settings_context(FakeParams()) == ("hyundai", False)


def test_settings_catalog_and_snapshot_follow_ray_capability_changes(monkeypatch, settings):
  import importlib.util
  import sys
  import types
  # Load the real settings feature independently of unrelated device/IPC routes.
  package = "openpilot.selfdrive.carrot.server.features"
  directory = Path(__file__).resolve().parents[1] / "features"
  namespace = types.ModuleType(package)
  namespace.__path__ = [str(directory)]
  monkeypatch.setitem(sys.modules, package, namespace)
  spec = importlib.util.spec_from_file_location(package + ".settings", directory / "settings.py")
  feature = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(feature)
  groups, by_name, groups_list = group_index(settings)
  parts = settings, groups, by_name, groups_list
  monkeypatch.setattr(feature, "get_settings_cached", lambda: parts)
  monkeypatch.setitem(feature.settings_cache, "categories", build_menu_categories(settings, by_name))
  monkeypatch.setattr(feature, "HAS_PARAMS", False)
  for name, result in (
    ("get_ssh_key_status", {}), ("read_setting_favorites", {"favorites": ["LongTuningKiV"]}),
    ("read_setting_profiles", {}), ("read_popular_values_memory", {}), ("read_setting_unit_index", {}),
    ("get_device_network_snapshot", {}), ("get_device_setting_group_names", []),
  ):
    monkeypatch.setattr(feature, name, lambda result=result: result)
  monkeypatch.setattr(feature, "get_device_setting_values", lambda status: {})
  monkeypatch.setattr(feature, "observe_param_values", lambda values: None)
  monkeypatch.setattr(feature, "get_param_values", lambda names, defaults: {
    name: 50 if name == "LongTuningKiV" else defaults[name] for name in names})
  tuning = {"LongTuningKpV", "LongTuningKiV", "LongTuningKf"}
  for active in (True, False, True):
    monkeypatch.setattr(feature, "current_vehicle_settings_context", lambda active=active: ("hyundai", active))
    catalog = feature._settings_catalog_payload()
    snapshot = feature._settings_snapshot_payload()
    visible = {item["name"] for items in catalog["items_by_group"].values() for item in items}
    assert tuning.isdisjoint(visible)
    assert tuning.isdisjoint(snapshot["values"])
    assert snapshot["favorites"] == []


def test_c3x_lite_hardware_setting_is_exposed(settings, params):
  by_name = {p["name"]: p for p in params}
  c3x_lite = by_name["HardwareC3xLite"]
  assert (c3x_lite["min"], c3x_lite["max"], c3x_lite["default"]) == (0, 1, 0)
  assert c3x_lite["control"] == "toggle"
  assert c3x_lite["risk"] == "high"

  vehicle = next(category for category in settings["menu"] if category["id"] == "VEHICLE")
  device_hardware = next(group for group in vehicle["groups"] if group["id"] == "VEH_DEVICE")
  assert device_hardware["params"] == ["CommaPedalEnabled", "HardwareC3xLite"]


def test_comma_pedal_toggle_is_default_off_and_under_device_hardware(settings, params):
  by_name = {p["name"]: p for p in params}
  pedal = by_name["CommaPedalEnabled"]
  assert pedal["title"] == "Comma Pedal사용"
  assert pedal["descr"].startswith("ACC 미 장착 차량에서 Comma Pedal 장치를 통한 종방향 제어를 허용합니다.")
  for key in ("descr", "edescr", "cdescr"):
    assert "CC_ONLY_CAR" in pedal[key] and "Cruise ready" in pedal[key]
    assert "HardwareC3xLite" not in pedal[key]
  assert "순정 크루즈 컨트롤이 우선" in pedal["descr"]
  assert (pedal["min"], pedal["max"], pedal["default"]) == (0, 1, 0)
  assert pedal["control"] == "toggle"
  assert pedal["risk"] == "high"
  params_keys = PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  assert '{"CommaPedalEnabled", {PERSISTENT, INT, "0"}}' in params_keys
  vehicle = next(category for category in settings["menu"] if category["id"] == "VEHICLE")
  device_hardware = next(group for group in vehicle["groups"] if group["id"] == "VEH_DEVICE")
  assert pedal["name"] in device_hardware["params"]


def test_wide_camera_fallback_setting_is_exposed(settings, params):
  by_name = {p["name"]: p for p in params}
  use_wide_camera = by_name["UseWideCamera"]
  assert (use_wide_camera["min"], use_wide_camera["max"], use_wide_camera["default"]) == (0, 1, 1)
  assert use_wide_camera["control"] == "toggle"
  assert use_wide_camera["risk"] == "high"
  assert "재부팅" in use_wide_camera["descr"]
  assert "Reboot" in use_wide_camera["edescr"]

  system = next(category for category in settings["menu"] if category["id"] == "SYSTEM")
  camera = next(group for group in system["groups"] if group["id"] == "SYS_CAMERA")
  assert camera["params"] == ["UseWideCamera"]

  params_keys = PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  assert '{"UseWideCamera", {PERSISTENT, BOOL, "1"}}' in params_keys


def test_driver_monitoring_setting_is_default_on_search_only_and_session_state_is_internal(settings, params):
  by_name = {p["name"]: p for p in params}
  enabled = by_name["DriverMonitoringEnabled"]
  assert (enabled["min"], enabled["max"], enabled["default"]) == (0, 1, 1)
  assert enabled["control"] == "toggle"
  assert enabled["risk"] == "high"
  assert enabled["search_only"] is True
  assert "DM 카메라" in enabled["descr"] and "법규" in enabled["descr"]
  assert "DM camera" in enabled["edescr"] and "laws" in enabled["edescr"]
  assert "DriverMonitoringSessionDisabled" not in by_name

  vehicle = next(category for category in settings["menu"] if category["id"] == "VEHICLE")
  driver_monitoring = next(group for group in vehicle["groups"] if group["id"] == "VEH_DM")
  assert driver_monitoring["params"][:2] == ["DriverMonitoringEnabled", "DriverMonitoringMode"]

  groups, indexed, _ = group_index(settings)
  categories = build_menu_categories(settings, indexed)
  driver_monitoring_view = next(
    group for category in categories for group in category["groups"] if group["id"] == "VEH_DM"
  )
  assert "DriverMonitoringEnabled" in driver_monitoring_view["sections"][0]["items"]
  assert driver_monitoring_view["count"] == sum(
    1 for name in driver_monitoring["params"]
    if not indexed[name].get("detail_parent") and not indexed[name].get("search_only")
  )
  assert enabled in groups[enabled["group"]]

  params_keys = PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  assert '{"DriverMonitoringEnabled", {PERSISTENT, BOOL, "1"}}' in params_keys
  assert '{"DriverMonitoringSessionDisabled", {CLEAR_ON_MANAGER_START | CLEAR_ON_IGNITION_ON, BOOL}}' in params_keys


def test_tpms_position_setting_matches_device_support(params):
  by_name = {p["name"]: p for p in params}
  show_tpms = by_name["ShowTpms"]
  assert (show_tpms["min"], show_tpms["max"], show_tpms["default"]) == (0, 3, 1)
  assert "C4(MICI)는 해당 없음" in show_tpms["descr"]
  assert "Not applicable to C4 (MICI)" in show_tpms["edescr"]

  params_keys = PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  assert '{"ShowTpms", {PERSISTENT, INT, "1"}}' in params_keys


def test_external_hud_brightness_and_orientation_use_catalog_controls(settings, params):
  by_name = {p["name"]: p for p in params}
  brightness = by_name["ClusterHudBrightness"]
  assert (brightness["min"], brightness["max"], brightness["default"]) == (0, 100, 0)
  assert "live_update" not in brightness

  orientation = by_name["ClusterHudOrientation"]
  assert (orientation["min"], orientation["max"], orientation["default"]) == (0, 3, 0)
  assert orientation["control"] == "select"
  assert orientation["descr"].endswith("0: 0도\n1: X\n2: 180도\n3: X")
  assert orientation["options"]["en"] == [
    "0 degrees",
    "Unsupported",
    "180 degrees",
    "Unsupported",
  ]
  panel_layout = by_name["ClusterHudPanelLayout"]
  assert (panel_layout["min"], panel_layout["max"], panel_layout["default"]) == (0, 1, 0)
  assert panel_layout["control"] == "select"
  assert panel_layout["options"]["en"] == [
    "Driving left / info right",
    "Info left / driving right",
  ]
  screen_mode = by_name["ClusterHudScreenMode"]
  assert (screen_mode["min"], screen_mode["max"], screen_mode["default"]) == (-1, 7, 0)
  assert screen_mode["descr"].startswith("-1: 3D 전체화면\n0: 기본(내비/주행 리포트)")
  assert screen_mode["edescr"].startswith("-1: 3D fullscreen\n0: Default (navigation/driving report)")
  assert screen_mode["cdescr"].startswith("-1: 3D全屏\n0: 默认(导航/驾驶报告)")

  display = next(category for category in settings["menu"] if category["id"] == "DISPLAY")
  hud = next(group for group in display["groups"] if group["id"] == "DISP_HUD")
  basic = next(group for group in hud["groups"] if group["id"] == "HUD_BASIC")
  screen = next(group for group in hud["groups"] if group["id"] == "HUD_SCREEN")
  assert basic["params"][:3] == [
    "ClusterHud",
    "ClusterHudBrightness",
    "ClusterHudOrientation",
  ]
  assert screen["params"] == [
    "ClusterHudEncoder",
    "ClusterHudScreenMode",
    "ClusterHudPanelLayout",
    "ClusterHudCameraViewMode",
  ]
  camera_view = by_name["ClusterHudCameraViewMode"]
  assert (camera_view["min"], camera_view["max"], camera_view["default"]) == (0, 4, 0)
  assert camera_view["control"] == "select"
  assert camera_view["options"]["ko"][2:] == ["일반 카메라", "광각 카메라", "속도 자동"]
  assert camera_view["options"]["en"][2:] == ["Narrow camera", "Wide camera", "Speed automatic"]

  params_keys = PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  assert '{"ClusterHudBrightness", {PERSISTENT, INT, "0"}}' in params_keys
  assert '{"ClusterHudOrientation", {PERSISTENT, INT, "0"}}' in params_keys
  assert '{"ClusterHudPanelLayout", {PERSISTENT, INT, "0"}}' in params_keys


def test_cluster_camera_preference_is_in_brightness_and_view(settings, params):
  by_name = {p["name"]: p for p in params}
  camera = by_name["ShowCameraWithCluster"]
  assert (camera["min"], camera["max"], camera["default"], camera["unit"]) == (0, 1, 0, 1)
  assert camera["descr"] == "0: 카메라 미표시(기본)\n1: 카메라 영상 표시"
  assert camera["edescr"] == "0: Hide camera (default)\n1: Show camera video"
  assert camera["cdescr"] == "0: 不显示摄像头（默认）\n1: 显示摄像头画面"

  display = next(category for category in settings["menu"] if category["id"] == "DISPLAY")
  brightness = next(group for group in display["groups"] if group["id"] == "DISP_BRIGHT")
  assert brightness["params"] == [
    "ShowCustomBrightness",
    "ShowModelView",
    "ShowCameraWithCluster",
  ]

  params_keys = PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  assert '{"ShowCameraWithCluster", {PERSISTENT, INT, "0"}}' in params_keys


def test_carrot_radar_is_fixed_without_mode_or_sensitivity(settings, params):
  by_name = {p["name"]: p for p in params}
  for removed_name in (
    "RadarLeadModelMode",
    "RadarDPathMode",
    "RadarMotionMode",
    "CarrotRadarMode",
    "CarrotRadarCutInSensitivity",
  ):
    assert removed_name not in by_name
  vehicle = next(category for category in settings["menu"] if category["id"] == "VEHICLE")
  radar = next(group for group in vehicle["groups"] if group["id"] == "VEH_RADAR")
  assert radar["params"] == [
    "EnableRadarTracks",
    "RadarTrackFlip",
    "EnableCornerRadar",
  ]


def test_parameter_names_are_unique(params):
  names = [p["name"] for p in params]
  assert len(names) == len(set(names))


def test_every_declared_display_unit_is_one_the_ui_knows(params):
  declared = {p["name"]: p["display_unit"] for p in params if "display_unit" in p}
  assert declared, "the migration should have left declarations behind"
  unknown = {name: unit for name, unit in declared.items() if unit not in KNOWN_DISPLAY_UNITS}
  assert unknown == {}


def test_every_declared_control_is_one_the_ui_knows(params):
  declared = {p["name"]: p["control"] for p in params if "control" in p}
  assert declared
  unknown = {name: kind for name, kind in declared.items() if kind not in KNOWN_CONTROL_KINDS}
  assert unknown == {}


# "raw" is the absence of a unit, so declaring it only adds noise.
def test_no_parameter_declares_the_empty_unit(params):
  assert [p["name"] for p in params if p.get("display_unit") == "raw"] == []


def test_steer_ratio_rate_has_safe_catalog_and_registry_defaults(params):
  by_name = {p["name"]: p for p in params}
  steer_ratio_rate = by_name["SteerRatioRate"]
  assert (steer_ratio_rate["min"], steer_ratio_rate["max"], steer_ratio_rate["default"]) == (30, 200, 100)
  assert steer_ratio_rate["display_unit"] == "percent"

  params_keys = PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  assert '{"SteerRatioRate", {PERSISTENT, INT, "100"}}' in params_keys


def test_control_overrides_land_on_parameters_that_need_them(params):
  by_name = {p["name"]: p for p in params}
  # Range inference would make these sliders, which is why they are pinned.
  assert by_name["ShowPathMode"]["control"] == "select"
  assert by_name["SoundLanguageSetting"]["control"] == "select"


def test_declared_options_cover_every_value_in_range(params):
  """Labels are indexed from `min`, so a short list silently blanks a choice."""
  declared = {p["name"]: p for p in params if "options" in p}
  assert declared

  for name, p in declared.items():
    span = p["max"] - p["min"] + 1
    for language, labels in p["options"].items():
      assert language in {"ko", "en", "zh", "zh-tw"}, f"{name}: unexpected language {language}"
      assert isinstance(labels, list), f"{name}.{language} must be a list"
      assert len(labels) == span, f"{name}.{language} has {len(labels)} labels for {span} values"
      assert all(isinstance(label, str) and label for label in labels), f"{name}.{language} has an empty label"


def test_option_labels_exist_in_every_supported_language(params):
  for p in (p for p in params if "options" in p):
    assert set(p["options"]) == {"ko", "en", "zh", "zh-tw"}, p["name"]


def test_every_declared_risk_is_one_the_ui_knows(params):
  declared = {p["name"]: p["risk"] for p in params if "risk" in p}
  unknown = {name: level for name, level in declared.items() if level not in KNOWN_RISK_LEVELS}
  assert unknown == {}


def test_live_geometry_has_zero_default_and_no_enable_switch(settings, params):
  from openpilot.selfdrive.carrot.server.services.params import clamp_numeric
  by_name = {p['name']: p for p in params}
  assert 'CenterToFrontRatioEnabled' not in by_name
  ratio = by_name['CenterToFrontRatio']
  assert (ratio['min'], ratio['nonzero_min'], ratio['max'], ratio['default'], ratio['unit']) == (0, 31, 69, 0, 1)
  assert ratio['display_unit'] == 'percent'
  assert not ratio.get('detail_parent') and not ratio.get('hidden_brands')
  assert ratio['risk'] == 'high'
  keys = PARAMS_KEYS_PATH.read_text(encoding='utf-8')
  assert '{"CenterToFrontRatio", {PERSISTENT, INT, "0"}}' in keys
  assert '{"CenterToFrontRatioEnabled", {PERSISTENT, BOOL}}' in keys  # Migration only, no recreated default.
  categories = build_menu_categories(settings, by_name)
  section = next(section for category in categories for group in category['groups'] for section in group['sections']
                 if 'SteerActuatorDelay' in section['items'])
  assert section['items'].index(ratio['name']) == section['items'].index('SteerActuatorDelay') + 1
  for raw, expected in ((0, 0), (1, 31), (30, 31), (40, 40), (60, 60), (99, 69)):
    assert clamp_numeric(raw, ratio) == expected
  assert clamp_numeric(1, by_name['SteerActuatorDelay']) == 1
  assert '재시작 없이' in ratio['descr']
  assert 'without restarting' in ratio['edescr']
  assert set(ratio['zero_label']) == {'ko', 'en', 'zh', 'zh-tw'}


def test_declared_nonzero_min_and_zero_labels_are_well_formed(params):
  for item in params:
    if 'nonzero_min' in item:
      assert item['min'] == item['default'] == 0
      assert 0 < item['nonzero_min'] <= item['max']
      assert set(item['zero_label']) == {'ko', 'en', 'zh', 'zh-tw'}
