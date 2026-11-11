"""Run the production persistent encoder against a real Linux FFmpeg process."""
import sys
from types import SimpleNamespace

import pytest

from openpilot.sunnypilot.formosalink.media_protocol import jpeg_size
from openpilot.sunnypilot.formosalink.stream_encoder import StreamEncoder

pytestmark = pytest.mark.skipif(sys.platform != 'linux', reason='Native encoder uses Linux pipe select and nice')


@pytest.mark.parametrize('width,height', [(64,48), (1928,1208)])
def test_actual_ffmpeg_first_frame_and_process_reuse(tmp_path, monkeypatch, width, height):
  import imageio_ffmpeg
  stride, offset = width+8, (width+8)*(height+8)
  data = bytearray([96]*offset+[128]*(stride*height//2))
  original = bytes(data)
  frame = SimpleNamespace(width=width, height=height, stride=stride, uv_offset=offset, data=data)
  (tmp_path/'ffmpeg').symlink_to(imageio_ffmpeg.get_ffmpeg_exe())
  monkeypatch.setitem(sys.modules, 'ffmpeg', SimpleNamespace(BIN_DIR=tmp_path))
  encoder = StreamEncoder()
  process = None
  try:
    for _ in range(3):
      jpeg = encoder(frame)
      out_width, out_height = jpeg_size(jpeg)
      assert 0 < out_width <= 640 and 0 < out_height <= 360
      if process is None:
        process = encoder.process
      assert encoder.process is process and process.poll() is None
    assert data == original
  finally:
    encoder.close()
  assert process is not None and process.poll() is not None
