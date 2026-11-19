import unittest
import numpy as np
from tools.training_studio.teacher_route_data import relative_future


class MeasuredRouteFutureTest(unittest.TestCase):
  def test_current_body_frame_and_first_future_time_are_preserved_through_turn(self):
    reference=np.array([[0,-1,0],[1,0,0],[0,0,1]],np.float32)
    positions=np.tile([10.,20.,0.],(70,1));positions[:,1]+=np.arange(70)*.1
    rotations=np.tile(reference,(70,1,1));times=np.arange(70,dtype=np.int64)*100000
    xyz,rot=relative_future(positions,rotations,times,3)
    np.testing.assert_allclose(xyz[0,:,0],np.arange(1,65)*.1,atol=1e-5)
    np.testing.assert_allclose(xyz[0,:,1:],0,atol=1e-5)
    np.testing.assert_allclose(rot,np.tile(np.eye(3),(1,64,1,1)),atol=1e-5)

  def test_incomplete_or_misaligned_future_is_rejected_instead_of_repeating_poses(self):
    positions=np.zeros((65,3));rotations=np.tile(np.eye(3),(65,1,1));times=np.arange(65)*100000
    with self.assertRaises(ValueError):relative_future(positions,rotations,times,1)
    times[20]+=100000
    with self.assertRaises(ValueError):relative_future(positions,rotations,times,0)


if __name__=='__main__':unittest.main()
