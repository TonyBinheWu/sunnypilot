"""Desktop GPU adapter for the FORMOSA cockpit render host. Windows DirectML only."""

import hashlib
import json
import time
from pathlib import Path

import numpy as np


class WorkstationOccupancy:
  def __init__(self, path: Path, expected_hash: str, profile_prefix: Path, adapter: int = 0):
    import onnxruntime as ort

    with path.open("rb") as model:
      if hashlib.file_digest(model, "sha256").hexdigest() != expected_hash:
        raise ValueError("occupancy model integrity check failed")
    if "DmlExecutionProvider" not in ort.get_available_providers():
      raise RuntimeError("Windows DirectML GPU provider is unavailable")
    options = ort.SessionOptions()
    options.enable_mem_pattern = False
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.add_session_config_entry("session.disable_cpu_ep_fallback", "1")
    options.enable_profiling = True
    options.profile_file_prefix = str(profile_prefix)
    self.session = ort.InferenceSession(str(path), options, providers=[("DmlExecutionProvider", {"device_id": str(adapter)})])
    if self.session.get_providers()[0] != "DmlExecutionProvider":
      raise RuntimeError("DirectML GPU was not selected")
    self.session.disable_fallback()
    self.mean = np.array([.485, .456, .406], dtype=np.float32)
    self.std = np.array([.229, .224, .225], dtype=np.float32)
    self.latencies = []
    self.profile = None

  def infer_rgba(self, pixels: bytes):
    if len(pixels) != 224 * 126 * 4:
      raise ValueError("expected one cropped RGBA frame")
    rgba = np.frombuffer(pixels, np.uint8).reshape(126, 224, 4)
    rgb = ((rgba[:, :, :3].astype(np.float32) / 255 - self.mean) / self.std).transpose(2, 0, 1)[None]
    started = time.monotonic()
    occupied, visible = self.session.run(["occupied", "visible_free"], {"rgb": np.ascontiguousarray(rgb)})
    elapsed = (time.monotonic() - started) * 1000
    self.latencies.append(elapsed)
    if self.profile is None:
      self.verify_profile()
    if len(self.latencies) > 512:
      del self.latencies[:256]
    return occupied, visible, elapsed

  def verify_profile(self):
    if self.profile is not None:
      return self.profile
    events = json.loads(Path(self.session.end_profiling()).read_text(encoding="utf-8"))
    executed = {event["args"].get("provider") for event in events if event.get("cat") == "Node"}
    if executed != {"DmlExecutionProvider"}:
      raise RuntimeError(f"unexpected kernel execution providers: {executed}")
    self.profile = sorted(executed)
    return self.profile
