import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

HAS_TORCH=importlib.util.find_spec('torch') is not None


@unittest.skipUnless(HAS_TORCH,'GPU training environment supplies torch')
class TeacherLearningTest(unittest.TestCase):
  def test_checkpointed_rollout_preserves_outputs_and_actual_gradients(self):
    import torch
    from torch import nn
    from tools.training_studio.teacher_train import rollout
    class Input(nn.Module):
      def forward(self,x,t): return x+t
    class Core(nn.Module):
      def __init__(self):
        super().__init__(); self.linear=nn.Linear(2,2)
      def forward(self,inputs_embeds,**kwargs): return SimpleNamespace(last_hidden_state=self.linear(inputs_embeds))
    class Space:
      def action_to_traj(self,x,*args): return x.cumsum(1),x
    torch.manual_seed(7)
    model=SimpleNamespace(expert=SimpleNamespace(action_in_proj=Input(),expert=Core(),action_out_proj=nn.Identity(),action_space=Space()))
    item={'device':'cpu','cache':SimpleNamespace(layers=[]),'positions':torch.zeros(1),'mask':torch.ones(1),
      'ego_history_xyz':torch.zeros(1),'ego_history_rot':torch.zeros(1)}
    a,xyz,_=rollout(model,item,grad=False)
    xyz.square().mean().backward()
    expected=model.expert.expert.linear.weight.grad.clone()
    model.expert.expert.zero_grad()
    b,xyz,_=rollout(model,item,grad=True)
    xyz.square().mean().backward()
    torch.testing.assert_close(a,b)
    torch.testing.assert_close(expected,model.expert.expert.linear.weight.grad)
    self.assertGreater(float(expected.abs().max()),0)

  def test_expansion_is_initially_identity_and_preserves_frozen_base_on_reload(self):
    import torch
    from torch import nn
    from safetensors.torch import save_file
    from tools.training_studio.teacher_lora import install,expand,load
    class Model(nn.Module):
      def __init__(self):
        super().__init__()
        self.vision=nn.Linear(4,4)
        self.expert=nn.Module()
        self.expert.expert=nn.Module()
        self.expert.expert.block=nn.Module()
        for key in ('q_proj','k_proj','v_proj','o_proj','up_proj','down_proj','gate_proj'):
          setattr(self.expert.expert.block,key,nn.Linear(4,4))
        self.expert.action_out_proj=nn.Linear(4,2)
      def forward(self,x):
        block=self.expert.expert.block
        return self.expert.action_out_proj(sum(getattr(block,key)(x) for key in ('q_proj','k_proj','v_proj','o_proj','up_proj','down_proj','gate_proj')))
    torch.manual_seed(3); model=Model()
    install(model)
    x=torch.randn(2,4)
    before=model(x).detach()
    expand(model)
    torch.testing.assert_close(before,model(x))
    protected=model.vision.weight.detach().clone()
    trainable={name:p for name,p in model.named_parameters() if p.requires_grad}
    optimizer=torch.optim.SGD(trainable.values(),lr=.001)
    model(x).square().mean().backward(); optimizer.step()
    torch.testing.assert_close(protected,model.vision.weight)
    self.assertTrue(all(name.startswith('expert.') for name in trainable))
    with tempfile.TemporaryDirectory() as directory:
      path=Path(directory)/'adapter.safetensors'
      save_file({name:p.detach().contiguous() for name,p in trainable.items()},str(path))
      torch.manual_seed(3); restored=Model()
      load(restored,path)
      torch.testing.assert_close(model(x),restored(x))

  def test_inference_context_copy_is_independent_and_normal_for_backprop(self):
    import torch
    from tools.training_studio.teacher_train import cache_copy
    with torch.inference_mode(): original=torch.ones(1,2,3)
    source=SimpleNamespace(layers=[SimpleNamespace(keys=original,values=original)])
    copied=cache_copy(source,'cpu')
    self.assertFalse(copied.layers[0].keys.is_inference())
    copied.layers[0].keys.zero_()
    self.assertEqual(float(source.layers[0].keys.sum()),6.)

  def test_dense_action_head_upgrade_preserves_a_trained_low_rank_head(self):
    import torch
    from tools.training_studio.teacher_lora import DeltaLinear,DenseActionDelta
    torch.manual_seed(8)
    base=torch.nn.Linear(4,2)
    base.requires_grad_(False)
    low_rank=DeltaLinear(base)
    with torch.no_grad(): low_rank.b.normal_()
    inputs=torch.randn(5,4)
    dense=DenseActionDelta.from_low_rank(low_rank)
    torch.testing.assert_close(low_rank(inputs),dense(inputs),rtol=1e-5,atol=1e-6)
    self.assertFalse(dense.base.weight.requires_grad)
    self.assertTrue(dense.delta_weight.requires_grad)


if __name__=='__main__': unittest.main()
