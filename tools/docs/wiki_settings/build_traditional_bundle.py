"""Build the offline settings reference. Requires opencc-python-reimplemented.

Only translated MANUAL blocks are seeded; AUTO content and hashes always come
from generate.py and the checked-in catalog. Source links/code are preserved.
traditional_manual.json supplies translations where the Chinese Wiki is empty.
Its English source hashes require review when upstream prose changes. Existing
Chinese explanations and their review markers remain intact.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from tools.docs.wiki_settings.generate import DEFAULT_CATALOG, REPO_ROOT, generate, scan_existing_settings

OUTPUT = REPO_ROOT / "openpilot/selfdrive/carrot/web/docs/settings"
PROTECTED = re.compile(r"(<!--.*?-->|```.*?```|`[^`]*`|https?://[^\s<>]+|\]\([^)]*\))", re.S)
TRANSLATIONS = Path(__file__).with_name("traditional_manual.json")


def translated_manual(param: str, english: str, original: str, translations: dict) -> str:
  entry = translations.get(param)
  if entry is None:
    return original
  if hashlib.sha256(english.encode("utf-8")).hexdigest() != entry["englishHash"]:
    raise ValueError(f"{param}: English guide changed; review its Traditional Chinese translation")
  manual = entry["manual"]
  # Translations must retain the source structure, IDs, and the original review status.
  def markers(text):
    return re.findall(r"<!-- CARROT:.*? -->", text)

  original_review = re.search(r"<!-- CARROT:REVIEW.*? -->", original)
  if original_review is None:
    raise ValueError(f"{param}: Original review marker is missing")
  expected = re.sub(r"<!-- CARROT:REVIEW.*? -->", original_review[0], english)
  if markers(manual) != markers(expected):
    raise ValueError(f"{param}: Traditional Chinese guide markers differ from source")
  for pattern in (r"`[^`]*`", r"https?://[^\s<>)]+", r"\d+(?:\.\d+)?"):
    if Counter(re.findall(pattern, manual)) != Counter(re.findall(pattern, expected)):
      raise ValueError(f"{param}: Traditional Chinese guide changed code, links, or numbers")
  return manual


def traditional_manual(text: str) -> str:
  from opencc import OpenCC

  converter = OpenCC("s2twp")
  parts = PROTECTED.split(text)
  for i in range(0, len(parts), 2):
    parts[i] = converter.convert(parts[i]).replace("設置", "設定").replace("默認", "預設").replace("日誌", "記錄")
  return "".join(parts)


def build(source: Path, output: Path) -> None:
  existing, _ = scan_existing_settings(source)
  translations = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))["settings"]
  source_commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
  with tempfile.TemporaryDirectory(prefix="carrot-docs-") as staging:
    seed = Path(staging)
    for (locale, param), item in existing.items():
      if locale not in ("ko", "en", "zh"):
        continue
      targets = [(locale, item.manual_block)]
      if locale == "zh":
        original = traditional_manual(item.manual_block)
        english = existing.get(("en", param))
        targets.append(("zh-tw", translated_manual(param, english.manual_block if english else "", original, translations)))
      for target, manual in targets:
        # Group is read from the actual catalog when rendering; only MANUAL is imported.
        text = (f'<!-- CARROT:GENERATED schema="1" locale="{target}" group="Imported" param="{param}" -->\n'
                f'<!-- CARROT:SETTING:BEGIN {param} -->\n{manual}\n<!-- CARROT:SETTING:END {param} -->\n')
        (seed / f"{target.upper()}-{param}.md").write_text(text, encoding="utf-8")
    result = generate(DEFAULT_CATALOG, wiki_dir=seed, locales=("ko", "en", "zh", "zh-tw"),
                      wiki_commit=source_commit, generated_at="2026-11-12T00:00:00Z")
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
