"""sunnypilot plain artifact worker. Keep the selector's tinygrad out of the primary interpreter."""
import mmap
from multiprocessing.connection import Connection
import os
import sys
import threading
import time

from openpilot.common import sunny_models as library


def watch_parent(pid):
  while os.getppid() == pid:
    time.sleep(.2)
  os._exit(1)


def main():
  key, w, h, socket_fd, file_fd, parent = sys.argv[1:]
  threading.Thread(target=watch_parent, args=(int(parent),), daemon=True).start()
  conn = Connection(int(socket_fd))
  try:
    entry = library.catalog()[key]
    model = library.model_file(key)
    big = entry['big']
    warp = library.warp_directory() / f"{'big_' if big else ''}driving_warp_{w}x{h}_tinygrad.pkl"
    if library.digest(model) != entry['sha256'] or library.digest(warp) != library.WARPS[warp.name][0]:
      raise ValueError('sunnypilot model or camera kernel checksum mismatch')
    if big:
      from openpilot.selfdrive.modeld.precompiled_worker import claim_gpu_owner
      claim_gpu_owner()
    sys.path.insert(0, str(library.runtime()))
    os.environ.update(DEV='USB+AMD:LLVM' if big else 'QCOM', GMMU='0', JIT_BATCH_SIZE='0')
    import numpy as np
    from tinygrad import Device
    import tinygrad
    from pathlib import Path
    if not Path(tinygrad.__file__).resolve().is_relative_to(library.runtime().resolve()):
      raise RuntimeError('Incorrect tinygrad runtime')
    from openpilot.sunnypilot.modeld_v2.helpers import load_model, patch_fetch_fw
    patch_fetch_fw()
    from openpilot.sunnypilot.modeld_v2.frame_fusion import fused_with_warp
    from openpilot.sunnypilot.modeld_v2.model_adapters import get_model_adapter
    from openpilot.sunnypilot.modeld_v2.inference import Inference
    if big and not Device['AMD'].is_usb:
      raise RuntimeError('USB AMD backend required')
    device = 'AMD' if big else 'QCOM'
    jits = load_model(str(model), extend=fused_with_warp(int(w), int(h), big))
    adapter = get_model_adapter(jits, int(w), int(h), device, device, jits['metadata'].get('warp_dev',device), big)
    engine = Inference(adapter, entry)
    shared = mmap.mmap(int(file_fd), 0)
    size = len(shared) // 2
    frames = {name: np.frombuffer(shared, np.uint8, size, i * size)
              for i, name in enumerate((adapter._road_key, adapter._wide_key))}
    # Exercise the selected model's actual output contract before declaring it loadable.
    dummy = dict(desire_pulse=np.zeros(8), lateral_control_params=np.zeros(2), action_t=np.zeros(2), traffic_convention=np.array([1., 0.]))
    transforms = {name: np.eye(3, dtype=np.float32) for name in ('img', 'big_img')}
    engine.run(frames, transforms, dummy)
    engine.reset()
    conn.send((True, [k for k in ('nav_map', 'navigation') if k in adapter.numpy_inputs]))
    while True:
      cmd = conn.recv()
      if isinstance(cmd, str) and cmd == 'reset':
        engine.reset()
        conn.send((True, None))
      else:
        output = engine.run(frames, *cmd)
        if big and Device[device].error_state.host.view(fmt='q')[0]:
          raise RuntimeError('AMD runtime error')
        conn.send((True, output))
  except (EOFError, BrokenPipeError):
    pass
  except Exception as exc:
    conn.send((False, str(exc)))
  finally:
    conn.close()


if __name__ == '__main__':
  main()
