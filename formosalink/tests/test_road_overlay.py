from types import SimpleNamespace

import pytest

from openpilot.sunnypilot.formosalink.stream_encoder import nv12_bytes


def test_overlay_only_paints_private_luma_and_chroma_planes():
  np = pytest.importorskip("numpy")
  width, height, stride = 64, 48, 72
  camera = bytes([128])*(stride*height*3//2)
  frame = SimpleNamespace(data=camera, width=width, height=height, stride=stride, uv_offset=height*stride)
  line = np.array([[np.nan, 10], [-3, 2], [15, 10], [60, 40]])
  raw, overlay = nv12_bytes(frame), nv12_bytes(frame, [(line, (170, 76, 68))])
  assert len(overlay) == len(raw) == width*height*3//2
  assert 170 in overlay[:width*height] and 76 in overlay[width*height:] and 68 in overlay[width*height:]
  assert frame.data == camera and set(raw) == {128}
