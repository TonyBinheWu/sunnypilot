"""Typed native settings catalog and fail-closed rule evaluation."""
import hashlib
import math

from openpilot.sunnypilot.formosalink.protocol import canonical
from openpilot.sunnypilot.formosalink.setting_labels import localize

LOCAL_ONLY = {
  "GsmDataEnabled", "FormosaLinkRemoteWeb",
  "AdbEnabled", "SshEnabled", "GithubUsername", "GithubSshKeys", "EnableGithubRunner", "EnableCopyparty",
  "JoystickDebugMode", "LateralManeuverMode", "LongitudinalManeuverMode", "OffroadMode", "DeviceBootMode",
  "SunnylinkUpdateNow", "SunnylinkInstallUpdate", "FormosaLinkEnabled", "FormosaLinkRemoteSettings",
  "IsOffroad", "DoReboot", "DoShutdown", "DoUninstall", "OnroadCycleRequested", "ParamsVersion", "FormosaLinkSettingsVersion",
  "LastUpdateException", "HasAcceptedTerms", "HasAcceptedTermsSP", "CompletedTrainingVersion",
  "RecordFront", "RecordAudio",
}


def revision(value):
  return hashlib.sha256(canonical(value)).hexdigest()


def rule_value(rule, values, capabilities, offroad):
  kind = rule.get("type")
  if kind in ("offroad_only", "not_engaged"):
    return offroad
  if kind == "not":
    result = rule_value(rule.get("condition", {}), values, capabilities, offroad)
    return None if result is None else not result
  if kind in ("all", "any"):
    results = [rule_value(x, values, capabilities, offroad) for x in rule.get("conditions", [])]
    if not results:
      return None
    if kind == "all":
      return False if False in results else None if None in results else True
    return True if True in results else None if None in results else False
  if kind == "capability":
    source, key = capabilities, rule.get("field")
  elif kind in ("param", "param_compare"):
    source, key = values, rule.get("key")
  else:
    return None
  if key not in source or source[key] is None:
    return None
  if kind != "param_compare":
    expected = rule.get("equals")
    compatible = type(source[key]) is type(expected) or type(source[key]) in (int, float) and type(expected) in (int, float)
    return compatible and source[key] == expected
  left, right = source[key], rule.get("value")
  if type(left) not in (int, float) or type(right) not in (int, float):
    return None
  operations = {">": lambda: left > right, ">=": lambda: left >= right, "<": lambda: left < right,
                "<=": lambda: left <= right, "==": lambda: left == right, "!=": lambda: left != right}
  return operations[rule["op"]]() if rule.get("op") in operations else None


def rules_pass(rules, values, capabilities, offroad):
  return all(rule_value(rule, values, capabilities, offroad) is True for rule in rules or [])


def native_items(schema):
  """Carry parent conditions down; never expose rule references as writable keys."""
  def visit(item, group, parents, remote):
    conditions = parents + item.get("visibility", []) + item.get("enablement", [])
    if "key" in item and "widget" in item:
      yield item, group, conditions, remote
    for child in item.get("sub_items", []):
      yield from visit(child, group, conditions, remote)
  for panel in schema.get("panels", []):
    group = panel.get("label", panel.get("id", "Settings"))
    remote = panel.get("remote_configurable") is True
    for section in [panel, *panel.get("sections", [])]:
      parents = panel.get("visibility", []) + panel.get("enablement", [])
      if section is not panel:
        parents += section.get("visibility", []) + section.get("enablement", [])
      for item in section.get("items", []):
        yield from visit(item, group, parents, remote)
      for sub in section.get("sub_panels", []):
        inherited = parents + sub.get("visibility", []) + sub.get("enablement", [])
        if sub.get("trigger_condition"):
          inherited += [sub["trigger_condition"]]
        for item in sub.get("items", []):
          yield from visit(item, group, inherited, remote)
  for brand, definition in schema.get("vehicle_settings", {}).items():
    for item in definition.get("items", []) if isinstance(definition, dict) else definition:
      yield from visit(item, "Vehicle", [{"type":"capability","field":"brand","equals":brand}], True)


def catalog(schema, values, types, capabilities, offroad, translate=lambda text: {"zh-TW":text,"en":text,"ja":text}):
  result = {}
  native_translate = translate
  def translate(text):
    return localize(text,native_translate)
  for item, group, conditions, remote in native_items(schema):
    key = item["key"]
    if key not in types or key in LOCAL_ONLY or "sunnylink" in key.lower():
      continue
    widget = item["widget"]
    entry = {"key":key, "group":translate(group), "title":translate(item.get("title", key)),
             "description":translate(item.get("description", "")), "type":types[key], "widget":widget,
             "enabled":bool(remote and offroad and widget != "info" and rules_pass(conditions, values, capabilities, offroad)),
             "unit":item.get("unit", "")}
    for name in ("min", "max", "step"):
      if name in item:
        entry[name] = item[name]
    if item.get("options"):
      entry["options"] = []
      for option in item["options"]:
        value = option["value"]
        if key == "TorqueControlTune" and value == "" and types[key] == "FLOAT":
          value = 0.0
        entry["options"].append({"value":value, "label":translate(option.get("label", str(value))),
          "enabled":rules_pass(option.get("enablement"), values, capabilities, offroad)})
    elif widget not in ("toggle", "info") and not all(name in entry for name in ("min", "max", "step")):
      entry["enabled"] = False
    result[key] = entry
  return list(result.values())


def validate_setting(entry, value):
  if not entry.get("enabled") or entry.get("key") in LOCAL_ONLY or "sunnylink" in entry.get("key", "").lower():
    raise ValueError("setting_unavailable")
  if entry.get("key")=="NavDestination":
    from openpilot.sunnypilot.formosalink.navigation import destination,encode
    return encode(destination(value))
  kind = entry["type"]
  if kind == "BOOL":
    if type(value) is not bool:
      raise ValueError("invalid_type")
  elif kind in ("INT", "FLOAT"):
    if type(value) not in (int, float) or not math.isfinite(value) or (kind == "INT" and type(value) is not int):
      raise ValueError("invalid_type")
  elif kind == "STRING":
    if not isinstance(value, str) or len(value) > 256 or any(ord(c) < 32 for c in value):
      raise ValueError("invalid_type")
  else:
    raise ValueError("unsupported_type")
  if "options" in entry:
    if not any(option["enabled"] and type(option["value"]) is not bool and option["value"] == value for option in entry["options"]):
      raise ValueError("invalid_option")
  elif kind in ("INT", "FLOAT"):
    minimum, maximum, step = entry["min"], entry["max"], entry["step"]
    if not minimum <= value <= maximum or step <= 0 or not math.isclose((value-minimum)/step, round((value-minimum)/step), abs_tol=1e-6):
      raise ValueError("out_of_range")
  return float(value) if kind == "FLOAT" else value
