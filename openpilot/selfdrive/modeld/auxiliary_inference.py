"""Run the second driving model off the publication thread, with a single owned camera pair."""
from types import SimpleNamespace
import math
import os
import threading
import time

import numpy as np


class AuxiliaryInference:
  def __init__(self, factory):
    self.runner = None
    self.gate = threading.Lock()
    self.wake = threading.Event()
    self.job = self.result = None
    self.last_used = -1
    self.status = 'loading'
    self.thread = threading.Thread(target=self.work, args=(factory,), name='aux-driving-inference', daemon=True)
    self.thread.start()

  def work(self, factory):
    runner = None
    try:
      if hasattr(os, 'sched_setscheduler'):
        os.sched_setscheduler(0, os.SCHED_OTHER, os.sched_param(0))
        # Use a different online CPU from modeld's dedicated publication core on AGNOS.
        if os.path.exists('/AGNOS'):
          os.sched_setaffinity(0, {4,5,6})
      runner = factory()
      self.runner, self.status = runner, 'warming'
      next_status = 0.
      previous = -1
      count = 0
      while True:
        self.wake.wait()
        frames, transforms, inputs, frame, eof = self.job
        try:
          self.wake.clear()
          output = runner.run(frames, transforms, inputs, False)
          timely = 0 <= time.monotonic() - eof < .12 and output is not None and not getattr(runner, 'held_output', False)
          count = (count + 1 if previous + 1 == frame else 1) if timely else 0
          previous = frame
          # A full five seconds of uninterrupted 20 Hz history before contributing.
          self.result = (frame, eof, summarize(output, inputs['action_t'][1])) if count >= 100 else None
          self.status = 'ready' if self.result else 'warming' if timely else 'late'
          if time.monotonic() >= next_status:
            publish_status(self.status, eof, time.monotonic()-eof, 'nav_map' in getattr(runner, 'views', {}))
            next_status = time.monotonic()+1.
        finally:
          self.job = None
          self.gate.release()
    except Exception:
      from openpilot.common.swaglog import cloudlog
      cloudlog.exception('Auxiliary driving inference unavailable')
    finally:
      self.runner, self.result, self.status = None, None, 'unavailable'
      publish_status(self.status, time.monotonic(), None)
      if runner is not None:
        runner.close()

  def submit(self, frames, transforms, inputs, frame, eof):
    if self.runner is None or not self.gate.acquire(blocking=False):
      return
    try:
      # VisionIPC reuses these buffers as soon as modeld receives its next frame.
      copies = {name: SimpleNamespace(data=bytes(buf.data), width=buf.width, height=buf.height, stride=buf.stride,
                                      uv_offset=buf.uv_offset) for name, buf in frames.items()}
      self.job = copies, {k: v.copy() for k, v in transforms.items()}, {k: v.copy() for k,v in inputs.items()}, frame, eof
      self.wake.set()
    except Exception:
      self.gate.release()
      self.result = None

  def acceleration(self, primary, action, frame, eof, now, permitted, action_t):
    result = self.result
    if not permitted or action.shouldStop or not result or not 0 <= frame - result[0] <= 1 or self.last_used >= result[0]:
      return action.desiredAcceleration
    self.last_used = result[0]
    if not (0 <= eof - result[1] <= .08 and 0 <= now - result[1] <= .12):
      return action.desiredAcceleration
    return refine(action.desiredAcceleration, summarize(primary, action_t), result[2])


def publish_status(state, eof, latency, nav=False):
  from openpilot.common import sunny_models
  from openpilot.common.big_model_catalog import atomic_json
  try:
    atomic_json(sunny_models.AUX_STATUS, {'state': state, 'eof': eof, 'latency': latency, 'nav': nav})
  except OSError:
    pass


def summarize(output, action_t):
  from openpilot.selfdrive.modeld.constants import ModelConstants
  plan = output['plan'][0]
  accel = output['action'][0, 1] if 'action' in output else np.interp(action_t, ModelConstants.T_IDXS, plan[:, 6])
  return (float(accel), *(float(np.interp(t, ModelConstants.T_IDXS, plan[:, axis])) for t, axis in ((1,1),(2,1),(1,3))))


def refine(current, primary, auxiliary):
  # Only refine existing moderate braking when independent motion plans agree.
  if not all(map(math.isfinite, (current, *primary, *auxiliary))) or not (-2.5 < current < -.15 and -2.5 < primary[0] < -.15):
    return current
  if not (-3 < auxiliary[0] < current and abs(primary[0]-auxiliary[0]) < 1.0):
    return current
  if abs(primary[1]-auxiliary[1]) > .5 or abs(primary[2]-auxiliary[2]) > .8 or abs(primary[3]-auxiliary[3]) > 1.:
    return current
  return max(current - .15, current + .25 * (auxiliary[0] - current))
