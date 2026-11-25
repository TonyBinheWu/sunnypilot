"""Independent ROAD / modelV2 observer for a C4 with a dedicated Chestnut."""
import os
import socket
import subprocess
import sys
import time
from collections import deque
from multiprocessing.connection import Connection
from pathlib import Path

from openpilot.selfdrive.modeld.vla_status import TTL_NS, WEIGHTS, camera_clock, compare, write_status
from openpilot.tools.vla.segment import MotionWindow, primary_action

INPUT_NS = 150_000_000


def require_target(device):
  # The pinned and branch tinygrad versions expose is_usb as a property and a method, respectively.
  usb = device.is_usb() if callable(device.is_usb) else device.is_usb
  if not usb or device.arch != 'gfx1200' or device.iface.dev_impl.vram_size != 8 << 30:
    raise RuntimeError('Expected Chestnut gfx1200 with 8 GiB of VRAM')


def gpu_worker(channel, parent):
  import ctypes
  import signal
  # Reap the device and lock even when the manager kills the supervisor during a native call.
  if ctypes.CDLL(None).prctl(1, signal.SIGKILL, 0, 0, 0) or os.getppid() != parent:
    return
  try:
    Path('/proc/self/oom_score_adj').write_text('800')
    from openpilot.selfdrive.modeld.precompiled_worker import claim_gpu_owner
    from openpilot.tools.vla.replay import decode, load_native, verify
    verify(WEIGHTS)
    claim_gpu_owner()
    from tinygrad import Device
    require_target(Device['AMD'])
    _, predict = load_native(WEIGHTS, 'AMD')
    channel.send(('ready', None))
    while True:
      key, rgb, history = channel.recv()
      channel.send((key, decode(predict(rgb, history))))
  except (EOFError, BrokenPipeError):
    pass
  except Exception:
    import traceback
    traceback.print_exc()
    channel.send(('error', None))
  finally:
    channel.close()


def copy_road(buf, frame_id):
  import numpy as np
  from PIL import Image
  if (buf.width, buf.height) != (1344, 760) or buf.stride < buf.width or buf.uv_offset < buf.stride * buf.height:
    return None
  raw = np.frombuffer(buf.data, np.uint8)
  end = buf.uv_offset + buf.stride * (buf.height // 2)
  if raw.size < end or buf.stride % 2 or int(buf.frame_id) != frame_id:
    return None
  y = raw[:buf.stride*buf.height].reshape(buf.height, buf.stride)[:, :buf.width]
  uv = raw[buf.uv_offset:end].reshape(buf.height//2, buf.stride//2, 2)[:, :buf.width//2]
  def plane(values):
    return np.asarray(Image.fromarray(values).resize((320, 192), Image.Resampling.BOX), dtype=np.int32)
  # Limited-range NV12, BT.601 (the replay decoder's NV12 conversion).
  luma = 298 * np.maximum(plane(y) - 16, 0)
  u, v = plane(uv[:, :, 0]) - 128, plane(uv[:, :, 1]) - 128
  rgb = np.clip((np.stack((luma + 409*v, luma - 100*u - 208*v, luma + 516*u), axis=-1) + 128) >> 8, 0, 255).astype(np.uint8)
  return rgb if int(buf.frame_id) == frame_id else None


def healthy_primary(model, now):
  return (model.visionCompute == 'nonUsb' and primary_action(model) is not None and
          0 <= now - model.timestampEof < INPUT_NS and model.frameAge == 0 and 0 <= model.frameDropPerc < 1 and
          0 < model.modelExecutionTime < .05)


def finished(key, requested, primary, action, now):
  if key != requested or not 0 <= now - requested[1] < TTL_NS:
    return {'state': 'expired'}
  return {'state': 'result', 'frame': key[0], 'eof': key[1], 'comparison': compare(primary, action),
          'longitudinal': action['longitudinal'], 'lateral': action['lateral']}


def start_worker():
  env = {**os.environ, 'DEV': 'USB+AMD:LLVM', 'GMMU': '0', 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'}
  local, child = socket.socketpair()
  with local, child:
    fd = child.fileno()
    worker = subprocess.Popen([sys.executable, '-m', 'openpilot.selfdrive.modeld.vla_observer', str(fd), str(os.getpid())],
                              pass_fds=(fd,), env=env)
    return worker, Connection(local.detach())


def main():
  from msgq.visionipc import VisionIpcClient, VisionStreamType
  from openpilot.cereal import messaging
  from openpilot.common.params import Params
  from openpilot.common.sunny_models import internal_primary
  from openpilot.selfdrive.modeld.signal_color_shadow import configure_worker_scheduling
  from openpilot.system.hardware import HARDWARE
  from openpilot.system.hardware.usbgpu import check_usbgpu_power

  configure_worker_scheduling()
  params = Params()
  if HARDWARE.get_device_type() != 'mici' or not internal_primary(boot=True):
    write_status('primary_owns_gpu')
  else:
    sm = messaging.SubMaster(['modelV2', 'carState', 'livePose', 'liveCalibration', 'deviceState'])
    camera = VisionIpcClient('camerad', VisionStreamType.VISION_STREAM_ROAD, True)
    observe(params, sm, camera, check_usbgpu_power)
  # manager reaps and starts exited on-road services. Keep a failed session dormant
  # after releasing the GPU so it cannot repeatedly reload or contend in this trip.
  while params.get_bool('IsOnroad') and params.get_bool('C4VlaObserve'):
    time.sleep(.5)


def observe(params, sm, camera, check_power):
  motion = MotionWindow()
  images = deque(maxlen=5)
  primaries = deque(maxlen=5)
  worker = channel = None
  pending = eligible_since = None
  status = {'state': 'waiting'}
  last_write = last_submit = 0
  deadline = misses = 0
  ready = False
  last_model = last_frame = (-1, -1)
  first_request = True
  last_published = None
  session = {'accepted': 0, 'expired': 0}
  try:
    while params.get_bool('C4VlaObserve') and params.get_bool('IsOnroad'):
      sm.update(0)
      now = camera_clock()
      events = sorted((sm.logMonoTime[k], k) for k in ('liveCalibration', 'carState', 'livePose') if sm.updated[k])
      for t, k in events:
        motion.observe(k, t, sm.valid[k], sm[k])
      motion.trim(now - 2_500_000_000)
      model, device = sm['modelV2'], sm['deviceState']
      # camerad timestamps use CLOCK_BOOTTIME; Python telemetry uses CLOCK_MONOTONIC.
      good = (abs(now - time.monotonic_ns()) < 5_000_000 and sm.alive['modelV2'] and sm.valid['modelV2'] and healthy_primary(model, now) and
              sm.valid['deviceState'] and sm.alive['deviceState'] and device.thermalStatus == 'green' and
              0 < device.memoryUsagePercent < 85 and not params.get_bool('UsbGpuActive') and not params.get_bool('UsbGpuLoading'))
      valid_motion = (motion.speed is not None and motion.vehicle_down is not None and motion.motion and motion.motion[-1] is not None and
                      0 <= now-motion.times[-1] < INPUT_NS and 0 <= now-motion.speed_time < INPUT_NS and
                      0 <= now-motion.calibration_time < 5_000_000_000)
      if not valid_motion and (pending is not None or status['state'] == 'result'):
        # Revoking a pending decision survives recovery before worker completion.
        if pending is not None:
          pending = (pending[0], None)
        status = {'state': 'waiting'}
      if sm.updated['modelV2']:
        key = int(model.frameId), int(model.timestampEof)
        if key[0] <= last_model[0] or key[1] <= last_model[1]:
          good = False
        last_model = key
        if good:
          primaries.append((key, primary_action(model)))
      if not good:
        if worker is not None:
          status = {'state': 'primary_guard'}
          break
        eligible_since = None
        primaries.clear()
        images.clear()
      elif eligible_since is None:
        eligible_since = now
      elif worker is None and now - eligible_since >= 2_000_000_000:
        if check_power() is not None:
          status = {'state': 'usb_unavailable'}
          break
        worker, channel = start_worker()
        deadline = now + 120_000_000_000
        status = {'state': 'loading'}
      if worker is not None:
        if worker.poll() is not None or (deadline and now > deadline):
          status = {'state': 'worker_failed'}
          break
        if channel.poll():
          key, value = channel.recv()
          if key == 'ready' and not ready:
            ready, status = True, {'state': 'waiting'}
          elif key == 'error' or pending is None:
            status = {'state': 'worker_failed'}
            break
          else:
            received = camera_clock()
            status = finished(key, *pending, value, received) if pending[1] is not None and valid_motion else {'state': 'waiting'}
            if status['state'] in ('result', 'expired'):
              session['last_ms'] = round((received - pending[0][1]) / 1e6)
              if status['state'] == 'result':
                session['accepted'] += 1
                session['last_comparison'] = status['comparison']
              else:
                session['expired'] += 1
            misses = misses + 1 if status['state'] == 'expired' else 0
            pending = None
            if misses >= 3:
              status = {'state': 'too_slow'}
              break
          deadline = 0
        if ready and pending is None and valid_motion and now - last_submit >= 500_000_000:
          if not camera.is_connected():
            camera.connect(False)
          buf = camera.recv(timeout_ms=0) if camera.is_connected() else None
          if buf is not None:
            key = int(camera.frame_id), int(camera.timestamp_eof)
            if key[0] > last_frame[0] and key[1] > last_frame[1] and 0 <= now-key[1] < INPUT_NS:
              rgb = copy_road(buf, key[0])
              if rgb is not None:
                images.append((key, rgb))
            last_frame = key
          paired = dict(primaries)
          for key, rgb in reversed(images):
            if key not in paired or not 0 <= camera_clock()-key[1] < INPUT_NS:
              continue
            history = motion.at(key[1])
            if history is None:
              break
            channel.send((key, rgb, history))
            last_submit = now
            pending = (key, paired[key])
            # Allow cold compilation once. Late results still expire from camera EOF.
            deadline = now + (45 if first_request else 12) * 1_000_000_000
            first_request = False
            images.clear()
            status = {'state': 'inferencing'}
            break
      if status.get('state') == 'result' and now - status['eof'] >= TTL_NS:
        status = {'state': 'expired'}
      if status != last_published or now-last_write >= 1_000_000_000:
        write_status(**status, session=session)
        last_write, last_published = now, status
      time.sleep(.01)
  except (EOFError, OSError, RuntimeError, ValueError):
    import traceback
    traceback.print_exc()
    status = {'state': 'worker_failed'}
  finally:
    if worker is not None:
      worker.kill()
      try:
        worker.wait(timeout=1)
      except subprocess.TimeoutExpired:
        status = {'state': 'worker_failed'}
    if channel is not None:
      channel.close()
    write_status(**(status if status.get('state') in ('too_slow', 'usb_unavailable', 'worker_failed', 'primary_guard') else {'state': 'idle'}),
                 session=session)


if __name__ == '__main__':
  if len(sys.argv) == 3:
    gpu_worker(Connection(int(sys.argv[1])), int(sys.argv[2]))
  else:
    main()
