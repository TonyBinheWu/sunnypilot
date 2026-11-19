import importlib.util
import unittest
import numpy as np
from tools.training_studio.teacher_optim import paired_indices


class PairCoverageTest(unittest.TestCase):
  def test_every_training_reference_is_used_with_one_stop_and_one_go_per_step(self):
    items=[{'row':{'stop_required':value}} for value in (True,True,True,False,False)]
    pairs=paired_indices(items,3)
    self.assertEqual(pairs,paired_indices(items,3));self.assertEqual(len(pairs),3)
    self.assertEqual({index for pair in pairs for index in pair},set(range(5)))
    for stop,go in pairs:self.assertTrue(items[stop]['row']['stop_required']);self.assertFalse(items[go]['row']['stop_required'])
    with self.assertRaises(ValueError):paired_indices(items[:3],0)


@unittest.skipUnless(importlib.util.find_spec('torch'),'pinned training image supplies torch')
class ProjectedPairTest(unittest.TestCase):
  def test_unit_task_balancing_preserves_descent_and_is_invariant_to_task_scale(self):
    import torch
    from tools.training_studio.teacher_optim import project_pair
    stop=torch.tensor([100.,0.]);go=torch.tensor([-1.,2.])
    joint,cosine,conflict=project_pair(stop,go,unit_gradients=True)
    scaled,_,_=project_pair(stop*1000,go*.01,unit_gradients=True)
    torch.testing.assert_close(joint,scaled)
    self.assertTrue(conflict);self.assertLess(cosine,0)
    self.assertGreater(float(torch.dot(joint,stop)),0.);self.assertGreater(float(torch.dot(joint,go)),0.)
    zero,_,_=project_pair(torch.zeros(2),go,unit_gradients=True)
    torch.testing.assert_close(zero,go/go.norm()/2)

  def test_conflicting_projection_descends_both_tasks_and_preserves_original_gradients(self):
    import torch
    from tools.training_studio.teacher_optim import project_pair
    stop=torch.tensor([1.,0.]);go=torch.tensor([-1.,1.]);a=stop.clone();b=go.clone()
    joint,cosine,conflict=project_pair(stop,go)
    self.assertTrue(conflict);self.assertLess(cosine,0)
    self.assertGreater(float(torch.dot(joint,stop)),0.);self.assertGreater(float(torch.dot(joint,go)),0.)
    torch.testing.assert_close(stop,a);torch.testing.assert_close(go,b)
    aligned=torch.tensor([2.,1.]);same,_,conflict=project_pair(stop,aligned)
    self.assertFalse(conflict);torch.testing.assert_close(same,(stop+aligned)/2)
    zero,cosine,conflict=project_pair(torch.zeros(2),go);self.assertIsNone(cosine);self.assertFalse(conflict);torch.testing.assert_close(zero,go/2)
    with self.assertRaises(ValueError):project_pair(torch.zeros(3),go)
    with self.assertRaises(ValueError):project_pair(torch.tensor([float('nan'),0.]),go)

  def test_actual_sgd_pair_improves_stop_and_proceed_without_changing_frozen_base(self):
    import torch
    from tools.training_studio.teacher_optim import paired_step
    parameter=torch.nn.Parameter(torch.tensor([.2,0.]));base=torch.tensor(7.);before_base=base.clone()
    optimizer=torch.optim.SGD([parameter],lr=.05)
    stop={'row':{'stop_required':True},'x':torch.tensor([1.,0.]),'target':0.}
    go={'row':{'stop_required':False},'x':torch.tensor([1.,1.]),'target':1.}
    def objective(item,grad):return ((parameter*item['x']).sum()-item['target']).square()
    before=[float(objective(item,False).detach()) for item in (stop,go)]
    result=paired_step({'expert':parameter},optimizer,objective,stop,go)
    self.assertTrue(result['gradient_projected']);self.assertGreater(result['parameter_delta_norm'],0.)
    self.assertLess(result['stop_loss'],before[0]);self.assertLess(result['go_loss'],before[1])
    torch.testing.assert_close(base,before_base)

  def test_guard_rolls_back_update_that_cannot_preserve_both_examples(self):
    import torch
    from tools.training_studio.teacher_optim import paired_step
    parameter=torch.nn.Parameter(torch.tensor([.2,0.]));before=parameter.detach().clone()
    optimizer=torch.optim.SGD([parameter],lr=1000.)
    stop={'row':{'stop_required':True},'x':torch.tensor([1.,0.]),'target':0.}
    go={'row':{'stop_required':False},'x':torch.tensor([1.,1.]),'target':1.}
    def objective(item,grad):return ((parameter*item['x']).sum()-item['target']).square()
    result=paired_step({'expert':parameter},optimizer,objective,stop,go,max_backtracks=2)
    self.assertEqual(result['step_scale'],0.);self.assertEqual(result['parameter_delta_norm'],0.)
    torch.testing.assert_close(parameter,before)


if __name__=='__main__':unittest.main()
