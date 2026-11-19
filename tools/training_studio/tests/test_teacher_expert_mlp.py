import importlib.util
import unittest
if importlib.util.find_spec('torch'):import torch


@unittest.skipUnless(importlib.util.find_spec('torch'),'pinned training image supplies torch')
class ExpertMlpTest(unittest.TestCase):
  def model(self):
    from torch import nn
    class Mlp(nn.Module):
      def __init__(self):
        super().__init__();self.fc1=nn.Linear(4,12,bias=False);self.fc2=nn.Linear(12,4,bias=False)
      def forward(self,x):return self.fc2(torch.relu(self.fc1(x)).square())
    model=nn.Module();model.expert=nn.Module();model.expert.expert=nn.Module();block=nn.Module();block.self_attn=nn.Module()
    for name in ('q_proj','k_proj','v_proj','o_proj'):setattr(block.self_attn,name,nn.Linear(4,4,bias=False))
    block.mlp=Mlp();model.expert.expert.layers=nn.ModuleList([block]);model.expert.action_out_proj=nn.Linear(4,2);model.vlm=nn.Module();model.vlm.mlp=Mlp()
    return model

  def test_pinned_expert_fc1_fc2_expand_without_changing_initial_output_or_vlm(self):
    from tools.training_studio.teacher_lora import install,expand,DeltaLinear,adapter_parameters
    torch.manual_seed(42);model=self.model();x=torch.randn(2,3,4);before=model.expert.expert.layers[0].mlp(x).detach().clone()
    install(model);paths=expand(model);block=model.expert.expert.layers[0]
    self.assertIsInstance(block.mlp.fc1,DeltaLinear);self.assertIsInstance(block.mlp.fc2,DeltaLinear)
    self.assertIn('expert.expert.layers.0.mlp.fc1',paths);self.assertIn('expert.expert.layers.0.mlp.fc2',paths)
    self.assertTrue(torch.equal(before,block.mlp(x)))
    self.assertIsInstance(model.vlm.mlp.fc1,torch.nn.Linear)
    block.mlp(x).square().sum().backward()
    self.assertGreater(float(block.mlp.fc1.b.grad.norm()),0.);self.assertGreater(float(block.mlp.fc2.b.grad.norm()),0.)
    keys=set(adapter_parameters(model));expand(model)
    self.assertEqual(set(adapter_parameters(model)),keys)

  def test_expanded_cosmos_mlp_adapters_round_trip_through_actual_loader(self):
    import tempfile
    from pathlib import Path
    from safetensors.torch import save_file
    from tools.training_studio.teacher_lora import install,expand,load,adapter_parameters
    torch.manual_seed(42);model=self.model();base={k:v.clone() for k,v in model.state_dict().items()};install(model);expand(model)
    with torch.no_grad():
      model.expert.expert.layers[0].mlp.fc1.b.fill_(.01);model.expert.expert.layers[0].mlp.fc2.b.fill_(-.02)
    with tempfile.TemporaryDirectory() as directory:
      path=Path(directory)/'expanded.safetensors';save_file({k:p.detach().contiguous() for k,p in adapter_parameters(model).items()},str(path))
      restored=self.model();restored.load_state_dict(base);load(restored,path)
      x=torch.randn(2,3,4);torch.testing.assert_close(restored.expert.expert.layers[0].mlp(x),model.expert.expert.layers[0].mlp(x),rtol=0,atol=0)
      self.assertEqual(set(adapter_parameters(restored)),set(adapter_parameters(model)))


if __name__=='__main__':unittest.main()
