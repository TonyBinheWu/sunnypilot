"""Occupancy and drive-first timing on the installed N16 runtime, inside the parked GPU owner."""
import json
import math
from pathlib import Path
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


def drive_step(artifact, manifest, width, height):
  from openpilot.selfdrive.modeld.precompiled_artifact import load_artifact
  from openpilot.selfdrive.modeld.output_validation import validate_compiled_output
  from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
  from openpilot.selfdrive.modeld.precompiled_model import sha256
  from tinygrad import Device, Tensor
  import model_runtime

  catalog = Path(__file__).resolve().parents[2] / "openpilot/selfdrive/modeld/model_catalog/catalog.json"
  expected = json.loads(catalog.read_text())["n16"]["egpu"]["sha256"]
  if manifest["format"] != "comma-run-model" or manifest["pickle"]["sha256"] != expected or sha256(artifact) != expected:
    raise ValueError("installed N16 eGPU artifact required")
  jits = load_artifact(artifact, manifest.get("serialization", "oob-v1"))
  metadata = jits["metadata"]
  if metadata["model_checkpoint"] != manifest["model_checkpoint"] or Device[jits["input_devices"]["model"]] is not Device["AMD"]:
    raise ValueError("unexpected N16 checkpoint or processor")
  execute = jits["run_model"][(width, height)]
  frame_size = model_runtime.nv12_copy_size(*get_nv12_info(width, height)[:3])
  queues, views, frames = model_runtime.make_input_queues(metadata["input_shapes"], 4, "AMD", frame_size)
  # Exercise the actual graph, transfer, output download and validation. Both camera
  # buffers are isolated timing inputs. No prediction is published to modeld.
  packed = np.zeros_like(frames["img"].base)
  for name in ("tfm", "big_tfm"):
    if name in views:
      offset = views[name].ctypes.data - frames["img"].base.ctypes.data
      np.ndarray(views[name].shape, views[name].dtype, buffer=packed, offset=offset)[:] = np.eye(3).reshape(views[name].shape)
  queues["packed_npy_inputs"] = Tensor(packed, device="NPY").realize()
  count = max(v.stop for v in metadata["output_slices"].values())

  def step():
    out, = execute(**{k: queues[k] for k in model_runtime.MODELD_INPUTS})
    validate_compiled_output(out.numpy().reshape(-1), count)
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
