from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

from openpilot.common.params import Params

from openpilot.selfdrive.carrot.carrot_controls import CarrotControls


def test_suspend_threshold_reads_remain_live_and_do_not_change_timers():
  control = CarrotControls.__new__(CarrotControls)
  control.lat_suspend_active = False
  control.lat_suspend_enter_t = control.lat_suspend_hold_t = 0.
  reads = []
  setting = [40]
  control.lat_suspend_angle = 300
  control.params = NS(get=lambda key: (reads.append(key), setting[0])[1])
  state = NS(steeringPressed=False, steeringAngleDeg=50.)
  for _ in range(100):
    assert control.lat_suspend_control(state, True)
  assert not reads
  state.steeringPressed = True
  for _ in range(50):
    assert control.lat_suspend_control(state, True)
  setting[0] = 60
  assert control.lat_suspend_control(state, True)
  assert control.lat_suspend_enter_t == 0.
  setting[0] = 40
  for _ in range(100):
    control.lat_suspend_control(state, True)
  assert control.lat_suspend_active
  count = len(reads)
  for _ in range(100):
    assert not control.lat_suspend_control(state, True)
  assert len(reads) == count
  state.steeringPressed = False
  state.steeringAngleDeg = 0.
  assert control.lat_suspend_control(state, True)
  assert not control.lat_suspend_active


def test_missing_suspend_setting_preserves_factory_then_last_observed_threshold(tmp_path):
  params = Params(str(tmp_path))
  with patch("openpilot.selfdrive.carrot.carrot_controls.Params", return_value=params):
    control = CarrotControls(None)
  key = "LatSuspendAngleDeg"
  state = NS(steeringPressed=True, steeringAngleDeg=20.)
  assert params.get_int(key) == 0 and params.get_default_value(key) == 300
  for _ in range(120):
    assert control.lat_suspend_control(state, True)
  params.put(key, 45)
  assert control.lat_suspend_control(state, True)
  params.put(key, 0)
  for _ in range(110):
    assert control.lat_suspend_control(state, True)
  Path(params.get_param_path(key)).write_text("unreadable")
  assert control.lat_suspend_control(state, True)
  assert control.lat_suspend_angle == 45
  params.remove(key)
  state.steeringAngleDeg = 50.
  for _ in range(110):
    control.lat_suspend_control(state, True)
  assert control.lat_suspend_active
  state.steeringAngleDeg = 5.
  state.steeringPressed = False
  for _ in range(60):
    control.lat_suspend_control(state, True)
  assert not control.lat_suspend_active
  assert not control.lat_suspend_control(state, False)
