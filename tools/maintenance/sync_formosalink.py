"""Synchronize only FormosaLink-owned source and narrow hooks across checkouts."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
OWNED_TREES = ("formosalink", "openpilot/sunnypilot/formosalink")
OWNED_FILES = (".github/workflows/formosalink.yml", "tools/deploy/publish_formosalink_iis.ps1", "tools/maintenance/sync_formosalink.py", "openpilot/system/ui/lib/branding.py", "openpilot/system/ui/widgets/branding.py")
KEY = '    {"FormosaLinkEnabled", {PERSISTENT, BOOL, "0"}},\n'
PREDICATE = '\n\ndef formosalink_enabled(started: bool, params: Params, CP: car.CarParams) -> bool:\n  return params.get_bool("FormosaLinkEnabled")\n'
PROCESS = '  # Optional FormosaPilot companion; telemetry only, independent of sunnylink.\n  PythonProcess("formosalink", "openpilot.sunnypilot.formosalink.agent", formosalink_enabled),\n\n'


def owned_files():
  result = [ROOT / name for name in OWNED_FILES]
  for name in OWNED_TREES:
    result.extend(p for p in (ROOT / name).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
  return sorted(result)


def hook_changes(target):
  changes = {}
  path = target / ".gitattributes"
  text = path.read_text(encoding="utf-8")
  attribute = "formosalink/web/assets/formosapilot-logo.png -filter -diff -merge -text"
  if attribute not in text:
    text = text.rstrip() + "\n\n# Keep the small FormosaLink brand mark available without Git LFS.\n" + attribute + "\n"
  native_attribute = "openpilot/sunnypilot/formosalink/assets/formosapilot-logo.png -filter -diff -merge -text"
  if native_attribute not in text:
    text = text.rstrip() + "\n" + native_attribute + "\n"
  if text != path.read_text(encoding="utf-8"):
    changes[path] = text
  path = target / "openpilot/common/params_keys.h"
  text = path.read_text(encoding="utf-8")
  if '"FormosaLinkEnabled"' not in text:
    anchor = '    {"DongleId", {PERSISTENT, STRING}},\n'
    if text.count(anchor) != 1:
      raise ValueError("Params anchor is ambiguous; review manually")
    changes[path] = text.replace(anchor, anchor + KEY, 1)
  elif KEY.strip() not in text:
    raise ValueError("existing FormosaLink parameter differs; review manually")
  text = changes.get(path,text)
  for key,kind,default in (("FormosaLinkRemoteSettings","BOOL","0"),("FormosaLinkSettingsVersion","STRING",""),("GsmDataEnabled","BOOL","1")):
    if '"'+key+'"' not in text:
      flags = "PERSISTENT | BACKUP" if key == "GsmDataEnabled" else "PERSISTENT"
      text = text.replace(KEY, KEY+'    {"'+key+'", {'+flags+', '+kind+', "'+default+'"}},\n',1)
  if text != path.read_text(encoding="utf-8"):
    changes[path] = text
  path = target / "openpilot/selfdrive/ui/ui.py"
  text = path.read_text(encoding="utf-8")
  hook = "    from openpilot.sunnypilot.formosalink.ui_sync import tick as formosalink_ui_tick\n    formosalink_ui_tick()\n"
  if hook not in text:
    anchor = "    ui_state.update()\n"
    if text.count(anchor)!=1:
      raise ValueError("UI update anchor is ambiguous")
    text = text.replace(anchor,anchor+hook,1)
    changes[path] = text
  path = target / "openpilot/system/manager/process_config.py"
  text = path.read_text(encoding="utf-8")
  if "def formosalink_enabled(" not in text:
    anchor = "\n\ndef iscar("
    if text.count(anchor) != 1:
      raise ValueError("manager predicate anchor is ambiguous")
    text = text.replace(anchor, PREDICATE + anchor, 1)
  elif PREDICATE.strip() not in text:
    raise ValueError("existing FormosaLink predicate differs; review manually")
  if 'PythonProcess("formosalink"' not in text:
    anchor = "  # sunnylink <3\n"
    if text.count(anchor) != 1:
      raise ValueError("manager process anchor is ambiguous")
    text = text.replace(anchor, PROCESS + anchor, 1)
  elif PROCESS.strip() not in text:
    raise ValueError("existing FormosaLink process differs; review manually")
  if text != path.read_text(encoding="utf-8"):
    changes[path] = text
  # Keep independent QR pairing next to the native device pairing entries.
  path = target / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/device.py"
  text = path.read_text(encoding="utf-8")
  import_line = "from openpilot.sunnypilot.formosalink.ui import formosalink_button\n"
  text = text.replace(import_line, "")
  anchor = "from openpilot.selfdrive.ui.layouts.settings.device import DeviceLayout\n"
  if text.count(anchor) != 1:
    raise ValueError("C3X device import anchor is ambiguous")
  text = text.replace(anchor, anchor + import_line, 1)
  if "      formosalink_button()," not in text:
    anchor = "      self._pair_device_btn,\n"
    if text.count(anchor) != 1:
      raise ValueError("C3X pairing entry anchor is ambiguous")
    text = text.replace(anchor, anchor + "      LineSeparator(),\n      formosalink_button(),\n", 1)
  if text != path.read_text(encoding="utf-8"):
    changes[path] = text
  path = target / "openpilot/selfdrive/ui/sunnypilot/mici/layouts/settings.py"
  text = path.read_text(encoding="utf-8")
  hook = "    from openpilot.sunnypilot.formosalink.ui import add_mici_pair_button\n    add_mici_pair_button(self._scroller)\n"
  if hook.strip() not in text:
    anchor = "    self._scroller.add_widget(self._language_button)\n"
    if text.count(anchor) != 1:
      raise ValueError("C4 pairing entry anchor is ambiguous")
    text = text.replace(anchor, anchor + hook, 1)
  brand_import = "from openpilot.sunnypilot.formosalink.brand_ui import FormosaPilotPanel, LOGO_ASSET\n"
  def insert_once(source, anchor, addition):
    if addition in source:
      return source
    if source.count(anchor) != 1:
      raise ValueError("FormosaPilot brand anchor is ambiguous; review manually")
    return source.replace(anchor, addition + anchor, 1)

  text = insert_once(text, "from openpilot.selfdrive.ui.mici.layouts.settings import settings as OP\n", brand_import)
  text = insert_once(text, "class SunnylinkBigButton(SettingsBigButton):",
                     "class FormosaBigButton(SettingsBigButton):\n  def _get_label_font_size(self):\n    return 36\n\n\n")
  text = insert_once(text, "    items = self._scroller._items.copy()\n",
                     '    formosa_panel = FormosaPilotPanel()\n    formosa_btn = FormosaBigButton("FormosaPilot", "FormosaLink", gui_app.texture(LOGO_ASSET, 80, 80))\n    formosa_btn.set_click_callback(lambda: gui_app.push_widget(formosa_panel))\n\n')
  text = insert_once(text, "    # front slots", "    items.insert(0, formosa_btn)\n\n")
  if text != path.read_text(encoding="utf-8"):
    changes[path] = text
  path = target / "openpilot/selfdrive/ui/sunnypilot/layouts/settings/settings.py"
  text = path.read_text(encoding="utf-8")
  text = insert_once(text, "from dataclasses import dataclass\n", brand_import)
  text = insert_once(text, '    "SUNNYLINK",\n', '    "FORMOSAPILOT",\n')
  text = insert_once(text, '      OP.PanelType.DEVICE: PanelInfo(',
                     '      OP.PanelType.FORMOSAPILOT: PanelInfo("FormosaPilot", FormosaPilotPanel(embedded=True), icon=LOGO_ASSET),\n')
  if 'font_size = 40 if self.panel_info.name == "FormosaPilot"' not in text:
    anchor = "    text_size = measure_text_cached(self.parent._font_medium, self.panel_info.name, 65)"
    if text.count(anchor) != 1:
      raise ValueError("C3X brand navigation text anchor is ambiguous")
    text = text.replace(anchor, '    font_size = 40 if self.panel_info.name == "FormosaPilot" else 55\n    text_size = measure_text_cached(self.parent._font_medium, self.panel_info.name, 40 if self.panel_info.name == "FormosaPilot" else 65)', 1)
    text = text.replace("self.panel_info.name, text_pos, 55, 0, text_color", "self.panel_info.name, text_pos, font_size, 0, text_color", 1)
  if text != path.read_text(encoding="utf-8"):
    changes[path] = text
  path = target / "openpilot/system/ui/lib/application.py"
  text = path.read_text(encoding="utf-8")
  if "    self._fallback_fonts = {}\n    self._fallback_codepoints = {}\n" not in text:
    anchor = "    self._fallback_fonts = {}\n"
    if text.count(anchor) != 1:
      raise ValueError("font shutdown anchor is ambiguous; review manually")
    changes[path] = text.replace(anchor, anchor + "    self._fallback_codepoints = {}\n", 1)
  path = target / "docs/architecture/module_map.json"
  text = path.read_text(encoding="utf-8")
  start = text.index('"id": "cloud"')
  end = text.index('"id":', start+6)
  section = text[start:end]
  if '"formosalink/"' not in section:
    anchor = '"openpilot/sunnypilot/sunnylink/",'
    section = section.replace(anchor, anchor + '\n        "openpilot/sunnypilot/formosalink/",\n        "formosalink/",\n        "tools/deploy/publish_formosalink_iis.ps1",\n        "tools/maintenance/sync_formosalink.py",', 1)
  if '".github/workflows/formosalink.yml"' not in section:
    section = section.replace('"checks": [', '"checks": [\n        ".github/workflows/formosalink.yml",', 1)
  updated = text[:start] + section + text[end:]
  json.loads(updated)
  if updated != text:
    changes[path] = updated
  path = target / "docs/architecture/README.md"
  text = path.read_text(encoding="utf-8")
  if "../../formosalink/README.md" not in text:
    changes[path] = text.rstrip() + "\n\n## FormosaPilot / FormosaLink\n\n兩分支共用獨立配對與唯讀監看模組；部署、協定、驗證限制與三語操作說明見 [FormosaLink](../../formosalink/README.md)。預設停用代理，保留各分支原有行車行為。\n"
  return changes


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--target", type=Path, required=True)
  parser.add_argument("--check", action="store_true")
  args = parser.parse_args()
  target = args.target.resolve()
  if not (target / "openpilot/system/manager/process_config.py").is_file():
    raise SystemExit("target is not a compatible checkout")
  changes = hook_changes(target)  # Validate every hook before writing anything.
  differences = []
  for source in owned_files():
    relative = source.relative_to(ROOT)
    destination = target / relative
    if not destination.is_file() or hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(destination.read_bytes()).digest():
      differences.append(str(relative))
      if not args.check:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
  for path, content in changes.items():
    differences.append(str(path.relative_to(target)))
    if not args.check:
      path.write_text(content, encoding="utf-8", newline="\n")
  print(json.dumps({"target":str(target),"check_only":args.check,"differences":differences}, ensure_ascii=True, indent=2))
  if args.check and differences:
    raise SystemExit(1)


if __name__ == "__main__":
  main()
