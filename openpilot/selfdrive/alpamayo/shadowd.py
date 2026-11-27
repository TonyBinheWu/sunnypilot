"""Supervise the isolated GPU worker and forward plans only in planner mode."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

MATCH_WAIT_NS = 100_000_000
EARLY_LEAD_NS = 160_000_000  # The -0.1 s exposures of the next slot are ready about 150-200 ms before it opens.
EARLY_CUTOFF_NS = 20_000_000  # Later than this, early encoding (~50 ms) would delay the slot about as much as it saves.
CAMERA_FRAME_NS = 50_000_000  # 20 FPS front cameras: frame IDs advance by period/50 ms per slot.
HELD_FRAMES_NS = 2_600_000_000  # Free-running: the worker keeps projections covering the 2 s history.
ANCHOR_WAIT_NS = 200_000_000  # Allows two-camera priming in this slot after a short overrun.
START_LATENESS_NS = 200_000_000  # the worker predicts a slot only if it picks it up within this time of its opening
RING_LATENESS_NS = 80_000_000  # the same with 100 ms slots, where a later slot opens soon after
RING_STARVATION_NS = 400_000_000  # with 100 ms slots, a slot after this long without a prediction uses START_LATENESS_NS

def planner_mode():
  """Alpamayo takes the place of the big driving model: installed, not turned off, and not in record-only mode."""
  from openpilot.selfdrive.alpamayo.install import ready
  from openpilot.common import sunny_models
  return sunny_models.key_for(True, True) == sunny_models.LAT2V and not sunny_models.internal_primary(True) and ready()


class WorkerStopped(RuntimeError):
  """A fresh worker can recover without restarting modeld or interrupting the local model."""


def worker_cpu_ticks(pid):
  # The worker leads its own process group. An idle parent can be waiting for active compiler processes.
  ticks, leader = 0, False
  for path in Path('/proc').glob('[0-9]*/stat'):
    try:
      fields = path.read_text().rsplit(')', 1)[1].split()
      if int(fields[2]) == pid:  # pgrp
        ticks += sum(map(int, fields[11:15]))  # user/system CPU for this process and reaped children
        leader |= path.parent.name == str(pid)
    except (OSError, IndexError, ValueError):
      continue  # Processes can exit while /proc is being read.
  return ticks if leader else None


def cache_directory(config, output):
  from openpilot.selfdrive.alpamayo.runtime import private_output
  cache = Path(config['cache'])
  if not cache.is_absolute() or not cache.is_dir():
    raise ValueError('Configure an absolute existing persistent cache directory')
  cache = private_output(cache)
  if cache.is_relative_to(output) or output.is_relative_to(cache):
    raise ValueError('Keep persistent cache and session output in separate directories')
  with tempfile.TemporaryFile(dir=cache):
    pass
  return cache


def prune_output(output, limit_bytes):
  """Keep the newest prediction sessions within the limit. Each session is one directory."""
  import shutil
  total = 0
  for session in sorted((p for p in output.iterdir() if p.is_dir()), key=lambda p: p.stat().st_mtime, reverse=True):
    total += sum(f.stat().st_size for f in session.rglob('*') if f.is_file())
    if total > limit_bytes:
      shutil.rmtree(session, ignore_errors=True)


def worker_environment(config, cache):
  repository = Path(__file__).resolve().parents[3]
  paths = [Path(config['tinygrad']), repository, repository/'opendbc_repo']
  from openpilot.selfdrive.alpamayo.install import ROOT, LLVM_FILE
  return dict(os.environ, LLVM_PATH=str(ROOT/'runtime'/LLVM_FILE), PYTHONPATH=os.pathsep.join(map(str, paths)), PYTHONNOUSERSITE='1',
              DEV='USB+AMD:LLVM', GMMU='0', TC_OPT='2', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
              XDG_CACHE_HOME=str(cache), CACHEDB=str(cache/'compiler-cache.db'))


def stop_worker(child):
  if child is None:
    return
  try:
    os.killpg(child.pid, signal.SIGTERM)
    child.wait(timeout=1)
  except (ProcessLookupError, subprocess.TimeoutExpired):
    pass
  try:
    os.killpg(child.pid, signal.SIGKILL)
  except ProcessLookupError:
    pass
  child.wait(timeout=1)


def main():
  if not planner_mode():
    return
  os.sched_setaffinity(0, {0, 1, 2, 3, 6})  # Frame copies stay off the worker's cores 5 and 7.
  from openpilot.selfdrive.alpamayo.runtime import private_output, ram_handoff, storage_ok
  from openpilot.selfdrive.alpamayo.install import config_path as installed_config
  config_path = installed_config().resolve()
  config = json.loads(config_path.read_text())
  if planner_mode() and (config.get('period_ms', 500) not in (0, 100, 250, 500) or config['inference'].get('variant', 'selected') != 'selected'):
    raise ValueError('Planner evaluation requires the selected free-running, 100, 250 or 500 ms configuration')
  python = Path(config['python'])
  if not python.is_file() or python == Path(sys.executable):
    raise ValueError('Configure a separate, pinned Alpamayo Python environment')
  output = Path(config['output'])
  if not output.is_absolute() or not output.is_dir() or not storage_ok(output, 128*1024**2):
    raise ValueError('Configure an existing output directory with recording disk reserve')
  output = private_output(output)
  if (limit := config.get('output_limit_gb')) is not None:
    prune_output(output, float(limit)*1024**3)
  os.umask(0o077)
  cache = cache_directory(config, output)
  def stop(*_):
    raise KeyboardInterrupt
  signal.signal(signal.SIGTERM, stop)
  boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
  for attempt in range(3):
    root = output/f'{boot}-{time.monotonic_ns()}'
    root.mkdir()
    try:
      with ram_handoff() as handoff:
        supervise(config, config_path, python, root, Path(handoff), cache, boot)
      return
    except WorkerStopped as exc:
      (root/'worker-exit.txt').write_text(str(exc)+'\n')
      if attempt == 2:
        raise
      time.sleep(2**attempt)


def supervise(config, config_path, python, root, handoff, cache, boot):
  from openpilot.selfdrive.alpamayo.capture import NativeProducer, device_healthy, healthy
  from openpilot.selfdrive.alpamayo.frontend import AwaitingFrame, Store, Unavailable
  from openpilot.selfdrive.alpamayo.planner import FREE_WINDOW, deliverable
  from openpilot.selfdrive.alpamayo.frontend import CAMERAS, Selection, anchor_window, slot_exposures
  from openpilot.selfdrive.alpamayo.runtime import FixedSlots, memory_ok, save_selection, storage_ok
  free = config.get('period_ms', 500) == 0
  slots = FixedSlots(500 if free else config.get('period_ms', 500))
  rolling = not free and slots.period_ms in (100, 250, 500)
  exposures = slot_exposures(slots.period_ns) if rolling else 2
  held = {c: {} for c in CAMERAS}  # Free-running: frames the worker retains, {camera: {frame_id: sof}}.
  anchor_wait = min(ANCHOR_WAIT_NS, max(slots.period_ns*2//5, 80_000_000))  # a frame is ready about 41 ms after its SOF
  frames_per_slot = slots.period_ns//CAMERA_FRAME_NS
  pm = None
  if planner_mode():
    from openpilot.cereal import messaging
    pm = messaging.PubMaster(['alpamayoPlan'])
  def publish(payload=None):
    if pm is not None:
      msg = messaging.new_message('alpamayoPlan', valid=payload is not None)
      if payload is not None:
        msg.alpamayoPlan = payload
        published = time.monotonic_ns()
        if deliverable(payload['queryMonoTime'],payload['readyMonoTime'],published):
          msg.logMonoTime = published
        else:
          msg = messaging.new_message('alpamayoPlan', valid=False)
      pm.send('alpamayoPlan', msg)
  store = Store()
  producer = NativeProducer(store)
  child = None
  worker_start = working_since = None
  next_check, last_ticks = 0., None
  admission = None
  backlog = []  # Superseded slots that still owe their camera pair to the worker's history ring.
  served_plan = False
  model_seen = False
  last_query, last_current = 0, {}
  last_priors, early_slot, last_slot_start = {}, None, None
  predicted, flips, flips_until = {}, {}, 0  # Early predictions and recent +-1 frame flips of the selected priors.
  try:
    producer.start()
    with (root/'worker.log').open('xb') as log:
      while True:
        health = producer.health
        now = time.monotonic_ns()
        if producer.error is not None:
          raise RuntimeError('Shadow input capture failed') from producer.error
        if not device_healthy(health, now):
          if child is not None:
            raise WorkerStopped('Device health stopped inference')
          producer.stop.wait(.05)
          continue
        model_healthy = healthy(health, now)
        if model_seen and not model_healthy:
          raise WorkerStopped('Small-model health stopped inference')
        if not model_healthy:
          admission = None  # Offroad or small model restarting: keep the warm worker, admit nothing.
          backlog.clear()
        model_seen |= model_healthy
        if not memory_ok() or not storage_ok(root, 128*1024**2):
          raise RuntimeError('Shadow resource reserve reached')
        if child is None:
          # Without keep-warm, power Chestnut up only after the small model runs: Karel dropped USB when the
          # warmup overlapped the onroad camera and Adreno load. With keep-warm the worker loads offroad.
          if not model_healthy:
            producer.stop.wait(.05)
            continue
          child = subprocess.Popen([str(python), '-m', 'openpilot.selfdrive.alpamayo.shadowd', str(config_path), str(root), str(handoff)],
                                   env=worker_environment(config, cache), stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
          worker_start = time.monotonic()
        if child.poll() is not None:
          raise WorkerStopped(f'Inference worker exited ({child.returncode})')
        ready = (root/'ready.json').exists()
        # Weights (~70 s) plus the graph warmup run before ready. A cold compiler cache takes considerably longer.
        if not ready and time.monotonic()-worker_start > 1500:
          raise WorkerStopped('Inference initialization timed out')
        # No slot or plan can be admitted until the small model is healthy.
        if not model_healthy:
          producer.stop.wait(.05)
          continue
        if (handoff/'working.bin').exists() or (handoff/'pending.bin').exists():
          elapsed = time.monotonic()
          if working_since is None:
            working_since, next_check, last_ticks = elapsed, elapsed+10, None
          # A new reasoning shape can compile for minutes even after a timely straight-road plan.
          if elapsed-working_since > 600:
            raise WorkerStopped('Inference worker stopped completing slots')
          if served_plan and elapsed >= next_check:
            ticks = worker_cpu_ticks(child.pid)
            if ticks is not None and ticks == last_ticks:
              raise WorkerStopped('Inference worker stopped making progress')
            last_ticks, next_check = ticks, elapsed+10
        else:
          working_since = None
        latest = handoff/'plan.json'
        if pm is not None and latest.exists():
          # Rename before reading: a newer result can replace the mailbox without being unlinked here.
          reading = latest.replace(handoff/'reading.json')
          payload = json.loads(reading.read_bytes())
          publish(payload)
          served_plan |= payload is not None and time.monotonic_ns() < payload['slotDeadline']
          working_since = None
          reading.unlink()
        if (handoff/'skipped').exists():
          (handoff/'skipped').unlink()
          slots.skip()
          publish()
          for frames in held.values():
            frames.clear()  # The worker may not have retained the rejected input.
        if free:
          # Free-running: start the next prediction as soon as the worker is idle, on the newest matched frames.
          now = time.monotonic_ns()
          if ready and not (handoff/'pending.bin').exists() and not (handoff/'working.bin').exists():
            try:
              selected = store.select(now, last_query, last_current, cached={c: set(f) for c, f in held.items()},
                                      cached_offsets=(0, 1, 2, 3) if config.get('free_cached_prior') else (0, 1, 2))
              context = {'slot_start_ns': now, 'slot_deadline_ns': now+FREE_WINDOW, 'period_ms': 0, 'missed_slots': 0,
                         'boot_id': boot}
              save_selection(handoff/'pending.bin', selected, context, {c: set(f) for c, f in held.items()})
              last_query = selected.query_ns
              last_current = {f.camera: f.sof_ns for f in selected.frames}
              for f in selected.frames:
                held[f.camera][f.frame_id] = f.sof_ns
              for frames in held.values():
                for frame_id in [i for i, sof in frames.items() if sof < now-HELD_FRAMES_NS]:
                  del frames[frame_id]
            except Unavailable:
              pass  # AwaitingFrame included: no fresh matched query yet.
          producer.stop.wait(.002)
          continue
        slot = slots.take(time.monotonic_ns()) if ready else None
        if slot is not None:
          if admission is not None and rolling:
            # Superseded before dispatch: encode only its camera pair so later queries find their -0.5/-1/-2 s history.
            backlog.append(dict(admission, anchor_only=True, expires_ns=admission['slot_start_ns']+anchor_window(slots.period_ns)))
          admission = dict(slot, expires_ns=slot['slot_start_ns']+2*slots.period_ns)
        # One input can wait while the worker runs: the next slot is selected as soon as it opens, and the worker decides on
        # pickup whether it is still timely enough to predict (otherwise it only anchors the camera pair).
        idle = not (handoff/'pending.bin').exists()
        slot = backlog.pop(0) if backlog and idle else admission
        if slot is not None:
          try:
            selected_ns = time.monotonic_ns()
            busy = (handoff/'pending.bin').exists()
            if busy:  # the queued input has not been picked up yet; this slot waits (a newer opening moves it to the backlog)
              producer.stop.wait(.002)
              continue
            if slot is admission:
              admission = None
            if selected_ns >= slot['expires_ns'] or busy:
              raise Unavailable('Busy or late slot')
            try:
              # A slot can start late (grid-snapped) or be anchored after newer slots opened; its frames keep their capture times.
              selected = store.select(selected_ns, last_query, last_current, half_second_slot=slot['slot_start_ns'] if rolling else None, exposures=exposures,
                                      max_age_ns=slot['expires_ns']-slot['slot_start_ns'] if rolling else 250_000_000)
            except AwaitingFrame:
              # The matched modelV2 can arrive after this slot opens. Keep the same opening, cutoff and deadline.
              if rolling and not slot.get('anchor_only') and selected_ns < slot['slot_start_ns']+min(MATCH_WAIT_NS, anchor_wait):
                admission = slot
                producer.stop.wait(.002)
                continue
              raise
            context = dict(slot, boot_id=boot)
            save_selection(handoff/'pending.bin', selected, context)
            last_query = selected.query_ns
            last_current = {f.camera: f.sof_ns for f in selected.frames}
            if len(selected.frames) == 4:
              last_priors = {f.camera: f.frame_id for f in selected.frames[0::2]}
              last_slot_start = slot['slot_start_ns']
              for camera, frame_id in last_priors.items():
                if predicted.get(camera) not in (None, frame_id) and abs(frame_id-predicted[camera]) == 1:
                  # The query flips between two adjacent frames while small-model arrival straddles the opening.
                  flips[camera], flips_until = predicted[camera]-frame_id, selected_ns+20_000_000_000
              predicted = {}
          except Unavailable as error:
            print(f'alpamayo slot {slot["slot_start_ns"]} skipped{" (anchor)" if slot.get("anchor_only") else ""} after '
                  f'{(time.monotonic_ns()-slot["slot_start_ns"])/1e6:.0f} ms: {error}', file=sys.stderr, flush=True)
            slots.skip()
            publish()
        upcoming = slots.next_ns
        now = time.monotonic_ns()
        # The worker projects early pairs on a separate thread and encodes them between predictions, so a busy worker
        # still receives them: at 4 Hz the GPU is never idle before an opening.
        if (ready and model_healthy and len(last_priors) == len(CAMERAS) and upcoming is not None and last_slot_start is not None and
            early_slot != upcoming and upcoming-EARLY_LEAD_NS <= now < upcoming-EARLY_CUTOFF_NS and not (handoff/'early.bin').exists()):
          # At 20 FPS the next slot's -0.1 s exposures are normally period/50 ms frames after this slot's. The slot still selects
          # its frames with the normal rules; a matching early encoding only turns into cache hits.
          with store.lock:
            rings = {c: tuple(store.frames[c]) for c in CAMERAS}
            calibration = tuple(store.states['extrinsicsCalibration'])
          def frame(camera, frame_id):
            return next((f for f in reversed(rings[camera]) if f.frame_id == frame_id and f.ready_ns <= now), None)
          ahead = frames_per_slot*((upcoming-last_slot_start)//slots.period_ns)
          frames = [frame(c, last_priors[c]+ahead) for c in CAMERAS]
          if now < flips_until and any(c in flips for c in CAMERAS):
            # Also encode the adjacent candidate for flipping cameras; the GPU is otherwise idle before the opening.
            alternates = [frame(c, last_priors[c]+ahead+flips[c]) if c in flips else f for c, f in zip(CAMERAS, frames)]
            frames += alternates if all(alternates) else []
          elif now >= flips_until:
            flips.clear()
          if all(frames[:2]):
            early_slot = upcoming
            predicted = {c: f.frame_id for c, f in zip(CAMERAS, frames)}
            try:
              save_selection(handoff/'early.bin', Selection(max(f.sof_ns for f in frames), now, tuple(frames),
                                                             {'extrinsicsCalibration': calibration}, {}, {}),
                             {'early': True, 'slot_start_ns': upcoming})
            except (Unavailable, RuntimeError, ValueError):
              pass  # Early encoding is optional; the slot itself is unaffected.
        producer.stop.wait(.002 if pm is not None else .02)
  finally:
    try:
      publish()
    finally:
      try:
        stop_worker(child)
      finally:
        producer.close()


if __name__ == '__main__':
  if len(sys.argv) == 4:
    if not planner_mode():
      raise RuntimeError('lat2v is not the qualified boot selection')
    # msgq publishers wake readers with SIGUSR2 by thread ID and keep the IDs of readers that exited. After the kernel
    # reuses such an ID for a thread of this worker, which does not use msgq, the default action killed the worker
    # mid-drive (exit -12, Karel 2026-11-22). Ignore it; compiler child processes inherit the setting.
    signal.signal(signal.SIGUSR2, signal.SIG_IGN)
    # runtime.worker moves per-slot threads to cores 5 and 7 once the onroad policy brings them online.
    os.sched_setaffinity(0, set(range(6)))
    from openpilot.selfdrive.alpamayo.runtime import worker
    worker(json.loads(Path(sys.argv[1]).read_text()), sys.argv[2], sys.argv[3])
  else:
    main()
