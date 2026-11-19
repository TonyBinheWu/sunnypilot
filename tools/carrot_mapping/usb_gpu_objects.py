"""Parked C4 qualification of two recorded front views on the vehicle USB AMD GPU."""
import argparse
from collections import Counter
import json
import multiprocessing
import os
from pathlib import Path
import sys
import time


def check_bridge(bridge, firmware_matches):
  if bridge is None or bridge.speed_mbps < 5000:
    raise RuntimeError("no single SuperSpeed USB eGPU bridge")
  if not firmware_matches(bridge.product):
    raise RuntimeError(f"firmware mismatch: {bridge.product}")


def parked(sm, params):
  from openpilot.sunnypilot.formosalink.telemetry import source_valid
  sm.update(0)
  return (params.get_bool("IsOffroad") and source_valid(sm, "deviceState", 2) and not sm["deviceState"].started
          and source_valid(sm, "pandaStates", 2) and len(sm["pandaStates"]) > 0
          and not any(p.ignitionLine or p.ignitionCan for p in sm["pandaStates"]))


def measure(args, parent_pid):
  # The Unix process must exit immediately if its offroad supervisor disappears.
  import ctypes
  import signal
  if ctypes.CDLL(None, use_errno=True).prctl(1, signal.SIGKILL, 0, 0, 0) != 0 or os.getppid() != parent_pid:
    raise RuntimeError("cannot supervise parked GPU process")
  import numpy as np
  from openpilot.selfdrive.modeld.precompiled_model import installed, sha256
  from openpilot.selfdrive.modeld.precompiled_worker import claim_gpu_owner
  from openpilot.system.hardware.usbgpu import get_usbgpu_device, is_current_usbgpu_firmware
  from .gpu_objects import INPUT, MODEL_SHA256, decode, model_input, output_grid
  from .gpu_priority_bench import metric

  check_bridge(get_usbgpu_device(), is_current_usbgpu_firmware)
  artifact = installed()
  if artifact is None:
    raise RuntimeError("installed driving-model runtime unavailable")
  manifest = json.loads((artifact.parent / "installed.json").read_text())
  if manifest["gpu_arch"] != "gfx1200" or sha256(args.model) != MODEL_SHA256:
    raise ValueError("unexpected model or GPU architecture")
  files = (args.road, args.wide)
  if files[0].samefile(files[1]) or any(p.stat().st_size != INPUT * INPUT * 4 for p in files):
    raise ValueError("supply two distinct letterboxed 416x416 RGBA recordings")
  frames = [p.read_bytes() for p in files]
  if frames[0] == frames[1]:
    raise ValueError("two identical samples cannot validate separate cameras")
  claim_gpu_owner()
  os.environ.update(DEV="USB+AMD:LLVM", GMMU="0", JIT_BATCH_SIZE="0")
  sys.path.insert(0, str(artifact.parent / manifest["runtime_directory"]))
  from tinygrad import Device, Tensor, TinyJit
  from tinygrad.nn.onnx import OnnxRunner
  from openpilot.selfdrive.modeld.egpu_usb_wait import configure_usb_wait
  from openpilot.selfdrive.modeld.egpu_usb_wrap import configure_usb_wrap
  configure_usb_wait(manifest)
  configure_usb_wrap(manifest)
  gpu = Device["AMD"]
  if not gpu.is_usb() or gpu.arch != manifest["gpu_arch"]:
    raise RuntimeError("USB AMD device required")
  runner = OnnxRunner(args.model)

  @TinyJit
  def infer(x):
    out, = runner({"images": x}).values()
    if out.device != x.device:
      raise RuntimeError("unexpected inference output device")
    return out.realize()

  grid, strides = output_grid()
  counts, times = {}, []
  for i in range(args.pairs + 3):
    started = time.monotonic()
    for lens, rgba in zip(("road", "wide"), frames, strict=True):
      raw = infer(Tensor(model_input(rgba), device="AMD")).numpy()
      if not np.isfinite(raw).all():
        raise RuntimeError("invalid object output")
      counts[lens] = dict(Counter(obj["kind"] for obj in decode(raw, grid, strides)))
    if i >= 3:
      times.append(time.monotonic() - started)
  mem = getattr(getattr(gpu.iface, "dev_impl", None), "vram_size", None)
  print(json.dumps({"execution": "USB AMD", "arch": gpu.arch, "vram_bytes": mem,
                    "pair_latency": metric(times), "image_detections": counts}), flush=True)


def main():
  from openpilot.cereal import messaging
  from openpilot.common.params import Params
  from openpilot.system.hardware.usbgpu import get_usbgpu_device, is_current_usbgpu_firmware
  parser = argparse.ArgumentParser(description=__doc__)
  for name in ("model", "road", "wide"):
    parser.add_argument(name, type=Path)
  parser.add_argument("--pairs", type=int, default=20, choices=range(3, 61), metavar="3..60")
  args = parser.parse_args()
  check_bridge(get_usbgpu_device(), is_current_usbgpu_firmware)
  sm, params = messaging.SubMaster(["deviceState", "pandaStates"]), Params()
  until = time.monotonic() + 4
  while not parked(sm, params):
    if time.monotonic() >= until:
      raise RuntimeError("fresh ignition-off and offroad state required")
    time.sleep(.05)
  worker = multiprocessing.get_context("spawn").Process(target=measure, args=(args, os.getpid()))
  worker.start()
  deadline = time.monotonic() + 180
  try:
    while worker.is_alive():
      if not parked(sm, params) or time.monotonic() > deadline:
        raise RuntimeError("parked qualification stopped")
      worker.join(.1)
    if worker.exitcode != 0:
      raise RuntimeError("USB GPU qualification did not finish")
  finally:
    if worker.is_alive():
      worker.kill()
    worker.join()


if __name__ == "__main__":
  main()
