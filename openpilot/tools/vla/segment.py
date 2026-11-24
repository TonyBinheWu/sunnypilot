"""Pair a recorded ROAD frame and primary model output with a causal ego-motion window."""
from bisect import bisect_right
import math


def history_at(eof, times, motion):
  # Vehicle yaw rate is clockwise about down. The VLA's local y axis points left.
  poses = [(0., 0., 0.)]
  x = y = heading = 0.
  for step in range(40):
    tick = eof - (40-step) * 50_000_000
    i = bisect_right(times, tick) - 1
    if i < 0 or tick-times[i] > 100_000_000 or motion[i] is None:
      return None
    speed, yaw_right = motion[i]
    dtheta = -.05 * yaw_right
    x += .05 * speed * math.cos(heading + dtheta/2)
    y += .05 * speed * math.sin(heading + dtheta/2)
    heading += dtheta
    if (step+1) % 5 == 0:
      poses.append((x,y,heading))
  # Require a valid terminal observation as well, including any disengaged sensor/gear interval.
  j = bisect_right(times, eof)-1
  window = motion[bisect_right(times, eof-2_000_000_000):j+1]
  if j < 0 or eof-times[j] > 100_000_000 or motion[j] is None or any(point is None for point in window):
    return None
  c, s = math.cos(heading), math.sin(heading)
  return [[(px-x)*c + (py-y)*s, -(px-x)*s + (py-y)*c, math.remainder(yaw-heading, math.tau)] for px,py,yaw in poses]


def recorded_pairs(events):
  indexes, primary, motion, times = {}, {}, [], []
  speed = vehicle_down = None
  speed_time = calibration_time = 0
  for msg in events:
    kind, t = msg.which(), msg.logMonoTime
    if kind == 'liveCalibration':
      cal = msg.liveCalibration
      vehicle_down = None
      calibration_time = t
      if msg.valid and cal.calStatus == 'calibrated' and len(cal.rpyCalib) == 3 and all(map(math.isfinite, cal.rpyCalib)):
        # z column of device_from_calib (Rz Ry Rx), used to rotate measured device rates to vehicle yaw.
        r, p, yaw = cal.rpyCalib
        vehicle_down = (math.cos(yaw)*math.sin(p)*math.cos(r) + math.sin(yaw)*math.sin(r),
                      math.sin(yaw)*math.sin(p)*math.cos(r) - math.cos(yaw)*math.sin(r), math.cos(p)*math.cos(r))
      if vehicle_down is None:
        times.append(t)
        motion.append(None)
    elif kind == 'carState':
      cs = msg.carState
      speed = cs.vEgo if msg.valid and cs.canValid and cs.gearShifter == 'drive' and math.isfinite(cs.vEgo) and cs.vEgo >= 0 else None
      speed_time = t
      if speed is None:
        times.append(t)
        motion.append(None)
    elif kind == 'livePose':
      pose, rate = msg.livePose, msg.livePose.angularVelocityDevice
      valid = (0 < pose.timestamp <= t and t-pose.timestamp <= 100_000_000 and msg.valid and pose.inputsOK and pose.posenetOK and
               pose.sensorsOK and rate.valid and vehicle_down is not None and
               speed is not None and 0 <= t-speed_time <= 100_000_000 and 0 <= t-calibration_time <= 5_000_000_000 and
               all(map(math.isfinite, (rate.x, rate.y, rate.z))))
      times.append(t)
      motion.append((speed, sum(a*b for a,b in zip(vehicle_down,(rate.x,rate.y,rate.z), strict=True))) if valid else None)
    elif kind == 'roadEncodeIdx' and msg.valid and msg.roadEncodeIdx.type == 'fullHEVC':
      idx = msg.roadEncodeIdx
      key = (idx.frameId, idx.timestampEof)
      indexes[key] = None if key in indexes else (idx.segmentNum, idx.segmentId)
    elif kind == 'modelV2' and msg.valid:
      m = msg.modelV2
      if m.visionCameraInputs in ('road', 'roadWide') and m.timestampEof > 0:
        key = (m.frameId, m.timestampEof)
        action = {'compute': str(m.visionCompute), 'desired_acceleration': m.action.desiredAcceleration,
                  'desired_curvature': m.action.desiredCurvature, 'should_stop': m.action.shouldStop}
        primary[key] = None if key in primary or not all(math.isfinite(action[k]) for k in ('desired_acceleration','desired_curvature')) else action
  segments = {idx[0] for idx in indexes.values() if idx is not None}
  if len(segments) != 1:
    return
  next_eof = 0
  for frame, eof in sorted(indexes.keys() & primary.keys(), key=lambda pair: pair[1]):
    key = (frame, eof)
    if eof < next_eof or indexes[key] is None or primary[key] is None:
      continue
    history = history_at(eof, times, motion)
    if history is not None:
      yield indexes[key][1], {'frame_id': frame, 'timestamp_eof_ns': eof, 'timestamp_us': eof//1000,
                              'egomotion': history, 'primary': primary[key]}
      next_eof = eof + 1_000_000_000


def segment_samples(directory):
  import bz2
  import cv2
  import zstandard
  from openpilot.cereal import log
  from openpilot.tools.vla.replay import resize_road
  logs = [p for p in (directory/'rlog', directory/'rlog.bz2', directory/'rlog.zst') if p.is_file()]
  video = directory/'fcamera.hevc'
  if len(logs) != 1 or not video.is_file():
    raise ValueError('Expected one local segment with its rlog and fcamera.hevc')
  with logs[0].open('rb') as source:
    if logs[0].suffix == '.zst':
      with zstandard.ZstdDecompressor().stream_reader(source) as stream:
        data = stream.read()
    elif logs[0].suffix == '.bz2':
      with bz2.BZ2File(source) as stream:
        data = stream.read()
    else:
      data = source.read()
  kinds = {'liveCalibration', 'carState', 'livePose', 'roadEncodeIdx', 'modelV2'}
  events = sorted((msg for msg in log.Event.read_multiple_bytes(data) if msg.which() in kinds), key=lambda msg: msg.logMonoTime)
  reader = cv2.VideoCapture(str(video.resolve()))
  index = -1
  try:
    if not reader.isOpened():
      raise ValueError('Cannot open the recorded front camera')
    for target, row in recorded_pairs(events):
      if target <= index:
        raise ValueError('Nonmonotonic recorded frame index')
      while index < target:
        if not reader.grab():
          raise ValueError('Video ended before its recorded frame index')
        index += 1
      ok, bgr = reader.retrieve()
      if not ok:
        raise ValueError('Could not decode the indexed road frame')
      yield row, resize_road(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
  finally:
    reader.release()
