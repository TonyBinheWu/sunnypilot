"""Run on a workstation/NAS, never in the driving process."""
import argparse
import json
import os
from pathlib import Path

from .pipeline import MAX_OBSERVATIONS, build_map, identifier, ply

MAX_FILE = 64 * 1024 * 1024


def read_json(path):
  if Path(path).stat().st_size > MAX_FILE:
    raise ValueError('input_file_too_large')
  return json.loads(Path(path).read_text(encoding='utf-8'))


def read_observations(paths):
  for path in paths:
    with open(path, encoding='utf-8') as stream:
      while line := stream.readline(128_001):
        if len(line) > 128_000:
          raise ValueError('observation_line_too_large')
        if line.strip():
          yield json.loads(line)


def write_new(path, text):
  # Revisions are immutable. Failed writes remove only this newly created file.
  with open(path, 'x', encoding='utf-8', newline='\n') as stream:
    try:
      stream.write(text)
      stream.flush()
      os.fsync(stream.fileno())
    except BaseException:
      stream.close()
      Path(path).unlink(missing_ok=True)
      raise


def extract(args):
  identifier(args.trip)
  identifier(args.vehicle)
  identifier(args.clock)
  if not Path(args.rlog).is_file():
    raise ValueError('local_rlog_file_required')
  # Full cereal reader; the opendbc CAN-only schema omits the required services.
  from openpilot.tools.lib.logreader import LogReader
  calibration, calibration_valid, calibration_time, rows = None, False, 0, 0
  # Incomplete streams are kept as .partial, never a completed observations file.
  partial = Path(str(args.output)+'.partial')
  if Path(args.output).exists():
    raise FileExistsError(args.output)
  with partial.open('x', encoding='utf-8') as out:
    for event in LogReader(args.rlog, sort_by_time=True):
      kind = event.which()
      if kind == 'liveCalibration':
        calibration = event.liveCalibration.to_dict()
        calibration_valid = bool(event.valid) and str(event.liveCalibration.calStatus) == 'calibrated'
        calibration_time = int(event.logMonoTime)
      elif kind == 'modelV2':
        model = event.modelV2
        if not model.timestampEof:
          continue
        rows += 1
        if rows > MAX_OBSERVATIONS:
          raise ValueError('observation_limit_split_input')
        lanes = []
        for i, line in enumerate(model.laneLines):
          if i >= len(model.laneLineProbs) or i >= len(model.laneLineStds):
            continue
          lanes.append({'probability': model.laneLineProbs[i], 'std_m': model.laneLineStds[i],
                        'points': [list(p) for p in zip(line.x, line.y, line.z, strict=True)]})
        record = {'schema': 'carrot-lane-observations/v1', 'trip_id': args.trip, 'vehicle_id': args.vehicle,
                  'clock_id': args.clock, 'frame_id': int(model.frameId), 'timestamp_ns': str(model.timestampEof),
                  'model_frame': 'calibrated_FRD', 'valid': bool(event.valid),
                  'calibration_valid': calibration_valid and 0 <= int(event.logMonoTime)-calibration_time <= 2_000_000_000,
                  'native_calibration': calibration, 'lanes': lanes}
        out.write(json.dumps(record, allow_nan=False, separators=(',', ':'))+'\n')
    if not rows:
      raise ValueError('no_model_frames')
    out.flush()
    os.fsync(out.fileno())
  # link+unlink gives no-overwrite publication even if another writer raced us.
  os.link(partial, args.output)
  partial.unlink()
  print(json.dumps({'model_frames': rows, 'output': str(args.output), 'pose_required': True}))


def demo():
  """Known synthetic geometry for UI/tests; never shipped as a real road map."""
  observations, trajectories = [], []
  for trip, offset in (('demo-a', 0), ('demo-b', .08)):
    trajectory = {'trip_id': trip, 'vehicle_id': trip, 'clock_id': trip, 'calibration_id': 'synthetic',
                  'source': 'synthetic', 'poses': []}
    for n in range(20):
      t = str(1_000_000_000+n*50_000_000)
      trajectory['poses'].append({'timestamp_ns': t, 'frame_id': n, 'translation': [0, n*2, 0],
                                 'quaternion_wxyz': [0, 2**-.5, 2**-.5, 0],
                                 'position_std_m': .1, 'orientation_std_deg': .2})
      observations.append({'schema': 'carrot-lane-observations/v1', 'trip_id': trip, 'vehicle_id': trip,
                           'clock_id': trip, 'frame_id': n, 'timestamp_ns': t,
                           'model_frame': 'calibrated_FRD', 'valid': True, 'calibration_valid': True,
                           'lanes': [{'probability': .95, 'std_m': .1,
                                      'points': [[x, side+offset+.0009*(x+n*2)**2, .01*x] for x in range(1, 30)]}
                                     for side in (-1.8, 1.8)]})
    trajectories.append(trajectory)
  return build_map(observations, {'schema': 'carrot-mapping-poses/v1',
                                'frame': {'id': 'synthetic-demo', 'axes': 'ENU', 'units': 'm'},
                                'trajectories': trajectories})


def main():
  parser = argparse.ArgumentParser(description='Offline lane map candidates; external optimized poses required.')
  sub = parser.add_subparsers(dest='command', required=True)
  ex = sub.add_parser('extract', help='Extract model lanes only; does not estimate VIO or map poses.')
  ex.add_argument('--rlog', required=True)
  ex.add_argument('--trip', required=True, help='Pseudonymous trip ID, consistent across segments')
  ex.add_argument('--vehicle', required=True, help='Pseudonymous vehicle ID, not a dongle ID')
  ex.add_argument('--clock', required=True, help='Unique boot-clock ID; change after reboot')
  ex.add_argument('--output', required=True, type=Path)
  build = sub.add_parser('build')
  build.add_argument('--observations', required=True, nargs='+')
  build.add_argument('--poses', required=True)
  build.add_argument('--previous', help='Previous immutable revision in the identical shared frame')
  build.add_argument('--output', required=True)
  build.add_argument('--ply', help='Optional 3D point cloud export')
  sample = sub.add_parser('demo', help='Generate synthetic data for viewer verification only')
  sample.add_argument('--output', required=True)
  args = parser.parse_args()
  if args.command == 'extract':
    extract(args)
    return
  result = demo() if args.command == 'demo' else build_map(
    read_observations(args.observations), read_json(args.poses), read_json(args.previous) if args.previous else None)
  write_new(args.output, json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2)+'\n')
  if getattr(args, 'ply', None):
    write_new(args.ply, ply(result))
  print(json.dumps({'revision': result['revision'], 'cells': len(result['cells']), 'ground_truth': False}))


if __name__ == '__main__':
  main()
