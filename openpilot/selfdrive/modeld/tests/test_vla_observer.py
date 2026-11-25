import json
from types import SimpleNamespace as NS

import numpy as np
import pytest

from openpilot.selfdrive.modeld import vla_observer as observer, vla_status
from openpilot.tools.vla.shared_bench import PERIOD, PrimarySchedule


def model(eof=1_000_000_000):
  return NS(visionCompute='nonUsb', visionCameraInputs='roadWide', frameId=1, timestampEof=eof, frameAge=0, frameDropPerc=.02, leadsV3=[],
            modelExecutionTime=.019, action=NS(desiredAcceleration=0., desiredCurvature=0., shouldStop=True))


@pytest.mark.parametrize(('attr', 'value'), [('visionCompute', 'usbGpu'), ('visionCameraInputs', 'wide'), ('frameAge', 1),
                                            ('frameDropPerc', 1), ('modelExecutionTime', .05), ('modelExecutionTime', float('nan'))])
def test_primary_health(attr, value):
  m = model()
  assert observer.healthy_primary(m, m.timestampEof)
  setattr(m, attr, value)
  assert not observer.healthy_primary(m, m.timestampEof)


@pytest.mark.parametrize(('key', 'age', 'state'), [((1, 10), 499_999_999, 'result'), ((1, 10), 500_000_000, 'expired'),
                                                   ((1, 10), -1, 'expired'), ((2, 10), 0, 'expired'), ((1, 11), 0, 'expired')])
def test_match_and_age(key, age, state):
  r = observer.finished(key, (1, 10), {'should_stop': True}, {'longitudinal': 'cruise', 'lateral': None}, 10 + age)
  assert r['state'] == state
  assert r.get('comparison') == ('only_primary_stop' if state == 'result' else None)


@pytest.mark.parametrize(('should_stop', 'vla', 'comparison'), [(False, 'stop', 'only_vla_stop'), (True, 'stop', 'both_stop'),
                         (True, 'yield', 'inconclusive'), (True, None, 'inconclusive'), (False, 'pass', 'inconclusive')])
def test_independent_stop_judgments(should_stop, vla, comparison):
  assert vla_status.compare({'should_stop': should_stop}, {'longitudinal': vla}) == comparison


@pytest.mark.parametrize('stop,lead,turn,action,lateral,expected', [
  (True, False, 'turn right', 'stop', 'turn left', 'stop_agreement'),
  (True, False, None, 'pass', 'keep lane', 'review_stop'),
  (False, False, None, 'stop', None, 'review_stop'),
  (False, True, 'turn left', 'yield', 'turn left', 'review_yield'),
  (False, True, None, 'follow', 'keep lane', 'observed_follow'),
  (False, False, None, 'follow', 'keep lane', 'insufficient_evidence'),
  (False, False, 'turn right', 'cruise', 'turn right', 'turn_agreement'),
  (False, False, 'turn right', 'cruise', 'turn left', 'review_direction'),
  (False, False, 'branch left', 'pass', 'turn right', 'insufficient_evidence'),
  (False, False, None, None, 'turn left', 'insufficient_evidence'),
])
def test_scene_assessment_requires_specific_corroboration(stop, lead, turn, action, lateral, expected):
  primary = {'should_stop': stop, 'visual_lead': lead, 'route_maneuver': turn}
  assert vla_status.scene_assessment(primary, {'longitudinal': action, 'lateral': lateral}) == expected


def test_status_expires_actions_but_retains_historical_counts(tmp_path):
  path = tmp_path/'vla.json'
  counts = {'accepted': 1, 'expired': 0}
  path.write_text(json.dumps({'state': 'result', 'updated': 1000, 'eof': 100, 'comparison': 'both_stop', 'session': counts}))
  assert vla_status.read_status(1001, path) == {'state': 'result', 'eof': 100, 'comparison': 'both_stop', 'session': counts}
  assert vla_status.read_status(500_000_100, path) == {'state': 'expired', 'session': counts}
  assert vla_status.read_status(4_000_000_000, path) == {'state': 'idle', 'session': counts}
  assert vla_status.read_status(0, path) == {'state': 'idle'}
  for corrupt in ('[]', '1', '{'):
    path.write_text(corrupt)
    assert vla_status.read_status(0, path) == {'state': 'idle'}


@pytest.mark.parametrize(('usb', 'arch', 'size', 'valid'), [(True, 'gfx1200', 8, True), (lambda: True, 'gfx1200', 8, True),
                         (False, 'gfx1200', 8, False), (True, 'gfx1201', 8, False), (True, 'gfx1200', 16, False)])
def test_target(usb, arch, size, valid):
  device = NS(is_usb=usb, arch=arch, iface=NS(dev_impl=NS(vram_size=size << 30)))
  if valid:
    observer.require_target(device)
  else:
    with pytest.raises(RuntimeError):
      observer.require_target(device)


def test_road_source_plane_padding_and_reuse():
  from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
  w, h = 1344, 760
  stride, yh, _, size = get_nv12_info(w, h)
  raw = np.zeros(size, dtype=np.uint8)
  raw[:stride*h].reshape(h, stride)[:, :w] = 81
  uv = raw[stride*yh:stride*(yh+h//2)].reshape(h//2, stride)
  uv[:, :w:2], uv[:, 1:w:2] = 90, 240
  buf = NS(width=w, height=h, stride=stride, uv_offset=stride*yh, frame_id=1, data=raw)
  rgb = observer.copy_road(buf, 1)
  assert rgb.shape == (192, 320, 3) and rgb.dtype == np.uint8
  assert (rgb[:, :, 0] > 250).all() and (rgb[:, :, 1:] <= 1).all()
  assert observer.copy_road(buf, 2) is None
  class Reused:
    frames = iter([1, 2])
    frame_id = property(lambda self: next(self.frames))
  recycled = Reused()
  recycled.__dict__.update(vars(buf))
  assert observer.copy_road(recycled, 1) is None
  buf.data = raw[:16]
  assert observer.copy_road(buf, 1) is None


def test_priority_schedule_skips_expired_releases_and_charges_deadline():
  now = [1_000_000_000]
  def run():
    now[0] += 20_000_000
  schedule = PrimarySchedule(run, lambda: now[0])
  schedule.dispatch()
  schedule.dispatch()
  now[0] += 222_000_000
  schedule.dispatch()
  assert schedule.release == 1_000_000_000 + 5*PERIOD
  assert schedule.report() == {'executed': 2, 'skipped': 3, 'late': 1, 'p95_release_to_output_ms': 62, 'max_release_to_output_ms': 62}


@pytest.mark.parametrize(('delay', 'fault', 'terminal'), [(70, None, 'idle'), (550, None, 'too_slow'), (100, 'gear', 'idle'),
                         (70, 'primary_slow', 'primary_guard'), (70, 'power', 'usb_unavailable')])
def test_observation_loop_with_aligned_streams(monkeypatch, delay, fault, terminal):
  now = [10_000_000_000]
  started = now[0]
  states, submitted, killed = [], [], []
  pending = []
  child = NS(poll=lambda: None, kill=lambda: killed.append(1), wait=lambda timeout: None)

  def send(packet):
    assert not pending
    key, _, history = packet
    assert len(history) == 9 and history[-1] == [0., 0., 0.]
    submitted.append(key)
    pending.append((now[0] + delay*1_000_000, (key, {'longitudinal': 'stop', 'lateral': 'keep lane'})))
  channel = NS(send=send, poll=lambda: bool(pending and now[0] >= pending[0][0]), recv=lambda: pending.pop(0)[1], close=lambda: None)
  def start():
    pending.append((now[0], ('ready', None)))
    return child, channel
  monkeypatch.setattr(observer, 'start_worker', start)
  monkeypatch.setattr(observer, 'write_status', lambda **kw: states.append(json.loads(json.dumps(kw))))
  monkeypatch.setattr(observer, 'camera_clock', lambda: now[0])
  monkeypatch.setattr(observer, 'time', NS(monotonic_ns=lambda: now[0], sleep=lambda s: now.__setitem__(0, now[0] + int(s*1e9))))
  monkeypatch.setattr(observer, 'copy_road', lambda *_: 'test-rgb')
  sm = type('Streams', (dict,), {})()
  sm.update = lambda _: update()
  sm.valid = sm.alive = dict.fromkeys(('deviceState', 'modelV2', 'liveCalibration', 'carState', 'livePose'), True)
  camera = NS(is_connected=lambda: True, recv=lambda timeout_ms: object())
  def update():
    t = now[0] - now[0] % PERIOD
    frame = (t - started) // PERIOD
    m = model(t)
    m.frameId = frame
    camera.frame_id, camera.timestamp_eof = frame, t
    gear = 'park' if fault == 'gear' and submitted else 'drive'
    if fault == 'primary_slow' and submitted:
      m.modelExecutionTime = .07
    sm['carState'], sm['liveCalibration'] = NS(canValid=True, gearShifter=gear, vEgo=2.), NS(calStatus='calibrated', rpyCalib=[0., 0., 0.])
    sm['livePose'] = NS(timestamp=t, inputsOK=True, sensorsOK=True, posenetOK=True, angularVelocityDevice=NS(valid=True, x=0., y=0., z=0.))
    sm['deviceState'], sm['modelV2'] = NS(memoryUsagePercent=40, thermalStatus='green'), m
    sm.logMonoTime = dict.fromkeys(sm.valid, t)
    sm.updated = dict.fromkeys(sm.valid, t == now[0])
  def flag(k):
    return k in ('C4VlaObserve', 'IsOnroad') and now[0] < started + 5_000_000_000
  observer.observe(NS(get_bool=flag), sm, camera, lambda: '12V off' if fault == 'power' else None)
  assert states[-1]['state'] == terminal
  if fault == 'power':
    assert not killed and not submitted
    return
  assert submitted and killed == [1]
  if delay > 500:
    assert len(submitted) == 3 and states[-1]['session']['expired'] == 3
  elif fault:
    assert not any(s['state'] == 'result' for s in states)
  else:
    assert states[-1]['session']['accepted'] > 0
    assert any(s.get('comparison') == 'both_stop' for s in states)
    assert states[-1]['session']['last_scene'] == 'stop_agreement'
