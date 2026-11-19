import asyncio

import pytest

from .gpu_priority_bench import DriveFirst
from .gpu_scene_relay import GpuSceneRelay


def test_idle_window_is_measured_from_next_drive_and_never_dispatches_expired_work():
  budget = DriveFirst(10, 5)
  assert budget.admit(1, 1.02, .8)
  for now, release, frame in [(1, 1.014, .8), (1, 1.1, .1), (1, 1.1, 1.1)]:
    assert not budget.admit(now, release, frame)
  budget.drive_completed(1.051, 1.05)
  assert not budget.admit(2, 3, 2)


def test_auxiliary_overrun_disables_future_dispatch():
  b = DriveFirst(8, 5)
  b.completed(1, 1.010, 1.05)
  assert not b.admit(2, 3, 2)
  with pytest.raises(ValueError):
    DriveFirst(float("nan"))


def test_relay_cannot_extend_capture_lifetime_with_duplicates_or_invalid_payloads():
  clock = [10.]
  relay = GpuSceneRelay(lambda: clock[0])
  jpeg = b"\xff\xd8image\xff\xd9"
  assert relay.publish(jpeg, 50, 3, 1)
  assert not relay.publish(jpeg, 50, 3, 1)
  assert not relay.publish(jpeg, float("nan"), 3, 1)
  assert not relay.publish(jpeg, 10, 1, 2)
  assert not relay.publish(b"invalid", 0, 0, 0)
  response = asyncio.run(relay.read(None))
  assert response.body == jpeg
  assert response.headers["X-Scene-Cells"] == "3"
  clock[0] += .9
  assert asyncio.run(relay.read(None)).status == 204


def test_parked_amd_bridge_gate():
  from types import SimpleNamespace
  from .usb_gpu_objects import check_bridge

  matches = lambda product: product == "approved"
  for bridge in (None, SimpleNamespace(speed_mbps=480, product="approved"), SimpleNamespace(speed_mbps=5000, product="unrecognized")):
    with pytest.raises(RuntimeError):
      check_bridge(bridge, matches)
  check_bridge(SimpleNamespace(speed_mbps=5000, product="approved"), matches)


def test_two_lens_yolox_accepts_only_supported_confident_finite_candidates():
  import numpy as np
  from .gpu_objects import INPUT, decode, model_input, output_grid

  image = np.zeros((INPUT, INPUT, 4), np.uint8)
  image[0, 0] = [1, 2, 3, 255]
  np.testing.assert_equal(model_input(image.tobytes())[0, :, 0, 0], [3, 2, 1])
  grid, strides = output_grid()
  raw = np.zeros((1, len(grid), 85), dtype=np.float32)
  for i, label in enumerate([2, 2, 0, 3]):
    raw[0, i, :4] = [12-i, 9, 1, 1]
    raw[0, i, 4] = raw[0, i, 5+label] = .9
  raw[0, 3, 0] = np.nan
  assert [x["kind"] for x in decode(raw,grid,strides)] == ["car", "person"]
