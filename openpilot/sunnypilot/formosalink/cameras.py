"""Owner-requested live streams from existing camera IPC; no control writes."""
import base64
import json
import logging
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import uuid

from openpilot.sunnypilot.formosalink.identity import read
from openpilot.sunnypilot.formosalink.protocol import sign

CAMERAS = ("wide-road", "driver")


def camera_clock():
  # camerad's C++ nanos_since_boot() includes suspend time on Linux.
  # Python monotonic() does not; comparing them rejects every post-resume frame.
  if hasattr(time, "CLOCK_BOOTTIME"):
    return time.clock_gettime(time.CLOCK_BOOTTIME)
  return time.monotonic()


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
  uv = np.frombuffer(frame.data, dtype=np.uint8, count=stride*(height//2), offset=getattr(frame, "uv_offset", stride*height)).reshape(height//2,stride)[:,:width]
  command = [str(Path(ffmpeg.BIN_DIR)/"ffmpeg"), "-hide_banner", "-loglevel", "error", "-threads", "1",
             "-f", "rawvideo", "-pix_fmt", "nv12", "-s", f"{width}x{height}", "-i", "pipe:0",
             "-frames:v", "1", "-vf", "scale=640:360:force_original_aspect_ratio=decrease:force_divisible_by=2",
             "-filter_threads", "1", "-threads", "1", "-q:v", "6", "-f", "image2", "-update", "1", "-vcodec", "mjpeg", "pipe:1"]
  return subprocess.run(command, input=y.tobytes()+uv.tobytes(), capture_output=True, check=True, timeout=2).stdout


class NativeCamera:
  def __init__(self, camera, name="camerad", encoder=encode_nv12):
    from msgq.visionipc import VisionIpcClient
    try:
      from msgq.visionipc import VisionStreamType
    except ImportError:
      from openpilot.cereal.visionipc import VisionStreamType
    stream = VisionStreamType.VISION_STREAM_WIDE_ROAD if camera == "wide-road" else (VisionStreamType.VISION_STREAM_DRIVER if hasattr(VisionStreamType, "VISION_STREAM_DRIVER")
                 else VisionStreamType.VISION_STREAM_CABIN)
    self._client_args = (name, stream, True)
    self.client = VisionIpcClient(*self._client_args)
    self.encoder = encoder

  def close(self):
    if hasattr(self.encoder, 'close'):
      self.encoder.close()

  def __call__(self):
    if not self.client.is_connected() and not self.client.connect(False):
      raise ValueError("camera unavailable")
    frame = self.client.recv(50)
    captured = self.client.timestamp_eof/1e9
    age = camera_clock()-captured
    if frame is None or not 0 <= age < 1:
      from msgq.visionipc import VisionIpcClient
      self.client = VisionIpcClient(*self._client_args)
      raise ValueError("camera frame unavailable")
    data = self.encoder(frame)
    return data, time.time()-(camera_clock()-captured), {"speed_kph":None, "engaged":None}


def stream_camera(identity, private, camera, stop):
  import websocket
  from openpilot.sunnypilot.formosalink.stream_encoder import StreamEncoder
  from openpilot.sunnypilot.formosalink.media_protocol import jpeg_size, validate_frame
  source, last_warning = None, None
  url = identity['origin'].replace('https://', 'wss://', 1).replace('http://', 'ws://', 1)+'/api/v1/agent/media/stream'
  try:
    while not stop.is_set():
      try:
        if source is None:
          source = NativeCamera(camera, encoder=StreamEncoder())
        # TLS certificate checks stay enabled. The signed handshake never enters a URL.
        with websocket.create_connection(url, timeout=2, suppress_origin=True) as socket:
          socket.send(json.dumps(sign(private, identity['device_id'], 'media-stream', {'camera':camera})))
          ready = json.loads(socket.recv())
          if ready != {'type':'ready', 'fps':8, 'transport':'wss-mjpeg-v1'}:
            raise ValueError('invalid stream acknowledgement')
          stream, sequence = str(uuid.uuid4()), 0
          while not stop.is_set():
            started = time.monotonic()
            data, sampled, hud = source()
            width, height = jpeg_size(data)
            frame = validate_frame({'version':1, 'stream':stream, 'sequence':sequence, 'sampled_at':sampled,
              'source':camera, 'width':width, 'height':height, 'jpeg':base64.b64encode(data).decode('ascii'), 'hud':hud})
            socket.send(json.dumps(frame, separators=(',', ':')))
            reply = socket.recv()
            if len(reply) > 2048 or json.loads(reply) != {'type':'ack', 'sequence':sequence}:
              raise ValueError('invalid frame acknowledgement')
            sequence += 1
            stop.wait(max(0, .125-(time.monotonic()-started)))
      except Exception as exc:
        now = time.monotonic()
        if last_warning is None or now-last_warning >= 30:
          logging.getLogger('formosalink-cameras').warning('Camera %s stream unavailable (%s)', camera, type(exc).__name__)
          last_warning = now
        if source is not None:
          source.close()
        stop.wait(2)
  finally:
    if source is not None:
      source.close()


def run(directory, stop):
  import requests
  workers, current_id = {}, None

  def retire(camera):
    event, thread = workers.pop(camera)
    event.set()
    thread.join(timeout=5)

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
          for camera in list(workers):
            retire(camera)
          current_id = identity["device_id"]
        for camera in set(workers)-set(demand['cameras']):
          retire(camera)
        for camera in demand["cameras"]:
          if stop.is_set():
            break
          if camera in workers and not workers[camera][1].is_alive():
            retire(camera)
          if camera not in workers:
            event = threading.Event()
            thread = threading.Thread(target=stream_camera, args=(identity, private, camera, event), daemon=True,
                                      name='formosalink-stream-'+camera)
            workers[camera] = event, thread
            thread.start()
      except Exception:
        for camera in list(workers):
          retire(camera)
        try:
          save_lease([])
        except OSError:
          pass
      stop.wait(2)
    for camera in list(workers):
      retire(camera)
    save_lease([])


def start(directory, stop):
  thread = threading.Thread(target=run,args=(directory,stop),name="formosalink-cameras",daemon=True)
  thread.start()
  return thread
