"""Pair a recorded ROAD frame and primary model output with a causal ego-motion window."""
from bisect import bisect_right
import math

from openpilot.selfdrive.navigation.helpers import nearby_maneuver


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


class MotionWindow:
  def __init__(self):
    self.times, self.motion = [], []
    self.speed = self.vehicle_down = None
    self.speed_time = self.calibration_time = 0

  def observe(self, kind, t, valid, data):
    point = None
    if kind == 'liveCalibration':
      self.vehicle_down = None
      self.calibration_time = t
      if valid and data.calStatus == 'calibrated' and len(data.rpyCalib) == 3 and all(map(math.isfinite, data.rpyCalib)):
        # z column of device_from_calib (Rz Ry Rx), used to rotate measured device rates to vehicle yaw.
        r, p, yaw = data.rpyCalib
        self.vehicle_down = (math.cos(yaw)*math.sin(p)*math.cos(r) + math.sin(yaw)*math.sin(r),
                             math.sin(yaw)*math.sin(p)*math.cos(r) - math.cos(yaw)*math.sin(r), math.cos(p)*math.cos(r))
        return
    elif kind == 'carState':
      self.speed_time = t
      self.speed = data.vEgo if valid and data.canValid and data.gearShifter == 'drive' and math.isfinite(data.vEgo) and data.vEgo >= 0 else None
      if self.speed is not None:
        return
    elif kind == 'livePose':
      pose, rate = data, data.angularVelocityDevice
      valid = (0 < pose.timestamp <= t and t-pose.timestamp <= 100_000_000 and valid and pose.inputsOK and pose.posenetOK and
               pose.sensorsOK and rate.valid and self.vehicle_down is not None and
               self.speed is not None and 0 <= t-self.speed_time <= 100_000_000 and 0 <= t-self.calibration_time <= 5_000_000_000 and
               all(map(math.isfinite, (rate.x, rate.y, rate.z))))
      if valid:
        point = (self.speed, sum(a*b for a,b in zip(self.vehicle_down, (rate.x,rate.y,rate.z), strict=True)))
    else:
      return
    if self.times and t < self.times[-1]:
      self.times.clear()
      self.motion.clear()
    self.times.append(t)
    self.motion.append(point)

  def trim(self, since):
    n = bisect_right(self.times, since)
    del self.times[:n]
    del self.motion[:n]

  def at(self, eof):
    return history_at(eof, self.times, self.motion)


def primary_action(m):
  if m.visionCameraInputs not in ('road', 'roadWide') or not m.timestampEof:
    return None
  if not all(map(math.isfinite, (m.action.desiredAcceleration, m.action.desiredCurvature))):
    return None
  return {'compute': str(m.visionCompute), 'desired_acceleration': m.action.desiredAcceleration,
          'desired_curvature': m.action.desiredCurvature, 'should_stop': m.action.shouldStop,
          'visual_lead': any(.7 <= lead.prob <= 1. and lead.x and 1.52 < lead.x[0] <= 120.
                             for lead in m.leadsV3)}


def recorded_pairs(events):
  indexes, primary, motion = {}, {}, MotionWindow()
  nav_events = []
  for msg in events:
    kind, t = msg.which(), msg.logMonoTime
    if kind in ('liveCalibration', 'carState', 'livePose'):
      motion.observe(kind, t, msg.valid, getattr(msg, kind))
    if kind in ('navInstructionCarrot', 'navRoute', 'mapRenderState', 'carState'):
      nav_events.append((t, kind, msg.valid, getattr(msg, kind)))
    if kind == 'roadEncodeIdx' and msg.valid and msg.roadEncodeIdx.type == 'fullHEVC':
      idx = msg.roadEncodeIdx
      key = (idx.frameId, idx.timestampEof)
      indexes[key] = None if key in indexes else (idx.segmentNum, idx.segmentId)
    elif kind == 'modelV2' and msg.valid:
      m = msg.modelV2
      if m.visionCameraInputs in ('road', 'roadWide') and m.timestampEof > 0:
        key = (m.frameId, m.timestampEof)
        primary[key] = None if key in primary else primary_action(m)
  segments = {idx[0] for idx in indexes.values() if idx is not None}
  if len(segments) != 1:
    return
  class NavSnapshot(dict):
    """Latest logged observations available at camera exposure, as in SubMaster."""
    def __init__(self):
      super().__init__()
      self.valid = {}
      self.logMonoTime = dict.fromkeys(('navInstructionCarrot', 'navRoute', 'mapRenderState', 'carState'), 0)

  snapshot = NavSnapshot()
  cursor = 0
  next_eof = 0
  for frame, eof in sorted(indexes.keys() & primary.keys(), key=lambda pair: pair[1]):
    key = (frame, eof)
    if eof < next_eof or indexes[key] is None or primary[key] is None:
      continue
    history = motion.at(eof)
    if history is not None:
      while cursor < len(nav_events) and nav_events[cursor][0] <= eof:
        t, kind, valid, value = nav_events[cursor]
        snapshot[kind], snapshot.valid[kind], snapshot.logMonoTime[kind] = value, valid, t
        cursor += 1
      turn = None
      if all(snapshot.valid.get(k) for k in snapshot.logMonoTime) and 0 <= eof - snapshot.logMonoTime['carState'] < 150_000_000:
        turn = nearby_maneuver(snapshot, eof, snapshot['carState'].vEgo)
      yield indexes[key][1], {'frame_id': frame, 'timestamp_eof_ns': eof, 'timestamp_us': eof//1000,
                              'egomotion': history, 'primary': {**primary[key], 'route_maneuver': turn}}
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
  kinds = {'liveCalibration', 'carState', 'livePose', 'roadEncodeIdx', 'modelV2', 'navRoute', 'navInstructionCarrot', 'mapRenderState'}
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
