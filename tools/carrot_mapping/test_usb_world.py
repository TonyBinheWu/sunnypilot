import numpy as np
import pytest

from .usb_world import check_volume, rgb_input, trial


def test_probabilities_and_unknown_rays():
  volume = np.zeros((1, 43, 36, 64), np.float32)
  free = np.zeros_like(volume)
  assert check_volume(volume, free) == 0
  volume[0, 1, 0, 1] = .4
  assert check_volume(volume, free) == 1
  free[0, 1, 0, 1] = 1
  with pytest.raises(ValueError):
    check_volume(volume, free)
  with pytest.raises(ValueError):
    rgb_input(bytes(16))
  image = rgb_input(bytes([255, 0, 0, 255]) * (224 * 126))
  assert image.shape == (1, 3, 126, 224) and image[0, 0, 0, 0] > 2


@pytest.mark.parametrize("drive_ms,aux_ms,admit", [(18, 4, True), (38, 10, False), (55, 1, False)])
def test_drive_has_priority(drive_ms, aux_ms, admit):
  clock = [0.]
  def advance(t):
    clock[0] += t
  report = trial(lambda:advance(drive_ms/1000), lambda:advance(aux_ms/1000), 10, lambda:clock[0], advance)
  assert bool(report["shared"]["aux"]["n"]) is admit
  assert report["suspended"] is (drive_ms > 50)
