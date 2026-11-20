import copy
import unittest
from tools.training_studio.teacher_quality import checkpoint_quality


class CheckpointQualityTest(unittest.TestCase):
  def baseline(self):
    return {'validation_loss':10.,'red_safe_count':2,'red_samples':3,'red_hold_speed_mse':.2,'lateral_trajectory_mse':5.,'go_velocity_mse':2.,'go_samples':3}

  def test_full_mean_improvement_cannot_hide_fixed_guard_regression(self):
    baseline=self.baseline();baseline['validation_guard']=self.baseline()
    candidate=copy.deepcopy(baseline);candidate['validation_loss']=9.;candidate['lateral_trajectory_mse']=4.
    candidate['validation_guard']['lateral_trajectory_mse']=5.001
    decision=checkpoint_quality(candidate,baseline,self.baseline())
    self.assertFalse(decision['passed']);self.assertTrue(all(decision['conditions']['full'].values()))
    self.assertFalse(decision['conditions']['validation_guard']['lateral_trajectory_mse'])

  def test_one_checkpoint_must_satisfy_every_comparison_without_missing_or_changed_samples(self):
    baseline=self.baseline();baseline['validation_guard']=self.baseline()
    candidate=copy.deepcopy(baseline)
    self.assertTrue(checkpoint_quality(candidate,baseline,self.baseline())['passed'])
    for field,value in (('validation_guard',None),('go_samples',4),('red_samples',2),('validation_loss',float('nan'))):
      broken=copy.deepcopy(candidate);broken[field]=value
      self.assertFalse(checkpoint_quality(broken,baseline,self.baseline())['passed'])
    stricter=self.baseline();stricter['red_safe_count']=3
    self.assertFalse(checkpoint_quality(candidate,baseline,stricter)['passed'])

  def test_new_validation_samples_do_not_relax_immutable_original_subset(self):
    baseline=self.baseline();baseline['parent_validation']=self.baseline();baseline['parent_validation_reference']=self.baseline()
    candidate=copy.deepcopy(baseline);candidate['validation_loss']=8.
    self.assertTrue(checkpoint_quality(candidate,baseline)['passed'])
    candidate['parent_validation']['red_safe_count']=1
    self.assertFalse(checkpoint_quality(candidate,baseline)['passed'])
    candidate=copy.deepcopy(baseline);del candidate['parent_validation']
    self.assertFalse(checkpoint_quality(candidate,baseline)['passed'])
    baseline['parent_validation']['lateral_trajectory_mse']=6.
    candidate=copy.deepcopy(baseline)
    self.assertFalse(checkpoint_quality(candidate,baseline)['passed'])

  def test_all_five_metrics_are_required(self):
    baseline=self.baseline()
    for name in ('validation_loss','red_hold_speed_mse','lateral_trajectory_mse','go_velocity_mse'):
      broken=copy.deepcopy(baseline);broken[name]+=.0001
      self.assertFalse(checkpoint_quality(broken,baseline)['passed'])
    broken=copy.deepcopy(baseline);broken['red_safe_count']=1
    self.assertFalse(checkpoint_quality(broken,baseline)['passed'])


if __name__=='__main__':unittest.main()
