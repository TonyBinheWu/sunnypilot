from types import SimpleNamespace
import importlib.util
import unittest

HAS_TORCH=importlib.util.find_spec('torch') is not None
if HAS_TORCH:import torch

from tools.training_studio.teacher_forward_motion import install,project_actions
from tools.training_studio.teacher_train import acceleration_error,held_brake_margin_loss,immediate_command_loss


@unittest.skipUnless(HAS_TORCH,'GPU training environment supplies torch')
class ForwardMotionTest(unittest.TestCase):
  def setUp(self):
    self.history=torch.zeros(1,20,3)
    self.rot=torch.eye(3).repeat(1,20,1,1)
    self.space=SimpleNamespace(dt=.1,accel_std=torch.tensor(2.),accel_mean=torch.tensor(.3))
    self.space.estimate_t0_states=lambda xyz,rot:{'v':(xyz[:,-1,0]-xyz[:,-2,0])/.1}

  def actions(self,acceleration):
    result=torch.zeros(1,len(acceleration),2)
    result[...,0]=(torch.tensor(acceleration)-self.space.accel_mean)/self.space.accel_std
    return result

  def velocities(self,action,initial=0.):
    return initial+torch.cumsum((action[...,0]*self.space.accel_std+self.space.accel_mean)*.1,-1)

  def test_braking_at_rest_cannot_become_a_reverse_future_or_consume_the_original_commands(self):
    action=self.actions([-.5]*64);original=action.clone()
    self.assertLess(float(self.velocities(action).min()),-3.)
    effective,_=project_actions(action,self.space,self.history,self.rot)
    torch.testing.assert_close(self.velocities(effective),torch.zeros(1,64),atol=1e-6,rtol=0)
    torch.testing.assert_close(action,original,atol=0,rtol=0)

  def test_stop_then_restart_has_no_accumulated_negative_velocity_debt(self):
    action=self.actions([-1.]*20+[1.]*10)
    effective,_=project_actions(action,self.space,self.history,self.rot)
    velocity=self.velocities(effective)
    self.assertAlmostEqual(float(velocity[0,19]),0.,places=6)
    self.assertAlmostEqual(float(velocity[0,20]),.1,places=6)
    self.assertAlmostEqual(float(velocity[0,-1]),1.,places=6)

  def test_moving_trajectory_and_curvature_are_bitwise_preserved_until_a_stop(self):
    self.history[0,-2,0]=-.4
    action=self.actions([-.2]*64);action[...,1]=torch.linspace(-.2,.2,64)
    effective,states=project_actions(action,self.space,self.history,self.rot)
    torch.testing.assert_close(effective,action,atol=0,rtol=0)
    self.assertEqual(float(states['v']),4.)

  def test_braking_to_rest_never_reverses_and_does_not_remove_steering(self):
    self.history[0,-2,0]=-.02
    action=self.actions([-1.]*10);action[...,1]=.15
    effective,_=project_actions(action,self.space,self.history,self.rot)
    velocity=self.velocities(effective,.2)
    self.assertGreaterEqual(float(velocity.min()),-1e-6)
    self.assertAlmostEqual(float(velocity[0,-1]),0.,places=6)
    torch.testing.assert_close(effective[...,1],action[...,1],atol=0,rtol=0)

  def test_forward_profile_handles_settling_rollback_without_mutating_observations_or_supplied_states(self):
    self.history[0,-2,0]=.01
    history=self.history.clone();states={'v':torch.tensor([-.005]),'heading':torch.tensor([.3])}
    effective,resolved=project_actions(self.actions([-.3]*64),self.space,self.history,self.rot,t0_states=states)
    self.assertAlmostEqual(float(resolved['v']),.1,places=6)
    self.assertAlmostEqual(float(states['v']),-.005,places=6)
    torch.testing.assert_close(self.history,history,atol=0,rtol=0)
    self.assertIs(resolved['heading'],states['heading'])
    self.assertGreaterEqual(float(self.velocities(effective,.1).min()),-1e-6)
    self.space.action_to_traj=lambda *args,**kwargs:None
    install(self.space)
    self.assertAlmostEqual(float(self.space.estimate_t0_states(self.history,self.rot)['v']),.1,places=6)

  def test_nonfinite_observed_speed_still_rejects_the_request(self):
    with self.assertRaisesRegex(ValueError,'nonfinite observed initial speed'):
      project_actions(self.actions([0.]*64),self.space,self.history,self.rot,t0_states={'v':torch.tensor([float('nan')])})

  def test_executed_peak_margin_never_releases_an_already_applied_brake(self):
    for acceleration in (-.1,-.2,-.4,-1.):
      action=self.actions([acceleration]*64).requires_grad_()
      loss=held_brake_margin_loss(action,self.space,executed_peak=True);loss.backward()
      self.assertTrue(bool((action.grad[...,0]>=0).all()))
      self.assertEqual(float(action.grad[...,1].abs().sum()),0.)
      if acceleration<=-.4:self.assertEqual(float(loss.detach()),0.)
      else:self.assertGreater(float(loss.detach()),0.)

  def test_completed_hold_does_not_train_to_release_an_adequate_brake(self):
    target=self.actions([0.]*64)
    for acceleration in (-.1,-.3,-1.):
      action=self.actions([acceleration]*64).requires_grad_()
      error=acceleration_error(action,target,self.space,completed_hold=True,forward_only=True)
      loss=immediate_command_loss(error)+held_brake_margin_loss(action,self.space)
      self.assertLess(float(loss.detach()),1e-10)
      loss.backward();self.assertLess(float(action.grad.abs().max()),1e-5)
    action=self.actions([.1]*64).requires_grad_()
    error=acceleration_error(action,target,self.space,completed_hold=True,forward_only=True)
    immediate_command_loss(error).backward()
    self.assertTrue(bool((action.grad[:,:20,0]>0).all()))
    self.assertEqual(float(action.grad[...,1].abs().sum()),0.)
    for held,forward in ((False,True),(True,False),(False,False)):
      torch.testing.assert_close(acceleration_error(action,target,self.space,completed_hold=held,forward_only=forward),torch.full((1,64),.1),atol=1e-6,rtol=0)

  def test_install_is_idempotent_and_uses_the_original_course_decoder(self):
    calls=[]
    def decoder(action,xyz,rot,t0_states=None):
      calls.append((action.clone(),t0_states));return 'original-course','original-body-rotation'
    self.space.action_to_traj=decoder
    install(self.space);first=self.space.action_to_traj;install(self.space)
    self.assertIs(first,self.space.action_to_traj)
    self.assertEqual(first(self.actions([-.3]*64),self.history,self.rot),('original-course','original-body-rotation'))
    self.assertEqual(len(calls),1)
    torch.testing.assert_close(self.velocities(calls[0][0]),torch.zeros(1,64),atol=1e-6,rtol=0)


if __name__=='__main__':unittest.main()
