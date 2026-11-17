import json

from opendbc.car.hyundai.steering_observations import SteeringObservations, decode, PROFILE_KEY, STATUS_KEY
from opendbc.car.hyundai.tests.test_low_speed_steer_reserve import state, torque_fixture
from opendbc.car.hyundai.tests.test_steering_handover_controller import step


class Memory(dict):
  def __init__(self, **kw):
    super().__init__(kw)
    self.writes = []

  def put_nonblocking(self, key, value):
    self.writes.append((key, value))
    self[key] = value


def observe(recorder, now=1., **kw):
  args = dict(now=now, enabled=True, active=True, cs=state(), requested=400, command=300,
              target_angle=30., base=270, ceiling=400, up=2, down=3, reason='rate_or_yield')
  args.update(kw)
  recorder.update(**args)


def test_records_are_bounded_async_and_restore_only_matching_profile():
  disk, runtime = Memory(), Memory()
  r = SteeringObservations('EV6', disk, runtime)
  cs = state()
  for n in range(6500):
    cs.steeringAngleDeg = n % 50
    observe(r, n*.01+1, cs=cs, requested=-400 if n % 2 else 400)
  assert r.data['stats']['samples'] == 6500
  assert r.data['stats']['left']['command'] == r.data['stats']['right']['command'] == 300
  assert r.data['stats']['left']['angleRate'] > 0
  assert len(disk.writes) == 2 and len(runtime.writes) <= 66
  assert len(runtime[STATUS_KEY]) < 8192
  restored = SteeringObservations('EV6', disk, Memory())
  assert restored.data['stats']['samples'] > 0
  assert SteeringObservations('OTHER', disk, Memory()).data['stats']['samples'] == 0
  assert decode(b'broken', 'EV6') is None
  damaged = json.loads(disk[PROFILE_KEY])
  damaged['stats']['left']['angle'] = float('nan')
  assert decode(json.dumps(damaged), 'EV6') is None
  # Mode exit flushes aggregates once; being inactive does not spam persistence.
  observe(r, 66., enabled=False, active=False)
  assert json.loads(disk[PROFILE_KEY])['stats']['samples'] == 6500
  count = len(disk.writes)
  for n in range(500):
    observe(r, 67.+n*.01, enabled=False, active=False)
  assert len(disk.writes) == count


def test_invalid_driver_fault_stale_and_high_speed_do_not_become_capabilities():
  r = SteeringObservations('EV6', Memory(), Memory())
  for overrides in [dict(enabled=False), dict(active=False), dict(cs=state(steeringPressed=True)),
                    dict(cs=state(steerFaultTemporary=True)), dict(reason='model'), dict(reason='request_cut')]:
    observe(r, **overrides)
  cs = state()
  cs.vEgoRaw = 100/3.6
  observe(r, cs=cs)
  cs.vEgoRaw = float('nan')
  observe(r, cs=cs)
  assert r.data['stats']['samples'] == 0
  observe(r, requested=float('nan'))
  assert r.previous is None


def test_observation_failure_and_tampered_records_cannot_change_real_can(monkeypatch):
  controller, cs, cc, settings = torque_fixture(monkeypatch)
  disk, runtime = Memory(), Memory()
  controller.steering_observations = SteeringObservations(controller.CP.carFingerprint, disk, runtime)
  trace = [step(controller, cs, cc)[0].torqueOutputCan for _ in range(300)]
  assert trace[-1] == 405
  current = json.loads(runtime[STATUS_KEY])['current']
  assert current['command'] == trace[200] and current['requested'] == 405
  # Even corrupted aggregate peaks never feed the cap, scale, or slew.
  controller.steering_observations.data['stats']['left']['command'] = 99999
  assert step(controller, cs, cc)[0].torqueOutputCan == 405
  class Failed:
    def update(self, **kw):
      raise OSError('storage unavailable')
  controller.steering_observations = Failed()
  assert step(controller, cs, cc)[0].torqueOutputCan == 405
  cs.out.vEgo = cs.out.vEgoRaw = 100/3.6
  assert [step(controller, cs, cc)[0].torqueOutputCan for _ in range(100)][-1] == 270
