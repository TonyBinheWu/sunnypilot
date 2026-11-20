import copy
import hashlib
import json
import os
import sys
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tools.training_studio.closed_loop import Loop, IntegrityError, audit_script, validate_manifest
from tools.training_studio.store import read_json, write_json


class ClosedLoopTest(unittest.TestCase):
  def manifest(self):
    validation=[{'sha256':f'v{i}','pixel_sha256':f'pixel-v{i}','split':'validation','seed':8000+i} for i in range(154)]
    train=[{'sha256':'t','pixel_sha256':'pixel-t','split':'train','seed':1000}]
    return {'samples':train+validation,'validation_guard_sha256s':[r['sha256'] for r in validation[:6]],'parent_validation_sha256s':[r['sha256'] for r in validation],'parent_validation_reference_checkpoint_sha256':'reference','validation_guard_reference':{'locked':True},'parent_validation_reference':{'validation_guard':{'locked':True}}}

  def test_manifest_never_admits_reserved_cases_missing_guards_or_cross_split_frames(self):
    manifest=self.manifest();validate_manifest(manifest,'reference')
    broken=copy.deepcopy(manifest);broken['samples'][0]['seed']=303
    with self.assertRaises(IntegrityError):validate_manifest(broken,'reference')
    broken=copy.deepcopy(manifest);broken['samples'][0]['pixel_sha256']='pixel-v0'
    with self.assertRaises(IntegrityError):validate_manifest(broken,'reference')
    broken=copy.deepcopy(manifest);broken['parent_validation_sha256s'].pop()
    with self.assertRaises(IntegrityError):validate_manifest(broken,'reference')
    with self.assertRaises(IntegrityError):validate_manifest(manifest,'other-reference')

  @unittest.skipIf(os.name!='posix','systemd installer runs inside Linux')
  def test_service_installer_preserves_virtualenv_interpreter_and_does_not_start_in_install_only(self):
    from tools.training_studio.install_autonomy import main
    with tempfile.TemporaryDirectory() as temp:
      root=Path(temp);venv=root/'venv/bin/python';venv.parent.mkdir(parents=True);venv.symlink_to(sys.executable)
      data=root/'store';data.mkdir();write_json(data/'config.json',{'teacher_adaptation':{'external_supervisor':True},'closed_loop':{'enabled':True}})
      with patch('pathlib.Path.home',return_value=root),patch('sys.executable',str(venv)),patch('sys.argv',['install','--root',str(data),'--install-only']),patch('tools.training_studio.install_autonomy.subprocess.run') as run:
        main()
      unit=(root/'.config/systemd/user/formosapilot-teacher-loop.service').read_text()
      self.assertIn(str(venv),unit);self.assertIn('Restart=on-failure',unit)
      self.assertFalse(any('start' in call.args[0] for call in run.call_args_list))

  def test_hosted_llm_endpoint_is_rejected_before_remote_setup(self):
    store=SimpleNamespace(config=lambda:{'teacher_url':'https://api.openai.com/v1'})
    with patch('tools.training_studio.closed_loop.Remote') as remote:
      with self.assertRaises(IntegrityError):Loop(store)
      remote.assert_not_called()

  def make_loop(self,root,safe):
    metric={'validation_loss':10.,'red_safe_count':2,'red_samples':3,'red_hold_speed_mse':.2,'lateral_trajectory_mse':5.,'go_velocity_mse':2.,'go_samples':3}
    baseline={**metric,'validation_guard':metric.copy()};row={**copy.deepcopy(baseline),'epoch':1}
    if not safe:row['red_safe_count']=1
    folder=root/'teacher-cycles/cycle-001';folder.mkdir(parents=True)
    write_json(root/'teacher-training-progress.json',{'cycle':1,'phase':'training','history':[row],'baseline':baseline})
    loop=Loop.__new__(Loop);loop.s=SimpleNamespace(root=root,enabled=lambda:True,config=lambda:{'teacher_adaptation':{'enabled':True}},event=Mock());loop.state={'attempts':{},'audit_jobs':{}};loop.native=SimpleNamespace(poll=lambda:None);loop.qualifier=None;loop.qual_key=None;loop.runtime_key='runtime'
    loop.latch=lambda:False;loop.gates=lambda:None;loop.dataset=lambda cycle:(folder,{'validation_guard_reference':metric},{});loop.descriptor=lambda cycle,r:{'file':'epoch-001.safetensors','epoch':1,'sha256':'a'*64,'metrics':r};loop.audit=lambda cycle,descriptor:True;loop.save=Mock()
    return loop

  def test_failed_offline_guard_never_starts_qualification(self):
    with tempfile.TemporaryDirectory() as temp:
      loop=self.make_loop(Path(temp),False)
      with patch('tools.training_studio.closed_loop.subprocess.Popen') as launch:
        loop.tick();launch.assert_not_called()
      self.assertEqual(list(loop.state['attempts'].values()),['rejected_offline'])

  def test_eligible_checkpoint_starts_only_original_fixed_checkpoint_qualifier(self):
    with tempfile.TemporaryDirectory() as temp:
      loop=self.make_loop(Path(temp),True)
      with patch('tools.training_studio.closed_loop.subprocess.Popen') as launch:
        loop.tick();command=launch.call_args.args[0]
      self.assertIn('tools.training_studio.teacher_checkpoint',command)
      self.assertEqual(command[command.index('--selection')+1],'completed')
      self.assertNotIn('qualified_sha256',loop.state)

  def test_transport_timeout_does_not_turn_into_a_tensor_integrity_failure(self):
    with tempfile.TemporaryDirectory() as temp:
      root=Path(temp);(root/'teacher-cycles/cycle-001').mkdir(parents=True)
      loop=Loop.__new__(Loop);loop.s=SimpleNamespace(root=root);loop.r=SimpleNamespace(root='/studio',call=Mock(side_effect=subprocess.TimeoutExpired('ssh',20)));loop.state={'audit_jobs':{}}
      with self.assertRaises(subprocess.TimeoutExpired):loop.audit(1,{'epoch':1,'sha256':'a'*64,'metrics':{}})
      self.assertFalse((root/'config.json').exists())

  def test_real_cpu_proof_rejects_changed_frozen_tensor_even_with_consistent_new_checksum(self):
    import numpy as np
    from safetensors.numpy import save_file
    with tempfile.TemporaryDirectory() as temp:
      root=Path(temp);anchor=root/'anchor.safetensors';checkpoint=root/'epoch-001.safetensors';out=root/'proof.json'
      old={f'anchor{i}':np.ones(1,dtype=np.float32) for i in range(242)};save_file(old,str(anchor));anchor_info={'path':str(anchor),'sha256':hashlib.sha256(anchor.read_bytes()).hexdigest()}
      new={**old,**{f'expert.layer{i}.mlp.fc1.a':np.zeros(1,dtype=np.float32) for i in range(112)}}
      for changed in (False,True):
        if changed:new['anchor0']=np.zeros(1,dtype=np.float32)
        save_file(new,str(checkpoint));checksum=hashlib.sha256(checkpoint.read_bytes()).hexdigest();write_json(checkpoint.with_suffix('.json'),{'sha256':checksum,'epoch':1,'fp32_expert':True,'mlp_only':True,'objective_revision':'ten_step_executed_peak_hold_and_steering_v10','metrics':{'actual':1}})
        exec(audit_script(anchor_info,str(checkpoint),checksum,str(out)),{})
        proof=read_json(out);self.assertEqual(proof['passed'],not changed)
        if changed:self.assertEqual(proof['kind'],'tensor_integrity')


if __name__=='__main__':unittest.main()
