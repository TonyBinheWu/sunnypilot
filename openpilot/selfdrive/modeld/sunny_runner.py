"""An isolated, version-pinned runtime with two shared camera buffers and one in-flight request."""
import mmap
from multiprocessing.connection import Connection
import os
import socket
import subprocess
import sys
import tempfile

import numpy as np

from openpilot.common import sunny_models as catalog
from openpilot.system.camerad.cameras.nv12_info import get_nv12_info


class SunnyModelState:
  signal_shadow = None
  held_output = False
  vision_input_names = ('img', 'big_img')

  def __init__(self, width, height, key):
    entry = catalog.catalog()[key]
    self.usbgpu = entry['big']
    self.key = key
    self.process = self.shared = self.connection = None
    self.stride, y_height, _, self.size = get_nv12_info(width, height)
    self.dims, self.uv_offset = (width, height), self.stride * y_height
    try:
      with tempfile.TemporaryFile() as f:
        f.truncate(self.size * 2)
        self.shared = mmap.mmap(f.fileno(), self.size * 2)
        a, b = socket.socketpair()
        with a, b:
          self.connection = Connection(a.detach())
          self.process = subprocess.Popen([sys.executable, '-m', 'openpilot.selfdrive.modeld.sunny_worker', key,
                                           str(width), str(height), str(b.fileno()), str(f.fileno()), str(os.getpid())],
                                          pass_fds=(b.fileno(), f.fileno()))
        self.views = dict.fromkeys(self.receive(105))
    except BaseException:
      self.close()
      raise

  def receive(self, timeout):
    if not self.connection.poll(timeout):
      raise TimeoutError('sunnypilot model response timed out')
    ok, result = self.connection.recv()
    if not ok:
      raise RuntimeError(result)
    return result

  def reset(self):
    self.connection.send('reset')
    self.receive(2)

  def run(self, bufs, transforms, inputs, prepare_only):
    try:
      for i, key in enumerate(self.vision_input_names):
        buf = bufs[key]
        if (buf.width, buf.height) != self.dims or buf.stride != self.stride or buf.uv_offset != self.uv_offset:
          raise ValueError('Unexpected NV12 camera layout')
        data = np.frombuffer(buf.data, np.uint8, count=self.size)
        np.frombuffer(self.shared, np.uint8, self.size, i * self.size)[:] = data
      self.connection.send((transforms, inputs))
      result = self.receive(.15)
      return None if prepare_only else result
    except BaseException:
      self.close()
      raise

  def close(self):
    if self.process is not None:
      self.process.kill()
      try:
        self.process.wait(timeout=.1)
      except subprocess.TimeoutExpired:
        import threading
        threading.Thread(target=self.process.wait, daemon=True).start()
      self.process = None
    if self.connection is not None:
      self.connection.close()
      self.connection = None
    if self.shared is not None:
      self.shared.close()
      self.shared = None
