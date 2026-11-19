from types import SimpleNamespace
import importlib.util
import unittest

from tools.training_studio.teacher_standstill import hold_acceleration,in_stop_zone


class ReferenceStandstillTest(unittest.TestCase):
  def test_feedback_opposes_forward_motion_and_rollback(self):
    self.assertAlmostEqual(hold_acceleration([.04,0],[1,0]),-.06)
    self.assertAlmostEqual(hold_acceleration([-.04,0],[1,0]),.06)
    self.assertAlmostEqual(hold_acceleration([0,-.04],[0,1]),.06)
    self.assertEqual(hold_acceleration([0,0],[1,0]),0.)
    self.assertEqual(hold_acceleration([10,0],[1,0]),-3.5)
    self.assertEqual(hold_acceleration([-10,0],[1,0]),1.6)
    with self.assertRaises(ValueError):hold_acceleration([float('nan'),0],[1,0])

  def test_reference_zone_matches_original_strict_boundary_without_using_a_latched_past_stop(self):
    scene=SimpleNamespace(stop_s=35.,vehicle=SimpleNamespace(LENGTH=4.),stopped=True)
    for distance,speed,valid in ((5.,0.,False),(4.999,0.,True),(0.,0.,True),(-.001,0.,False),(2.,.15,False),(2.,.149,True)):
      scene.state=lambda:(None,0,0,33.-distance,speed)
      self.assertEqual(in_stop_zone(scene),valid)


@unittest.skipUnless(importlib.util.find_spec('torch'),'GPU training environment supplies torch')
class SignedCommandTest(unittest.TestCase):
  def test_near_rest_observer_does_not_erase_real_forward_or_reverse_motion(self):
    import torch
    from tools.training_studio.teacher_motion import install
    for speed in (-.2,-.04,0.,.04,.2):
      space=SimpleNamespace(dt=.1,estimate_t0_states=lambda xyz,rot:{'v':torch.tensor([speed]),'theta':torch.tensor([.02])})
      install(space);history=torch.zeros(1,20,3);history[0,:,0]=torch.arange(-19,1)*speed*.1
      actual=space.estimate_t0_states(history,None)
      self.assertAlmostEqual(float(actual['v']),0. if abs(speed)<=.05 else speed,places=6)
      self.assertAlmostEqual(float(actual['theta']),.02,places=6)

  def test_a_single_slow_chord_during_braking_is_not_a_stationary_window(self):
    import torch
    from tools.training_studio.teacher_motion import install
    space=SimpleNamespace(dt=.1,estimate_t0_states=lambda xyz,rot:{'v':torch.tensor([.2])})
    install(space);history=torch.zeros(1,20,3);history[0,-3,0]=-.03;history[0,-2,0]=-.001
    self.assertAlmostEqual(float(space.estimate_t0_states(history,None)['v']),.2,places=6)

  def test_hold_loss_uses_the_same_initial_state_as_the_pinned_decoder(self):
    import torch
    from tools.training_studio.teacher_train import signed_held_command_loss
    space=SimpleNamespace(dt=.1,accel_std=torch.tensor(1.),accel_mean=torch.tensor(0.),estimate_t0_states=lambda xyz,rot:{'v':torch.zeros(1)})
    history=torch.zeros(1,20,3);history[0,-2,0]=.004
    self.assertEqual(float(signed_held_command_loss(torch.zeros(1,64,2),space,history,torch.eye(3))),0.)

  def test_signed_hold_gradient_arrests_reverse_and_forward_motion_symmetrically(self):
    import torch
    from tools.training_studio.teacher_train import signed_held_command_loss
    space=SimpleNamespace(dt=.1,accel_std=torch.tensor(1.),accel_mean=torch.tensor(0.))
    for speed in (-.04,.04):
      history=torch.zeros(1,20,3);history[0,-2,0]=-speed*.1
      action=torch.zeros(1,64,2,requires_grad=True)
      loss=signed_held_command_loss(action,space,history);loss.backward()
      self.assertGreater(float(loss.detach()),0.)
      self.assertTrue(bool((action.grad[:,:20,0]*speed>0).all()))
      self.assertEqual(float(action.grad[...,1].abs().sum()),0.)
      self.assertEqual(float(action.grad[:,20:].abs().sum()),0.)

  def test_at_rest_a_negative_acceleration_is_reverse_motion_not_a_free_brake_margin(self):
    import torch
    from tools.training_studio.teacher_train import signed_held_command_loss,held_command_loss
    space=SimpleNamespace(dt=.1,accel_std=torch.tensor(1.),accel_mean=torch.tensor(0.));history=torch.zeros(1,20,3)
    action=torch.zeros(1,64,2)
    self.assertEqual(float(signed_held_command_loss(action,space,history)),0.)
    action[...,0]=-.1
    self.assertEqual(float(held_command_loss(action,space,history)),0.)
    self.assertGreater(float(signed_held_command_loss(action,space,history)),0.)


if __name__=='__main__':unittest.main()
