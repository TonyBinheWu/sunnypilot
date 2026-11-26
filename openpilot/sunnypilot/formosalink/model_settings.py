"""Owner-facing selections use the same per-runner slots and download queue as the native UI."""
import json
import math
import re
import time

from openpilot.sunnypilot.models.model_name import DEFAULT_BIG_MODEL, DEFAULT_MODEL


def labels(zh, en, ja):
  return {"zh-TW": zh, "en": en, "ja": ja}


SLOTS = {
  "DrivingModelSmall": ("", "ModelManager_ActiveBundle", DEFAULT_MODEL,
                       labels("小模型（內建處理器）", "Small model (onboard processor)", "小型モデル（内蔵プロセッサ）")),
  "DrivingModelBig": ("_Chestnut", "ModelManager_ActiveBundleChestnut", DEFAULT_BIG_MODEL,
                     labels("大模型（Chestnut）", "Big model (Chestnut)", "大型モデル（Chestnut）")),
}
ACTION = "DrivingModelAction"
QUEUE = "ModelManager_DownloadRef"
GROUP = labels("模型", "Models", "モデル")
HELP = labels("儲存後車機會下載並驗證檔案。請以已設定模型和下載結果確認完成。",
              "Saving asks the device to download and verify the files. Check the configured model and transfer result.",
              "保存すると本体がダウンロードと検証を行います。設定済みモデルと結果を確認してください。")
ACTIONS = {"refresh": labels("重新取得模型清單", "Refresh model lists", "モデル一覧を更新"),
           "cancel": labels("取消下載", "Cancel download", "ダウンロードを中止"),
           "clear": labels("清除未使用的模型快取", "Clear unused model files", "未使用のモデルキャッシュを削除")}


def option(value, title, enabled=True):
  return {"value": value, "label": title, "enabled": enabled}


def entry(key, title, options, enabled):
  return {"key": key, "type": "STRING", "widget": "option", "group": GROUP, "title": title, "description": HELP,
          "enabled": enabled, "options": options}


class ModelSettings:
  def __init__(self, params, selector_version, progress):
    self.params = params
    self.selector_version = selector_version
    self.progress = progress
    self.action = None
    self.action_at = 0.0
    self.previous_result = None

  def catalog_for(self, suffix):
    # Read the manager's own manifest cache. Listing names must never parse/download artifacts or write chunk manifests.
    cache = self.params.get("ModelManager_ModelsCache" + suffix) or {}
    models = {}
    for bundle in reversed(cache.get("bundles", []) if isinstance(cache, dict) else []):
      if not isinstance(bundle, dict) or str(bundle.get("minimum_selector_version")) != str(self.selector_version):
        continue
      ref, name = bundle.get("ref"), bundle.get("display_name")
      if isinstance(ref, str) and re.fullmatch("[a-f0-9]{40}", ref) and isinstance(name, str) and name.strip():
        models[ref] = name[:240]
    return models

  @staticmethod
  def slot(key):
    return key.split("Page", 1)[0]

  def handles(self, key):
    return self.slot(key) in SLOTS or key == ACTION

  def selected(self, active_key):
    bundle = self.params.get(active_key)
    if isinstance(bundle, dict) and bundle.get("minimumSelectorVersion") == self.selector_version and isinstance(bundle.get("ref"), str):
      return bundle["ref"], str(bundle.get("displayName") or bundle["ref"])[:240]
    return "", ""

  def capture(self, parked):
    pending = self.params.get(QUEUE)
    clearing = self.params.get_bool("ModelManager_ClearCache")
    progress = self.progress()
    running = bool(progress and progress.ref and str(progress.status) == "downloading")
    busy = bool(pending or running or clearing)
    entries, values, names, configured = [], {}, {}, []
    for key, (suffix, active_key, default, title) in SLOTS.items():
      active, name = self.selected(active_key)
      models = self.catalog_for(suffix)
      names.update(models)
      configured.append(name or default)
      options = [option(ref, labels(name, name, name)) for ref, name in models.items()]
      stock = option("", labels(f"{default}（預設）", f"{default} (default)", f"{default}（標準）"))
      # Each signed option list has a 128-item wire limit. Keep every model selectable as manifests grow.
      for start in range(0, max(1, len(options)), 127):
        page = start // 127 + 1
        field = key if page == 1 else f"{key}Page{page}"
        heading = title if len(options) <= 127 else {k: f"{v} ({page})" for k, v in title.items()}
        entries.append(entry(field, heading, [stock, *options[start:start + 127]], parked and not busy))
        values[field] = active
    options = [option("", labels("選擇操作", "Choose an action", "操作を選択"), False)]
    options.extend(option(action, title, bool(pending) if action == "cancel" else not busy) for action, title in ACTIONS.items())
    maintenance = entry(ACTION, labels("模型管理", "Model maintenance", "モデル管理"), options, parked)
    maintenance["pending_ref"] = pending or ""
    maintenance["description"] = labels("重新取得清單、取消傳輸，或清理目前未使用的模型檔案。",
                                        "Refresh the lists, cancel a transfer, or remove unused model files.",
                                        "一覧を更新、転送を中止、または未使用のモデルファイルを削除できます。")
    entries.append(maintenance)
    values[ACTION] = ""
    result = self.params.get("ModelManager_LastDownload") or {}
    if self.action and (pending or self.previous_result != result or time.monotonic() - self.action_at > 120):
      self.action = None
    status = result.get("status", "idle") if isinstance(result, dict) else "idle"
    ref = result.get("ref", "") if isinstance(result, dict) else ""
    percent = None
    if pending:
      ref, status = pending, "queued"
      if running and progress.ref == ref:
        artifacts = [m.artifact.downloadProgress for m in progress.models if m.artifact.fileName]
        if artifacts:
          status = "verifying" if any(str(a.status) == "verifying" for a in artifacts) else "downloading"
          percent = round(sum(max(0, min(100, a.progress)) for a in artifacts if math.isfinite(a.progress)) / len(artifacts))
    if self.action == "refresh" and not pending:
      refreshed = all((self.params.get("ModelManager_LastSyncTime" + suffix) or 0) > 0 for suffix, _, _, _ in SLOTS.values())
      status = "refreshed" if refreshed else "refresh_failed" if time.monotonic() - self.action_at > 30 else "refreshing"
    elif self.action == "clear" and not pending:
      status = "cleared"
    elif self.action == "cancel" and not pending:
      status = "cancelling" if running else "cancelled"
    elif self.action == "default" and not pending:
      status = "default_restored"
    if clearing:
      status = "clearing"
    detail = {"configured": configured, "status": status, "name": names.get(ref, "") if pending or not self.action else "", "percent": percent}
    return entries, values, json.dumps(detail, ensure_ascii=False, separators=(",", ":"))

  def apply(self, key, value, expected, expected_pending):
    pending = self.params.get(QUEUE)
    if (pending or "") != expected_pending:
      raise ValueError("conflict")
    previous = self.params.get("ModelManager_LastDownload") or {}
    if key == ACTION and value == "cancel":
      if not pending:
        raise ValueError("conflict")
      self.params.remove(QUEUE)
      if self.params.get(QUEUE) == pending:
        raise ValueError("write_failed")
      self.action, self.action_at, self.previous_result = value, time.monotonic(), previous
      return
    if pending or self.params.get_bool("ModelManager_ClearCache"):
      raise ValueError("conflict")
    if key == ACTION:
      if value == "refresh":
        for suffix, _, _, _ in SLOTS.values():
          self.params.put("ModelManager_LastSyncTime" + suffix, 0, block=True)
      elif value == "clear":
        self.params.put("ModelManager_ClearCache", True, block=True)
      else:
        raise ValueError("invalid_option")
      self.action, self.action_at, self.previous_result = value, time.monotonic(), previous
      return
    self.action = None
    suffix, active_key, _, _ = SLOTS[self.slot(key)]
    if self.selected(active_key)[0] != expected:
      raise ValueError("conflict")
    if value == "":
      self.params.remove(active_key)
      if self.params.get(active_key) is not None:
        raise ValueError("write_failed")
      self.action, self.action_at, self.previous_result = "default", time.monotonic(), previous
    elif value in self.catalog_for(suffix):
      self.params.put(QUEUE, value, block=True)
      if self.params.get(QUEUE) != value:
        result = self.params.get("ModelManager_LastDownload") or {}
        if result == previous or result.get("ref") != value:
          raise ValueError("write_failed")
    else:
      raise ValueError("invalid_option")
