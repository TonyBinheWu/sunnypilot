"""Bounded settings-sync wire format, independent of native openpilot libraries."""
import math
import re
import time
import uuid

from openpilot.sunnypilot.formosalink.settings import revision

MAX_MANAGEMENT_BYTES = 524288
MANAGEMENT_FRESH_SECONDS = 10
COMMAND_TTL = 20
REASONS = {"applied", "offroad_required", "local_disabled", "conflict", "expired", "setting_unavailable", "invalid_type",
           "invalid_option", "out_of_range", "unsupported_type", "write_failed", "wrong_session", "wrong_device"}


def valid_hash(value):
  return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def scalar(value):
  return value is None or type(value) in (bool, str, int, float) and (not isinstance(value, str) or len(value) <= 4096) and (
    type(value) not in (int, float) or math.isfinite(value))


def validate_snapshot(data):
  fields = {"version", "session", "sampled_at", "offroad", "remote_enabled", "catalog_revision", "revision", "catalog", "values", "info", "receipts"}
  if not isinstance(data, dict) or set(data) != fields or type(data["version"]) is not int or data["version"] != 1:
    raise ValueError("invalid settings snapshot")
  uuid.UUID(str(data["session"]))
  if type(data["sampled_at"]) not in (int, float) or not math.isfinite(data["sampled_at"]) or abs(time.time()-data["sampled_at"]) > 90:
    raise ValueError("expired settings snapshot")
  if type(data["offroad"]) is not bool or type(data["remote_enabled"]) is not bool or not valid_hash(data["catalog_revision"]):
    raise ValueError("invalid settings state")
  if not isinstance(data["values"], dict) or len(data["values"]) > 256 or any(not isinstance(key, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9]{0,95}", key) or not scalar(value) for key, value in data["values"].items()):
    raise ValueError("invalid settings values")
  if data["revision"] != revision({"catalog":data["catalog_revision"], "values":data["values"]}):
    raise ValueError("settings revision mismatch")
  catalog = data["catalog"]
  if catalog is not None:
    if not isinstance(catalog, list) or len(catalog) > 256 or any(not isinstance(x, dict) or not isinstance(x.get("key"), str) for x in catalog):
      raise ValueError("invalid settings catalog")
    if len({x["key"] for x in catalog}) != len(catalog):
      raise ValueError("duplicate catalog keys")
    for item in catalog:
      if not isinstance(item, dict) or not isinstance(item.get("key"), str) or item["key"] not in data["values"]:
        raise ValueError("invalid catalog key")
      if item.get("type") not in ("BOOL", "INT", "FLOAT", "STRING") or item.get("widget") not in ("toggle", "option", "multiple_button", "info", "navigation") or type(item.get("enabled")) is not bool:
        raise ValueError("invalid catalog type")
      for name in ("title", "description", "group"):
        labels = item.get(name)
        if not isinstance(labels, dict) or set(labels) != {"zh-TW", "en", "ja"} or any(not isinstance(v, str) or len(v) > 4096 for v in labels.values()):
          raise ValueError("invalid catalog labels")
      if "options" in item and (not isinstance(item["options"], list) or len(item["options"]) > 128):
        raise ValueError("invalid catalog options")
      for option in item.get("options", []):
        if not isinstance(option, dict) or set(option) != {"value", "label", "enabled"} or not scalar(option["value"]) or type(option["enabled"]) is not bool:
          raise ValueError("invalid option")
        if not isinstance(option["label"], dict) or set(option["label"]) != {"zh-TW", "en", "ja"} or any(not isinstance(v, str) or len(v)>4096 for v in option["label"].values()):
          raise ValueError("invalid option label")
      for bound in ("min", "max", "step"):
        if bound in item and (type(item[bound]) not in (int, float) or not math.isfinite(item[bound])):
          raise ValueError("invalid range")
    if revision(catalog) != data["catalog_revision"]:
      raise ValueError("catalog revision mismatch")
  if not isinstance(data["info"], dict) or len(data["info"]) > 64:
    raise ValueError("invalid device information")
  for key, value in data["info"].items():
    if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", key) or not (scalar(value) or isinstance(value, list) and len(value) <= 32 and all(scalar(v) for v in value)):
      raise ValueError("invalid device information field")
  if not isinstance(data["receipts"], list) or len(data["receipts"]) > 32:
    raise ValueError("invalid command receipts")
  for receipt in data["receipts"]:
    if not isinstance(receipt, dict) or set(receipt) != {"id", "status", "reason"} or receipt["status"] not in ("applied", "rejected") or receipt["reason"] not in REASONS:
      raise ValueError("invalid command receipt")
    uuid.UUID(receipt["id"])
  return data
