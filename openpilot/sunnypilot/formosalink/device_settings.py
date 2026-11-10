"""Device-authoritative settings capture and guarded single-parameter writes."""
import json
import math
import time
import uuid

from openpilot.sunnypilot.formosalink.settings import LOCAL_ONLY, catalog, native_items, revision, validate_setting


class SettingsProvider:
  """Injected I/O permits testing the same apply path without native device access."""
  def __init__(self, params, schema, capabilities, guard, info=lambda: {}, translate=None):
    self.params, self.schema, self.capabilities, self.guard, self.info = params, schema, capabilities, guard, info
    self.translate = translate
    self.session = str(uuid.uuid4())
    self._offroad = False

  def capture(self):
    offroad = self.guard()
    if offroad and not self._offroad:
      self.session = str(uuid.uuid4())
    self._offroad = offroad
    values, types = {}, {}
    keys = {item["key"] for item, _, _, _ in native_items(self.schema)}
    def referenced(node):
      if isinstance(node, dict):
        if node.get("type") in ("param", "param_compare") and "key" in node:
          keys.add(node["key"])
        for value in node.values():
          referenced(value)
      elif isinstance(node, list):
        for value in node:
          referenced(value)
    referenced(self.schema)
    for key in keys:
      if key in LOCAL_ONLY:
        continue
      try:
        kind = self.params.get_type(key).name
        if kind not in ("BOOL", "INT", "FLOAT", "STRING"):
          continue
        value = self.params.get(key, return_default=True)
        if value is None:
          value = {"BOOL":False,"INT":0,"FLOAT":0.0,"STRING":""}[kind]
        if type(value) not in (bool, int, float, str) or isinstance(value, str) and len(value) > 4096:
          continue
        if type(value) in (float, int) and not math.isfinite(value):
          continue
        values[key], types[key] = value, kind
      except Exception as exc:
        if isinstance(exc,(KeyError,ValueError,OSError,RuntimeError)) or type(exc).__name__=="UnknownKeyName":
          continue
        raise
    entries = catalog(self.schema, values, types, self.capabilities(), offroad,
                      **({"translate":self.translate} if self.translate else {}))
    published = {item["key"]:values[item["key"]] for item in entries}
    catalog_hash = revision(entries)
    return {"version":1,"session":self.session,"sampled_at":time.time(),"offroad":offroad,
            "remote_enabled":self.allowed(), "catalog":entries,
            "catalog_revision":catalog_hash,"values":published,
            "revision":revision({"catalog":catalog_hash,"values":published}),"info":self.info(),"receipts":[]}

  def apply(self, command, device_id, deadline):
    receipt = {"id":command.get("id", ""),"status":"rejected","reason":"setting_unavailable"}
    try:
      if set(command) != {"id", "device_id", "session", "expected_revision", "key", "value", "created_at", "expires_at"}:
        raise ValueError("setting_unavailable")
      uuid.UUID(command["id"])
      if command["device_id"] != device_id:
        raise ValueError("wrong_device")
      if not math.isfinite(deadline) or time.monotonic() >= deadline:
        raise ValueError("expired")
      state = self.capture()
      if not state["offroad"]:
        raise ValueError("offroad_required")
      if not state["remote_enabled"]:
        raise ValueError("local_disabled")
      if command["session"] != state["session"]:
        raise ValueError("wrong_session")
      if command["expected_revision"] != state["revision"]:
        raise ValueError("conflict")
      entry = next((item for item in state["catalog"] if item["key"] == command["key"]), None)
      if not entry:
        raise ValueError("setting_unavailable")
      value = validate_setting(entry, command["value"])
      # Re-capture dependencies/capabilities too, not only the selected key.
      latest = self.capture()
      if latest["session"] != state["session"] or latest["revision"] != state["revision"]:
        raise ValueError("conflict")
      # Recheck the hardware/manager guard and local opt-in immediately before I/O.
      if not self.guard():
        raise ValueError("offroad_required")
      if not self.allowed():
        raise ValueError("local_disabled")
      if time.monotonic() >= deadline:
        raise ValueError("expired")
      current = self.params.get(command["key"], return_default=True)
      if current is None:
        current = {"BOOL":False,"INT":0,"FLOAT":0.0,"STRING":""}[entry["type"]]
      if current != state["values"][command["key"]]:
        raise ValueError("conflict")
      self.params.put(command["key"], value, block=True)
      if self.params.get(command["key"], return_default=True) != value:
        raise ValueError("write_failed")
      receipt.update(status="applied", reason="applied")
      self.params.put("FormosaLinkSettingsVersion", str(uuid.uuid4()), block=True)
      self.params.put("ParamsVersion", int(self.params.get("ParamsVersion") or 0)+1, block=True)
    except ValueError as exc:
      from openpilot.sunnypilot.formosalink.management_protocol import REASONS
      receipt["reason"] = str(exc) if str(exc) in REASONS else "setting_unavailable"
    except (OSError, RuntimeError, TypeError, KeyError):
      if receipt["status"] != "applied":
        receipt["reason"] = "write_failed"
    return receipt

  def allowed(self):
    return self.params.get_bool("FormosaLinkEnabled") and self.params.get_bool("FormosaLinkRemoteSettings")


class NativeSettingsProvider(SettingsProvider):
  def __init__(self):
    from openpilot.cereal import messaging
    from openpilot.common.params import Params
    from openpilot.sunnypilot.sunnylink.capabilities import generate_capabilities
    from openpilot.sunnypilot.sunnylink.tools.generate_settings_schema import generate_schema
    from openpilot.sunnypilot.formosalink.device_info import DeviceInformation, NativeTranslations
    self.sm = messaging.SubMaster(["deviceState", "pandaStates"])
    params = Params()
    information = DeviceInformation(self.sm, params)
    super().__init__(params, generate_schema(), lambda: generate_capabilities(params), self.parked,
                     information.capture, NativeTranslations())

  def parked(self):
    from openpilot.sunnypilot.formosalink.telemetry import source_valid
    self.sm.update(0)
    return bool(source_valid(self.sm,"deviceState",2) and source_valid(self.sm,"pandaStates",2)
                and self.params.get_bool("IsOffroad") and not self.sm["deviceState"].started
                and not any(p.ignitionLine or p.ignitionCan for p in self.sm["pandaStates"]))
