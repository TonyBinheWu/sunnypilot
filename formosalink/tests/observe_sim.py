"""Observe real simulator messages with the production read-only telemetry adapter.

Run inside an isolated Linux native build. Profiles describe UI only, not hardware.
"""
import argparse
import json
import os
from pathlib import Path
import time


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--prefix", required=True)
  parser.add_argument("--output", type=Path, required=True)
  parser.add_argument("--duration", type=float, default=55)
  parser.add_argument("--profile", choices=("C3X", "C4"), required=True)
  args = parser.parse_args()
  if Path("/AGNOS").exists():
    parser.error("simulator observer is PC-only")
  os.environ["OPENPILOT_PREFIX"] = args.prefix
  from openpilot.sunnypilot.formosalink.telemetry import OpenpilotSampler
  sampler = OpenpilotSampler()
  args.output.mkdir(parents=True, exist_ok=True)
  started = time.monotonic()
  valid = moving = count = 0
  with (args.output / "formosalink-telemetry.jsonl").open("w",encoding="utf-8") as file:
    while time.monotonic()-started < args.duration:
      snapshot = sampler.sample(count)
      file.write(json.dumps(snapshot,allow_nan=False)+"\n")
      file.flush()
      metrics = snapshot["metrics"]
      valid += int(metrics["sample_valid"])
      moving += int((metrics.get("speed_kph") or 0)>3.6)
      count += 1
      time.sleep(.5)
  result = {"profile":args.profile,"hardware_emulated":False,"samples":count,"valid_samples":valid,
            "moving_samples":moving,"passed":valid>=10 and moving>=5,"writes_to_control_or_params":False}
  (args.output / "observer.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
  print(json.dumps(result))
  return 0 if result["passed"] else 1


if __name__ == "__main__":
  raise SystemExit(main())
