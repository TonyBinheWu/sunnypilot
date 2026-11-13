#!/usr/bin/env python3
"""Import missing setting guides without replacing existing Wiki explanations."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil

import generate


def seed_missing_guides(source: Path, wiki: Path) -> int:
  existing, _ = generate.scan_existing_settings(wiki)
  bundled, _ = generate.scan_existing_settings(source)
  missing = {key for key in bundled if key not in existing}
  pages = {bundled[key].page for key in missing}
  # Preflight every page before copying anything. A renamed or grouped page must
  # never replace an existing parameter's manual text or an unmanaged page.
  for page in pages:
    if (wiki / page).exists() or any(item.page == page and key not in missing for key, item in bundled.items()):
      raise generate.GenerationError(f"refusing to overwrite existing Wiki content: {page}")
  for page in sorted(pages):
    shutil.copyfile(source / page, wiki / page)
  return len(missing)


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--source-dir", type=Path, required=True)
  parser.add_argument("--wiki-dir", type=Path, required=True)
  args = parser.parse_args()
  print(f"Imported {seed_missing_guides(args.source_dir, args.wiki_dir)} missing setting guides.")


if __name__ == "__main__":
  main()
