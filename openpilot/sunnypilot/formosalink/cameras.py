"""Owner-requested, low-rate previews from existing camera IPC; no control writes."""
import json
import logging
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time

from openpilot.sunnypilot.formosalink.identity import read
from openpilot.sunnypilot.formosalink.protocol import sign

CAMERAS = ("wide-road", "driver")


def lease_path():
  return Path(os.environ.get("FORMOSALINK_CAMERA_LEASE", "/dev/shm/formosalink-camera.json"))


def camera_requested():
  try:
    value = json.loads(lease_path().read_text())
    remaining = value["until"]-time.monotonic()
    return bool(0 < remaining <= 16 and value["cameras"] and set(value["cameras"]) <= set(CAMERAS))
  except (OSError, ValueError, KeyError, TypeError):
    return False


def save_lease(cameras, seconds=15):
  path = lease_path()
  if not cameras:
    path.unlink(missing_ok=True)
    return
  if set(cameras)-set(CAMERAS) or type(seconds) is not int or not 1 <= seconds <= 15:
    raise ValueError("invalid camera lease")
  name = None
  try:
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
      name = stream.name
      json.dump({"until":time.monotonic()+seconds, "cameras":cameras}, stream)
    os.replace(name, path)
  finally:
    if name:
      Path(name).unlink(missing_ok=True)


def encode_nv12(frame):
  import numpy as np
  import ffmpeg
  width, height, stride = frame.width, frame.height, frame.stride
  if not (0 < width <= 4096 and 0 < height <= 2160 and width%2 == height%2 == 0 and width <= stride <= 8192):
    raise ValueError("invalid native camera layout")
  # Strip each plane's padding. Never modify the shared camera buffer.
  y = np.frombuffer(frame.data, dtype=np.uint8, count=stride*height).reshape(height,stride)[:,:width]
  uv = np.frombuffer(frame.data, dtype=np.uint8, count=stride*(height//2), offset=frame.uv_offset).reshape(height//2,stride)[:,:width]
  command = [str(Path(ffmpeg.BIN_DIR)/"ffmpeg"), "-hide_banner", "-loglevel", "error", "-threads", "1",
             "-f", "rawvideo", "-pix_fmt", "nv12", "-s", f"{width}x{height}", "-i", "pipe:0",
             "-frames:v", "1", "-vf", "scale=640:360:force_original_aspect_ratio=decrease:force_divisible_by=2",
             "-filter_threads", "1", "-threads", "1", "-q:v", "6", "-f", "image2", "-update", "1", "-vcodec", "mjpeg", "pipe:1"]
  return subprocess.run(command, input=y.tobytes()+uv.tobytes(), capture_output=True, check=True, timeout=2).stdout


class NativeCamera:
  def __init__(self, camera, name="camerad"):
    from msgq.visionipc import VisionIpcClient
    from openpilot.cereal.visionipc import VisionStreamType
    stream = VisionStreamType.VISION_STREAM_WIDE_ROAD if camera == "wide-road" else VisionStreamType.VISION_STREAM_CABIN
    self._client_args = (name, stream, True)
    self.client = VisionIpcClient(*self._client_args)

  def __call__(self):
    if not self.client.is_connected() and not self.client.connect(False):
      raise ValueError("camera unavailable")
    frame = self.client.recv(50)
    captured = self.client.timestamp_eof/1e9
    age = time.monotonic()-captured
    if frame is None or not 0 <= age < 1:
      from msgq.visionipc import VisionIpcClient
      self.client = VisionIpcClient(*self._client_args)
      raise ValueError("camera frame unavailable")
    data = encode_nv12(frame)
    return data, time.time()-(time.monotonic()-captured), {"speed_kph":None, "engaged":None}


def run(directory, stop):
  import requests
  from openpilot.sunnypilot.formosalink.media_agent import PreviewPublisher
  publishers, current_id = {}, None
  log = logging.getLogger("formosalink-cameras")
  with requests.Session() as session:
    while not stop.is_set():
      try:
        identity, private, _ = read(directory)
        response = session.post(identity["origin"]+"/api/v1/agent/media/watch",
                                json=sign(private,identity["device_id"],"media-watch"), timeout=3)
        response.raise_for_status()
        if len(response.content) > 2048:
          raise ValueError("oversized camera request")
        demand = response.json()
        if set(demand) != {"cameras", "seconds"} or not isinstance(demand["cameras"],list):
          raise ValueError("invalid camera request")
        save_lease(demand["cameras"], demand["seconds"])
        if current_id != identity["device_id"]:
          publishers.clear()
          current_id = identity["device_id"]
        publishers = {key:value for key,value in publishers.items() if key in demand["cameras"]}
        for camera in demand["cameras"]:
          if stop.is_set():
            break
          try:
            if camera not in publishers:
              publishers[camera] = PreviewPublisher(identity,private,NativeCamera(camera),camera=camera)
            publishers[camera].once(session)
          except Exception as exc:
            log.debug("Camera preview unavailable (%s)", type(exc).__name__)
      except Exception:
        publishers.clear()
        try:
          save_lease([])
        except OSError:
          pass
      stop.wait(2)
    save_lease([])


def start(directory, stop):
  thread = threading.Thread(target=run,args=(directory,stop),name="formosalink-cameras",daemon=True)
  thread.start()
  return thread
