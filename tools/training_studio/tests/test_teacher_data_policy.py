import unittest
import tempfile
from pathlib import Path
from tools.training_studio.teacher_data import training_seeds
from tools.training_studio.teacher_train import observed_inputs
from tools.training_studio.teacher_adapt import closed_loop_score
from tools.training_studio.store import write_json


class TeacherDataPolicyTest(unittest.TestCase):
  def test_training_never_reuses_qualification_seeds_or_validation_seed_range(self):
    for cycle in range(1,10001):
      seeds=training_seeds(cycle)
      train={seed for seed,split in seeds if split=='train'}
      validation={seed for seed,split in seeds if split=='validation'}
      self.assertFalse(train & validation)
      self.assertFalse((train|validation)&{300,301,302,303})
      self.assertEqual(len(train),2)
      self.assertTrue(all(0<=seed<10000 for seed,_ in seeds))

  def test_future_labels_and_scorer_truth_never_enter_model_inputs(self):
    keys=('image_frames','camera_indices','absolute_timestamps','ego_history_timestamps','ego_history_xyz','ego_history_rot','nav_text')
    source={key:key for key in keys}
    source.update(future_xyz='labels',future_rot='labels',stop_required=True,front_distance_m=1.5,signal_green_at=19)
    self.assertEqual(observed_inputs(source),{key:key for key in keys})

  def test_training_parent_ranking_uses_real_failures_instead_of_offline_loss(self):
    with tempfile.TemporaryDirectory() as directory:
      root=Path(directory)
      write_json(root/'safe'/'red'/'result.json',{'scenario':'red_light','status':'fail','failures':['lane_envelope'],
        'max_center_error_m':1.,'red_wait_audit':{'longest_contiguous_red_stop_s':.4},'validation_loss':100})
      write_json(root/'unsafe'/'red'/'result.json',{'scenario':'red_light','status':'fail','failures':['collision'],
        'max_center_error_m':0.,'red_wait_audit':{'longest_contiguous_red_stop_s':10},'validation_loss':.001})
      self.assertGreater(closed_loop_score(root/'safe'),closed_loop_score(root/'unsafe'))
      self.assertLess(closed_loop_score(root/'empty'),closed_loop_score(root/'unsafe'))


if __name__=='__main__': unittest.main()
