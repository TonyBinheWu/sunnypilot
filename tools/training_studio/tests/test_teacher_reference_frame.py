import unittest
import importlib.util
if importlib.util.find_spec('torch'):import torch
from tools.training_studio.teacher_reference_frame import install,shift,validate_offset,PROFILE


class ReferencePackageTest(unittest.TestCase):
  def test_remote_snapshot_contains_the_decoder_calibration_dependency(self):
    import io,tarfile
    from tools.training_studio.remote import Remote
    remote=object.__new__(Remote);remote.root='/owned-studio';captured=[]
    remote.call=lambda command,**kwargs:captured.append(kwargs['input'])
    program=remote.program(snapshot=True)
    with tarfile.open(fileobj=io.BytesIO(captured[0]),mode='r:gz') as archive:
      body=archive.extractfile('tools/training_studio/teacher_reference_frame.py').read()
      self.assertIn(PROFILE.encode(),body)
    self.assertTrue(program.startswith('/owned-studio/program-'))


def rotation(angle):
  c,s=angle.cos(),angle.sin();zero=torch.zeros_like(c);one=torch.ones_like(c)
  return torch.stack((c,-s,zero,s,c,zero,zero,zero,one),-1).reshape(*angle.shape,3,3)


@unittest.skipUnless(importlib.util.find_spec('torch'),'pinned training image supplies torch')
class ReferenceFrameTest(unittest.TestCase):
  def test_rigid_reference_round_trip_for_both_turns_without_mutation(self):
    for sign in (-1,1):
      rot=rotation(torch.linspace(0,sign*1.5,64).reshape(1,64))
      xyz=torch.arange(192,dtype=torch.float32).reshape(1,64,3)/10;before=xyz.clone();axis=torch.tensor([[[1.,0.,0.]]])
      axle=shift(xyz,rot,axis,-1.4166)
      torch.testing.assert_close(shift(axle,rot,axis,1.4166),xyz)
      self.assertTrue(torch.equal(xyz,before))
      self.assertFalse(torch.equal(axle,xyz))

  def test_straight_reference_is_bitwise_unchanged(self):
    xyz=torch.randn(2,20,3);rot=torch.eye(3).expand(2,20,3,3);axis=rot[:,-1,:,0].unsqueeze(-2)
    self.assertTrue(torch.equal(shift(xyz,rot,axis,-1.4166),xyz))

  def test_offset_is_validated_and_disabled_profile_does_not_wrap(self):
    for value in (True,-1.,3.1,float('nan'),float('inf'),'1.4'):
      with self.assertRaises(ValueError):validate_offset(value)
    class Space:pass
    space=Space();install(space,0.)
    self.assertFalse(hasattr(space,'_studio_reference_profile'))

  def test_inverse_and_decode_use_one_axle_conversion_and_return_center(self):
    class Space:
      def estimate_t0_states(self,h,r):self.observed=h.clone();return {'v':h.sum()}
      def traj_to_action(self,h,r,x,fr):self.inverse_inputs=(h.clone(),x.clone());return x
      def action_to_traj(self,a,h,r,t0_states=None):self.decoded_history=h.clone();self.states=t0_states;return a,self.future_rot
    space=Space();install(space,1.4166);decode=space.action_to_traj;install(space,1.4166)
    self.assertIs(space.action_to_traj,decode)
    with self.assertRaises(ValueError):install(space,1.)
    h=torch.randn(1,20,3);hr=rotation(torch.linspace(-.4,0,20)[None]);x=torch.randn(1,64,3);fr=rotation(torch.linspace(0,.9,64)[None]);space.future_rot=fr
    h_copy=h.clone();x_copy=x.clone();axle_future=space.traj_to_action(h,hr,x,fr)
    result,rr=space.action_to_traj(axle_future,h,hr,t0_states={'v':torch.tensor(123.)})
    torch.testing.assert_close(result,x);self.assertTrue(torch.equal(rr,fr))
    self.assertTrue(torch.equal(space.decoded_history,space.inverse_inputs[0]))
    self.assertTrue(torch.equal(space.observed,space.inverse_inputs[0]))
    self.assertTrue(torch.equal(h,h_copy));self.assertTrue(torch.equal(x,x_copy))
    self.assertEqual(space._studio_reference_profile,PROFILE)

  def test_reference_conversion_keeps_heading_gradients(self):
    angle=torch.tensor([[.3]],requires_grad=True);rot=rotation(angle);xyz=torch.zeros(1,1,3,requires_grad=True)
    shift(xyz,rot,torch.tensor([[[1.,0.,0.]]]),1.4166)[...,1].sum().backward()
    self.assertGreater(abs(float(angle.grad)),1.)
    self.assertEqual(float(xyz.grad[...,1]),1.)

  def test_bad_dimensions_are_rejected(self):
    with self.assertRaises(ValueError):shift(torch.zeros(1,3),torch.zeros(1,2,2),torch.zeros(1,3),1.)


if __name__=='__main__':unittest.main()
