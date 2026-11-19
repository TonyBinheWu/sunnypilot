import struct
from types import SimpleNamespace

from openpilot.selfdrive.carrot.realtime.compact_state import encode_carrot_state_frame


def test_invalid_event_flag_preserves_frame_layout_and_sequence():
  valid = encode_carrot_state_frame("radarState", SimpleNamespace(), 65535)
  invalid = encode_carrot_state_frame("radarState", SimpleNamespace(), 65535, valid=False)
  assert valid[5] == 0 and invalid[5] == 1
  assert valid[:5] == invalid[:5] and valid[6:] == invalid[6:]


def test_device_resource_fields_append_after_existing_telemetry():
  state = SimpleNamespace(memoryUsagePercent=40, freeSpacePercent=82, cpuTempC=[48.], deviceType="tici",
                          started=True, cpuUsagePercent=[5, 11, 85], gpuUsagePercent=37)
  frame = encode_carrot_state_frame("deviceState", state, 5)
  assert frame.endswith(struct.pack("<Hfffb", 3, 5., 11., 85., 37))
