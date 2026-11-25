"""Parked C4 timing experiment for one selected sunnypilot large model plus PhysicalAI on one Chestnut."""
import argparse
import json
import math
import os
from pathlib import Path
import threading
import time

from openpilot.selfdrive.modeld.vla_observer import require_target
from openpilot.selfdrive.modeld.vla_status import TTL_NS, WEIGHTS, parked
from openpilot.tools.vla.replay import REVISION, decode, load_native, verify

PERIOD = 50_000_000


class PrimarySchedule:
  """Dispatch only the most recent due release. Charge lateness to its original release time."""
  def __init__(self, run, clock=time.monotonic_ns):
    self.run, self.clock = run, clock
    self.release = clock()
    self.skipped = 0
    self.latencies = []

  def dispatch(self):
    now = self.clock()
    if now < self.release:
      return
    skipped = (now - self.release) // PERIOD
    self.skipped += skipped
    release = self.release + skipped * PERIOD
    self.release = release + PERIOD
    self.run()
    self.latencies.append(self.clock() - release)

  def report(self):
    ordered = sorted(self.latencies)
    return {'executed': len(ordered), 'skipped': self.skipped, 'late': sum(t > PERIOD for t in ordered),
            'p95_release_to_output_ms': round(ordered[math.ceil(.95 * len(ordered)) - 1] / 1e6, 2),
            'max_release_to_output_ms': round(ordered[-1] / 1e6, 2)}


def run_bench(key, weights, iterations):
  import numpy as np
  from openpilot.selfdrive.modeld.sunny_worker import load_engine
  from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
  verify(weights)
  engine = load_engine(key, 1344, 760, validate_device=require_target)
  from tinygrad import Device
  from tinygrad.helpers import GlobalCounters
  device = Device['AMD']
  size = get_nv12_info(1344, 760)[3]
  frames = {name: np.full(size, 128, np.uint8) for name in (engine.adapter._road_key, engine.adapter._wide_key)}
  inputs = {'desire_pulse': np.zeros(8), 'lateral_control_params': np.zeros(2), 'action_t': np.zeros(2), 'traffic_convention': np.array([1., 0.])}
  transforms = {name: np.eye(3, dtype=np.float32) for name in ('img', 'big_img')}

  def primary():
    engine.run(frames, transforms, inputs)
    if device.error_state.host.view(fmt='q')[0]:
      raise RuntimeError('AMD runtime error')

  primary()
  engine.reset()
  baseline = PrimarySchedule(primary)
  while len(baseline.latencies) < 100:
    time.sleep(max(0, (baseline.release - time.monotonic_ns()) / 1e9))
    baseline.dispatch()
  print(json.dumps({'primary': key, 'primary_only': baseline.report()}), flush=True)

  # Both engines now use the same device object, queue, allocation pool and lifetime GPU lock.
  sampled_bytes = GlobalCounters.mem_used_per_device['AMD']
  engine.reset()
  schedule = None

  def checkpoint():
    nonlocal sampled_bytes
    device.synchronize()
    sampled_bytes = max(sampled_bytes, GlobalCounters.mem_used_per_device['AMD'])
    schedule.dispatch()

  _, predict = load_native(weights, 'AMD', checkpoint)
  rgb = np.full((192, 320, 3), 130, np.uint8)
  history = [[0., 0., 0.] for _ in range(9)]
  observations = []
  schedule = PrimarySchedule(primary)
  for _ in range(iterations):
    start = time.monotonic_ns()
    checkpoint()
    action = decode(predict(rgb, history))
    checkpoint()
    elapsed = time.monotonic_ns() - start
    observations.append({'ms': round(elapsed / 1e6, 2), 'within_budget': elapsed < TTL_NS, 'action': action})
  report = schedule.report()
  timing_met = (not baseline.skipped and max(baseline.latencies) <= PERIOD and not report['skipped'] and
                not report['late'] and all(o['within_budget'] for o in observations))
  return {'primary': key, 'target': device.arch, 'vram_bytes': device.iface.dev_impl.vram_size, 'weights_revision': REVISION,
          'sampled_amd_tensor_bytes': sampled_bytes, 'primary_only': baseline.report(), 'shared': report,
          'vla_observations': observations, 'synthetic_timing_targets_met': timing_met}


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--weights', type=Path, default=WEIGHTS)
  parser.add_argument('--iterations', type=int, choices=range(1, 11), default=3)
  args = parser.parse_args()
  if not Path('/AGNOS').is_file():
    parser.error('Requires a parked C4 with a Chestnut')
  from openpilot.common.params import Params
  from openpilot.common.sunny_models import key_for
  from openpilot.system.hardware import HARDWARE
  from openpilot.system.hardware.usbgpu import check_usbgpu_power
  params = Params()
  key = key_for(True)
  if HARDWARE.get_device_type() != 'mici' or not parked(params) or key is None:
    parser.error('Park the C4 and install/select a sunnypilot large model')

  def watchdog():
    end = time.monotonic() + 600
    while parked(params) and time.monotonic() < end:
      time.sleep(.05)
    os._exit(2)

  threading.Thread(target=watchdog, daemon=True).start()
  if reason := check_usbgpu_power():
    parser.error(reason)
  report = run_bench(key, args.weights, args.iterations)
  print(json.dumps(report), flush=True)
  return 0 if report['synthetic_timing_targets_met'] else 1


if __name__ == '__main__':
  raise SystemExit(main())
