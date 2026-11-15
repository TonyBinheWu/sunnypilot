"""Bounded, deterministic lane candidates in an explicitly shared metric frame.

Pose quality numbers are supplied by an external optimizer, not measured here.
Repeated frames are correlated; support counts must never be called accuracy.
"""
import hashlib
import json
import math
import re
from bisect import bisect_left
from collections import Counter, defaultdict

import numpy as np

SCHEMA = 'carrot-lane-map/v1'
MAX_OBSERVATIONS = 100_000
MAX_CELLS = 25_000
ID = re.compile(r'^[A-Za-z0-9_.-]{1,80}$')


def identifier(value):
  if not isinstance(value, str) or not ID.fullmatch(value):
    raise ValueError('invalid_identifier')
  return value


def finite(value, low, high):
  if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not low <= value <= high:
    raise ValueError('invalid_number')
  return float(value)


def vector(value, size, limit):
  if not isinstance(value, list) or len(value) != size:
    raise ValueError('invalid_vector')
  return np.array([finite(v, -limit, limit) for v in value])


def rotation(q):
  w, x, y, z = vector(q, 4, 1.001)
  if abs(np.linalg.norm([w, x, y, z]) - 1) > .001:
    raise ValueError('quaternion_not_unit')
  return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                   [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                   [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


def timestamp(value):
  # JSON strings avoid the JS 53-bit timestamp precision limit.
  if isinstance(value, bool) or not (isinstance(value, int) or isinstance(value, str) and value.isdigit()):
    raise ValueError('invalid_timestamp')
  value = int(value)
  if not 0 < value < 2**64:
    raise ValueError('invalid_timestamp')
  return value


def digest(value):
  return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def pose_index(document):
  if document.get('schema') != 'carrot-mapping-poses/v1':
    raise ValueError('unsupported_pose_schema')
  frame = document.get('frame', {})
  identifier(frame.get('id'))
  if frame.get('axes') != 'ENU' or frame.get('units') != 'm':
    raise ValueError('explicit_metric_ENU_required')
  trajectories = document.get('trajectories')
  if not isinstance(trajectories, list) or not 1 <= len(trajectories) <= 64:
    raise ValueError('trajectory_limit')
  result = {}
  for trip in trajectories:
    key = identifier(trip.get('trip_id'))
    if key in result:
      raise ValueError('duplicate_trip')
    for name in ('vehicle_id', 'clock_id', 'calibration_id'):
      identifier(trip.get(name))
    if trip.get('source') not in ('vio_optimized', 'rtk_fused', 'surveyed', 'synthetic'):
      raise ValueError('pose_source_required')
    rows = trip.get('poses')
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_OBSERVATIONS:
      raise ValueError('pose_limit')
    times, poses = [], []
    for row in rows:
      t = timestamp(row.get('timestamp_ns'))
      if times and t <= times[-1]:
        raise ValueError('pose_clock_not_increasing')
      poses.append((row, rotation(row.get('quaternion_wxyz')), vector(row.get('translation'), 3, 100_000)))
      finite(row.get('position_std_m'), 0, 1000)
      finite(row.get('orientation_std_deg'), 0, 180)
      times.append(t)
    result[key] = (trip, times, poses)
  # Never silently reuse another project's origin, even if axes have the same name.
  return {'id': frame['id'], 'axes': 'ENU', 'units': 'm'}, result


def build_map(observations, pose_document, previous=None):
  frame, index = pose_index(pose_document)
  if previous is not None and (previous.get('schema') != SCHEMA or previous.get('frame') != frame):
    raise ValueError('previous_frame_mismatch')
  if previous is not None:
    if (previous.get('revision') != digest({k: v for k, v in previous.items() if k != 'revision'})
        or previous.get('method') != 'model_lane_voxels_external_pose' or previous.get('voxel_m') != [1, 1, .5]
        or previous.get('ground_truth') is not False or previous.get('control_eligible') is not False
        or not isinstance(previous.get('cells'), list) or len(previous['cells']) > MAX_CELLS):
      raise ValueError('previous_revision_invalid')
    for cell in previous['cells']:
      vector(cell.get('xyz'), 3, 100_000)
  rejected, buckets, trips, seen, last = Counter(), {}, {}, set(), {}
  count = 0
  fingerprints = defaultdict(list)
  for obs in observations:
    count += 1
    if count > MAX_OBSERVATIONS:
      raise ValueError('observation_limit')
    if obs.get('schema') != 'carrot-lane-observations/v1' or obs.get('model_frame') != 'calibrated_FRD':
      raise ValueError('unsupported_observation_schema')
    trip_id = identifier(obs.get('trip_id'))
    if trip_id not in index:
      rejected['missing_trajectory'] += 1
      continue
    trip, times, poses = index[trip_id]
    if obs.get('clock_id') != trip['clock_id'] or obs.get('vehicle_id') != trip['vehicle_id']:
      raise ValueError('trip_identity_or_clock_mismatch')
    t, fid = timestamp(obs.get('timestamp_ns')), obs.get('frame_id')
    if not isinstance(fid, int) or isinstance(fid, bool) or fid < 0:
      raise ValueError('invalid_frame_id')
    key = (trip_id, t, fid)
    if key in seen:
      rejected['duplicate_frame'] += 1
      continue
    seen.add(key)
    if trip_id in last and t <= last[trip_id]:
      raise ValueError('observation_clock_not_increasing')
    last[trip_id] = t
    fingerprints[trip_id].append(digest({k: obs.get(k) for k in ('timestamp_ns', 'frame_id', 'lanes')}))
    i = bisect_left(times, t)
    i = min((j for j in (i-1, i) if 0 <= j < len(times)), key=lambda j: abs(times[j]-t))
    pose, rot, origin = poses[i]
    if abs(times[i]-t) > 25_000_000 or ('frame_id' in pose and pose['frame_id'] != fid):
      rejected['pose_time_or_frame_mismatch'] += 1
      continue
    if obs.get('valid') is not True or obs.get('calibration_valid') is not True:
      rejected['invalid_model_or_calibration'] += 1
      continue
    if pose['position_std_m'] > 1 or pose['orientation_std_deg'] > 2:
      rejected['pose_uncertainty'] += 1
      continue
    lanes = obs.get('lanes')
    if not isinstance(lanes, list) or len(lanes) > 4:
      raise ValueError('lane_limit')
    for lane in lanes:
      prob = finite(lane.get('probability'), 0, 1)
      std = finite(lane.get('std_m'), 0, 1000)
      points = lane.get('points')
      if not isinstance(points, list) or len(points) > 64:
        raise ValueError('lane_point_limit')
      if prob < .7 or std > 1:
        rejected['weak_lane'] += 1
        continue
      for raw in points:
        point = vector(raw, 3, 1000)
        if not 0 <= point[0] <= 60 or abs(point[1]) > 20 or abs(point[2]) > 10:
          rejected['range'] += 1
          continue
        bound = pose['position_std_m'] + std + np.linalg.norm(point)*math.radians(pose['orientation_std_deg'])
        if bound > 2:
          rejected['combined_uncertainty'] += 1
          continue
        world = rot @ point + origin
        if any(abs(v) > 100_000 for v in world):
          rejected['world_range'] += 1
          continue
        # Remove sub-nanometre floating-point noise at an exact voxel boundary.
        cell = tuple(math.floor(round(float(v)/s, 9)) for v, s in zip(world, (1, 1, .5), strict=True))
        if cell not in buckets:
          if len(buckets) >= MAX_CELLS:
            raise ValueError('cell_limit_split_project')
          buckets[cell] = {}
        # One vote per trip per cell: high frame rates cannot inflate support.
        existing = buckets[cell].get(trip_id)
        if existing is None or bound < existing[1]:
          buckets[cell][trip_id] = (world, bound)
        trips[trip_id] = {k: trip[k] for k in ('vehicle_id', 'clock_id', 'calibration_id', 'source')}
  # Same copied model observations under a new trip ID must not create independent support.
  signatures = [digest(value) for value in fingerprints.values()]
  if len(signatures) != len(set(signatures)):
    raise ValueError('duplicated_trip_content')
  cells = []
  for key, values in sorted(buckets.items()):
    coords = np.array([v[0] for v in values.values()])
    centre = np.median(coords, axis=0)
    radii = np.linalg.norm(coords-centre, axis=1)
    # Dispersion is observed disagreement, not surveyed accuracy or covariance.
    cells.append({'id': ','.join(map(str, key)), 'xyz': np.round(centre, 4).tolist(),
                  'trip_ids': sorted(values), 'vehicle_count': len({trips[t]['vehicle_id'] for t in values}),
                  'dispersion_m': round(float(max(radii)), 4),
                  'input_bound_m': round(float(max(v[1] for v in values.values())), 4)})
  old = {c['id']: c for c in previous.get('cells', [])} if previous else {}
  new = {c['id']: c for c in cells}
  changes = {'added_cells': sorted(new.keys()-old.keys()) if previous else [],
             'unobserved_cells': sorted(old.keys()-new.keys()),
             'shifted_cells': sorted(k for k in old.keys() & new.keys()
                                     if np.linalg.norm(np.array(new[k]['xyz'])-old[k]['xyz']) > .3)}
  project = {'schema': SCHEMA, 'frame': frame, 'ground_truth': False, 'control_eligible': False,
             'method': 'model_lane_voxels_external_pose', 'voxel_m': [1, 1, .5],
             'pose_verified': False, 'parent_revision': previous.get('revision') if previous else None,
             'trips': trips, 'cells': cells, 'changes': changes,
             'observations': count, 'rejected': dict(sorted(rejected.items())),
             'limitations': ['front_only', 'model_predictions', 'external_pose_unverified',
                             'correlated_errors', 'voxel_boundary_artifacts', 'changes_are_observations_only']}
  project['revision'] = digest(project)
  return project


def ply(project):
  rows = project['cells']
  header = f'ply\nformat ascii 1.0\ncomment model candidates, not ground truth\nelement vertex {len(rows)}\nproperty float x\nproperty float y\nproperty float z\nend_header\n'
  return header + ''.join(' '.join(map(str, r['xyz']))+'\n' for r in rows)
