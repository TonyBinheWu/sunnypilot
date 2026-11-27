"""Parked, offline RX 9060 qualification against a real paired C4 recording."""
from bisect import bisect_left, bisect_right
from contextlib import ExitStack
from dataclasses import replace
import json
from pathlib import Path
import sys

import numpy as np

from openpilot.selfdrive.alpamayo.capture import SERVICES, state_value
from openpilot.selfdrive.alpamayo.frontend import (CAMERAS, FRAME_SLACK_NS, FRAME_TOLERANCE_NS, OFFSETS_NS, Frame,
                                                  Preparer, Selection, State, Unavailable)
from openpilot.selfdrive.alpamayo import install

# Keep the replay entirely local. Match encoded display indices to original camera EOF
# and frame ID before handing the images to the same calibration and input code as live.
VIDEO = {1: ('wideRoadEncodeIdx', 'wideRoadCameraState', 'ecamera.hevc'),
         6: ('roadEncodeIdx', 'roadCameraState', 'fcamera.hevc')}


def recorded_windows(directory, config, needed):
  from openpilot.selfdrive.alpamayo.history import measured_history
  import zstandard
  from openpilot.cereal import log
  sources = {SERVICES.get(k, k): k for k in ('deviceMotion', 'extrinsicsCalibration', 'vehicleParameters', 'carState', 'carParams', 'navInstruction')}
  states = {k: [] for k in sources.values()}
  cameras = {k: {} for k in CAMERAS}
  indexes = {k: {} for k in CAMERAS}
  with zstandard.open(directory/'rlog.zst', 'rb') as stream:
    data = stream.read((160 << 20) + 1)
  if len(data) > 160 << 20:
    raise ValueError('Replay segment exceeds the memory budget')
  mici = False
  for event in log.Event.read_multiple_bytes(data):
    kind, stamp = event.which(), int(event.logMonoTime)
    if kind == 'deviceState' and event.valid:
      mici = str(event.deviceState.deviceType) == 'mici'
    elif kind in sources:
      msg = getattr(event, kind)
      key = sources[kind]
      value, valid = state_value(key, msg)
      t = int(msg.timestamp) if key == 'deviceMotion' else stamp
      if 0 < t <= stamp:
        states[key].append(State(t, stamp, value if valid and event.valid else None, valid and event.valid))
    else:
      for cam, (idx_name, cam_name, _) in VIDEO.items():
        if kind == idx_name and event.valid:
          idx = getattr(event, kind)
          if idx.segmentNum == int(directory.name.rsplit('--', 1)[1]):
            key = (idx.frameId, idx.timestampEof, idx.timestampSof)
            indexes[cam][key] = idx.segmentId if key not in indexes[cam] else None
        elif kind == cam_name and event.valid:
          cs = getattr(event, kind)
          if str(cs.sensor) == 'os04c10' and 0 < cs.timestampSof <= cs.timestampEof:
            cameras[cam][(cs.frameId, cs.timestampEof)] = cs.timestampSof
  del data
  if not mici:
    raise ValueError('Recording is not from C4')
  # Use three consecutive plans and only decode their ten-image windows.
  rows = {k: sorted((sof, fid, eof, indexes[k][fid, eof, sof]) for (fid, eof), sof in cameras[k].items()
                    if indexes[k].get((fid, eof, sof)) is not None) for k in CAMERAS}
  times = {k: [r[0] for r in rows[k]] for k in CAMERAS}
  prep = Preparer(config['geometry'], default_navigation=config['default_navigation'], navigation_within_m=config['navigation_within_m'])
  selections = []
  pending = set(needed)
  for rows_ in states.values():
    rows_.sort(key=lambda row: (row.stamp, row.received))
  stamps = {kind: [r.stamp for r in rows_] for kind, rows_ in states.items()}

  def window(kind, start, end, receipt):
    rows_ = states[kind][bisect_left(stamps[kind], start):bisect_right(stamps[kind], end)]
    # Match live Store replacement, retaining only revisions received by the deadline.
    return tuple({r.stamp: r for r in rows_ if r.received <= receipt}.values())
  for query in times[6][::5]:
    frames = []
    for cam in CAMERAS:
      for offset in OFFSETS_NS:
        target = query + offset
        i = bisect_right(times[cam], min(query, target + FRAME_SLACK_NS)) - 1
        if i < 0 or target-times[cam][i] > FRAME_TOLERANCE_NS:
          continue
        sof, fid, eof, idx = rows[cam][i]
        frames.append((Frame(cam, fid, sof, eof, eof, eof, None, 'nv12'), idx))
    if len(frames) != 10 or any(len({f.frame_id for f, _ in frames if f.camera == k}) != 5 for k in CAMERAS):
      selections.clear()
      continue
    now = max(f.eof_ns for f, _ in frames)
    history = {k: window(k, 0 if k == 'carParams' else query-3_500_000_000, now, now) for k in states}
    selection = Selection(query, now, tuple(f for f, _ in frames), history, {})
    try:
      cal, _, _, _, history_data, _, _ = prep.state_inputs(selection)
      if history_data['speed_m_s'] < 2.:
        raise Unavailable('Moving replay required')
      # Future motion is used exclusively for scoring, never placed in Selection.
      horizon = query+1_900_000_000
      motion = window('deviceMotion', query-200_000_000, horizon, horizon+100_000_000)
      xyz, rotation, _ = measured_history(motion, horizon, cal['rpyCalib'])
      ground = (xyz[0]-xyz[0, 0]) @ rotation[0, 0]
      turn = rotation[0, 0].T @ rotation[0, 15]
      angle = np.arctan2(turn[1, 0], turn[0, 0])
      scenario = 'left' if angle > .1 else 'right' if angle < -.1 else 'straight' if abs(angle) < .04 else None
      if scenario not in pending:
        raise Unavailable('Scenario already covered')
      for f, _ in frames:
        from openpilot.selfdrive.alpamayo.frontend import STATE_LIMITS, required
        required(history['extrinsicsCalibration'], f.sof_ns, STATE_LIMITS['extrinsicsCalibration'])
    except Unavailable:
      selections.clear()
      continue
    if selections and (query-selections[-1][0].query_ns > 400_000_000 or selections[-1][3] != scenario):
      selections.clear()
    selections.append((selection, frames, ground[1:16, :2], scenario))
    if len(selections) == 3:
      yield selections
      pending.remove(scenario)
      if not pending:
        return
      selections = []


def decode_windows(directory, config, selections):
  import av
  from functools import partial
  from openpilot.selfdrive.alpamayo.selected.camera import calibrated_image
  prep = Preparer(config['geometry'], sampler=partial(calibrated_image, cache_dir=config['cache']),
                  default_navigation=config['default_navigation'], navigation_within_m=config['navigation_within_m'])
  pixels = {}
  for cam, (_, _, filename) in VIDEO.items():
    wanted = {idx for _, frames, _, _ in selections for f, idx in frames if f.camera == cam}
    with av.open(str(directory/filename)) as video:
      for i, frame in enumerate(video.decode(video=0)):
        if i in wanted:
          if (frame.width, frame.height) != (1344, 760):
            raise ValueError('Unexpected recorded camera size')
          pixels[cam, i] = frame.to_ndarray(format='nv12')
        if i >= max(wanted):
          break
  samples = []
  for selection, frames, ground, scenario in selections:
    exact = tuple(replace(f, pixels=pixels[f.camera, idx]) for f, idx in frames)
    samples.append((*prep.prepare(replace(selection, frames=exact)), ground, scenario))
  return samples


def qualify(root):
  import capnp
  import zstandard
  from openpilot.selfdrive.alpamayo.runtime import load_adapter, run_prediction
  from openpilot.selfdrive.alpamayo.planner import MAX_LATENCY
  config = json.loads(install.CONFIG.read_bytes())
  candidates = sorted((p for p in root.glob('*--*') if p.name.rsplit('--', 1)[-1].isdigit()
                       and all((p/f).is_file() for f in ('rlog.zst', 'fcamera.hevc', 'ecamera.hevc'))
                       and not any(p.glob('*.lock'))), key=lambda p: p.stat().st_mtime, reverse=True)
  needed = {'left', 'right', 'straight'}
  windows = []
  for directory in candidates:
    try:
      for selections in recorded_windows(directory, config, needed):
        windows.append((directory, selections))
        needed.remove(selections[0][3])
    except (OSError, ValueError, KeyError, EOFError, capnp.KjException, zstandard.ZstdError):
      continue
    if not needed:
      break
  if needed:
    raise ValueError('Missing synchronized moving C4 recordings for: '+', '.join(sorted(needed)))
  with ExitStack() as stack:
    adapter = load_adapter(config)
    stack.callback(adapter.close)
    adapter.warmup()
    scores = []
    for directory, selections in windows:
      for arrays, meta, ground, scenario in decode_windows(directory, config, selections):
        result = run_prediction(adapter, arrays, meta, hash_inputs=False)
        if not 0 < result['inference_ms'] <= MAX_LATENCY / 1e6:
          raise ValueError('Recorded inference missed the model latency limit')
        trajectory = np.asarray(result['prediction']['xyz'])[0]
        speed = np.linalg.norm(trajectory[0, :2]) / .1
        if abs(speed-meta['vehicle_history']['speed_m_s']) > 2.:
          raise ValueError('Recorded trajectory does not match the source vehicle speed')
        forward, lateral = np.max(np.abs(trajectory[:15, :2]-ground), axis=0)
        if lateral > .5 or forward > 2.:
          raise ValueError(f'{scenario} replay exceeded the 1.5 s trajectory error limit')
        scores.append(dict(scenario=scenario, inference_ms=round(result['inference_ms'], 1),
                           lateral_error_m=round(float(lateral), 3), forward_error_m=round(float(forward), 3)))
    report = dict(arch=adapter.manifest['arch'], vram_bytes=adapter.manifest['vram_bytes'], samples=scores,
                  weights=adapter.manifest['fp8_weights_sha256'])
    install.write(install.ROOT/'replay-result.json', json.dumps(report)+'\n')


if __name__ == '__main__':
  try:
    qualify(Path(sys.argv[1]))
  except ValueError as exc:
    install.status('error', str(exc))
    raise
