import copy
import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest

from tools.training_studio.engine import TEACHER_REVISION
from tools.training_studio.server import initialize
from tools.training_studio.store import write_json
from tools.training_studio.teacher_control import check_health,qualified,training_ready,adaptation_progress
from tools.training_studio.qualify_teacher import qualify
from tools.training_studio.qualification import log_progress


class TeacherControlTest(unittest.TestCase):
  def setUp(self):
    self.health={'teacher_ready':True,'provenance':{'revision':TEACHER_REVISION,'weights_verified':True,'camera_ids':[1,6],'input_profile':'experimental_front_only','action_expert_adapter':{'sha256':'a'*64}}}
    cases=[{'scenario':name,'seed':303,'passed':True} for name in ('lane_center','pedestrian','left_turn','right_turn','yield_left','yield_right','left_arrow','right_arrow')]
    cases += [{'scenario':'red_light','seed':seed,'passed':True} for seed in (300,301,302)]
    self.receipt={'passed':True,'input_profile':'experimental_front_only','provenance':self.health['provenance'],'cases':cases}

  def test_qualification_is_bound_to_exact_weights_adapter_and_all_cases(self):
    self.assertTrue(qualified(self.receipt,self.health))
    altered=copy.deepcopy(self.health)
    altered['provenance']['action_expert_adapter']['sha256']='b'*64
    self.assertFalse(qualified(self.receipt,altered))
    incomplete=copy.deepcopy(self.receipt)
    incomplete['cases'].pop()
    self.assertFalse(qualified(incomplete,self.health))
    self.assertFalse(check_health({'teacher_ready':True,'provenance':{**self.health['provenance'],'camera_ids':[0,1,2,3,4,6]}}))

  def test_stale_or_disconnected_teacher_cannot_start_optimizer(self):
    with tempfile.TemporaryDirectory() as directory:
      store=initialize(directory)
      path=store.root/'teacher-health.json'
      write_json(path,{'connected':True,'qualified':True,'updated':time.time()})
      self.assertTrue(training_ready(store))
      write_json(path,{'connected':True,'qualified':True,'updated':time.time()-60})
      self.assertFalse(training_ready(store))
      write_json(path,{'connected':False,'qualified':True,'updated':time.time()})
      self.assertFalse(training_ready(store))

  def test_failed_actual_episode_never_issues_qualification_receipt(self):
    with tempfile.TemporaryDirectory() as directory:
      root=Path(directory)
      write_json(root/'batch'/'qualification.json',{'passed':False})
      with self.assertRaises(ValueError): qualify(root/'batch',root/'receipt.json')
      self.assertFalse((root/'receipt.json').exists())

  def test_full_curriculum_receipt_rejects_a_failed_case_even_if_summary_claims_pass(self):
    with tempfile.TemporaryDirectory() as directory:
      root=Path(directory)
      checksum=hashlib.sha256(json.dumps(self.health['provenance'],sort_keys=True).encode()).hexdigest()
      for index,case in enumerate(self.receipt['cases']):
        episode=root/'batch'/str(index)
        write_json(episode/'provenance.json',self.health)
        write_json(episode/'result.json',{'backend':'nvidia_alpamayo2_edge','revision':TEACHER_REVISION,
          'scenario':case['scenario'],'seed':case['seed'],'status':'pass','failures':[],
          'model_provenance_sha256':checksum,'model_inputs_include_signal_ground_truth':False,'scripted_fallback':False})
      write_json(root/'batch'/'qualification.json',{'passed':True})
      receipt=qualify(root/'batch',root/'passed.json')
      self.assertTrue(qualified(receipt,self.health))
      result=root/'batch'/'0'/'result.json'
      value=json.loads(result.read_text())
      write_json(result,{**value,'status':'fail','failures':['lane_envelope']})
      with self.assertRaises(ValueError): qualify(root/'batch',root/'rejected.json')
      self.assertFalse((root/'rejected.json').exists())

  def test_progress_reports_counts_and_timing_without_reasoning_text(self):
    with tempfile.TemporaryDirectory() as directory:
      path=Path(directory)/'case.log'
      path.write_text(json.dumps({'plan':3,'simulation_time_s':5,'inference_s':1.1,'cot':'private reasoning'})+'\n')
      self.assertEqual(log_progress(path),{'plan':3,'simulation_time_s':5,'inference_s':1.1})

  def test_live_supervisor_progress_wins_over_an_old_remote_clock(self):
    with tempfile.TemporaryDirectory() as directory:
      store=initialize(directory)
      (store.root/'teacher-pilot.log').write_text(json.dumps({'phase':'completed','updated':9999999999})+'\n')
      write_json(store.root/'teacher-training-progress.json',{'phase':'training','cycle':3,'updated':1})
      self.assertEqual(adaptation_progress(store)['cycle'],3)
      self.assertEqual(adaptation_progress(store)['phase'],'training')


if __name__=='__main__': unittest.main()
