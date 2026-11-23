"""Device-specific presentation settings shared by the native UI and desktop editor."""
from functools import cache
import json
from pathlib import Path

PROFILE_PATH = Path(__file__).with_name("layout_profile.json")
MENU = {
  "c3x": ("device", "network", "toggles", "software", "firehose", "developer", "egpu"),
  "c4": ("toggles", "network", "device", "language", "pair", "firehose", "egpu", "developer", "formosalink"),
}
# Minimum, maximum and stock value in native layout pixels.
LIMITS = {
  "c3x": {"menu_font": (42, 72, 65), "menu_spacing": (85, 110, 110), "hud_x": (0, 180, 0), "hud_y": (-100, 0, 0),
          "speed_font": (80, 138, 120), "speed_x": (-12, 175, 0), "speed_y": (-18, 16, 0),
          "cruise_font": (38, 72, 60), "cruise_x": (-175, 32, 0), "cruise_y": (-16, 16, 0)},
  "c4": {"menu_font": (40, 70, 64), "menu_spacing": (8, 38, 20), "hud_x": (-6, 44, 0), "hud_y": (-22, 4, 0),
         "speed_font": (52, 88, 80), "speed_x": (-10, 164, 0), "speed_y": (-9, 9, 0),
         "cruise_font": (28, 48, 40), "cruise_x": (-185, 16, 0), "cruise_y": (-8, 8, 0)},
}


# Scene design coordinates are percentages of the preview viewport.
SCENE_LIMITS = {"scene_style": (0, 2, 0)}
for layer, color in {"vehicle": 0xdde5ec, "lane": 0xf5f2d8, "path": 0x38cfc6, "map": 0x227df2}.items():
  SCENE_LIMITS.update({f"{layer}_size": (50, 150, 100), f"{layer}_color": (0, 0xffffff, color),
                       f"{layer}_x": (-30, 30, 0), f"{layer}_y": (-30, 30, 0)})
for fields in LIMITS.values():
  fields.update(SCENE_LIMITS)


def defaults():
  return {"version": 1, "devices": {key: {"order": list(order), **{field: spec[2] for field, spec in LIMITS[key].items()}}
                                     for key, order in MENU.items()}}


def validate(profile):
  if not isinstance(profile, dict) or profile.keys() != {"version", "devices"} or type(profile["version"]) is not int or profile["version"] != 1:
    raise ValueError("Unsupported layout version")
  devices = profile["devices"]
  if not isinstance(devices, dict) or devices.keys() != MENU.keys():
    raise ValueError("Both device layouts are required")
  for key, expected in MENU.items():
    values = devices[key]
    if isinstance(values, dict) and not SCENE_LIMITS.keys() & values.keys():
      values.update({k: spec[2] for k, spec in SCENE_LIMITS.items()})
    if not isinstance(values, dict) or values.keys() != {"order", *LIMITS[key]}:
      raise ValueError(f"Invalid {key} layout fields")
    order = values["order"]
    if not isinstance(order, list) or not all(isinstance(item, str) for item in order) or sorted(order) != sorted(expected):
      raise ValueError(f"Invalid {key} menu order")
    for field, (low, high, _) in LIMITS[key].items():
      if type(values[field]) is not int or not low <= values[field] <= high:
        raise ValueError(f"Invalid {key} {field}")
  return profile


@cache
def _load():
  try:
    return validate(json.loads(PROFILE_PATH.read_text(encoding="utf-8")))
  except (ValueError, OSError):
    return defaults()


def device_layout(device):
  return _load()["devices"][device]


def large_display_layout():
  from openpilot.system.hardware import HARDWARE, PC
  # C3 and C3X use the same renderer. Only C3X has an editable profile.
  if not PC and HARDWARE.get_device_type() != "tizi":
    return defaults()["devices"]["c3x"]
  return device_layout("c3x")
