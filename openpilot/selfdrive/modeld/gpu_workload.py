"""Publish owner-side allocator and completed inference timing when the local resource view is open."""
import json
import os
import time
from pathlib import Path

ROOT = Path("/dev/shm")
WATCH = ROOT / "carrot-resource-view"


class GpuWorkload:
  def __init__(self, backend, model, role="primary"):
    self.backend, self.model = backend, str(model)[:128]
    self.start = time.monotonic()
    self.work = 0.
    self.path = ROOT / f"carrot-gpu-work-{role}.json"

  def completed(self, started, finished):
    self.work += max(0., finished - started)
    window = finished - self.start
    if window < 1.:
      return
    busy = round(min(100., self.work * 100 / window), 1)
    self.start, self.work = finished, 0.
    try:
      if not 0 <= time.time() - WATCH.stat().st_mtime <= 6:
        return
      dev = getattr(getattr(self.backend, "iface", None), "dev_impl", None)
      total = getattr(dev, "vram_size", None)
      allocator = getattr(getattr(dev, "mm", None), "pa_allocator", None)
      free = sum(size for size, _, _, unused in allocator.blocks.values() if unused) if allocator is not None else None
      row = dict(pid=os.getpid(), model=self.model, arch=str(self.backend.arch), at=finished,
                 worker_busy=busy, total_bytes=total, free_bytes=free)
      tmp = self.path.with_suffix(f".{os.getpid()}.tmp")
      tmp.write_text(json.dumps(row))
      tmp.replace(self.path)
    except (OSError, AttributeError, TypeError, ValueError, RuntimeError):
      pass  # Display sampling must never interrupt the producer.
