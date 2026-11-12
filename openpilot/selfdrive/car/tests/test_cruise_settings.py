import threading
from types import SimpleNamespace

import pytest

from openpilot.common.constants import CV
from openpilot.selfdrive.car.cruise import VCruiseCarrot


class Settings:
  def __init__(self):
    self.values = {'AutoCruiseControl': 10, 'AutoNaviSpeedSafetyFactor': 90, 'CruiseSpeed1': 0,
                   'CruiseSpeed2': 80, 'AutoRoadSpeedLimitOffset': -1, 'UseLaneLineSpeed': 60}
    self.calls = []
    self.read = lambda key: self.values.get(key, 0)

  def get_int(self, key):
    self.calls.append(key)
    return self.read(key)

  get_float = get_bool = get_int


def helper():
  h = VCruiseCarrot.__new__(VCruiseCarrot)
  h.params = Settings()
  h.frame = 0
  h.useLaneLineSpeed = h.useLaneLineSpeedApply = 60
  h.nRoadLimitSpeed = 50
  return h


def test_disk_stall_cannot_block_periodic_cruise_application():
  h = helper()
  h.refresh_params()
  previous = h.periodic_settings
  entered, release = threading.Event(), threading.Event()

  def stalled(key):
    if key == 'AutoCruiseControl':
      entered.set()
      assert release.wait(5)
    return 25

  h.params.read = stalled
  worker = threading.Thread(target=h.refresh_params)
  worker.start()
  try:
    assert entered.wait(5)
    reads = len(h.params.calls)
    # The actual control-path method completes while storage is still blocked.
    h.update_params(True)
    assert len(h.params.calls) == reads
    assert h.autoCruiseControl == 10
    assert h.periodic_settings is previous
  finally:
    release.set()
    worker.join(5)
  assert not worker.is_alive()
  h.update_params(True)
  assert h.autoCruiseControl == 25


@pytest.mark.parametrize('metric', [True, False])
def test_snapshot_keeps_conversion_lane_override_and_dynamic_road_limit(metric):
  direct, cached = helper(), helper()
  cached.refresh_params()
  for h in (direct, cached):
    h.update_params(metric)
    h.nRoadLimitSpeed = 80
    h.frame = 10
    h.update_params(metric)
  fields = ('autoCruiseControl', 'useLaneLineSpeedApply', 'applyModelSpeed', '_cruise_speed_table')
  assert [getattr(cached, f) for f in fields] == [getattr(direct, f) for f in fields]
  assert cached._cruise_speed_table[0] == pytest.approx(72)
  assert cached._cruise_speed_table[1] == pytest.approx(80 * (1 if metric else CV.MPH_TO_KPH))


def test_failed_refresh_never_publishes_partial_preferences():
  h = helper()
  h.refresh_params()
  previous = h.periodic_settings

  def failed(key):
    if key == 'AutoCruiseControl':
      raise OSError('storage unavailable')
    return 25

  h.params.read = failed
  with pytest.raises(OSError):
    h.refresh_params()
  assert h.periodic_settings is previous
  h.update_params(True)
  assert h.autoCruiseControl == 10


@pytest.mark.parametrize('brand', ['hyundai', 'gm'])
def test_only_gm_consumes_its_brake_command(brand):
  h = helper()
  h.CP = SimpleNamespace(brand=brand)
  h._brake_pressed_count = h._soft_hold_active = 0
  h.v_cruise_kph = h.v_ego_kph_set = 50
  h.disengage_on_accelerator = True
  h._gas_tok = False
  h._gas_pressed_count = 0
  h._gas_tok_timer = 40
  h._auto_speed_up = lambda value: value
  h._cruise_ready = False
  h.autoCruiseControl = 0
  actions, writes = [], []
  h.params.values['ActivateCruiseAfterBrake'] = 1
  h.params.put_bool_nonblocking = lambda key, value: writes.append((key, value))
  h._cruise_control = lambda *args: actions.append(args)
  h._update_cruise_state(SimpleNamespace(vEgo=0), SimpleNamespace(enabled=False), 50)
  if brand == 'gm':
    assert writes == [('ActivateCruiseAfterBrake', False)]
    assert actions == [(1, -1, 'Cruise on (brake)')]
  else:
    assert 'ActivateCruiseAfterBrake' not in h.params.calls
    assert not writes and not actions
