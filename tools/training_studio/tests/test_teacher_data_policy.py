import unittest
import tempfile
from pathlib import Path
from tools.training_studio.teacher_data import training_seeds
from tools.training_studio.teacher_train import observed_inputs
from tools.training_studio.teacher_adapt import closed_loop_score,restore_parent_ranking,remember_tested_scenarios
from tools.training_studio.store import write_json
from tools.training_studio.teacher_policy_data import check_source
from tools.training_studio.edge_inputs import MODEL_REVISION
import hashlib
import json


class TeacherDataPolicyTest(unittest.TestCase):
  def test_rehearsal_keeps_passed_scene_types_without_held_out_samples(self):
    state={'rehearsal':['red_light']}
    remember_tested_scenarios(state,[{'scenario':'lane_center','seed':303,'status':'pass'},
      {'scenario':'pedestrian','seed':303,'status':'fail','input':'held-out-packet'}])
    self.assertEqual(state,{'rehearsal':['lane_center','pedestrian','red_light']})

  def test_on_policy_labels_require_observed_source_identity_and_separate_seeds(self):
    provenance={'revision':MODEL_REVISION,'camera_ids':[1,6],'weights_verified':True,'adapter_sha256':'a'*64}
    fingerprint=hashlib.sha256(json.dumps(provenance,sort_keys=True).encode()).hexdigest()
    result={'seed':1027,'scenario':'red_light','backend':'nvidia_alpamayo2_edge','revision':MODEL_REVISION,'scripted_fallback':False,
      'model_inputs_include_signal_ground_truth':False,'model_provenance_sha256':fingerprint,
      'status':'fail','failures':['red_hold_not_maintained']}
    self.assertEqual(check_source(result,{'provenance':provenance},'train'),fingerprint)
    self.assertEqual(check_source({**result,'scenario':'pedestrian'},{'provenance':provenance},'train'),fingerprint)
    for changed,split in (({**result,'seed':300},'train'),(result,'validation'),
      ({**result,'model_inputs_include_signal_ground_truth':True},'train'),({**result,'model_provenance_sha256':'b'*64},'train'),
      ({**result,'scenario':'yield_left'},'train')):
      with self.assertRaises(ValueError): check_source(changed,{'provenance':provenance},split)

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

  def test_training_parent_preserves_fixed_lane_tracking_before_longer_but_failed_hold(self):
    with tempfile.TemporaryDirectory() as directory:
      root=Path(directory)
      write_json(root/'centered'/'red'/'result.json',{'scenario':'red_light','status':'fail',
        'failures':['red_hold_not_maintained'],'max_center_error_m':.17,
        'red_wait_audit':{'longest_contiguous_red_stop_s':1.8}})
      write_json(root/'drifting'/'red'/'result.json',{'scenario':'red_light','status':'fail',
        'failures':['lane_envelope','red_hold_not_maintained'],'max_center_error_m':1.14,
        'red_wait_audit':{'longest_contiguous_red_stop_s':2.3}})
      self.assertGreater(closed_loop_score(root/'centered'),closed_loop_score(root/'drifting'))

  def test_training_parent_does_not_reward_risk_absent_only_because_later_cases_were_untested(self):
    with tempfile.TemporaryDirectory() as directory:
      root=Path(directory)
      write_json(root/'advanced'/'red'/'result.json',{'scenario':'red_light','status':'pass','failures':[]})
      write_json(root/'advanced'/'pedestrian'/'result.json',{'scenario':'pedestrian','status':'fail','failures':['crossed_before_permission']})
      write_json(root/'early'/'red'/'result.json',{'scenario':'red_light','status':'fail','failures':['red_hold_not_maintained']})
      self.assertGreater(closed_loop_score(root/'advanced'),closed_loop_score(root/'early'))

  def test_parent_keeps_actual_release_progress_before_excess_hold_duration(self):
    from types import SimpleNamespace
    with tempfile.TemporaryDirectory() as directory:
      root=Path(directory)
      for cycle,hold,failures in ((9,12.,['crossed_before_permission']),
        (11,9.,['crossed_before_permission','insufficient_progress']),
        (13,5.,['crossed_before_permission'])):
        batch=root/'teacher-cycles'/f'cycle-{cycle:03d}'/'qualification-balanced'
        adapter={'path':f'/studio/teacher/cycle-{cycle:03d}/output/balanced.safetensors','sha256':str(cycle)*32,
          'cycle':cycle,'training_epoch':6}
        provenance={'action_expert_adapter':adapter}
        fingerprint=hashlib.sha256(json.dumps(provenance,sort_keys=True).encode()).hexdigest()
        rows=[{'scenario':'red_light','status':'pass','failures':[],
          'red_wait_audit':{'longest_contiguous_red_stop_s':hold},'model_provenance_sha256':fingerprint},
          {'scenario':'pedestrian','status':'fail','failures':failures,'model_provenance_sha256':fingerprint}]
        for name,row in zip(('red','pedestrian'),rows):write_json(batch/name/'result.json',row)
        write_json(batch/'red'/'provenance.json',{'provenance':provenance})
        write_json(batch/'qualification.json',{'passed':False,'results':rows})
      state={'ranking_version':4}
      restore_parent_ranking(SimpleNamespace(root=root),state)
      self.assertEqual(state['ranking_version'],5)
      self.assertIn('cycle-013',state['parent']['path'])
      self.assertNotIn('qualified_sha256',state)


if __name__=='__main__': unittest.main()
