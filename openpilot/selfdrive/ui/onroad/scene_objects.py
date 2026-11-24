"""Display-only ROAD camera classifications. No control services consume this data."""
import json
import math
import os
from pathlib import Path
import time

import numpy as np

PACKET = Path('/dev/shm/driving-scene-objects.json')
MODEL = Path(__file__).resolve().parents[2] / 'carrot/web/vendor/bev-detector/efficientdet_lite0.tflite'
CLASSES = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}


def anchors():
  # Fixed anchors embedded in this EfficientDet-Lite0's MediaPipe metadata.
  values = []
  for count in (40, 20, 10, 5, 3):
    for row in range(count):
      for col in range(count):
        for scale in (1., 2**(1/3), 2**(2/3)):
          size = 3 * scale / count
          for aspect in (1., math.sqrt(2), 1/math.sqrt(2)):
            values.append(((col + .5)/count, (row + .5)/count, size*aspect, size/aspect))
  return np.array(values, dtype=np.float32)


class RoadDetector:
  def __init__(self):
    import cv2
    self.net = cv2.dnn.readNetFromTFLite(np.fromfile(MODEL, dtype=np.uint8))
    self.anchors = anchors()

  def detect(self, bgr):
    import cv2
    self.net.setInput(cv2.dnn.blobFromImage(bgr, 1., (320, 320), swapRB=True))
    scores, offsets = self.net.forward(['StatefulPartitionedCall:1', 'StatefulPartitionedCall:0'])
    labels = scores[0].argmax(axis=1)
    conf = scores[0, np.arange(len(labels)), labels]
    keep = (conf >= .5) & np.isin(labels, list(CLASSES))
    if not keep.any():
      return []
    xy, wh = np.split(self.anchors[keep], 2, axis=1)
    dy, dx, dh, dw = offsets[0, keep].T
    center = xy + np.column_stack((dx, dy)) * wh
    extent = np.exp(np.clip(np.column_stack((dw, dh)), -5, 5)) * wh
    boxes = np.column_stack((center - extent / 2, extent))
    labels, conf = labels[keep], conf[keep]
    indices = cv2.dnn.NMSBoxesBatched(boxes.tolist(), conf.tolist(), labels.tolist(), .49, .45)
    return [(CLASSES[labels[i]], boxes[i]) for i in np.asarray(indices).flatten()[:24]]


def project(box, size, inverse, height):
  x, y, w, h = box
  u, v = x + w / 2, y + h
  if not (w > 0 and h > 0 and 0 < u < 1 and 0 < v < .99):
    return None
  ray = inverse @ (u * size[0], v * size[1], 1.)
  if not np.isfinite(ray).all() or ray[2] <= .01:
    return None
  forward, lateral = ray[:2] * (height / ray[2])
  if 1 <= forward <= 65 and abs(lateral) <= 18:
    return float(forward), float(lateral)
  return None


def read_objects(now):
  try:
    with PACKET.open('rb') as f:
      packet = json.loads(f.read(4096))
    if not 0 <= now - packet['eof'] * 1e-9 < .65:
      return ()
    return tuple((kind, d, y) for kind, d, y in packet['objects'][:24]
                 if kind in CLASSES.values() and 1 <= d <= 65 and abs(y) <= 18)
  except (OSError, ValueError, TypeError, KeyError):
    return ()


def main():
  import cv2
  from msgq.visionipc import VisionIpcClient, VisionStreamType
  from openpilot.cereal import messaging
  from openpilot.common.transformations.camera import DEVICE_CAMERAS, view_frame_from_device_frame
  from openpilot.common.transformations.orientation import rot_from_euler

  os.nice(15)
  cores = os.sched_getaffinity(0) & {0, 1, 2, 3}
  if cores:
    os.sched_setaffinity(0, cores)
  cv2.setNumThreads(1)
  detector = RoadDetector()
  sm = messaging.SubMaster(['liveCalibration', 'deviceState', 'roadCameraState'])
  camera = VisionIpcClient('camerad', VisionStreamType.VISION_STREAM_ROAD, True)
  while not camera.connect(False):
    time.sleep(.5)
  temporary = PACKET.with_suffix('.tmp')
  while True:
    time.sleep(.25)
    buf = camera.recv(timeout_ms=50)
    sm.update(0)
    if buf is None or not all(sm.valid[s] and sm.alive[s] for s in ('liveCalibration', 'deviceState', 'roadCameraState')):
      continue
    eof = camera.timestamp_eof
    if not 0 <= time.monotonic() - eof * 1e-9 < .25:
      continue
    calib = sm['liveCalibration']
    config = DEVICE_CAMERAS.get((str(sm['deviceState'].deviceType), str(sm['roadCameraState'].sensor)))
    if (config is None or (buf.width, buf.height) != (config.fcam.width, config.fcam.height) or calib.calStatus != 'calibrated'
        or len(calib.height) != 1 or not .5 <= calib.height[0] <= 3 or len(calib.rpyCalib) != 3
        or not np.isfinite(calib.rpyCalib).all()):
      continue
    inverse = np.linalg.inv(config.fcam.intrinsics @ view_frame_from_device_frame @ rot_from_euler(calib.rpyCalib))
    raw = np.frombuffer(buf.data, dtype=np.uint8)
    rows, stride, uv = buf.height, buf.stride, buf.uv_offset
    y = raw[:rows*stride].reshape(rows, stride)[:, :buf.width]
    chroma = raw[uv:uv+rows//2*stride].reshape(rows//2, stride//2, 2)[:, :buf.width//2]
    image = cv2.cvtColorTwoPlane(cv2.resize(y, (320, 320)), cv2.resize(chroma, (160, 160)), cv2.COLOR_YUV2BGR_NV12)
    objects = []
    for kind, box in detector.detect(image):
      position = project(box, (buf.width, rows), inverse, calib.height[0])
      if position:
        objects.append((kind, *position))
    temporary.write_text(json.dumps({'frame': camera.frame_id, 'eof': eof, 'objects': objects}))
    temporary.replace(PACKET)


if __name__ == '__main__':
  main()
