"""Measure drive-first GPU scheduling on a workstation with a local CUDA N16 worker and DirectML cockpit.
No car connection. Persistent CUDA state/output stays on the GPU between driving frames.
"""
import argparse
import hashlib
import json
import math
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

N16 = "01effc679eb46d6036ce0302673a87fe2dcfcc95a679daeeb929679e53c3647a"
OCC = "d477bac0f82ace6c8663b222d2c0c00987906a6939f545a5fdf60ef81138b787"
PERIOD = .05


class DriveFirst:
  """Admission for synchronous, non-preemptible jobs; never carry a backlog into the next frame."""
  def __init__(self, qualified_ms, reserve_ms=5):
    if not all(math.isfinite(n) and n > 0 for n in (qualified_ms, reserve_ms)):
      raise ValueError("invalid budget")
    self.cost = qualified_ms / 1000
    self.reserve = reserve_ms / 1000
    self.suspended = False

  def admit(self, now, next_drive, source_time):
    return (not self.suspended and 0 <= now - source_time < .9 - self.cost
            and now + self.cost + self.reserve <= next_drive)

  def drive_completed(self, now, deadline):
    if now > deadline:
      self.suspended = True

  def completed(self, start, finish, next_drive):
    if finish-start > self.cost or finish > next_drive-self.reserve:
      self.suspended = True


def driving_worker(model):
  import numpy as np
  import onnxruntime as ort
  with model.open("rb") as f:
    if hashlib.file_digest(f, "sha256").hexdigest() != N16:
      raise ValueError("N16 file does not match the branch catalog")
  ort.preload_dlls(directory="")
  options = ort.SessionOptions()
  options.log_severity_level = 3
  session = ort.InferenceSession(str(model), options, providers=[("CUDAExecutionProvider", {"device_id":0})])
  if session.get_providers()[0] != "CUDAExecutionProvider":
    raise RuntimeError("CUDA unavailable")
  session.disable_fallback()
  dtype = {"tensor(float)":np.float32, "tensor(uint8)":np.uint8}
  inputs = {i.name:ort.OrtValue.ortvalue_from_numpy(np.zeros(i.shape,dtype[i.type]), "cuda", 0) for i in session.get_inputs()}
  names = [s.name for s in session.get_outputs()]
  spec = json.loads((Path(__file__).resolve().parents[2]/"openpilot/selfdrive/modeld/model_catalog/n16.json").read_text())
  state = {k:"next_"+k for k in spec["input_shapes"] if k.startswith("state_")}
  if set(names) != set(spec["output_shapes"]) or not state or any(k not in inputs or v not in names for k,v in state.items()):
    raise ValueError(f"unknown state layout {state}")
  def step():
    io = session.io_binding()
    for name, tensor in inputs.items():
      io.bind_ortvalue_input(name,tensor)
    for name in names:
      io.bind_output(name, "cuda", 0)
    session.run_with_iobinding(io)
    io.synchronize_outputs()
    output = dict(zip(names, io.get_outputs(), strict=True))
    for source, dest in state.items():
      inputs[source] = output[dest]
    # Include host transfer/validation of the driving output; no GPU work remains pending at ACK.
    if not np.isfinite(output["outputs"].numpy()).all():
      raise ValueError("non-finite driving result")
  for _ in range(4):
    step()
  print("ready", flush=True)
  for cmd in sys.stdin:
    if cmd.strip() != "frame":
      break
    step()
    print("done", flush=True)


def metric(values):
  values = sorted(values)
  def quantile(q):
    return round(1000*values[max(0,math.ceil(q*len(values))-1)],2)
  return {"n":len(values),"median_ms":round(1000*statistics.median(values),2),"p95_ms":quantile(.95),"max_ms":quantile(1)} if values else {"n":0}


def benchmark(args):
  from .gpu_workstation import WorkstationOccupancy
  if args.frames < 20 or not args.worker:
    raise ValueError("at least 20 frames and a driving worker are required")
  with tempfile.TemporaryDirectory() as tmp, subprocess.Popen(args.worker, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1) as driver:
    try:
      if driver.stdout.readline().strip() != "ready":
        raise RuntimeError("N16 worker failed before warmup")
      gpu = WorkstationOccupancy(args.model, OCC, Path(tmp)/"profile")
      pixels = bytes(224*126*4)
      def cockpit():
        gpu.infer_rgba(pixels)
      warm = []
      for _ in range(25):
        start = time.monotonic()
        cockpit()
        warm.append(time.monotonic()-start)
      budget = DriveFirst(1000 * max(warm[3:]) * 1.25)
      report = {"period_ms":PERIOD*1000, "reserve_ms":budget.reserve*1000, "cockpit_budget_ms":round(budget.cost*1000,2),
                "cockpit_warm":metric(warm[3:])}
      for mode in ("drive_only", "shared"):
        duration, auxiliary, slack, late = [], [], [], 0
        release = time.monotonic()
        for _ in range(args.frames):
          time.sleep(max(0, release-time.monotonic()))
          start = time.monotonic()
          driver.stdin.write("frame\n")
          driver.stdin.flush()
          if driver.stdout.readline().strip() != "done":
            raise RuntimeError("driving inference failed")
          now = time.monotonic()
          deadline = release + PERIOD
          duration.append(now-start)
          slack.append(deadline-now)
          late += int(now > deadline)
          if mode == "shared":
            budget.drive_completed(now, deadline)
          if mode == "shared" and budget.admit(now, deadline, release):
            cockpit()
            finish = time.monotonic()
            auxiliary.append(finish-now)
            budget.completed(now,finish,deadline)
          # Skip missed releases instead of issuing a burst of obsolete work.
          release = deadline + PERIOD*max(0, math.floor((time.monotonic()-deadline)/PERIOD))
        report[mode] = {"drive":metric(duration), "available":metric(slack), "drive_late":late,
                        "cockpit":metric(auxiliary), "cockpit_suspended":budget.suspended}
      report["occupancy_execution"] = gpu.verify_profile()
      print(json.dumps(report,indent=2))
    finally:
      if driver.poll() is None:
        try:
          driver.stdin.write("quit\n")
          driver.stdin.flush()
          driver.wait(timeout=10)
        except (OSError,subprocess.TimeoutExpired):
          driver.kill()


if __name__ == "__main__":
  p = argparse.ArgumentParser(description=__doc__)
  sub = p.add_subparsers(dest="action", required=True)
  sub.add_parser("cuda-drive").add_argument("model", type=Path)
  bench = sub.add_parser("bench")
  bench.add_argument("model", type=Path)
  bench.add_argument("--frames", type=int, default=100)
  bench.add_argument("worker", nargs=argparse.REMAINDER)
  args = p.parse_args()
  if args.action == "cuda-drive":
    driving_worker(args.model)
  else:
    benchmark(args)
