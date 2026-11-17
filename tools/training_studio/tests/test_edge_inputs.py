import unittest
import numpy as np

from tools.training_studio.edge_inputs import validate_front_sample


def sample():
  now=2_000_000
  return {'image_frames':np.zeros((10,1,3,8,8),np.uint8),'camera_indices':np.repeat(np.array([1,6],np.int64),5),
    'absolute_timestamps':now+np.tile(np.array([-2_000_000,-1_000_000,-500_000,-100_000,0],np.int64),2),
    'ego_history_timestamps':now+np.arange(-19,1,dtype=np.int64)*100_000,
    'ego_history_xyz':np.zeros((1,1,20,3),np.float32),
    'ego_history_rot':np.tile(np.eye(3,dtype=np.float32),(1,1,20,1,1)),
    'nav_text':['Follow the current lane. Side and rear views are unavailable.']}


class InputContractTest(unittest.TestCase):
  def test_exact_observation_contract(self):
    validate_front_sample(sample())

  def test_real_capture_jitter_is_tolerated_without_fabricating_timestamps(self):
    data=sample()
    data['absolute_timestamps'][:5]+=5_000
    original=data['absolute_timestamps'].copy()
    with self.assertRaises(ValueError):
      validate_front_sample(data)
    validate_front_sample(data,timestamp_tolerance_us=35_000)
    np.testing.assert_array_equal(data['absolute_timestamps'],original)

  def test_missing_history_and_extra_camera_are_rejected(self):
    data=sample()
    data['absolute_timestamps'][3]+=100_000
    with self.assertRaises(ValueError):
      validate_front_sample(data,timestamp_tolerance_us=35_000)
    data=sample()
    data['camera_indices'][0]=0
    with self.assertRaises(ValueError):
      validate_front_sample(data)

  def test_ego_rotations_must_be_proper(self):
    data=sample()
    data['ego_history_rot'][0,0,0,0,0]=-1
    with self.assertRaises(ValueError):
      validate_front_sample(data)


if __name__=='__main__':
  unittest.main()
