import importlib.util
import unittest
from types import SimpleNamespace
from tools.training_studio.teacher_precision import resolve,PROFILE

class PrecisionPackageTest(unittest.TestCase):
  def test_snapshot_includes_the_actual_precision_dependency(self):
    import io,tarfile
    from tools.training_studio.remote import Remote
    remote=object.__new__(Remote);remote.root='/owned';captured=[];remote.call=lambda command,**kwargs:captured.append(kwargs['input']);remote.program(snapshot=True)
    with tarfile.open(fileobj=io.BytesIO(captured[0]),mode='r:gz') as archive:self.assertIn(PROFILE.encode(),archive.extractfile('tools/training_studio/teacher_precision.py').read())

  def test_pointer_profile_is_explicit_and_cannot_be_overridden(self):
    self.assertFalse(resolve(None,None));self.assertFalse(resolve(None,{}));self.assertTrue(resolve(None,{'fp32_expert':True}));self.assertTrue(resolve(True,{}))
    for cli,pointer in [(False,{'fp32_expert':True}),(True,{'fp32_expert':False}),(None,{'fp32_expert':1}),(None,{'fp32_expert':'false'}),(1,{})]:
      with self.subTest(cli=cli,pointer=pointer),self.assertRaises(ValueError):resolve(cli,pointer)

@unittest.skipUnless(importlib.util.find_spec('torch'),'pinned training environment supplies torch')
class ExpertPrecisionTest(unittest.TestCase):
  def model(self):
    import torch
    from tools.training_studio.teacher_lora import DenseActionDelta
    model=torch.nn.Module();model.vlm=torch.nn.Linear(2,2,dtype=torch.bfloat16);model.expert=torch.nn.Module();model.expert.core=torch.nn.Linear(2,2,dtype=torch.bfloat16);model.expert.action_out_proj=DenseActionDelta(torch.nn.Linear(2,2,dtype=torch.bfloat16))
    def sample(cache,prefix_length,positions,mask,batch,device,diffusion):
      self.assertFalse(torch.is_autocast_enabled(device));self.assertEqual(cache.layers[0].keys.dtype,torch.float32)
      return model.expert.action_out_proj(model.expert.core(cache.layers[0].keys))
    model._sample_actions=sample;return model

  def cache(self):
    import torch
    return SimpleNamespace(layers=[SimpleNamespace(keys=torch.ones(2,2,dtype=torch.bfloat16),values=torch.zeros(2,2,dtype=torch.bfloat16))])

  def test_cache_conversion_preserves_original_context_and_detaches_prefix(self):
    import torch
    from tools.training_studio.teacher_precision import fp32_cache
    source=self.cache();source.layers[0].keys.requires_grad_();copy=fp32_cache(source,'cpu')
    self.assertIsNot(copy,source);self.assertIsNot(copy.layers[0],source.layers[0]);self.assertEqual(copy.layers[0].keys.dtype,torch.float32);self.assertFalse(copy.layers[0].keys.requires_grad)
    copy.layers[0].keys.zero_();self.assertTrue(torch.equal(source.layers[0].keys,torch.ones_like(source.layers[0].keys)))

  def test_only_expert_changes_dtype_and_nested_autocast_is_disabled(self):
    import torch
    from tools.training_studio.teacher_precision import install
    model=self.model();cache=self.cache();install(model,True);wrapped=model._sample_actions;install(model,True);self.assertIs(model._sample_actions,wrapped)
    self.assertEqual(model.vlm.weight.dtype,torch.bfloat16);self.assertTrue(all(p.dtype==torch.float32 for p in model.expert.parameters()))
    with torch.autocast('cpu',dtype=torch.bfloat16):result=model._sample_actions(cache,2,None,None,1,'cpu',{})
    self.assertEqual(result.dtype,torch.float32);self.assertEqual(cache.layers[0].keys.dtype,torch.bfloat16)
    result.square().sum().backward();self.assertTrue(torch.isfinite(model.expert.action_out_proj.delta_weight.grad).all())
    with self.assertRaises(ValueError):install(model,False)

  def test_disabled_profile_preserves_the_existing_sampler_and_dtypes(self):
    import torch
    from tools.training_studio.teacher_precision import install
    model=self.model();sampler=model._sample_actions;install(model,False);self.assertIs(model._sample_actions,sampler);self.assertEqual(model.expert.core.weight.dtype,torch.bfloat16)
    with self.assertRaises(ValueError):install(model,1)

  def test_checkpoint_records_actual_profile_and_rejects_a_mismatch(self):
    import tempfile
    from pathlib import Path
    from tools.training_studio.teacher_precision import install
    from tools.training_studio.teacher_train import save_epoch_checkpoint
    model=self.model();install(model,True)
    with tempfile.TemporaryDirectory() as folder:
      folder=Path(folder)
      with self.assertRaises(ValueError):save_epoch_checkpoint(model,folder,1,{},dataset_sha256='d',parent_sha256='p',objective_revision='v')
      self.assertEqual(list(folder.iterdir()),[])
      pointer=save_epoch_checkpoint(model,folder,1,{},dataset_sha256='d',parent_sha256='p',objective_revision='v',fp32_expert=True);self.assertIs(pointer['fp32_expert'],True)

if __name__=='__main__':unittest.main()
