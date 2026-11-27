"""Check the stock package on a host with DEV=MOCKUSB+AMD:LLVM and tinygrad_repo on PYTHONPATH."""
import pickle
import unittest
from pathlib import Path

import numpy as np
from examples.openpilot.helpers import load_pickle
from tinygrad import Context, Device, Tensor
from tinygrad.engine.realize import lower_and_compile

from openpilot.system.camerad.cameras.nv12_info import get_nv12_info

MODELS = Path(__file__).resolve().parents[2] / "openpilot/selfdrive/modeld/models"


class TestChestnutPackage(unittest.TestCase):
  def test_stock_model_and_camera_warps(self):
    # Initialize the emulated USB device before staging the weights in host RAM.
    # The pinned tinygrad mock has 512 MiB of VRAM.
    self.assertEqual(Device.default.device, "AMD")
    with Context(DEV="CPU:LLVM"):
      model = load_pickle(MODELS / "big_driving_tinygrad.pkl", out_of_band=True)
    lower_and_compile(model["run"].captured._linear)
    image_shape, image_dtype, model_device = model["input_specs"]["new_img"]
    self.assertEqual(model_device, "AMD")
    self.assertIn("outputs", model["output_specs"])

    for width, height in ((1344, 760), (1928, 1208)):
      with self.subTest(camera=(width, height)):
        with (MODELS / f"big_driving_warp_{width}x{height}_tinygrad.pkl").open("rb") as f:
          warp = pickle.load(f)
        stride, y_height, uv_height, _ = get_nv12_info(width, height)
        self.assertEqual(warp["input_specs"]["input_frame"], ((2, stride * (y_height + uv_height)), "|u1", model_device))
        self.assertEqual(warp["input_specs"]["M_inv"], ((2, 3, 3), "<f4", model_device))
        captured = warp["run"].captured
        captured._linear = lower_and_compile(captured._linear)
        self.assertEqual(captured.ret.shape, image_shape)
        self.assertEqual(np.dtype(captured.ret.dtype.fmt), np.dtype(image_dtype))

        frames = np.zeros((2, stride * (y_height + uv_height)), dtype=np.uint8)
        expected = []
        _, _, half_h, half_w = image_shape
        for i, frame in enumerate(frames):
          y = frame[:stride * y_height].reshape(y_height, stride)
          y[:] = (7 * np.arange(y_height)[:, None] + np.arange(stride) + 43 * i) % 251
          uv = frame[stride * y_height:].reshape(uv_height, stride)
          uv[:, ::2], uv[:, 1::2] = 25 + i, 220 - i
          crop = y[:2 * half_h, :2 * half_w]
          expected.append(np.stack((crop[::2, ::2], crop[1::2, ::2], crop[::2, 1::2], crop[1::2, 1::2],
                                    uv[:half_h, :2 * half_w:2], uv[:half_h, 1:2 * half_w:2])))
        transforms = np.stack([np.eye(3, dtype=np.float32)] * 2)
        actual = warp["run"](input_frame=Tensor(frames, device="AMD"), M_inv=Tensor(transforms, device="AMD"))
        np.testing.assert_array_equal(actual.numpy(), expected)


if __name__ == "__main__":
  unittest.main()
