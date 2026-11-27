"""C4 selection, parked validation and the modeld-side lat2v handoff."""
from contextlib import suppress
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from openpilot.common import sunny_models
from openpilot.common.model_download import notify


def strictly_parked(params):
  return (params.get_bool('IsOffroad') and not any(params.get_bool(k) for k in
          ('IsOnroad', 'IsEngaged', 'ForceOffroad', 'ForceOffroadActive')))


def guarded(command, offroad, progress, env=None):
  from openpilot.selfdrive.alpamayo.install import ROOT, STATUS
  # The installer, its package manager, and the GPU verifier all stop on ignition.
  if not offroad():
    raise ValueError('Park before preparing lat2v')
  ROOT.mkdir(parents=True, exist_ok=True)
  with (ROOT/'preparation.log').open('ab') as log:
    # A host-interpreter supervisor can still read Params while an isolated GPU
    # process runs. If the initiating Web/native UI exits, its entire job stops.
    runner = [sys.executable, '-m', 'openpilot.selfdrive.alpamayo.carrot', str(os.getpid()),
              json.dumps(command), json.dumps({k: v for k, v in (env or {}).items() if os.environ.get(k) != v})]
    child = subprocess.Popen(runner, start_new_session=True, stdout=log, stderr=log)
    try:
      while child.poll() is None:
        if not offroad():
          raise ValueError('lat2v preparation interrupted by ignition')
        try:
          state = json.loads(STATUS.read_bytes())
          notify(progress, state.get('phase', 'installing'), state['text'], state.get('received', 0), state.get('total'))
        except (OSError, ValueError, KeyError):
          pass
        time.sleep(.25)
      if child.returncode:
        try:
          state = json.loads(STATUS.read_bytes())
        except (OSError, ValueError):
          state = {}
        detail = state.get('text') if state.get('step') == 'error' else None
        raise ValueError(detail or 'lat2v preparation failed; see its preparation.log')
    finally:
      if child.poll() is None:
        with suppress(ProcessLookupError):
          os.killpg(child.pid, signal.SIGTERM)
        try:
          child.wait(timeout=3)
        except subprocess.TimeoutExpired:
          with suppress(ProcessLookupError):
            os.killpg(child.pid, signal.SIGKILL)
          child.wait()


def prepare_selection(offroad, progress=None):
  from openpilot.common.params import Params
  from openpilot.system.hardware import HARDWARE
  from openpilot.system.hardware.usbgpu import get_usbgpu_device
  from openpilot.selfdrive.alpamayo import install
  from openpilot.selfdrive.alpamayo.shadowd import worker_environment
  from openpilot.system.hardware.hw import Paths

  if HARDWARE.get_device_type() != 'mici':
    raise ValueError('lat2v requires a comma four')
  params = Params()
  def parked():
    return offroad() and strictly_parked(params)
  if not parked():
    raise ValueError('Turn ignition off to prepare lat2v')
  if not install.complete():
    install.ROOT.mkdir(parents=True, exist_ok=True)
    install.status('prepare', 'Preparing pinned lat2v runtime and model')
    guarded([sys.executable, '-m', 'openpilot.selfdrive.alpamayo.install'], parked, progress)
  bridge = get_usbgpu_device()
  if bridge is None or bridge.speed_mbps < 5000:
    raise ValueError('lat2v downloaded; connect a powered 5 Gbps Chestnut to verify')
  if not install.ready():
    config = json.loads(install.CONFIG.read_bytes())
    install.status('verify', 'lat2v: parked C4 camera replay on RX 9060')
    command = [config['python'], '-m', 'openpilot.selfdrive.alpamayo.qualify', Paths.log_root()]
    guarded(command, parked, progress, worker_environment(config, Path(config['cache'])))
    if not parked():
      raise ValueError('Ignition changed before lat2v verification completed')
    install.write(install.ROOT/'qualified', install.qualification_id()+'\n')


class CarrotPlan:
  def __init__(self, messaging, params):
    from openpilot.selfdrive.alpamayo.planner import BigModelState, PlanSelector
    self.sock = messaging.sub_sock('alpamayoPlan')
    self.selector = PlanSelector()
    self.state = BigModelState(time.monotonic())
    self.params = params

  def update(self, sm, event, local_action, lat_delay, long_delay, v_ego_stopping, radar_guard=False):
    from openpilot.cereal import messaging
    from openpilot.selfdrive.alpamayo.planner import BigModelState
    now = time.monotonic_ns()
    for msg in messaging.drain_sock(self.sock):
      if msg.valid:
        self.selector.receive(msg.alpamayoPlan, now, msg.logMonoTime)
    cs, pose = sm['carState'], sm['livePose']
    pose_fresh = (sm.all_checks(['livePose', 'carState']) and cs.canValid and pose.inputsOK and
                  pose.sensorsOK and pose.posenetOK and pose.orientationNED.valid and
                  0 <= now-pose.timestamp < 250_000_000 and 0 <= now-sm.logMonoTime['carState'] < 150_000_000)
    if pose_fresh and sm.updated['livePose']:
      self.selector.motion(pose.timestamp, cs.vEgo, -pose.orientationNED.z)
    m = event.modelV2
    m.localAction = local_action
    candidate = None
    if (event.valid and pose_fresh and sm.all_checks(['liveCalibration', 'carControl']) and
        str(sm['liveCalibration'].calStatus) == 'calibrated' and self.selector.pose_at(self.selector.query) is not None):
      candidate = self.selector.candidate_action(now, cs.vEgo, lat_delay, long_delay, v_ego_stopping)
    if candidate is not None and radar_guard:
      from openpilot.selfdrive.controls.lib.near_radar import MAX_SPEED, boot_time_ns, occupied_side
      curvature = candidate['desiredCurvature']
      if 0 < cs.vEgo <= MAX_SPEED and abs(curvature) > .01:
        side = 'right' if curvature > 0 else 'left'
        if occupied_side(sm, side, boot_time_ns()) is not False:
          candidate = None
    old = self.state.state
    control = sm['carControl']
    engaged = not sm.all_checks(['carControl']) or control.enabled or control.latActive or control.longActive
    if self.state.update(now*1e-9, candidate is not None, engaged):
      m.action = candidate
      m.alpamayoQueryMonoTime = self.selector.query
    if self.state.state != old:
      active = self.state.state == BigModelState.ACTIVE
      self.params.put_bool('UsbGpuActive', active)
      self.params.put_bool('UsbGpuLoading', False)
      self.params.put_bool('UsbGpuStartupFailed', not active)
      sunny_models.mark_load(True, None if active else sunny_models.LAT2V)


def run_parked(parent, command, environment):
  from openpilot.common.params import Params
  from openpilot.selfdrive.alpamayo.install import ROOT, status
  from openpilot.selfdrive.alpamayo.runtime import storage_ok
  params = Params()
  if os.getpgrp() != os.getpid() or os.getppid() != parent or not strictly_parked(params):
    return 1
  child = subprocess.Popen(command, env={**os.environ, **environment})
  while child.poll() is None:
    if not storage_ok(ROOT):
      status('error', 'Insufficient free space to preserve the recording reserve')
      os.killpg(os.getpid(), signal.SIGKILL)
    if os.getppid() != parent or not strictly_parked(params):
      os.killpg(os.getpid(), signal.SIGKILL)
    time.sleep(.2)
  return child.returncode


if __name__ == '__main__':
  sys.exit(run_parked(int(sys.argv[1]), json.loads(sys.argv[2]), json.loads(sys.argv[3])))
