"""Synchronize only FormosaLink-owned source and narrow hooks across checkouts."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
OWNED_TREES = ("formosalink", "openpilot/sunnypilot/formosalink")
OWNED_FILES = (".github/workflows/formosalink.yml", "tools/deploy/publish_formosalink_iis.ps1", "tools/maintenance/sync_formosalink.py")
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
    changes[path] = text.rstrip() + "\n\n# Keep the small FormosaLink brand mark available without Git LFS.\n" + attribute + "\n"
  path = target / "openpilot/common/params_keys.h"
  text = path.read_text(encoding="utf-8")
  if '"FormosaLinkEnabled"' not in text:
    anchor = '    {"DongleId", {PERSISTENT, STRING}},\n'
    if text.count(anchor) != 1:
      raise ValueError("Params anchor is ambiguous; review manually")
    changes[path] = text.replace(anchor, anchor + KEY, 1)
  elif KEY.strip() not in text:
    raise ValueError("existing FormosaLink parameter differs; review manually")
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
  if text != path.read_text(encoding="utf-8"):
    changes[path] = text
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
