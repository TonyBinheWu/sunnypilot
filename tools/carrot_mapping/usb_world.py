"""Occupancy and drive-first timing on the installed N16 runtime, inside the parked GPU owner."""
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import time

import numpy as np

from .gpu_priority_bench import DriveFirst, PERIOD, metric


def rgb_input(raw):
  if len(raw) != 224 * 126 * 4:
    raise ValueError("expected rectified, central-FOV 224x126 RGBA")
  image = np.frombuffer(raw, np.uint8).reshape(126, 224, 4)[:, :, :3].astype(np.float32) / 255
  image -= np.asarray([.485, .456, .406], np.float32)
  image /= np.asarray([.229, .224, .225], np.float32)
  return np.ascontiguousarray(image.transpose(2, 0, 1)[None])


def check_volume(occupied, free):
  if any(a.shape != (1, 43, 36, 64) or not np.isfinite(a).all() or a.min() < -.001 or a.max() > 1.001
         for a in (occupied, free)):
    raise ValueError("invalid ray occupancy output")
  if np.any(np.diff(free, axis=1) > .002) or np.any(occupied + free > 1.002):
    raise ValueError("inconsistent visible-free probabilities")
  return int((occupied[0].max(axis=0) >= .22).sum())


def verify_n16_artifact(manifest, digest):
  catalog = Path(__file__).resolve().parents[2] / "openpilot/selfdrive/modeld/model_catalog/catalog.json"
  expected = json.loads(catalog.read_text())["n16"]["egpu"]["sha256"]
  if manifest["format"] != "comma-generic-onnx" or manifest["pickle"]["sha256"] != expected or digest != expected:
    raise ValueError("installed generic N16 eGPU artifact required")


def drive_step(artifact, manifest, width, height):
  from openpilot.selfdrive.modeld.egpu_output_recovery import OutputRecovery
  from openpilot.selfdrive.modeld.generic_model_runtime import GenericModelRuntime, model_metadata, use_compiled_copies
  from openpilot.selfdrive.modeld.output_validation import validate_compiled_output
  from openpilot.selfdrive.modeld.precompiled_artifact import load_artifact
  from openpilot.selfdrive.modeld.precompiled_model import sha256
  from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
  from tinygrad import Device

  verify_n16_artifact(manifest, sha256(artifact))
  jits = load_artifact(artifact, manifest.get("serialization", "oob-v1"))
  checkpoint, _, _, _ = model_metadata(jits)
  if checkpoint != manifest["model_checkpoint"] or Device[jits["input_specs"]["new_img"][2]] is not Device["AMD"]:
    raise ValueError("unexpected N16 checkpoint or processor")

  # C4 uses the generic AMD warp and recurrent model. Keep the benchmark's
  # warp cache and model state separate from the installed driving worker.
  with TemporaryDirectory(prefix="world-warp-") as scratch:
    runtime = GenericModelRuntime(jits, width, height, Path(scratch), get_nv12_info(width, height), use_compiled_copies(manifest))
  runtime.packed.fill(0)
  for name in ("tfm", "big_tfm"):
    runtime.views[name][:] = np.eye(3, dtype=np.float32)
  runtime.bind_shared(runtime.packed)
  recovery = OutputRecovery(runtime, runtime.count, lambda *args, **kwargs: None)

  def step():
    result = recovery.run()
    if result is None:
      raise ValueError("N16 held an output during qualification")
    validate_compiled_output(result, runtime.count)
  return step


def trial(drive, auxiliary, frames, clock=time.monotonic, sleep=time.sleep):
  for _ in range(4):
    drive()
  def phase(budget=None):
    release = clock()
    durations, jobs, late, missed = [], [], 0, 0
    for _ in range(frames):
      sleep(max(0, release - clock()))
      start = clock()
      drive()
      finish = clock()
      deadline = release + PERIOD
      durations.append(finish - start)
      late += int(finish > deadline)
      if budget:
        budget.drive_completed(finish, deadline)
        if budget.admit(finish, deadline, release):
          auxiliary()
          end = clock()
          jobs.append(end - finish)
          budget.completed(finish, end, deadline)
      skip = max(0, math.floor((clock() - deadline) / PERIOD))
      missed += skip
      release = deadline + skip * PERIOD
    return {"drive": metric(durations), "late": late, "skipped": missed, "aux": metric(jobs)}

  baseline = phase()
  warm = []
  for _ in range(7):
    start = clock()
    auxiliary()
    warm.append(clock() - start)
  budget = DriveFirst(1250 * max(warm[3:]))
  if baseline["late"] or baseline["skipped"]:
    budget.suspended = True
  shared = phase(budget)
  return {"baseline": baseline, "shared": shared, "suspended": budget.suspended,
          "aux_warm": metric(warm[3:]), "budget_ms": 1000 * budget.cost}


def qualify(artifact, manifest, model, frames, samples, width, height):
  from tinygrad import Device, Tensor, TinyJit
  from tinygrad.nn.onnx import OnnxRunner

  gpu = Device["AMD"]
  if Device[Device.DEFAULT] is not gpu or not gpu.is_usb():
    raise RuntimeError("required Chestnut USB AMD backend unavailable")
  drive = drive_step(artifact, manifest, width, height)
  runner = None

  @TinyJit
  def infer(rgb):
    out = runner({"rgb": rgb})
    occupied, free = out["occupied"], out["visible_free"]
    if Device[occupied.device] is not gpu or Device[free.device] is not gpu:
      raise RuntimeError("unexpected world inference device")
    return occupied.realize(), free.realize()

  inputs = [rgb_input(raw) for raw in samples]
  counts = {}

  def auxiliary():
    nonlocal runner
    if runner is None:
      runner = OnnxRunner(model)
    for lens, image in zip(("road", "wide"), inputs, strict=True):
      occupied, free = infer(Tensor(image, device="AMD"))
      counts[lens] = check_volume(occupied.numpy(), free.numpy())
  report = trial(drive, auxiliary, frames)
  return {**report, "execution": "parked USB AMD replay", "arch": Device["AMD"].arch,
          "vram_bytes": getattr(getattr(Device["AMD"].iface, "dev_impl", None), "vram_size", None),
          "frame_width": width, "frame_height": height, "surface_rays": counts}
