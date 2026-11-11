"""Build the offline settings reference. Requires opencc-python-reimplemented.

Only translated MANUAL blocks are seeded; AUTO content and hashes always come
from generate.py and the checked-in catalog. Source links/code are preserved.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import tempfile

from opencc import OpenCC
from tools.docs.wiki_settings.generate import DEFAULT_CATALOG, REPO_ROOT, generate, scan_existing_settings

OUTPUT = REPO_ROOT / "openpilot/selfdrive/carrot/web/docs/settings"
PROTECTED = re.compile(r"(<!--.*?-->|```.*?```|`[^`]*`|https?://[^\s<>]+|\]\([^)]*\))", re.S)


def traditional_manual(text: str) -> str:
  converter = OpenCC("s2twp")
  parts = PROTECTED.split(text)
  for i in range(0, len(parts), 2):
    parts[i] = converter.convert(parts[i]).replace("設置", "設定").replace("默認", "預設").replace("日誌", "記錄")
  return "".join(parts)


def build(source: Path, output: Path) -> None:
  existing, _ = scan_existing_settings(source)
  source_commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
  with tempfile.TemporaryDirectory(prefix="carrot-docs-") as staging:
    seed = Path(staging)
    for (locale, param), item in existing.items():
      if locale not in ("ko", "en", "zh"):
        continue
      targets = [(locale, item.manual_block)]
      if locale == "zh":
        targets.append(("zh-tw", traditional_manual(item.manual_block)))
      for target, manual in targets:
        # Group is read from the actual catalog when rendering; only MANUAL is imported.
        text = (f'<!-- CARROT:GENERATED schema="1" locale="{target}" group="Imported" param="{param}" -->\n'
                f'<!-- CARROT:SETTING:BEGIN {param} -->\n{manual}\n<!-- CARROT:SETTING:END {param} -->\n')
        (seed / f"{target.upper()}-{param}.md").write_text(text, encoding="utf-8")
    result = generate(DEFAULT_CATALOG, wiki_dir=seed, locales=("ko", "en", "zh", "zh-tw"),
                      wiki_commit=source_commit, generated_at="2026-11-11T00:00:00Z")
    output.mkdir(parents=True, exist_ok=True)
    # Write only generator output, never the source checkout or its Git metadata.
    for name, text in result.pages.items():
      (output / name).write_bytes(text.encode("utf-8"))
    print(f"Generated {len(result.index['settings'])} settings in four locales from Wiki {source_commit}")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--source-wiki", required=True, type=Path)
  parser.add_argument("--output", default=OUTPUT, type=Path)
  args = parser.parse_args()
  build(args.source_wiki, args.output)
