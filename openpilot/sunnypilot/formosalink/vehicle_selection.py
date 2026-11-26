"""Expose the installed native vehicle picker through parked settings sync."""
import json
from pathlib import Path

from openpilot.common.basedir import BASEDIR

KEY = "CarPlatformBundle"
# The native car_list.json is a symlink to this file in the pinned opendbc checkout.
CAR_LIST = Path(BASEDIR) / "opendbc_repo/opendbc/sunnypilot/car/car_list.json"


def load_vehicles():
  try:
    with CAR_LIST.open(encoding="utf-8") as source:
      return json.load(source)
  except (OSError, ValueError):
    return {}


def selected_name(bundle, vehicles):
  if not isinstance(bundle, dict) or not isinstance(platform := bundle.get("platform"), str) or not platform:
    return ""
  name = bundle.get("name")
  if isinstance(name, str) and vehicles.get(name, {}).get("platform") == platform:
    return name
  # Older bundles may only contain the platform ID, shared by several trims.
  matches = [name for name, data in vehicles.items() if data["platform"] == platform
             and (not bundle.get("model") or data.get("model") == bundle["model"])]
  return matches[0] if len(matches) == 1 else platform


def entry(vehicles, offroad):
  return {
    "key": KEY, "type": "STRING", "widget": "option", "enabled": offroad, "unit": "",
    "group": {"zh-TW": "車輛", "en": "Vehicle", "ja": "車両"},
    "title": {"zh-TW": "選擇車型", "en": "Select vehicle", "ja": "車種を選択"},
    "description": {
      "zh-TW": "請選擇與實車年份及駕駛輔助配備相符的車型。儲存後，下次啟動行程時會使用這個選擇。",
      "en": "Match the model year and driver assistance equipment of your vehicle. Your selection takes effect on the next drive.",
      "ja": "実車の年式と運転支援装備に合う車種を選んでください。保存した設定は次の走行開始時に反映されます。",
    },
    "vehicles": {name: data["platform"] for name, data in vehicles.items()},
  }
