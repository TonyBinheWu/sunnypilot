"""One low-priority, single-threaded FFmpeg encoder per requested camera."""
import os
from pathlib import Path
import select
import subprocess
import time

from openpilot.sunnypilot.formosalink.media_protocol import MAX_JPEG_BYTES


def nv12_bytes(frame):
  import numpy as np
  width, height, stride = frame.width, frame.height, frame.stride
  if not (0 < width <= 4096 and 0 < height <= 2160 and width % 2 == height % 2 == 0 and width <= stride <= 8192):
    raise ValueError('invalid native camera layout')
  y = np.frombuffer(frame.data, dtype=np.uint8, count=stride*height).reshape(height, stride)[:, :width]
  uv = np.frombuffer(frame.data, dtype=np.uint8, count=stride*(height//2), offset=frame.uv_offset).reshape(height//2, stride)[:, :width]
  return y.tobytes()+uv.tobytes()


class StreamEncoder:
  def __init__(self):
    self.process, self.layout = None, None

  def close(self):
    process, self.process = self.process, None
    if process is not None:
      if process.poll() is None:
        process.terminate()
        try:
          process.wait(timeout=1)
        except subprocess.TimeoutExpired:
          process.kill()
          process.wait(timeout=1)
      process.stdin.close()
      process.stdout.close()

  def __call__(self, frame):
    import ffmpeg
    layout = (frame.width, frame.height)
    data = nv12_bytes(frame)
    if self.process is None or self.process.poll() is not None or layout != self.layout:
      self.close()
      # nice affects this encoder only; never lower priority of camera/model/control processes.
      command = ['nice', '-n', '10', str(Path(ffmpeg.BIN_DIR)/'ffmpeg'), '-hide_banner', '-loglevel', 'error',
                 '-threads', '1', '-f', 'rawvideo', '-pix_fmt', 'nv12', '-s', f'{layout[0]}x{layout[1]}',
                 '-r', '8', '-probesize', '32', '-analyzeduration', '0', '-i', 'pipe:0', '-vf', 'scale=640:360:force_original_aspect_ratio=decrease:force_divisible_by=2',
                 '-filter_threads', '1', '-threads', '1', '-q:v', '8', '-vcodec', 'mjpeg',
                 '-f', 'image2', '-update', '1', '-flush_packets', '1', 'pipe:1']
      self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
      self.layout = layout
      os.set_blocking(self.process.stdin.fileno(), False)
      os.set_blocking(self.process.stdout.fileno(), False)
    deadline = time.monotonic()+1.5
    try:
      view = memoryview(data)
      while view:
        if not select.select([], [self.process.stdin], [], max(0, deadline-time.monotonic()))[1]:
          raise TimeoutError('encoder input timeout')
        view = view[os.write(self.process.stdin.fileno(), view[:65536]):]
      output = bytearray()
      while not output.endswith(b'\xff\xd9'):
        if not select.select([self.process.stdout], [], [], max(0, deadline-time.monotonic()))[0]:
          raise TimeoutError('encoder output timeout')
        chunk = os.read(self.process.stdout.fileno(), 65536)
        if not chunk:
          raise ValueError('encoder stopped')
        output.extend(chunk)
        if len(output) > MAX_JPEG_BYTES:
          raise ValueError('oversized encoded frame')
      return bytes(output)
    except Exception:
      self.close()
      raise
