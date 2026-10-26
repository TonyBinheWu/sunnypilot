#!/usr/bin/env python3
"""Read-only diagnostic for modeld_tinygrad startup on comma hardware."""
import os
import shutil
import subprocess
from pathlib import Path

from openpilot.common.hardware.hw import Paths
from openpilot.common.params import Params
from openpilot.sunnypilot.models.helpers import get_selected_bundle, get_active_model_runner

def main():
  params = Params()
  print("== modeld runner ==")
  print("runner cached:", params.get("ModelRunnerTypeCache"))
  try:
    print("runner selected:", get_active_model_runner(params, force_check=True))
  except Exception as exc:
    print("runner selection error:", repr(exc))
  print("== selected model bundles ==")
  model_root = Path(Paths.model_root())
  print("model root:", model_root)
  for source in ("qcom", "chestnut"):
    try:
      bundle = get_selected_bundle(params, source)
      if bundle is None:
        print(f"{source}: NO ACTIVE BUNDLE")
        continue
      print(f"{source}: runner={bundle.runner} models={len(bundle.models)}")
      for model in bundle.models:
        filename = model.artifact.fileName
        # Require the file to remain within the configured model storage root.
        candidate = (model_root / filename).resolve()
        if not candidate.is_relative_to(model_root.resolve()):
          print(f"  unsafe model filename: {filename!r}")
          continue
        print(f"  {filename}: exists={candidate.is_file()} size={candidate.stat().st_size if candidate.is_file() else 0}")
    except Exception as exc:
      print(f"{source}: ERROR {exc!r}")
  print("== executable ==")
  binary = Path("/data/openpilot/openpilot/sunnypilot/modeld_v2/modeld")
  print(binary, "exists=", binary.exists(), "executable=", os.access(binary, os.X_OK))
  print("== processes ==")
  for cmd in (["pgrep", "-af", "modeld"], ["df", "-h", "/data"]):
    try:
      subprocess.run(cmd, check=False, timeout=5)
    except Exception as exc:
      print(cmd[0], repr(exc))
  print("== recent tombstones ==")
  for path in sorted(Path("/data/tombstones").glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]:
    print(path)

if __name__ == "__main__":
  main()
