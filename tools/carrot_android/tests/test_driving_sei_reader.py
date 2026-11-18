import importlib.util
import io
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('driving_sei_reader', Path(__file__).parents[1] / 'extract_driving_sei.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def message(value, hevc=True, uuid=reader.UUID):
  payload=uuid+json.dumps(value).encode()
  size=len(payload)
  sizes=b'\xff'*(size//255)+bytes([size%255])
  return b'\0\0\0\1'+(b'\x4e\1' if hevc else b'\6')+b'\5'+sizes+payload+b'\x80'


def test_both_codecs_multiple_messages_and_unrelated_uuid():
  for hevc,codec in [(True,'hevc'),(False,'h264')]:
    value={'schema':'formosa.drive.v1','speed_mps':20,'longitudinal_active':False,'padding':'x'*300}
    raw=message(value,hevc)+message(value,hevc,b'x'*16)+message({'schema':'other'},hevc)+message(value,hevc)
    assert list(reader.driving_metadata(io.BytesIO(raw),codec))==[value,value]


def test_fragmented_start_codes_and_truncated_payload():
  class Fragmented(io.BytesIO):
    def read(self,_size):return super().read(3)
  value={'schema':'formosa.drive.v1','speed_mps':None}
  assert list(reader.driving_metadata(Fragmented(message(value)),'hevc'))==[value]
  assert list(reader.driving_metadata(io.BytesIO(message(value)[:-6]),'hevc'))==[]
