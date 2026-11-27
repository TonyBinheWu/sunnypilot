"""Prepare the standby model before live eGPU publication, without publishing."""
import json
import numpy as np
import psutil
import time

from openpilot.selfdrive.modeld.local_gpu_warp import vehicle_device_type


def prepare_c4_stock_standby(camera, model_path, model_factory):
  if vehicle_device_type() != 'mici':
    return None
  # The generic C4 worker uses AMD for warp and inference. Other runtimes can
  # initialize QCOM themselves. Leave headroom for both the worker and camerad.
  if psutil.virtual_memory().available < model_path.stat().st_size + 1024**3:
    return None
  manifest = json.loads((model_path.parent / 'installed.json').read_text())
  if manifest['format'] != 'comma-generic-onnx':
    return None
  standby = model_factory(camera.width, camera.height, False, enable_shadow=False)
  warm_internal_model_from_camera(standby, camera)
  return standby


def warm_internal_model_from_camera(model, camera):
  # Synthetic inputs need one correctly allocated VisionIPC buffer, not a
  # synchronized live pair. The non-conflated extra stream can have an old
  # queue after the long external-model load; normal live pairing drains it.
  deadline = time.monotonic() + 2
  while time.monotonic() < deadline:
    buf = camera.recv()
    if buf is not None:
      warm_internal_model(model, dict.fromkeys(model.vision_input_names, buf))
      return
  raise RuntimeError('camera buffer unavailable for internal standby warmup')


def warm_internal_model(model, bufs):
  transforms = {name: np.eye(3, dtype=np.float32) for name in bufs}
  inputs = {'desire_pulse': np.zeros(8, np.float32), 'traffic_convention': np.array([1., 0.], np.float32),
            'action_t': np.zeros(2, np.float32)}
  shadow, model.signal_shadow = model.signal_shadow, None
  try:
    # Exercise warp, policy dispatch and synchronous readback. Constructing the
    # model alone leaves expensive first-use work on the future fallback path.
    for _ in range(3):
      if model.run(bufs, transforms, inputs, False) is None:
        raise RuntimeError('internal standby warmup produced no output')
  finally:
    model.reset()  # synthetic warmup must not become live recurrent history
    model.signal_shadow = shadow
