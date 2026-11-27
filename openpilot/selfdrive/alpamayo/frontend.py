"""Causal, bounded two-camera inputs shared by live capture and replay."""
from bisect import bisect_right
from collections import OrderedDict, deque
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import copy
import hashlib
import json
from operator import attrgetter
import re
import threading

import numpy as np

from openpilot.selfdrive.alpamayo.segments import FrontImages, IMAGE

CAMERAS = (1, 6)
_stamp = attrgetter('stamp')
OFFSETS_NS = (-2_000_000_000, -1_000_000_000, -500_000_000, -100_000_000, 0)
HALF_SECOND_NS = 500_000_000
ROLLING_PERIODS_NS = (100_000_000, 250_000_000, 500_000_000)  # Each divides the -2, -1 and -0.5 s history offsets.


def ring_offsets(period_ns):
  """History offsets whose images are earlier slots' current exposures. With 100 ms slots the -0.1 s image is one too."""
  return tuple(offset for offset in OFFSETS_NS[:-1] if offset % period_ns == 0)


def anchor_window(period_ns):
  """How long after its opening a superseded slot can still be selected and encoded as a history anchor."""
  return max(4*period_ns, 800_000_000)


def slot_exposures(period_ns):
  """Exposures per camera that a rolling slot sends: the current one, and the -0.1 s one unless the ring holds it."""
  return len(OFFSETS_NS)-len(ring_offsets(period_ns))
FRAME_TOLERANCE_NS = 150_000_000
CAMERA_PERIOD_NS = 49_000_000  # 20 Hz frames jitter by ~0.2 ms: an older query means a newer frame exposed by the opening is on its way.
QUERY_WAIT_NS = 60_000_000
# A history exposure may start up to this long after its nominal offset, but never after the query. Real cameras jitter by
# about 0.2 ms per frame; without slack the -0.1 s image alternates between the 100 ms and 150 ms old exposures.
FRAME_SLACK_NS = 10_000_000
STATE_SAMPLE_OFFSETS_NS = np.arange(-38, 1, dtype=np.int64)*50_000_000  # car states and learned parameters are read only here
STATE_HISTORY_NS = 2_100_000_000  # the oldest state time any consumer reads: the -1.9 s history sample minus its tolerance
STATE_LIMITS = {'extrinsicsCalibration': 1_000_000_000, 'carState': 150_000_000,
                'vehicleParameters': 1_000_000_000, 'carParams': 120_000_000_000,
                'deviceMotion': 100_000_000, 'navInstructionCarrot': 2_000_000_000}


class Unavailable(ValueError):
  """A complete causal input is unavailable."""


class AwaitingFrame(Unavailable):
  """The camera and its exact modeld publication have not both arrived yet."""


class Priming(Unavailable):
  """A real anchor pair was retained, but the two-second history is incomplete."""
  def __init__(self, reason, anchors):
    super().__init__(reason)
    self.anchors = anchors


@dataclass(frozen=True)
class Frame:
  camera: int
  frame_id: int
  sof_ns: int
  eof_ns: int
  received_ns: int
  ready_ns: int
  pixels: np.ndarray
  format: str = 'rgb'

  def reference(self):
    return {'view': self.camera, 'frame_id': self.frame_id, 'capture_ns': self.sof_ns, 'eof_ns': self.eof_ns,
            'received_ns': self.received_ns, 'ready_ns': self.ready_ns, 'source_format': self.format}


@dataclass(frozen=True)
class State:
  stamp: int
  received: int
  value: object
  valid: bool = True


@dataclass(frozen=True)
class Selection:
  query_ns: int
  selected_ns: int
  frames: tuple[Frame, ...]
  states: dict[str, tuple[State, ...]]
  small_model: dict
  camera_gaps: dict = field(default_factory=dict)


def finite_state(value):
  """value when it is finite JSON within 64 KiB; None when it contains a non-finite number."""
  try:
    size = len(json.dumps(value, allow_nan=False))  # ensure_ascii=True; one byte per character.
  except ValueError:
    return None
  if size > 64*1024:
    raise ValueError('State exceeds 64 KiB')
  return value


def required(rows, stamp, max_age):
  index = bisect_right(rows, stamp, key=_stamp)-1
  if index < 0 or stamp-rows[index].stamp > max_age or not rows[index].valid:
    raise Unavailable('Missing, invalid, or stale state')
  return rows[index].value, rows[index].stamp


class Store:
  def __init__(self, frame_limit=64, byte_limit=256*1024**2, state_limit=512):
    if frame_limit < 5 or byte_limit <= 0 or state_limit < 40:
      raise ValueError('Insufficient positive history bounds')
    self.frame_limit, self.byte_limit, self.state_limit = frame_limit, byte_limit, state_limit
    self.frames = {camera: deque() for camera in CAMERAS}
    self.camera_gaps = dict.fromkeys(CAMERAS, 0)
    self.states = {kind: [] for kind in (*STATE_LIMITS, 'modelV2')}
    self.bytes = 0
    self.lock = threading.Lock()

  def add_frame(self, frame):
    if (frame.camera not in CAMERAS or frame.frame_id < 0 or
        not 0 < frame.sof_ns <= frame.eof_ns <= frame.received_ns <= frame.ready_ns or
        frame.pixels.dtype != np.uint8 or not frame.pixels.flags.c_contiguous or frame.pixels.flags.writeable or
        frame.pixels.nbytes > min(self.byte_limit, 8*1024**2) or
        frame.format not in ('rgb', 'nv12') or
        (frame.format == 'rgb' and (frame.pixels.ndim != 3 or frame.pixels.shape[0] != 3)) or
        (frame.format == 'nv12' and (frame.pixels.ndim != 2 or frame.pixels.shape[0] % 3 or frame.pixels.shape[1] % 2))):
      raise ValueError('Invalid frame or mutable pixel storage')
    with self.lock:
      ring = self.frames[frame.camera]
      if ring and (frame.sof_ns <= ring[-1].sof_ns or frame.frame_id <= ring[-1].frame_id):
        return False
      if ring:
        self.camera_gaps[frame.camera] += max(0, frame.frame_id-ring[-1].frame_id-1)
      ring.append(frame)
      self.bytes += frame.pixels.nbytes
      for candidate in self.frames.values():
        while candidate and (len(candidate) > self.frame_limit or candidate[0].sof_ns < frame.sof_ns-3_300_000_000):
          self.bytes -= candidate.popleft().pixels.nbytes
      while self.bytes > self.byte_limit:
        oldest = min((r for r in self.frames.values() if r), key=lambda r: r[0].sof_ns)
        self.bytes -= oldest.popleft().pixels.nbytes
    return True

  def add_state(self, kind, stamp, received, value, valid=True, *, owned=False):
    """modelV2 values are capture.SmallModelOutput: select() converts and checks only the matched one."""
    if kind not in self.states or not 0 < stamp <= received:
      raise ValueError('Invalid state timestamps')
    if kind == 'modelV2':
      if not (hasattr(value, 'decode') and type(value.frame_id) is int and type(value.eof_ns) is int):
        raise ValueError('Expected an undecoded modelV2 output')
      owned = True  # immutable until decoded
    elif valid and finite_state(value) is None:
      if not owned:
        raise ValueError('Nonfinite state value')
      valid = False  # An invalid live update must still supersede the earlier state.
    row = State(stamp, received, (value if owned else copy.deepcopy(value)) if valid else None, valid)
    with self.lock:
      rows = self.states[kind]
      index = bisect_right(rows, stamp, key=_stamp)
      if index and rows[index-1].stamp == stamp:
        if received <= rows[index-1].received:
          return
        rows[index-1] = row
      else:
        rows.insert(index, row)
      horizon = 121_000_000_000 if kind == 'carParams' else 3_300_000_000
      while rows and (len(rows) > self.state_limit or rows[0].stamp < received-horizon):
        rows.pop(0)

  def select(self, now, last_query=0, last_current=None, *, half_second_slot=None, cached=None, cached_offsets=(0, 1, 2),
             max_age_ns=250_000_000, exposures=2):
    """cached: {camera: frame IDs the worker already holds}. For the listed history offsets, prefer the newest held frame
    inside the same causal window, so free-running inference re-encodes as few images as possible."""
    with self.lock:
      rings = {c: tuple(f for f in ring if f.ready_ns <= now) for c, ring in self.frames.items()}
      states = {k: tuple(r for r in rows if r.received <= now) for k, rows in self.states.items()}
      gaps = self.camera_gaps.copy()
    # The query is the newest narrow frame exposed by the slot opening; it never waits for the small model, whose output
    # trails the camera by about two frames. A frame is ready about 41 ms after its SOF, so the opening's last frame
    # arrives within QUERY_WAIT_NS. The matched small-model output is recorded when present.
    current = next((frame for frame in reversed(rings[6]) if half_second_slot is None or frame.sof_ns <= half_second_slot), None)
    if current is None:
      raise AwaitingFrame('No query frame')
    if half_second_slot is not None and half_second_slot-current.sof_ns > CAMERA_PERIOD_NS and now < half_second_slot+QUERY_WAIT_NS:
      raise AwaitingFrame('Slot frame not ready')
    query = current.sof_ns
    model = next((row for row in states['modelV2'] if row.valid and (row.value.frame_id, row.value.eof_ns) == (current.frame_id, current.eof_ns)), None)
    if query <= last_query or not 0 <= now-query <= max_age_ns:
      raise AwaitingFrame('No fresh query')
    if half_second_slot is not None and not (query <= half_second_slot <= now and half_second_slot-query <= FRAME_TOLERANCE_NS):
      raise AwaitingFrame('No fresh half-second anchor')
    offsets = OFFSETS_NS if half_second_slot is None else OFFSETS_NS[-exposures:]
    frames = []
    for camera in CAMERAS:
      ring = rings[camera]
      times = [f.sof_ns for f in ring]
      for k, offset in enumerate(offsets):
        desired = query+offset
        index = bisect_right(times, min(desired+FRAME_SLACK_NS, query))-1
        if index < 0 or desired-times[index] > FRAME_TOLERANCE_NS:
          raise Unavailable('Missing causal camera history')
        if cached and half_second_slot is None and k in cached_offsets:
          held = cached.get(camera, ())
          index = next((j for j in range(index, -1, -1) if desired-times[j] <= FRAME_TOLERANCE_NS and ring[j].frame_id in held), index)
        frames.append(ring[index])
      if len({f.sof_ns for f in frames[-len(offsets):]}) != len(offsets) or frames[-1].sof_ns <= (last_current or {}).get(camera, 0):
        raise Unavailable('Repeated or stalled camera history')
    # Only the matched small-model output is consumed. Vehicle states are read at most STATE_HISTORY_NS before the query
    # (the -1.9 s history sample and its tolerance) through latest-row lookups: keep those rows and the newest older one.
    del states['modelV2']
    for kind, rows in states.items():
      states[kind] = rows[max(bisect_right(rows, query-STATE_HISTORY_NS, key=_stamp)-1, 0):]
    for kind in ('carState', 'vehicleParameters'):
      # Consumers read these only at the STATE_SAMPLE_OFFSETS_NS grid through required(): keeping each sample's latest
      # row returns identical lookups and a ~5x smaller snapshot header (carState arrives at 100 Hz).
      rows = states[kind]
      keep = sorted({i for i in (bisect_right(rows, int(query+offset), key=_stamp)-1 for offset in STATE_SAMPLE_OFFSETS_NS) if i >= 0})
      states[kind] = tuple(rows[i] for i in keep)
    output = model.value.decode() if model else None  # None for a non-finite output, like an invalid row
    return Selection(query, now, tuple(frames), states, {'log_mono_time': model.stamp if output is not None else None, 'model': output}, gaps)


DEFAULT_NAVIGATION = 'Follow the road.'


def navigation(rows, query, default=DEFAULT_NAVIGATION, within_m=None):
  # Without usable route guidance the model gets the default instruction, so it follows the road where straight ends.
  text, meta = route_navigation(rows, query)
  if text and within_m is not None and meta['instruction']['maneuverDistance'] > within_m:
    # A maneuver far ahead makes the model start it early: with "Turn right in 800m" 39% of straight-road plans moved more
    # than 1 m right within 6.4 s (12% at 150 m). The model gets the instruction only inside `navigation_within_m`.
    return default, dict(meta, source='default-far', model_instruction=default)
  if text:
    return text, meta
  return default, dict(meta, source='default', model_instruction=default)


def route_navigation(rows, query):
  # A received cancellation or route replacement invalidates older guidance,
  # even when its publication follows the selected camera's exposure.
  if rows and not rows[-1].valid:
    return '', {'source': 'unavailable', 'log_mono_time': rows[-1].stamp}
  try:
    value, stamp = required(rows, query, STATE_LIMITS['navInstructionCarrot'])
  except Unavailable:
    return '', {'source': 'unavailable', 'log_mono_time': None}
  secondary = ' '.join(value.get('maneuverSecondaryText', '').split())
  kind, modifier = value.get('maneuverType', ''), value.get('maneuverModifier', '')
  distance = value['maneuverDistance']
  # Legacy HUD messages have no provider timestamp. A fresh relay of old native guidance must not extend its life.
  source_stamp = value.get('carrotSourceMonoTime', 0) if value.get('carrotSource', 'unknown') != 'unknown' else stamp
  if (not 0 < source_stamp <= stamp or query - source_stamp >= STATE_LIMITS['navInstructionCarrot'] or
      not np.isfinite(distance) or distance < 0 or
      any(not row.valid or any(row.value.get(key) != value.get(key) for key in
          ('carrotSource', 'routeRevision', 'maneuverPrimaryText', 'maneuverSecondaryText', 'maneuverType', 'maneuverModifier'))
          or not np.isfinite(row.value['maneuverDistance']) or row.value['maneuverDistance'] < 0
          for row in rows if row.stamp > stamp)):
    return '', {'source': 'unavailable', 'log_mono_time': stamp}
  direction = {'left': 'left', 'right': 'right', 'slight left': 'slightly left', 'slight right': 'slightly right',
               'sharp left': 'sharply left', 'sharp right': 'sharply right', 'straight': 'straight'}.get(modifier, '')
  action = {'turn': 'Turn', 'end of road': 'At the end of the road, turn', 'fork': 'Keep', 'merge': 'Merge',
            'on ramp': 'Take the ramp', 'off ramp': 'Take the exit', 'continue': 'Continue', 'new name': 'Continue',
            'depart': 'Depart', 'arrive': 'Arrive at the destination', 'roundabout': 'Enter the roundabout',
            'rotary': 'Enter the roundabout', 'roundabout turn': 'At the roundabout, turn',
            'exit roundabout': 'Exit the roundabout', 'exit rotary': 'Exit the roundabout'}.get(kind, '')
  if modifier == 'uturn':
    action, direction = 'Make a U-turn', ''
  # The model gets only maneuver, direction, roundabout exit and distance ("Turn right in 100m").
  # Road names and sign text stay in the audit; an unrecognized maneuver sends the default text.
  text = ''
  if action:
    text = action+(f' {direction}' if direction and kind != 'arrive' else '')
    if kind in ('roundabout', 'rotary', 'roundabout turn'):
      banner = value['maneuverPrimaryText']+' '+secondary
      exit_match = re.search(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+exit\b|\bexit\s+(\d{1,2})\b', banner, re.IGNORECASE)
      if exit_match:
        text = f'At the roundabout, take exit {exit_match.group(1) or exit_match.group(2)}'
  if not text:
    return '', {'source': 'unavailable', 'log_mono_time': stamp}
  text = f'{text} in {round(distance)}m'
  return text, {'source': 'navInstructionCarrot', 'log_mono_time': stamp, 'instruction': value, 'model_instruction': text}


class Preparer:
  def __init__(self, geometry, cache_limit=48, sampler=None, *, segmented=False, period_ns=HALF_SECOND_NS, free=False,
               default_navigation=DEFAULT_NAVIGATION, navigation_within_m=None):
    self.default_navigation = default_navigation  # ALPAMAYO_CONFIG `default_navigation`
    self.navigation_within_m = navigation_within_m  # ALPAMAYO_CONFIG `navigation_within_m`; None sends every distance
    self.state_pool = None  # created on first use, on the worker thread's cores
    if cache_limit < 0:
      raise ValueError('Negative image cache capacity')
    if any(tuple(geometry['cameras'][str(c)]['prepared_size']) != (768, 432) for c in CAMERAS):
      raise ValueError('Keep the full calibrated reference resolution: 768x432')
    self.geometry = copy.deepcopy(geometry)
    self.cache, self.cache_limit = OrderedDict(), cache_limit
    self.sampler = sampler
    self.segmented = segmented
    if period_ns not in ROLLING_PERIODS_NS:
      raise ValueError('Rolling front history requires a 100, 250 or 500 ms slot period')
    if free and not segmented:
      raise ValueError('Free-running inference requires retained CPU inputs')
    self.free = free
    self.on_current = None  # Called with a complete slot's projected current pair before the rest of preparation.
    self.retained = OrderedDict()  # Free-running: (camera, frame_id, sof, calibration) -> projected bytes.
    self.period = period_ns
    # Older history images are the current exposures of earlier slots: -2, -1 and -0.5 s back (and -0.1 s with 100 ms slots).
    self.ring = ring_offsets(period_ns)
    self.lags = tuple(-offset//period_ns for offset in self.ring)
    self.per_slot = slot_exposures(period_ns)
    self.anchors = deque(maxlen=self.lags[0]+2)  # two spare entries: a missed slot can be replaced by its neighbour
    self.early_views = OrderedDict()  # (camera, frame_id, sof, calibration) -> projected bytes of a predicted -0.1 s exposure
    self.early_lock = threading.Lock()  # early() runs on the worker's early-encoding thread

  def free_images(self, selected):
    """Free-running: reuse held projections; project only frames that arrived with pixels."""
    keys, fresh = [], []
    for frame in selected.frames:
      calibration, stamp = required(selected.states['extrinsicsCalibration'], frame.sof_ns, STATE_LIMITS['extrinsicsCalibration'])
      key = self.early_key(frame, calibration)
      keys.append((key, stamp, calibration))
      if key not in self.retained and frame.pixels is None:
        raise Unavailable('A held camera frame needs projection again')
      if key not in self.retained and all(frame is not f for f in fresh):
        fresh.append(frame)
    if fresh:
      projected, _ = self.project(tuple(fresh), selected.states, reuse=False)
      for frame, (image, ref) in zip(fresh, projected, strict=True):
        self.retained[self.early_key(frame, ref['image_calibration'])] = image
    views = []
    for frame, (key, stamp, calibration) in zip(selected.frames, keys, strict=True):
      self.retained.move_to_end(key)
      views.append((self.retained[key], {**frame.reference(), 'image_calibration_ns': stamp, 'image_calibration': copy.deepcopy(calibration)}))
    while len(self.retained) > 96:
      self.retained.popitem(last=False)
    return views, len(selected.frames)-len(fresh)

  def early(self, selected):
    """Project a predicted -0.1 s pair before its slot. The slot reuses these exact bytes if it selects the same frames."""
    if not self.segmented:
      raise Unavailable('Early projection requires retained CPU inputs')
    unique = list({(f.camera, f.frame_id): f for f in selected.frames}.values())  # Alternates can repeat a frame.
    projected = {(f.camera, f.frame_id): image for (image, ref), f in zip(self.project(unique, selected.states, reuse=False)[0], unique, strict=True)}
    refs = []
    for frame in unique:
      calibration, _ = required(selected.states['extrinsicsCalibration'], frame.sof_ns, STATE_LIMITS['extrinsicsCalibration'])
      with self.early_lock:
        self.early_views[self.early_key(frame, calibration)] = projected[(frame.camera, frame.frame_id)]
    for frame in selected.frames:
      refs.append((projected[(frame.camera, frame.frame_id)], {'view': frame.camera, 'capture_ns': frame.sof_ns}))
    with self.early_lock:
      while len(self.early_views) > 8:
        self.early_views.popitem(last=False)
    return refs

  @staticmethod
  def early_key(frame, calibration):
    return frame.camera, frame.frame_id, frame.sof_ns, json.dumps(calibration, sort_keys=True)

  def prepare(self, selected, half_second_slot=None):
    query, states = selected.query_ns, selected.states
    if half_second_slot is not None:
      # The state inputs (history, parameters, navigation) do not depend on the images: compute them on a second thread
      # while this one projects and uploads the camera pair. Image errors keep their priority over state errors.
      if self.state_pool is None:
        self.state_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='alpamayo-states')  # inherits the worker's cores
      pending = self.state_pool.submit(self.state_inputs, selected)
      try:
        views, hits = self.rolling_images(selected, half_second_slot)
      except BaseException:
        concurrent.futures.wait([pending])
        raise
      cal, cal_ns, xyz, rot, history, nav, nav_meta = pending.result()
    else:
      cal, cal_ns, xyz, rot, history, nav, nav_meta = self.state_inputs(selected)
      views, hits = self.free_images(selected) if self.free else self.project(selected.frames, states)
    images, refs = zip(*views, strict=True)
    refs = [dict(ref, requested_ns=query+offset) for ref, offset in zip(refs, OFFSETS_NS*2, strict=True)]
    arrays = {'image_frames': FrontImages(images) if self.segmented and (half_second_slot is not None or self.free) else np.stack(images),
              'camera_indices': np.array([1]*5+[6]*5, dtype=np.int64),
              'absolute_timestamps': np.array([ref['capture_ns']//1000 for ref in refs], dtype=np.int64),
              'ego_history_xyz': xyz, 'ego_history_rot': rot, 'nav_text': [nav]}
    metadata = {'query_ns': query, 'selected_ns': selected.selected_ns, 'frames': refs, 'small_model': selected.small_model,
                'calibration_rpy': cal['rpyCalib'], 'calibration': copy.deepcopy(cal), 'calibration_log_mono_time': cal_ns,
                'ego_history_xyz': xyz.tolist(),
                'ego_history_rot': rot.tolist(), 'vehicle_history': history, 'navigation_text': nav, 'navigation': nav_meta,
                'camera_profile': 'calibrated_vehicle_history', 'image_cache_hits': hits, 'camera_gaps': selected.camera_gaps}
    return arrays, metadata

  def state_inputs(self, selected):
    """Calibration, ego history, vehicle parameters and navigation text of a selection; independent of its images."""
    from openpilot.selfdrive.alpamayo.history import ego_history
    query, states = selected.query_ns, selected.states
    cal, cal_ns = required(states['extrinsicsCalibration'], query, STATE_LIMITS['extrinsicsCalibration'])
    xyz, rot, history = ego_history(states, query, cal['rpyCalib'])
    cp, cp_ns = required(states['carParams'], query, STATE_LIMITS['carParams'])
    history['car_params'] = {'source_ns': cp_ns, 'age_ms': (query-cp_ns)/1e6, 'values': copy.deepcopy(cp)}
    history['learned_parameters'] = []
    for sample_ns in query+STATE_SAMPLE_OFFSETS_NS:
      parameters, stamp = required(states['vehicleParameters'], int(sample_ns), STATE_LIMITS['vehicleParameters'])
      history['learned_parameters'].append({'sample_ns': int(sample_ns), 'source_ns': stamp, 'age_ms': (int(sample_ns)-stamp)/1e6,
                                            'values': copy.deepcopy(parameters),
                                            'applied_stiffness_factor': max(parameters['stiffnessFactor'], .1),
                                            'applied_steer_ratio': max(parameters['steerRatio'], .1)})
    nav, nav_meta = navigation(states.get('navInstructionCarrot', ()), query, self.default_navigation, self.navigation_within_m)
    return cal, cal_ns, xyz, rot, history, nav, nav_meta

  def older(self, opening, query):
    """Earlier slots' current exposures for each ring offset, per camera; None while the ring lacks one.

    A missed slot is replaced by a neighbouring slot when its exposures still lie within FRAME_TOLERANCE_NS of the offset.
    """
    slots = dict(self.anchors)
    chosen = []
    for offset in self.ring:
      target = opening+offset
      chosen.append(next((s for s in (target, target-self.period, target+self.period) if s in slots and s < opening and
                          all(abs(query+offset-ref['capture_ns']) <= FRAME_TOLERANCE_NS for _, ref in slots[s])), None))
    if None in chosen or len(set(chosen)) != len(chosen):
      return None
    return [[slots[s][i] for s in chosen] for i in range(len(CAMERAS))]

  def next_front_images(self):
    """The next slot's ring images of the first camera (before its own exposures arrive), for early prefill; else None."""
    if not self.anchors:
      return None
    opening = self.anchors[-1][0]+self.period
    older = self.older(opening, opening)
    return None if older is None else [image for image, _ in older[0]]

  def rolling_images(self, selected, opening, *, anchor_only=False):
    """Only retain owned, calibrated pixels. The worker unmaps the input after each slot."""
    query, frames, per = selected.query_ns, selected.frames, self.per_slot
    # A superseded slot is anchored after newer slots opened; its frames still carry their own capture times.
    window = anchor_window(self.period) if anchor_only else self.period
    if not (len(frames) == per*len(CAMERAS) and opening <= selected.selected_ns < opening+window and
            0 <= opening-query <= FRAME_TOLERANCE_NS and frames[-1].sof_ns == query):
      raise Unavailable('Front query is outside its slot')
    if self.anchors and opening <= self.anchors[-1][0]:
      raise Unavailable('Front slot did not advance')
    for i, camera in enumerate(CAMERAS):
      exposures = frames[per*i:per*i+per]
      current = exposures[-1]
      if not (all(f.camera == camera for f in exposures) and 0 <= query-current.sof_ns <= FRAME_TOLERANCE_NS and
              max(f.ready_ns for f in exposures) <= selected.selected_ns):
        raise Unavailable('Missing, repeated or stale front exposure')
      if per == 2:
        prior = exposures[0]
        if not (prior.frame_id < current.frame_id and prior.sof_ns < current.sof_ns and
                -FRAME_SLACK_NS <= query-100_000_000-prior.sof_ns <= FRAME_TOLERANCE_NS):
          raise Unavailable('Missing, repeated or stale front exposure')
      if self.anchors:
        _, last = self.anchors[-1][1][i]
        if last['capture_ns'] >= exposures[0].sof_ns or last['frame_id'] >= exposures[0].frame_id:
          raise Unavailable('Front exposure did not advance')
    older = self.older(opening, query)
    complete = older is not None and not anchor_only
    # The older images come directly from the anchor ring. These exposures must advance, so project their actual bytes once.
    fresh, hits = self.project(frames if complete else frames[per-1::per], selected.states, reuse=False)
    current_views = fresh[per-1::per] if complete else fresh
    if complete and self.on_current is not None:
      self.on_current([(image, ref) for image, ref in current_views])
    self.anchors.append((opening, [(image, dict(ref, anchor_slot_ns=opening, anchor_query_ns=query, anchor_selected_ns=selected.selected_ns))
                                  for image, ref in current_views]))
    if anchor_only:
      raise Priming('Retaining current camera pair after worker overrun', self.anchors[-1][1])
    if older is None:
      reason = 'Repriming after missed slots or a capture gap' if len(self.anchors) == self.anchors.maxlen else 'Priming front-camera anchors'
      raise Priming(f'{reason} ({len(self.anchors)} of {self.lags[0]} slots)', self.anchors[-1][1])
    return [frame for i, view in enumerate(older) for frame in (*view, *fresh[per*i:per*i+per])], hits+len(self.ring)*len(CAMERAS)

  def project(self, frames, states, *, reuse=True):
    from openpilot.selfdrive.alpamayo.geometry import calibrated_image
    refs, keys, missing, hits = [], [], {}, 0
    cache = self.cache if reuse else {}
    for frame in frames:
      calibration, stamp = required(states['extrinsicsCalibration'], frame.sof_ns, STATE_LIMITS['extrinsicsCalibration'])
      # Content identity survives the process boundary and invalidates reused
      # frame IDs, changed pixels, and changed calibration without approximation.
      key = (frame.camera, frame.pixels.shape, frame.format, hashlib.sha256(frame.pixels).digest(), json.dumps(calibration, sort_keys=True)) if reuse else len(keys)
      with self.early_lock:
        early = None if reuse else self.early_views.get(self.early_key(frame, calibration))
      if early is not None:
        cache[key] = early
        hits += 1
      elif key in cache or key in missing:
        hits += 1
      else:
        missing[key] = frame, calibration
      keys.append(key)
      refs.append({**frame.reference(), 'image_calibration_ns': stamp, 'image_calibration': copy.deepcopy(calibration)})
    def warp(item):
      frame, calibration = item
      pixels = frame.pixels
      if frame.format == 'nv12' and self.sampler is None:
        import av
        pixels = np.ascontiguousarray(av.VideoFrame.from_ndarray(pixels, format='nv12').to_ndarray(format='rgb24').transpose(2, 0, 1))
      # The native sampler takes NV12 directly and converts only the region it samples.
      image = (self.sampler or calibrated_image)(pixels, frame.camera, self.geometry, calibration)
      if self.segmented and not reuse:
        if image.shape != IMAGE[1:] or image.dtype != np.uint8:
          raise ValueError('Invalid calibrated exposure')
        return image.tobytes(order='C')  # Freeze only newly projected pixels, before the source mapping closes.
      if np.shares_memory(image, frame.pixels):
        image = image.copy()  # The source mapping closes when this snapshot finishes.
      image.flags.writeable = False
      return image
    if self.sampler is not None and not reuse and len(missing) > 1:
      # Each camera owns its two fresh warps. A changed calibration then builds one map per camera.
      def camera_images(camera):
        return {key: warp(item) for key, item in missing.items() if item[0].camera == camera}
      with ThreadPoolExecutor(max_workers=1) as pool:
        wide = pool.submit(camera_images, CAMERAS[0])
        cache.update(camera_images(CAMERAS[1]))
        cache.update(wide.result())
    elif self.sampler is not None and len(missing) > 1:
      # Both workers finish before mapped frame storage is released. Only this thread mutates the LRU.
      with ThreadPoolExecutor(max_workers=2) as pool:
        cache.update(zip(missing, pool.map(warp, missing.values()), strict=True))
    else:
      cache.update((key, warp(item)) for key, item in missing.items())
    images = [cache[key] for key in keys] if self.segmented and not reuse else [cache[key][None] for key in keys]
    if reuse:
      for key in keys:
        self.cache.move_to_end(key)
      while len(self.cache) > self.cache_limit:
        self.cache.popitem(last=False)
    return list(zip(images, refs, strict=True)), hits
