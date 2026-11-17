"""Actual N16 action + residual head distillation; exports the complete original graph."""
from pathlib import Path
import time

from tools.training_studio.store import BASE, read_json, write_json
from openpilot.sunnypilot.formosalink.training_protocol import digest_file

WEIGHT = "model.on_policy.off_policy.temporal_hydra.final_layer.action.weight"
BIAS = WEIGHT.removesuffix("weight") + "bias"
SCALE = "model.on_policy.off_policy.temporal_hydra.scale_layer.action.scale"
FEATURES, CONTEXT, ACTION = "add_86", "select_14", "add_104"


def instrument(source, destination):
  import onnx
  from tools.training_studio import plan_head
  model = onnx.load(str(source))
  # These taps are audited against the pinned N16, not the older 512-feature model.
  if not any(WEIGHT in node.input and node.input[0] == FEATURES for node in model.graph.node):
    raise ValueError("unsupported N16 feature contract")
  names = {name for node in model.graph.node for name in node.output}
  if not {FEATURES, CONTEXT, ACTION} <= names:
    raise ValueError("N16 action/residual graph changed")
  for name in (FEATURES, CONTEXT, ACTION):
    model.graph.output.append(onnx.helper.make_tensor_value_info(name, onnx.TensorProto.FLOAT16, [1, 2 if name == ACTION else 512]))
  model.graph.output.append(onnx.helper.make_tensor_value_info(plan_head.FEATURES,onnx.TensorProto.FLOAT16,[1,512]))
  onnx.save(model, str(destination))


def head_graph(model, destination):
  import onnx
  producers = {name: node for node in model.graph.node for name in node.output}
  required, seen, pending = set(), set(), [ACTION]
  while pending:
    name = pending.pop()
    if name in seen:
      continue
    seen.add(name)
    if name not in (FEATURES, CONTEXT) and name in producers:
      node = producers[name]
      required.add(id(node))
      pending.extend(node.input)
  nodes = [node for node in model.graph.node if id(node) in required]
  # Protobuf repeated fields can materialize wrappers; compare serialized nodes instead.
  required_outputs = seen - {FEATURES, CONTEXT}
  nodes = [node for node in model.graph.node if any(name in required_outputs for name in node.output)]
  graph = onnx.helper.make_graph(nodes, "n16_action_residual",
    [onnx.helper.make_tensor_value_info(name, onnx.TensorProto.FLOAT16, [1,512]) for name in (FEATURES,CONTEXT)],
    [onnx.helper.make_tensor_value_info(ACTION, onnx.TensorProto.FLOAT16, [1,2])],
    [value for value in model.graph.initializer if value.name in seen])
  result = onnx.helper.make_model(graph, opset_imports=model.opset_import, ir_version=model.ir_version)
  onnx.checker.check_model(result)
  onnx.save(result, str(destination))


def network_from(model, device="cpu"):
  import torch
  import torch.nn.functional as F
  from onnx import numpy_helper
  arrays = {value.name: numpy_helper.to_array(value).copy() for value in model.graph.initializer
    if value.name in (WEIGHT, BIAS, SCALE) or value.name.startswith(("model.on_policy.action_encoder.", "model.on_policy.residual_hydra."))}

  class Head(torch.nn.Module):
    def __init__(self):
      super().__init__()
      self.names = [name for name in arrays if name != SCALE]
      self.values = torch.nn.ParameterList([torch.nn.Parameter(torch.from_numpy(arrays[name][:2] if name in (WEIGHT,BIAS) else arrays[name]).float()) for name in self.names])
      self.register_buffer("scale", torch.from_numpy(arrays[SCALE][:2]).float())

    def weights(self):
      return dict(zip(self.names, self.values, strict=True))

    @staticmethod
    def half(value):
      return value.half().float()

    def forward(self, features, context):
      weights = self.weights()
      def linear(value, prefix):
        return self.half(F.linear(value, self.half(weights[prefix+".weight"]), self.half(weights[prefix+".bias"]) if prefix+".bias" in weights else None))
      mean = self.half(self.half(F.linear(features, self.half(weights[WEIGHT]), self.half(weights[BIAS]))) * self.scale)
      encoded = linear(mean, "model.on_policy.action_encoder.net.0")
      encoded = self.half(encoded * self.half(torch.sigmoid(encoded)))
      hidden = self.half(context + linear(encoded, "model.on_policy.action_encoder.net.2"))
      prefix = "model.on_policy.residual_hydra.head_mlp.residual_action"
      value = self.half(F.layer_norm(hidden, (512,), self.half(weights[prefix+".norm.weight"]), self.half(weights[prefix+".norm.bias"]), 1e-5))
      value = self.half(F.gelu(linear(value, prefix+".c_fc"), approximate="tanh"))
      value = self.half(linear(value, prefix+".c_proj") + hidden)
      return self.half(mean + self.half(torch.tanh(linear(value, "model.on_policy.residual_hydra.final_layer.residual_action"))))

  return Head().to(device)


def compare(model, network, features, context, folder, device):
  import numpy as np
  import onnxruntime as ort
  import torch
  folder = Path(folder)
  torch.set_num_threads(4)
  head_graph(model, folder / "head-check.onnx")
  options = ort.SessionOptions()
  options.intra_op_num_threads = 2
  session = ort.InferenceSession(str(folder / "head-check.onnx"), sess_options=options, providers=["CPUExecutionProvider"])
  selected = np.linspace(0, len(features)-1, min(16,len(features)), dtype=int)
  actual = np.concatenate([session.run([ACTION], {FEATURES:features[i:i+1].astype(np.float16), CONTEXT:context[i:i+1].astype(np.float16)})[0] for i in selected]).astype(np.float32)
  with torch.no_grad():
    predicted = network(torch.from_numpy(features[selected]).float().to(device), torch.from_numpy(context[selected]).float().to(device)).cpu().numpy()
  error = float(np.max(np.abs(actual-predicted)))
  if not np.isfinite(error) or error > .02:
    raise ValueError(f"FP16 N16 head parity failed: {error}")
  return {"max_error": error, "tolerance": .02, "samples": len(selected), "passed": True}


def train(folder):
  import hashlib
  import numpy as np
  import onnx
  from onnx import numpy_helper
  import torch
  import torch.nn.functional as F
  from tools.training_studio import plan_head
  folder = Path(folder)
  plan = read_json(folder / "plan.json")
  config = plan["config"]
  source = folder / "source.onnx"
  source_hash = digest_file(source)
  data = np.load(folder / "dataset.npz", allow_pickle=False)
  features, context, target = [data[key].astype(np.float32) for key in ("features", "context", "target")]
  plan_features,plan_target=[data[key].astype(np.float32) for key in ("plan_features","plan_target")]
  split, groups = data["split"], data["group"]
  if any(not np.isfinite(value).all() for value in (features,context,target,plan_features,plan_target)):
    raise ValueError("nonfinite training data")
  for a,b in (("train","validation"),("train","test"),("validation","test")):
    if set(groups[split==a]) & set(groups[split==b]):
      raise ValueError("route leakage")
  masks = {name:np.flatnonzero(split==name) for name in ("train","validation","test")}
  if any(not len(indices) for indices in masks.values()):
    raise ValueError("all three route splits require usable teacher samples")
  device = config.get("training_device", "cuda")
  if device == "cuda" and not torch.cuda.is_available():
    raise RuntimeError("CUDA training worker unavailable; configure the DGX worker")
  torch.manual_seed(int(config.get("seed",7)))
  model = onnx.load(str(source))
  network = network_from(model, device)
  trajectory_network=plan_head.network_from(model,device)
  preflight = compare(model, network, features, context, folder, device)
  trajectory_preflight=plan_head.compare(model,trajectory_network,plan_features,folder,device)
  weights = network.weights()
  mutable=set(weights)|{plan_head.WEIGHT,plan_head.BIAS}
  protected_before = hashlib.sha256(b"".join(value.SerializeToString() for value in model.graph.initializer if value.name not in mutable)).hexdigest()
  # Training consumes train only. Validation is reported each epoch; test is evaluated once after export.
  def metrics(indices):
    losses = []
    with torch.no_grad():
      for batch in np.array_split(indices, max(1,(len(indices)+127)//128)):
        x,c,y = [torch.from_numpy(value[batch]).to(device) for value in (features,context,target)]
        px,py=[torch.from_numpy(value[batch]).to(device) for value in (plan_features,plan_target)]
        value=F.smooth_l1_loss(network(x,c),y,reduction="none").mean(1)+.1*plan_head.loss(trajectory_network(px),py)
        losses.extend(value.cpu().tolist())
    return float(np.mean(losses))
  baseline = {name:metrics(masks[name]) for name in ("train","validation")}
  epochs, batch_size = int(config.get("epochs",20)), int(config.get("batch_size",128))
  parameters_list=[*network.parameters(),*trajectory_network.parameters()]
  optimizer = torch.optim.AdamW(parameters_list,lr=float(config.get("learning_rate",.00001)),weight_decay=0)
  generator = np.random.default_rng(int(config.get("seed",7)))
  history = []
  parameters = sum(value.numel() for value in parameters_list)
  for epoch in range(epochs):
    for batch in np.array_split(generator.permutation(masks["train"]),max(1,(len(masks["train"])+batch_size-1)//batch_size)):
      x,c,y = [torch.from_numpy(value[batch]).to(device) for value in (features,context,target)]
      px,py=[torch.from_numpy(value[batch]).to(device) for value in (plan_features,plan_target)]
      optimizer.zero_grad()
      loss = F.smooth_l1_loss(network(x,c),y)+.1*plan_head.loss(trajectory_network(px),py).mean()
      if not torch.isfinite(loss):
        raise ValueError("nonfinite distillation loss")
      loss.backward()
      gradients = [value.grad for value in parameters_list if value.grad is not None]
      if not gradients or not all(torch.isfinite(value).all() for value in gradients):
        raise ValueError("missing or nonfinite gradients")
      torch.nn.utils.clip_grad_norm_(parameters_list,1.)
      optimizer.step()
    row = {"epoch":epoch+1, **{name:metrics(masks[name]) for name in ("train","validation")}}
    history.append(row)
    write_json(folder / "progress.json", {"stage":"train", "epoch":epoch+1,"epochs":epochs,"history":history,
      "trainable_parameters":parameters,"backbone_frozen":True,"updated":time.time()})
  changed = 0
  for value in model.graph.initializer:
    if value.name in weights:
      array = numpy_helper.to_array(value).copy()
      replacement = weights[value.name].detach().cpu().numpy().astype(array.dtype)
      original = array[:2] if value.name in (WEIGHT,BIAS) else array
      changed += int(np.count_nonzero(original != replacement))
      if value.name in (WEIGHT,BIAS):
        array[:2] = replacement
      else:
        array = replacement
      value.CopyFrom(numpy_helper.from_array(array,value.name))
  changed+=plan_head.export(model,trajectory_network)
  if changed == 0:
    raise ValueError("no FP16 weights changed")
  protected_after = hashlib.sha256(b"".join(value.SerializeToString() for value in model.graph.initializer if value.name not in mutable)).hexdigest()
  if protected_after != protected_before:
    raise ValueError("protected N16 backbone changed")
  after = compare(model,network,features,context,folder,device)
  trajectory_after=plan_head.compare(model,trajectory_network,plan_features,folder,device)
  onnx.checker.check_model(model)
  onnx.save(model,str(folder / "candidate.onnx"))
  result = {"base":BASE,"source_sha256":source_hash,"candidate_sha256":digest_file(folder / "candidate.onnx"),
    "snapshot":plan["snapshot"],"scope":"action_residual_and_3d_trajectory_heads","backbone_frozen":True,"trainable_parameters":parameters,
    "changed_parameters":changed,"baseline":baseline,"final":history[-1],"history":history,"export_parity":{"before":preflight,"after":after},
    "trajectory_export_parity":{"before":trajectory_preflight,"after":trajectory_after},
    "trajectory_horizon_s":6.4,"near_horizon_weight":3,"device":device,"epochs":epochs,"teacher":read_json(folder / "teacher.json")}
  write_json(folder / "training.json",result)
