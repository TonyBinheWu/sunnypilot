"""Read-only VisionIPC and service capture. Importing opens no connections."""
import threading
import time

import numpy as np

from openpilot.selfdrive.alpamayo.frontend import Frame, STATE_LIMITS, finite_state

CP_FIELDS = ('mass', 'rotationalInertia', 'wheelbase', 'centerToFront', 'steerRatioRear',
             'tireStiffnessFront', 'tireStiffnessRear', 'steerRatio')

# Names inside the worker describe its inputs; wire names are owned by Carrot.
SERVICES = {'vehicleParameters': 'liveParameters', 'extrinsicsCalibration': 'liveCalibration', 'deviceMotion': 'livePose'}


def copy_vision_buffer(camera, client, buf, clock=time.monotonic_ns):
  received = clock()
  width, height, stride, uv_offset = int(buf.width), int(buf.height), int(buf.stride), int(buf.uv_offset)
  if (width, height) != (1344, 760) or stride < width or uv_offset < height*stride:
    raise ValueError('Qualify camera geometry before using a source other than 1344x760')
  raw = np.frombuffer(buf.data, dtype=np.uint8)
  if len(raw) < uv_offset+(height//2-1)*stride+width:
    raise ValueError('Truncated VisionIPC NV12 buffer')
  y = np.ndarray((height, width), np.uint8, buffer=raw, strides=(stride, 1))
  uv = np.ndarray((height//2, width), np.uint8, buffer=raw, offset=uv_offset, strides=(stride, 1))
  packed = np.concatenate((y, uv))
  packed.flags.writeable = False
  return Frame(camera, int(client.frame_id), int(client.timestamp_sof), int(client.timestamp_eof), received, clock(), packed, 'nv12')


def state_value(kind, msg):
  if kind == 'carState':
    return {k: float(getattr(msg, k)) for k in ('vEgo', 'steeringAngleDeg', 'aEgo')}, bool(msg.canValid)
  if kind == 'carParams':
    return {k: float(getattr(msg, k)) for k in CP_FIELDS}, True
  if kind == 'vehicleParameters':
    return {k: float(getattr(msg, k)) for k in ('stiffnessFactor', 'steerRatio', 'angleOffsetDeg', 'roll', 'centerToFrontRatio')}, bool(msg.valid and msg.sensorValid)
  if kind == 'extrinsicsCalibration':
    return {k: list(getattr(msg, k)) for k in ('rpyCalib', 'wideFromDeviceEuler')}, str(msg.calStatus) == 'calibrated'
  if kind == 'deviceMotion':
    value = [[float(getattr(msg.orientationNED, a)) for a in 'xyz'], [float(getattr(msg.velocityDevice, a)) for a in 'xyz']]
    return value, bool(msg.inputsOK and msg.sensorsOK and msg.posenetOK and msg.orientationNED.valid and msg.velocityDevice.valid and msg.timestamp > 0)
  if kind == 'navInstruction':
    value = {k: str(getattr(msg, k)) for k in ('maneuverPrimaryText', 'maneuverSecondaryText', 'maneuverType', 'maneuverModifier')}
    return dict(value, maneuverDistance=float(msg.maneuverDistance)), True
  if kind == 'modelV2':
    value = msg.to_dict()
    if value.get('alpamayoQueryMonoTime'):
      value['action'] = value['localAction']  # Preserve the independent small-model comparison.
    return value, True
  raise ValueError(kind)


class SmallModelOutput:
  """A received modelV2 event, converted to a dict only when it matches a query frame.

  Converting and checking every 20 Hz modelV2 took about 6.6 ms on a little core and held the GIL,
  delaying frame copies and slot selection. Only about 3% of slots find their matched output.
  """
  __slots__ = ('frame_id', 'eof_ns', 'raw')

  def __init__(self, raw, msg):
    self.frame_id, self.eof_ns, self.raw = int(msg.frameId), int(msg.timestampEof), raw

  def decode(self):
    """The recorded dict, or None when it is not finite JSON (the row is then invalid)."""
    from openpilot.cereal import messaging
    return finite_state(state_value('modelV2', messaging.log_from_bytes(self.raw).modelV2)[0])


class NativeProducer:
  def __init__(self, store):
    self.store = store
    self.stop = threading.Event()
    self.threads = []
    self.error = self.health = None

  def guarded(self, work, *args):
    try:
      work(*args)
    except Exception as exc:
      self.error = exc
      self.stop.set()

  def camera(self, camera, stream):
    from msgq.visionipc import VisionIpcClient
    while not self.stop.is_set():
      # camerad restarts with every ignition cycle; a warm supervisor reconnects after frames stop.
      client = VisionIpcClient('camerad', stream, True)
      while not self.stop.is_set() and not client.connect(False):
        self.stop.wait(.1)
      last = time.monotonic()
      while not self.stop.is_set() and time.monotonic()-last < 2.:
        buf = client.recv(100)
        if buf is not None:
          last = time.monotonic()
          self.store.add_frame(copy_vision_buffer(camera, client, buf))

  def states(self):
    from openpilot.cereal import messaging
    kinds = (*STATE_LIMITS, 'modelV2')
    # Every queued message, not only the latest: a delayed loop must not leave gaps in the measured motion history.
    socks = {kind: messaging.sub_sock(SERVICES.get(kind, kind)) for kind in kinds}
    sm = messaging.SubMaster(['modelV2', 'deviceState', 'roadCameraState', 'wideRoadCameraState'])
    while not self.stop.is_set():
      sm.update(0)
      received = time.monotonic_ns()
      for kind, sock in socks.items():
        raws = messaging.drain_sock_raw(sock)
        received = time.monotonic_ns()  # after the drain: no message is stamped later than its receipt
        for raw in raws:
          event = messaging.log_from_bytes(raw)
          msg = getattr(event, SERVICES.get(kind, kind))
          value, valid = (SmallModelOutput(raw, msg), True) if kind == 'modelV2' else state_value(kind, msg)
          stamp = int(msg.timestamp) if kind == 'deviceMotion' and msg.timestamp > 0 else int(event.logMonoTime)
          # state_value constructs detached Python values. The store can keep them without copying the full modelV2 again.
          self.store.add_state(kind, stamp, received, value, bool(event.valid and valid), owned=True)
      self.health = {'time_ns': received, 'model_alive': bool(sm.alive['modelV2'] and sm.valid['modelV2']),
                     'model_age_ns': received-int(sm.logMonoTime['modelV2']),
                     'device_valid': bool(sm.all_checks(['deviceState', 'roadCameraState', 'wideRoadCameraState']) and
                                          str(sm['deviceState'].deviceType) == 'mici' and
                                          all(str(sm[k].sensor) == 'os04c10' for k in ('roadCameraState', 'wideRoadCameraState'))),
                     'thermal_status': str(sm['deviceState'].thermalStatus)}
      self.stop.wait(.005)

  def start(self):
    from msgq.visionipc import VisionStreamType
    jobs = [(self.camera, (1, VisionStreamType.VISION_STREAM_WIDE_ROAD)),
            (self.camera, (6, VisionStreamType.VISION_STREAM_ROAD)), (self.states, ())]
    for work, args in jobs:
      thread = threading.Thread(target=self.guarded, args=(work, *args), daemon=True)
      self.threads.append(thread)
      thread.start()

  def close(self):
    self.stop.set()
    for thread in self.threads:
      thread.join(timeout=.5)


def device_healthy(health, now):
  return (health is not None and health['device_valid'] and 0 <= now-health['time_ns'] < 500_000_000 and
          health['thermal_status'] not in ('red', 'danger'))


def healthy(health, now):
  return device_healthy(health, now) and health['model_alive'] and 0 <= health['model_age_ns'] < 250_000_000
