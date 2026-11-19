import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

HAS_TORCH=importlib.util.find_spec('torch') is not None


@unittest.skipUnless(HAS_TORCH,'GPU training environment supplies torch')
class TeacherLearningTest(unittest.TestCase):
  def test_completed_epoch_retains_frozen_adapters_and_cannot_overwrite_qualified_snapshot(self):
    import hashlib,json
    import torch
    from torch import nn
    from safetensors.torch import load_file
    from tools.training_studio.teacher_lora import DeltaLinear
    from tools.training_studio.teacher_train import save_epoch_checkpoint
    model=nn.Module();model.expert=DeltaLinear(nn.Linear(2,2));model.vlm=DeltaLinear(nn.Linear(2,2));model.vlm.requires_grad_(False)
    with tempfile.TemporaryDirectory() as directory:
      pointer=save_epoch_checkpoint(model,directory,1,{'validation_loss':5},dataset_sha256='d'*64,parent_sha256='p'*64,objective_revision='v3')
      path=Path(directory)/pointer['file'];saved=load_file(str(path))
      self.assertIn('vlm.a',saved);torch.testing.assert_close(saved['vlm.a'],model.vlm.a)
      self.assertEqual(pointer['sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
      self.assertFalse(pointer['driving_qualified'])
      self.assertEqual(json.loads(path.with_suffix('.json').read_text()),pointer)
      original=path.read_bytes()
      with self.assertRaises(FileExistsError):save_epoch_checkpoint(model,directory,1,{},dataset_sha256='x',parent_sha256='y',objective_revision='z')
      self.assertEqual(path.read_bytes(),original)

  def test_immediate_steering_has_correct_symmetric_gradients_and_prioritizes_next_commands(self):
    import torch
    from tools.training_studio.teacher_train import immediate_steering_loss
    space=SimpleNamespace(dt=.1,curvature_std=torch.tensor(.1))
    history=torch.zeros(1,20,3);history[0,-2,0]=-.5
    for curvature in (-1.,1.):
      target=torch.zeros(1,64,2);target[:,:3,1]=curvature
      prediction=torch.zeros_like(target,requires_grad=True)
      loss=immediate_steering_loss(prediction,target,space,history);loss.backward()
      self.assertTrue(torch.isfinite(prediction.grad).all())
      self.assertTrue(bool((prediction.grad[:,:3,1]*curvature<0).all()))
      self.assertEqual(float(prediction.grad[...,0].abs().sum()),0.)
      self.assertEqual(float(prediction.grad[:,20:].abs().sum()),0.)
      self.assertEqual(float(immediate_steering_loss(target,target,space,history)),0.)
    early=torch.zeros(1,64,2);early[:,:3,1]=1.
    late=torch.zeros_like(early);late[:,17:20,1]=1.
    self.assertGreater(float(immediate_steering_loss(early,torch.zeros_like(early),space,history)),10*float(immediate_steering_loss(late,torch.zeros_like(late),space,history)))
    parked=torch.zeros_like(history)
    self.assertGreater(float(immediate_steering_loss(early,torch.zeros_like(early),space,parked)),0.)

  def test_stationary_brake_margin_learns_against_creep_without_penalizing_sufficient_braking(self):
    import torch
    from tools.training_studio.teacher_train import held_brake_margin_loss
    space=SimpleNamespace(accel_std=torch.tensor(2.),accel_mean=torch.tensor(.3))
    action=torch.zeros(1,64,2);action[...,0]=-.15;action.requires_grad_()
    loss=held_brake_margin_loss(action,space);loss.backward()
    self.assertGreater(float(loss),0.)
    self.assertTrue(bool((action.grad[:,:10,0]>0).all()))
    self.assertEqual(float(action.grad[:,10:,0].abs().sum()),0.)
    self.assertEqual(float(action.grad[...,1].abs().sum()),0.)
    braking=torch.zeros_like(action);braking[...,0]=-.25
    self.assertEqual(float(held_brake_margin_loss(braking,space)),0.)

  def test_moving_approach_commands_supervise_braking_without_forcing_brakes_on_distant_approaches(self):
    import torch
    from tools.training_studio.teacher_train import immediate_command_loss
    for target_acceleration in (-2.4,1.2):
      target=torch.full((1,64),target_acceleration)
      prediction=torch.zeros_like(target,requires_grad=True)
      loss=immediate_command_loss(prediction-target);loss.backward()
      self.assertTrue(torch.isfinite(prediction.grad).all())
      self.assertTrue(bool((prediction.grad[:,:10]*target_acceleration<0).all()))
      self.assertEqual(float(prediction.grad[:,20:].abs().sum()),0.)
    pulse=torch.zeros(1,64);pulse[:,0]=.2;pulse[:,1]=-.2;pulse.requires_grad_()
    self.assertEqual(float(pulse.mean()),0.)
    hold=immediate_command_loss(pulse);self.assertGreater(float(hold),0.);hold.backward()
    self.assertGreater(float(pulse.grad[0,0]),0.);self.assertLess(float(pulse.grad[0,1]),0.)
    early=torch.zeros(1,64);early[:,3:10]=2
    late=torch.zeros_like(early);late[:,13:20]=2
    self.assertGreater(float(immediate_command_loss(early)),float(immediate_command_loss(late)))

  def test_first_decision_error_cannot_hide_behind_correct_template_completion(self):
    import torch
    from tools.training_studio.teacher_reasoning_train import decision_objective
    target=torch.zeros(1,20,dtype=torch.long)
    early=torch.zeros(1,20,2);early[...,0]=6;early[:,0,0]=0;early[:,0,1]=6
    late=torch.zeros_like(early);late[...,0]=6;late[:,-1,0]=0;late[:,-1,1]=6
    first,mean_first,_=decision_objective(early,target);last,mean_last,_=decision_objective(late,target)
    torch.testing.assert_close(mean_first,mean_last)
    self.assertGreater(float(first),10*float(last))
    early.requires_grad_();loss,_,_=decision_objective(early,target);loss.backward()
    self.assertTrue(torch.isfinite(early.grad).all())
    self.assertLess(float(early.grad[0,0,0]),0.)
    self.assertGreater(float(early.grad[0,0].abs().sum()),100*float(early.grad[0,1].abs().sum()))

  def test_restart_supervision_prioritizes_executed_commands_over_equally_wrong_later_commands(self):
    import torch
    from tools.training_studio.teacher_train import restart_command_loss
    early=torch.zeros(1,64);early[:,:3]=1.6
    late=torch.zeros_like(early);late[:,17:20]=1.6
    torch.testing.assert_close(early[:,:20].square().mean(),late[:,:20].square().mean())
    self.assertGreater(float(restart_command_loss(early)),10*float(restart_command_loss(late)))
    prediction=torch.zeros_like(early,requires_grad=True)
    loss=restart_command_loss(prediction-early);loss.backward()
    self.assertTrue(bool((prediction.grad[:,:3]<0).all()))
    self.assertEqual(float(prediction.grad[:,20:].abs().sum()),0.)
    self.assertEqual(float(restart_command_loss(torch.zeros_like(early))),0.)

  def test_permitted_motion_loss_has_a_restart_gradient_at_zero_velocity_and_preserves_turn_direction(self):
    import torch
    from tools.training_studio.teacher_train import proceed_velocity_loss
    target=torch.zeros(1,64,3);target[:,:20,0]=1.5;target[:,:20,1]=.3
    prediction=torch.zeros_like(target,requires_grad=True)
    loss=proceed_velocity_loss(prediction,target)
    self.assertGreater(float(loss.detach()),0.)
    loss.backward()
    self.assertTrue(bool((prediction.grad[:,:20,0]<0).all()))
    self.assertTrue(bool((prediction.grad[:,:20,1]<0).all()))
    self.assertEqual(float(proceed_velocity_loss(target,target)),0.)
    self.assertEqual(float(prediction.grad[:,20:].abs().sum()),0.)

  def test_stop_selection_and_loss_reject_stopping_just_outside_original_zone(self):
    import torch
    from tools.training_studio.teacher_train import valid_stopped_trajectory,stop_zone_loss
    xyz=torch.zeros(1,64,3);velocity=torch.zeros_like(xyz)
    self.assertFalse(bool(valid_stopped_trajectory(xyz,velocity,5.1)))
    self.assertFalse(bool(valid_stopped_trajectory(xyz,velocity,5.)))
    self.assertTrue(bool(valid_stopped_trajectory(xyz,velocity,4.9)))
    advanced=xyz.clone();advanced[...,0]=.2
    self.assertTrue(bool(valid_stopped_trajectory(advanced,velocity,5.1)))
    overshot=xyz.clone();overshot[...,0]=5.2
    self.assertFalse(bool(valid_stopped_trajectory(overshot,velocity,5.1)))
    moving=velocity.clone();moving[:,-1,0]=.2
    self.assertFalse(bool(valid_stopped_trajectory(advanced,moving,5.1)))
    late_entry=xyz.clone();late_entry[...,0]=.095
    late_entry[:,-10:,0]=torch.linspace(.095,.105,10)
    late_velocity=torch.diff(torch.cat((torch.zeros_like(late_entry[:,:1]),late_entry),dim=1),dim=1)/.1
    self.assertFalse(bool(valid_stopped_trajectory(late_entry,late_velocity,5.1)))
    held=torch.ones(1,64)
    prediction=xyz.clone().requires_grad_()
    loss=stop_zone_loss(prediction,advanced,held,5.1)
    self.assertGreater(float(loss.detach()),0.)
    loss.backward()
    self.assertTrue(bool((prediction.grad[...,0]<0).all()))
    self.assertEqual(float(stop_zone_loss(advanced,advanced,held,5.1)),0.)
    self.assertEqual(float(stop_zone_loss(xyz,xyz,held,9.)),0.)

  def test_stop_command_loss_catches_positive_pulses_even_when_signed_speed_later_cancels(self):
    import torch
    from tools.training_studio.teacher_train import held_command_loss
    space=SimpleNamespace(dt=.1,accel_std=torch.tensor(1.),accel_mean=torch.tensor(0.))
    history=torch.zeros(1,20,3)
    zero=torch.zeros(1,64,2)
    self.assertEqual(float(held_command_loss(zero,space,history)),0.)
    for positive,negative in ((0,1),(1,0)):
      pulse=zero.clone()
      pulse[0,positive,0]=.5; pulse[0,negative,0]=-.5
      pulse.requires_grad_()
      loss=held_command_loss(pulse,space,history)
      self.assertGreater(float(loss.detach()),0.)
      loss.backward()
      self.assertGreater(float(pulse.grad[0,positive,0]),0.)

  def test_motion_initialization_resolves_sign_conflict_without_changing_observed_reverse_or_forward_fit(self):
    import torch
    from tools.training_studio.teacher_motion import install
    fitted=torch.tensor([-.02,-1.,2.,-.1])
    measured=torch.tensor([.04,-1.,1.,0.])
    history=torch.zeros(4,2,3)
    history[:,-2,0]=-measured*.1
    original=history.clone()
    theta=torch.tensor([.01,.02,.03,.04])
    space=SimpleNamespace(dt=.1,estimate_t0_states=lambda *args:{'v':fitted,'theta':theta})
    install(space); installed=space.estimate_t0_states; install(space)
    self.assertIs(space.estimate_t0_states,installed)
    result=space.estimate_t0_states(history,torch.eye(3).expand(4,2,3,3))
    torch.testing.assert_close(result['v'],torch.tensor([.04,-1.,2.,0.]))
    torch.testing.assert_close(result['theta'],theta)
    torch.testing.assert_close(history,original)

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
    from tools.training_studio.teacher_train import spill_prefix,load_prefix
    with tempfile.TemporaryDirectory() as directory:
      spilled=spill_prefix(item,Path(directory)/'prefix.pt')
      model.expert.expert.zero_grad()
      c,xyz,_=rollout(model,spilled,grad=True)
      xyz.square().mean().backward()
      torch.testing.assert_close(a,c,rtol=0,atol=0)
      torch.testing.assert_close(expected,model.expert.expert.linear.weight.grad,rtol=0,atol=0)
      load_prefix.cache_clear()

  def test_disk_prefix_cache_keeps_only_one_context_and_preserves_kv(self):
    import torch
    from tools.training_studio.teacher_train import spill_prefix,load_prefix
    with tempfile.TemporaryDirectory() as directory:
      for index in range(20):
        keys=torch.full((1,2,3),float(index))
        item={'cache':SimpleNamespace(layers=[SimpleNamespace(keys=keys,values=keys+1)]),
          'positions':torch.tensor([index]),'mask':torch.ones(1),'row':{'index':index}}
        spilled=spill_prefix(item,Path(directory)/f'{index}.pt')
        self.assertNotIn('cache',spilled)
        restored=load_prefix(spilled['prefix_path'])
        torch.testing.assert_close(restored['cache'].layers[0].keys,keys,rtol=0,atol=0)
        torch.testing.assert_close(restored['cache'].layers[0].values,keys+1,rtol=0,atol=0)
        self.assertEqual(load_prefix.cache_info().currsize,1)
      load_prefix.cache_clear()

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

  def test_combined_checkpoint_keeps_frozen_visual_decisions_during_expert_continuation(self):
    import torch
    from torch import nn
    from safetensors.torch import save_file
    from tools.training_studio.teacher_lora import DeltaLinear,install,expand,load,adapter_parameters,reasoning_path
    class Model(nn.Module):
      def __init__(self):
        super().__init__()
        self.config=SimpleNamespace(vlm_config=SimpleNamespace(text_config=SimpleNamespace(num_hidden_layers=8)))
        self.vlm=nn.Module();self.vlm.model=nn.Module();self.vlm.model.language_model=nn.Module()
        self.vlm.model.language_model.layers=nn.ModuleList()
        for index in range(8):
          layer=nn.Module();layer.self_attn=nn.Module();layer.self_attn.q_proj=nn.Linear(4,4);layer.self_attn.v_proj=nn.Linear(4,4)
          self.vlm.model.language_model.layers.append(layer)
        self.expert=nn.Module();self.expert.expert=nn.Module();self.expert.expert.block=nn.Module();self.expert.expert.block.q_proj=nn.Linear(4,4);self.expert.action_out_proj=nn.Linear(4,2)
      def forward(self,x):
        features=sum(layer.self_attn.q_proj(x)+layer.self_attn.v_proj(x) for layer in self.vlm.model.language_model.layers)
        return self.expert.action_out_proj(self.expert.expert.block.q_proj(features))
    torch.manual_seed(17);model=Model();install(model);expand(model)
    name='vlm.model.language_model.layers.7.self_attn.q_proj';parent=model.get_submodule(name.rpartition('.')[0]);parent.q_proj=DeltaLinear(parent.q_proj)
    with torch.no_grad():parent.q_proj.b.normal_(std=.03)
    model.vlm.requires_grad_(False);x=torch.randn(3,4)
    frozen={key:p.detach().clone() for key,p in model.vlm.named_parameters()}
    torch.optim.SGD((p for p in model.parameters() if p.requires_grad),lr=.00001).zero_grad()
    model(x).square().mean().backward()
    torch.optim.SGD((p for p in model.parameters() if p.requires_grad),lr=.00001).step()
    for key,p in model.vlm.named_parameters():torch.testing.assert_close(p,frozen[key])
    saved=adapter_parameters(model)
    self.assertIn(name+'.a',saved);self.assertIn(name+'.b',saved)
    self.assertFalse(any('.base.' in key for key in saved))
    for invalid in ('vlm.model.language_model.layers.0.self_attn.q_proj','vlm.model.language_model.layers.8.self_attn.q_proj','vlm.model.language_model.layers.7.self_attn.k_proj','vlm.model.visual.q_proj'):
      self.assertFalse(reasoning_path(model,invalid))
      with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'invalid.safetensors';save_file({invalid+'.a':torch.zeros(8,4)},str(path))
        with self.assertRaises(ValueError):load(Model(),path)
    with tempfile.TemporaryDirectory() as directory:
      path=Path(directory)/'combined.safetensors';save_file({k:p.detach().contiguous() for k,p in saved.items()},str(path))
      torch.manual_seed(17);restored=Model();load(restored,path);restored.vlm.requires_grad_(False)
      torch.testing.assert_close(model(x),restored(x))
      self.assertEqual(set(saved),set(adapter_parameters(restored)))
      self.assertTrue(all(not p.requires_grad for p in restored.vlm.parameters()))

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
