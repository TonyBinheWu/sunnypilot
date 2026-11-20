import copy
import tempfile
from pathlib import Path
import unittest
import torch
from safetensors.torch import save_file
from tools.training_studio.tests import test_teacher_expert_mlp as fixtures
from tools.training_studio.teacher_lora import install,expand,load,adapter_parameters,enable_output_residual,train_mlp_with_output_residual


class OutputResidualTest(unittest.TestCase):
  def model(self):return fixtures.ExpertMlpTest.model(None)

  def forward(self,model,x):
    block=model.expert.expert.layers[0];x=block.self_attn.q_proj(x)
    return model.expert.action_out_proj(x+block.mlp(x))

  def test_zero_initialization_is_identity_and_sgd_changes_only_declared_new_scope(self):
    torch.manual_seed(42);model=self.model();install(model);expand(model);x=torch.randn(2,3,4)
    before=self.forward(model,x).detach();enable_output_residual(model)
    torch.testing.assert_close(self.forward(model,x),before,rtol=0,atol=0)
    selected=train_mlp_with_output_residual(model);self.assertEqual(len(selected),6)
    for name,p in model.named_parameters():self.assertEqual(p.requires_grad,name in selected)
    frozen={name:p.detach().clone() for name,p in model.named_parameters() if name not in selected}
    optimizer=torch.optim.SGD(selected.values(),lr=.01);loss=(self.forward(model,x)-1).square().mean();loss.backward();optimizer.step()
    self.assertGreater(float(model.expert.action_out_proj.output_residual_weight.detach().abs().sum()),0.)
    self.assertGreater(float(model.expert.action_out_proj.output_residual_bias.detach().abs().sum()),0.)
    self.assertLess(float((self.forward(model,x)-1).square().mean().detach()),float(loss.detach()))
    for name,p in model.named_parameters():
      if name in frozen:torch.testing.assert_close(p,frozen[name],rtol=0,atol=0)

  def test_real_safetensors_loader_preserves_old_parameters_and_restores_learned_readout(self):
    torch.manual_seed(42);plain=self.model();model=copy.deepcopy(plain);install(model);expand(model);enable_output_residual(model)
    with torch.no_grad():
      model.expert.action_out_proj.delta_weight.fill_(.04)
      model.expert.action_out_proj.output_residual_weight.normal_(0,.02)
      model.expert.action_out_proj.output_residual_bias.copy_(torch.tensor([.1,-.2]))
    saved={name:p.detach().contiguous() for name,p in adapter_parameters(model).items()}
    with tempfile.TemporaryDirectory() as directory:
      path=Path(directory)/'teacher.safetensors';save_file(saved,str(path));restored=copy.deepcopy(plain);load(restored,path)
      self.assertEqual(set(adapter_parameters(restored)),set(saved));x=torch.randn(2,3,4)
      torch.testing.assert_close(self.forward(restored,x),self.forward(model,x),rtol=0,atol=0)
      for name,p in adapter_parameters(restored).items():torch.testing.assert_close(p,saved[name],rtol=0,atol=0)
      malformed=dict(saved);malformed['expert.action_out_proj.output_residual_weight']=malformed['expert.action_out_proj.output_residual_weight'][:1].contiguous();save_file(malformed,str(path))
      with self.assertRaisesRegex(RuntimeError,'shape mismatch'):load(copy.deepcopy(plain),path)
      malformed=dict(saved);malformed.pop('expert.action_out_proj.output_residual_bias');save_file(malformed,str(path))
      with self.assertRaisesRegex(RuntimeError,'topology mismatch'):load(copy.deepcopy(plain),path)

  def test_readout_scope_requires_an_expanded_explicit_residual(self):
    model=self.model()
    with self.assertRaises(ValueError):enable_output_residual(model)
    install(model);expand(model)
    with self.assertRaises(ValueError):train_mlp_with_output_residual(model)


if __name__=='__main__':unittest.main()
