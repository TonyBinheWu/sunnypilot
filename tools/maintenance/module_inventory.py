"""Read-only module inventory and conservative upgrade-impact report."""
import argparse
from collections import deque
import fnmatch
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
MAP_FILE = ROOT / "docs/architecture/module_map.json"
PROFILES = ("hkg-enhanced", "ccnc-port")


def git(*args: str) -> str:
  return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8", "surrogateescape")


def matches(path: str, pattern: str) -> bool:
  return path.startswith(pattern) if pattern.endswith("/") else fnmatch.fnmatchcase(path, pattern)


def load_modules(profile: str) -> dict:
  data = json.loads(MAP_FILE.read_text(encoding="utf-8"))
  if data["schema_version"] != 1:
    raise ValueError("Unsupported module map schema")
  modules = {item["id"]: item for item in data["modules"]}
  if len(modules) != len(data["modules"]):
    raise ValueError("Duplicate module IDs")
  for key, item in modules.items():
    for dep in item["requires"] + item["optional_requires"]:
      if dep not in modules or dep == key:
        raise ValueError(f"Invalid dependency: {key} -> {dep}")
    if not item["paths_to_watch"] or not set(item["branches"]).issubset(PROFILES):
      raise ValueError(f"Invalid paths or branches for {key}")
  return {key: item for key, item in modules.items() if profile in item["branches"]}


def dependencies(item: dict, active: dict) -> set[str]:
  return set(item["requires"] + item["optional_requires"]) & active.keys()


def check_modules(modules: dict) -> None:
  paths = git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")
  visited: set[str] = set()
  visiting: set[str] = set()

  def visit(key: str):
    if key in visiting:
      raise ValueError(f"Upgrade dependency cycle at {key}")
    if key in visited:
      return
    visiting.add(key)
    for dep in dependencies(modules[key], modules):
      visit(dep)
    visiting.remove(key)
    visited.add(key)

  for key, item in modules.items():
    visit(key)
    if not any(matches(path, pattern) for path in paths if path for pattern in item["paths_to_watch"]):
      raise ValueError(f"No current source paths match {key}")
    for check in item["checks"]:
      if not (ROOT / check).is_file():
        raise ValueError(f"Missing check entry: {check}")


def impact(modules: dict, reference: str, inactive: dict) -> dict:
  # Resolve to a commit before diffing, so a ref cannot be interpreted as a git option.
  commit = git("rev-parse", "--verify", "--end-of-options", f"{reference}^{{commit}}").strip()
  paths = sorted(set(filter(None, git("diff", "--name-only", "-z", commit, "--").split("\0"))))
  direct: dict[str, list[str]] = {}
  inactive_paths: dict[str, list[str]] = {}
  unmapped = []
  for path in paths:
    owners = [key for key, item in modules.items() if any(matches(path, pattern) for pattern in item["paths_to_watch"])]
    if not owners:
      disabled = [key for key, item in inactive.items() if any(matches(path, pattern) for pattern in item["paths_to_watch"])]
      if disabled:
        for key in disabled:
          inactive_paths.setdefault(key, []).append(path)
      else:
        unmapped.append(path)
    for key in owners:
      direct.setdefault(key, []).append(path)
  affected = set(direct)
  queue = deque(direct)
  while queue:
    provider = queue.popleft()
    for consumer, item in modules.items():
      if consumer not in affected and provider in dependencies(item, modules):
        affected.add(consumer)
        queue.append(consumer)
  return {
    "reference": reference,
    "reference_commit": commit,
    "changed_file_count": len(paths),
    "direct": dict(sorted(direct.items())),
    "indirect": sorted(affected - direct.keys()),
    "inactive_module_paths": inactive_paths,
    "unmapped": unmapped,
    "recommended_checks": sorted({check for key in affected for check in modules[key]["checks"]}),
  }


def render_catalog(modules: list[dict]) -> str:
  lines = ["# 模組部件目錄", "", "由 `module_map.json` 產生的 15 個維護部件。路徑可重疊，表示監看範圍，不代表獨立套件或可單獨部署的服務。",
           "", "| ID | 部件 | 適用分支 |", "| --- | --- | --- |"]
  for item in modules:
    lines.append(f"| `{item['id']}` | {item['title']} | {'、'.join(item['branches'])} |")
  for item in modules:
    lines += ["", f"## {item['id']}：{item['title']}", "", "**程式與監看路徑**", ""]
    lines += [f"* `{path}`" for path in item["paths_to_watch"]]
    lines += ["", "**對外契約**", ""] + ["* " + text for text in item["contracts"]]
    deps = "、".join(f"`{key}`" for key in item["requires"]) or "無上層模組依賴"
    lines += ["", "**升級依賴**：" + deps + "。"]
    if item["optional_requires"]:
      lines += ["", "**功能啟用時的依賴**：" + "、".join(f"`{key}`" for key in item["optional_requires"]) + "。"]
    lines += ["", "**成組升級單位**：" + item["upgrade_unit"] + "。", "", "**驗證入口**", ""]
    lines += [f"* `{check}`" for check in item["checks"]]
    if item["id"] == "vehicle_safety":
      lines += ["* 子模組內另行驗證 car／controller、Panda safety 與 mutation；主儲存庫 CI 不能替代這些測試。"]
    if item["id"] == "inference":
      lines += ["* CPU loader／contract 成功後，仍須驗證兩種裝置的 QCOM 與實際使用的 Chestnut 後端。"]
  return "\n".join(lines) + "\n"


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--profile", choices=PROFILES, help="Target maintenance branch; defaults to the current branch")
  parser.add_argument("--diff", metavar="REF", help="Compare REF to the current tracked worktree")
  parser.add_argument("--check", action="store_true", help="Validate IDs, dependencies, current paths and check entries")
  output = parser.add_mutually_exclusive_group()
  output.add_argument("--json", action="store_true", help="Print machine-readable output")
  output.add_argument("--catalog", action="store_true", help="Print the complete cross-branch Markdown component catalog")
  args = parser.parse_args()
  try:
    profile = args.profile or git("branch", "--show-current").strip()
    if profile not in PROFILES:
      raise ValueError("Use --profile hkg-enhanced or --profile ccnc-port for a temporary/detached checkout")
    modules = load_modules(profile)
    check_modules(modules)
    all_modules = json.loads(MAP_FILE.read_text(encoding="utf-8"))["modules"]
    inactive = {item["id"]: item for item in all_modules if profile not in item["branches"]}
    result = {"profile": profile, "map_valid": True, "active_modules": list(modules)}
    if args.diff:
      result.update(impact(modules, args.diff, inactive))
    if args.catalog:
      print(render_catalog(all_modules), end="")
    elif args.json:
      print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
      print(f"{profile}: {len(modules)} active module definitions validated.")
      if args.diff:
        print(f"Changed tracked files: {result['changed_file_count']}")
        print("Direct modules: " + (", ".join(result["direct"]) or "none"))
        print("Dependent modules: " + (", ".join(result["indirect"]) or "none"))
        for key, paths in result["direct"].items():
          print(f"  {key}: " + ", ".join(paths))
        print("Suggested checks:")
        for check in result["recommended_checks"]:
          print(f"  {check}")
        for key, paths in result["inactive_module_paths"].items():
          print(f"Inactive module {key} (review branch scope): " + ", ".join(paths))
        if result["unmapped"]:
          print("Unmapped paths (review manually):")
          for path in result["unmapped"]:
            print(f"  {path}")
      elif not args.check:
        for key, item in modules.items():
          print(f"  {key}: {item['title']}")
    return 0
  except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
    print(f"Module inventory failed: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
  raise SystemExit(main())
