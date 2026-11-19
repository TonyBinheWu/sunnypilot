import hashlib
from pathlib import Path
import tempfile
import unittest
import numpy as np

from tools.training_studio.store import read_json,write_json
from tools.training_studio.teacher_replay import append_replay


class TeacherReplayTest(unittest.TestCase):
  def test_quarantined_draft_cannot_be_added_even_when_packet_checksums_are_valid(self):
    with tempfile.TemporaryDirectory() as folder:
      data=Path(folder)/'data';source=Path(folder)/'source'
      base=[self.packet(data,'base.npz',1000,'train',1),self.packet(data,'validation.npz',8000,'validation',2)]
      write_json(data/'manifest.json',{'samples':base});before=(data/'manifest.json').read_bytes()
      manifest=self.source(source,[self.packet(source,'draft.npz',1001,'train',3)])
      write_json(source/'not-for-training.json',{'reason':'future permission was not observed'})
      with self.assertRaisesRegex(ValueError,'quarantined'):append_replay(data,manifest)
      self.assertEqual((data/'manifest.json').read_bytes(),before)

  def packet(self,root,name,seed,split,color):
    frames=np.full((10,1,3,2,2),color,np.uint8)
    path=root/name;root.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(path,image_frames=frames,future_xyz=np.zeros((1,64,3),np.float32),
      future_rot=np.broadcast_to(np.eye(3,dtype=np.float32),(1,64,3,3)))
    return {'file':name,'seed':seed,'split':split,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'pixel_sha256':hashlib.sha256(frames.tobytes()).hexdigest()}

  def source(self,root,rows):
    write_json(root/'manifest.json',{'samples':rows,'data_source':'simulation_on_policy',
      'reference_controls_used_only_for_supervision':True,'ground_truth_given_to_inference':False})
    return root/'manifest.json'

  def test_replay_adds_verified_packets_once_without_changing_the_frozen_source(self):
    with tempfile.TemporaryDirectory() as folder:
      data=Path(folder)/'data';source=Path(folder)/'source'
      base=[self.packet(data,'base.npz',1000,'train',1),self.packet(data,'validation.npz',8000,'validation',2)]
      write_json(data/'manifest.json',{'samples':base})
      rows=[self.packet(source,'corrected.npz',1001,'train',3)]
      manifest=self.source(source,rows);original=manifest.read_bytes()
      self.assertEqual(append_replay(data,manifest),1)
      merged=(data/'manifest.json').read_bytes()
      self.assertEqual(len(read_json(data/'manifest.json')['samples']),3)
      self.assertEqual(append_replay(data,manifest),0)
      self.assertEqual((data/'manifest.json').read_bytes(),merged)
      self.assertEqual(manifest.read_bytes(),original)

  def test_replay_rejects_duplicate_validation_images_before_modifying_the_dataset(self):
    with tempfile.TemporaryDirectory() as folder:
      data=Path(folder)/'data';source=Path(folder)/'source'
      base=[self.packet(data,'base.npz',1000,'train',1),self.packet(data,'validation.npz',8000,'validation',2)]
      write_json(data/'manifest.json',{'samples':base});original=(data/'manifest.json').read_bytes()
      rows=[self.packet(source,'duplicate.npz',1001,'train',2)]
      with self.assertRaises(ValueError): append_replay(data,self.source(source,rows))
      self.assertEqual((data/'manifest.json').read_bytes(),original)


if __name__=='__main__': unittest.main()
