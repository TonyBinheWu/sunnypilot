import importlib.util
import unittest

HAS_TORCH=importlib.util.find_spec('torch') is not None
if HAS_TORCH:import torch


@unittest.skipUnless(HAS_TORCH,'pinned training environment supplies torch')
class CommonDescentTest(unittest.TestCase):
  def test_common_direction_protects_a_minority_hold_that_averaging_would_hurt(self):
    from tools.training_studio.teacher_optim import project_group
    gradients=[torch.tensor(v,dtype=torch.float32) for v in ([1,0,0],[-.9,.2,0],[-.9,.3,0],[-.9,.4,0],[0,1,.1],[0,1,-.1])]
    unit=torch.stack([g/g.norm() for g in gradients])
    self.assertLess(float((unit@unit.mean(0))[0]),0.)
    joint,weights,gain,conflict=project_group(gradients)
    self.assertTrue(conflict);self.assertGreater(gain,0.)
    self.assertTrue(bool((unit@joint>0).all()))
    self.assertAlmostEqual(sum(weights),1.,places=6)
    self.assertTrue(all(v>=0 for v in weights))
    scaled,_,_,_=project_group([g*scale for g,scale in zip(gradients,(.01,100,2,.5,10,.1))])
    torch.testing.assert_close(scaled,joint,atol=1e-6,rtol=1e-5)

  def test_nearly_opposed_tasks_remain_descent_after_unit_normalization(self):
    from tools.training_studio.teacher_optim import project_group
    torch.manual_seed(0);axis=torch.randn(256);axis=axis/axis.norm()
    gradients=[((-1.)**i)*axis+1e-5*torch.randn(256) for i in range(6)]
    joint,_,_,_=project_group(gradients);self.assertGreater(float(joint.norm()),1e-6)
    unit=torch.stack([g.double()/g.double().norm() for g in gradients])
    self.assertGreater(float((unit@(joint.double()/joint.double().norm())).min()),0.)

  def test_opposed_singular_and_zero_gradients_do_not_create_a_harmful_direction(self):
    from tools.training_studio.teacher_optim import project_group
    joint,_,gain,_=project_group([torch.tensor([1.,0.]),torch.tensor([-1.,0.]),torch.zeros(2)])
    torch.testing.assert_close(joint,torch.zeros(2),atol=1e-6,rtol=0)
    self.assertGreaterEqual(gain,-1e-6)
    joint,weights,_,_=project_group([torch.zeros(2)]*6)
    self.assertEqual(weights,[0.]*6);self.assertEqual(float(joint.norm()),0.)
    with self.assertRaises(ValueError):project_group([torch.tensor([float('nan')]),torch.ones(1)])
    with self.assertRaises(ValueError):project_group([torch.ones(2),torch.ones(3)])

  def test_actual_sgd_group_checks_all_six_losses_and_keeps_frozen_base(self):
    from tools.training_studio.teacher_optim import paired_step
    parameter=torch.nn.Parameter(torch.zeros(6));base=torch.tensor(7.);unchanged=base.clone()
    items=[{'row':{'stop_required':i%2==0},'axis':i} for i in range(6)]
    def objective(item,grad):return (parameter[item['axis']]-1).square()
    before=[float(objective(item,False).detach()) for item in items]
    reports=[]
    result=paired_step({'expert':parameter},torch.optim.SGD([parameter],lr=.1),objective,*items[:2],unit_gradients=True,extra_items=items[2:],progress=lambda **row:reports.append(row))
    after=[float(objective(item,False).detach()) for item in items]
    self.assertEqual(result['task_count'],6)
    self.assertTrue(all(a<b for a,b in zip(after,before)))
    self.assertGreater(result['parameter_delta_norm'],0.)
    self.assertEqual({row['group_task'] for row in reports if row['group_stage']=='gradient'},set(range(1,7)))
    self.assertEqual({row['group_task'] for row in reports if row['group_stage']=='verify'},set(range(1,7)))
    self.assertEqual(result['task_losses_before'],before)
    torch.testing.assert_close(base,unchanged)
    with self.assertRaises(ValueError):paired_step({'expert':parameter},torch.optim.SGD([parameter],lr=.1),objective,*items[:2],extra_items=items[2:])

  def test_separate_safety_tasks_prevent_composite_loss_from_buying_unsafe_motion(self):
    from tools.training_studio.teacher_optim import paired_step
    parameter=torch.nn.Parameter(torch.zeros(9))
    items=[{'row':{'stop_required':i%2==0},'axis':i} for i in range(6)]
    def composite(item,grad):
      k=item['axis'];loss=(parameter[k]-1).square()
      return loss+(-.2*parameter[6+k//2] if k%2==0 else 0)
    def safety(item,grad):return (parameter[6+item['axis']//2]+1).square()
    before=[float(safety(item,False).detach()) for item in items[::2]]
    result=paired_step({'expert':parameter},torch.optim.SGD([parameter],lr=.1),composite,*items[:2],unit_gradients=True,extra_items=items[2:],safety_objective=safety)
    after=[float(safety(item,False).detach()) for item in items[::2]]
    self.assertEqual(result['task_count'],9)
    self.assertEqual(len(result['task_losses_after']),9)
    self.assertTrue(all(a<b for a,b in zip(after,before)))
    self.assertTrue(all(a<=b for a,b in zip(result['task_losses_after'],result['task_losses_before'])))
    self.assertGreater(result['parameter_delta_norm'],0)

  def test_twelve_task_update_protects_steering_and_stopping_separately(self):
    from tools.training_studio.teacher_optim import paired_step
    parameter=torch.nn.Parameter(torch.zeros(12))
    items=[{'row':{'stop_required':i%2==0},'axis':i} for i in range(6)]
    def composite(item,grad):
      k=item['axis'];side=6+k//2 if k%2==0 else 9+k//2
      return (parameter[k]-1).square()-.2*parameter[side]
    def stop(item,grad):return (parameter[6+item['axis']//2]+1).square()
    def lateral(item,grad):return (parameter[9+item['axis']//2]+1).square()
    result=paired_step({'expert':parameter},torch.optim.SGD([parameter],lr=.1),composite,*items[:2],unit_gradients=True,extra_items=items[2:],safety_objective=stop,lateral_objective=lateral)
    self.assertEqual(result['task_count'],12)
    self.assertEqual(len(result['safety_losses_after']),3)
    self.assertEqual(len(result['lateral_losses_after']),3)
    self.assertTrue(all(a<b for a,b in zip(result['task_losses_after'],result['task_losses_before'])))
    self.assertGreater(result['parameter_delta_norm'],0)

  def test_zero_extra_constraints_do_not_change_reported_primary_loss(self):
    from tools.training_studio.teacher_optim import paired_step
    results=[];weights=[]
    items=[{'row':{'stop_required':i%2==0},'axis':i} for i in range(6)]
    for count in (6,9,12):
      p=torch.nn.Parameter(torch.zeros(6))
      def objective(item,grad):return (p[item['axis']]-1).square()
      def zero(item,grad):return p[0]*0
      result=paired_step({'expert':p},torch.optim.SGD([p],lr=.1),objective,*items[:2],unit_gradients=True,extra_items=items[2:],safety_objective=zero if count>=9 else None,lateral_objective=zero if count==12 else None)
      results.append(result);weights.append(p.detach().clone())
    for result,weight in zip(results[1:],weights[1:]):
      torch.testing.assert_close(weight,weights[0]);self.assertAlmostEqual(result['loss'],results[0]['loss']);self.assertAlmostEqual(result['loss_before_step'],results[0]['loss_before_step'])

  def test_stop_safety_loss_separates_boundary_speed_and_overshoot(self):
    from tools.training_studio.teacher_train import stop_safety_loss
    xyz=torch.zeros(1,64,3);velocity=torch.zeros_like(xyz)
    self.assertEqual(float(stop_safety_loss(xyz,velocity,3.)),0.)
    self.assertGreater(float(stop_safety_loss(xyz,velocity,6.)),0.)
    xyz[...,0]=4.
    self.assertGreater(float(stop_safety_loss(xyz,velocity,3.)),0.)
    xyz.zero_();velocity[:,-1,0]=.2
    self.assertGreater(float(stop_safety_loss(xyz,velocity,3.)),0.)

  def test_completed_hold_near_both_legal_boundaries_never_gets_a_forward_or_reverse_target(self):
    from tools.training_studio.teacher_train import stop_safety_loss
    for front in (.01,4.7,4.95,4.9999):
      xyz=torch.zeros(1,64,3,requires_grad=True);velocity=torch.zeros_like(xyz)
      loss=stop_safety_loss(xyz,velocity,front,completed_hold=True)
      self.assertEqual(float(loss.detach()),0.)
      loss.backward();torch.testing.assert_close(xyz.grad,torch.zeros_like(xyz))
    xyz=torch.zeros(1,64,3);velocity=torch.zeros_like(xyz);velocity[:,-1,0]=.2
    self.assertGreater(float(stop_safety_loss(xyz,velocity,4.95,completed_hold=True)),0.)

  def test_realistic_grouped_sampling_covers_every_task_in_each_update(self):
    from tools.training_studio.teacher_optim import paired_groups,stop_mode
    from tools.training_studio.teacher_reasoning_train import maneuver_class
    items=[]
    for mode in ('hold','approach','recover'):
      items.extend({'row':{'stop_required':True,'scenario':'red_light','maintain_stop_reference':mode=='hold','front_distance_m':6.},'observed_speed_mps':0. if mode=='recover' else 3.} for _ in range(7))
    for scenario in ('left_turn','lane_center','right_turn'):
      items.extend({'row':{'stop_required':False,'scenario':scenario}} for _ in range(7))
    groups=paired_groups(items,2)
    self.assertEqual(len(groups),7)
    for group in groups:
      self.assertEqual({stop_mode(items[i]) for i in group[::2]},{'hold','approach','recover'})
      self.assertEqual({maneuver_class(items[i]['row']) for i in group[1::2]},{'left','right','straight'})
    self.assertEqual(set(i for group in groups for i in group),set(range(len(items))))
    self.assertEqual(paired_groups(items,2,correction_warmup=True),groups)
    correction=next(i for i,item in enumerate(items) if not item['row']['stop_required'] and item['row']['scenario']=='left_turn')
    items[correction]['row']={**items[correction]['row'],'turn_reference_speed_mps':2.}
    permitted=next(i for i,item in enumerate(items) if not item['row']['stop_required'] and item['row']['scenario']=='lane_center')
    items[permitted]['row']={**items[permitted]['row'],'correction_priority':True}
    warm=paired_groups(items,2,correction_warmup=True)
    self.assertEqual(warm[1:],groups)
    self.assertIn(correction,warm[0][1::2])
    self.assertIn(permitted,warm[0][1::2])
    self.assertEqual({stop_mode(items[i]) for i in warm[0][::2]},{'hold','approach','recover'})
    self.assertEqual({maneuver_class(items[i]['row']) for i in warm[0][1::2]},{'left','right','straight'})
    self.assertEqual(warm,paired_groups(items,2,correction_warmup=True))


if __name__=='__main__':unittest.main()
