from pathlib import Path
import tempfile
import unittest

from tools.training_studio.release import accept,request_publish
from tools.training_studio.server import initialize
from tools.training_studio.store import write_json
from openpilot.sunnypilot.formosalink.training_protocol import digest_file


class ReleaseTest(unittest.TestCase):
  def test_training_completion_alone_cannot_publish(self):
    with tempfile.TemporaryDirectory() as temporary:
      store=initialize(Path(temporary)/'studio')
      folder=store.root/'runs'/'n16-test'
      folder.mkdir(parents=True)
      (folder/'candidate.onnx').write_bytes(b'fixture')
      write_json(folder/'training.json',{'candidate_sha256':digest_file(folder/'candidate.onnx')})
      write_json(folder/'evaluation.json',{'publishable':False})
      with self.assertRaises(ValueError):
        request_publish(store,'n16-test')
      self.assertFalse((folder/'publish-request.json').exists())

  def test_device_evidence_must_match_candidate(self):
    with tempfile.TemporaryDirectory() as temporary:
      store=initialize(Path(temporary)/'studio')
      folder=store.root/'runs'/'n16-test'
      folder.mkdir(parents=True)
      (folder/'candidate.onnx').write_bytes(b'fixture')
      checksum=digest_file(folder/'candidate.onnx')
      write_json(folder/'training.json',{'candidate_sha256':checksum})
      closed=Path(temporary)/'closed.json'
      device=Path(temporary)/'device.json'
      write_json(closed,{'candidate_sha256':checksum,'passed':True,'cases':[{'passed':True,'evidence_sha256':'a'*64}]})
      write_json(device,{'candidate_sha256':'b'*64,'passed':True})
      with self.assertRaises(ValueError):
        accept(store,'n16-test',closed,device)


if __name__=='__main__':
  unittest.main()
