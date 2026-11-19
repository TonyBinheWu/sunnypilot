import importlib.util
import unittest
from tools.training_studio.teacher_standstill import gentle_recovery_acceleration,stop_training_margin,RECOVERY_PROFILE,RECOVERY_INTERIOR_MARGIN_M

class GentleRecoveryTest(unittest.TestCase):
  def row(self):return {'stop_required':True,'maintain_stop_reference':False,'scenario':'red_light','front_distance_m':5.236,'recovery_reference_profile':RECOVERY_PROFILE,'stop_interior_margin_m':RECOVERY_INTERIOR_MARGIN_M}

  def test_recovery_uses_a_small_launch_and_brakes_as_it_reaches_the_target(self):
    self.assertEqual(gentle_recovery_acceleration([0,0],[1,0],5.001),.15)
    self.assertEqual(gentle_recovery_acceleration([0,0],[1,0],4.8),0.)
    self.assertLess(gentle_recovery_acceleration([.25,0],[1,0],5.2),0.)
    self.assertLess(gentle_recovery_acceleration([.2,0],[1,0],4.81),0.)
    self.assertEqual(gentle_recovery_acceleration([-.04,0],[1,0],5.2),.15)
    self.assertEqual(gentle_recovery_acceleration([0,-.04],[0,1],5.2),.15)
    for velocity,distance in [([float('nan'),0],5.2),([0,0],float('inf'))]:
      with self.assertRaises(ValueError):gentle_recovery_acceleration(velocity,[1,0],distance)

  def test_new_margin_is_bound_to_a_verified_recovery_profile_and_legacy_rows_keep_their_margin(self):
    self.assertEqual(stop_training_margin(self.row(),True),.15)
    self.assertEqual(stop_training_margin({'maintain_stop_reference':True},True),0.)
    self.assertEqual(stop_training_margin({},True),.5);self.assertEqual(stop_training_margin({},False),0.)
    for change in ({'recovery_reference_profile':'unknown'},{'front_distance_m':4.99},{'front_distance_m':6.01},{'maintain_stop_reference':True},{'stop_required':False},{'scenario':'lane_center'},{'stop_interior_margin_m':0.}):
      with self.subTest(change=change),self.assertRaises(ValueError):stop_training_margin({**self.row(),**change},True)

  @unittest.skipUnless(importlib.util.find_spec('torch'),'pinned training image supplies torch')
  def test_matching_the_audited_recovery_future_has_no_contradictory_interior_penalty(self):
    import torch
    from tools.training_studio.teacher_train import stop_zone_loss,valid_stopped_trajectory
    target=torch.zeros(1,64,3);target[...,0]=.436;held=torch.ones(1,64);front=5.236
    self.assertEqual(float(stop_zone_loss(target,target,held,front,interior_margin_m=stop_training_margin(self.row(),True))),0.)
    self.assertGreater(float(stop_zone_loss(target,target,held,front,interior_margin_m=.5)),0.)
    self.assertTrue(bool(valid_stopped_trajectory(target,torch.zeros_like(target),front)))
    at_boundary=torch.zeros_like(target)
    self.assertFalse(bool(valid_stopped_trajectory(at_boundary,torch.zeros_like(target),5.)))
    speed=torch.zeros_like(target);speed[...,0]=.15
    self.assertFalse(bool(valid_stopped_trajectory(target,speed,front)))

if __name__=='__main__':unittest.main()
