"""Distill observed 3D trajectory/velocity/yaw rows, preserving the rest of N16's plan head."""
import math

FEATURES="add_66"
OUTPUT="mul_53"
WEIGHT="model.off_policy.temporal_hydra.final_layer.plan.weight"
BIAS=WEIGHT.removesuffix("weight")+"bias"
SCALE="model.off_policy.temporal_hydra.scale_layer.plan.scale"
TIMES=[10*(index/32)**2 for index in range(33)]
VALID=[index for index,value in enumerate(TIMES) if value<=6.4]
COLUMNS=(0,1,2,3,4,5,11,14)  # position xyz, velocity xyz, body yaw, yaw rate
ROWS=[index*15+column for index in VALID for column in COLUMNS]


def targets(result, speed):
  import numpy as np
  path=np.vstack((np.zeros((1,3)),np.asarray(result["xyz"],np.float64))) * np.array([1,-1,-1])
  rotations=np.asarray(result["rot"],np.float64)
  if rotations.shape!=(64,3,3) or not np.isfinite(rotations).all():
    raise ValueError("finite teacher body rotations required for yaw distillation")
  yaw=np.r_[0,-np.unwrap(np.arctan2(rotations[:,1,0],rotations[:,0,0]))]
  ticks=np.arange(65)*.1
  velocity=np.gradient(path,.1,axis=0)
  velocity[0]=[speed,0,0]
  yaw_rate=np.gradient(yaw,.1)
  fields=np.column_stack((path,velocity,yaw,yaw_rate))
  return np.stack([np.interp(np.array(TIMES)[VALID],ticks,fields[:,axis]) for axis in range(8)],axis=-1).astype(np.float32)


def network_from(model,device="cpu"):
  import torch
  import torch.nn.functional as F
  from onnx import numpy_helper
  arrays={value.name:numpy_helper.to_array(value).copy() for value in model.graph.initializer if value.name in (WEIGHT,BIAS,SCALE)}
  if arrays[WEIGHT].shape!=(990,512):
    raise ValueError("N16 plan contract changed")
  class PlanHead(torch.nn.Module):
    def __init__(self):
      super().__init__()
      self.weight=torch.nn.Parameter(torch.from_numpy(arrays[WEIGHT][ROWS]).float())
      self.bias=torch.nn.Parameter(torch.from_numpy(arrays[BIAS][ROWS]).float())
      self.register_buffer("scale",torch.from_numpy(arrays[SCALE][ROWS]).float())

    def forward(self,features):
      value=F.linear(features,self.weight.half().float(),self.bias.half().float()).half().float()
      return (value*self.scale).half().float().reshape(-1,len(VALID),len(COLUMNS))
  return PlanHead().to(device)


def loss(prediction,target):
  import torch
  import torch.nn.functional as F
  delta=prediction-target
  # Wrap yaw differences; positions and velocities stay in metric units.
  yaw=torch.atan2(torch.sin(delta[...,6]),torch.cos(delta[...,6]))
  error=torch.cat((delta[...,:6],yaw.unsqueeze(-1),delta[...,7:]),dim=-1)
  value=F.smooth_l1_loss(error,torch.zeros_like(error),reduction="none")
  weights=prediction.new_tensor([3. if TIMES[index]<=2 else 1. for index in VALID])[None,:,None]
  columns=prediction.new_tensor([1.,1.,1.,.2,.2,.2,.2,.1])[None,None,:]
  return (value*weights*columns).mean((1,2))


def compare(model,network,features,folder,device):
  import numpy as np
  import onnx
  import onnxruntime as ort
  import torch
  graph=onnx.helper.make_graph([
    onnx.helper.make_node("Gemm",[FEATURES,WEIGHT,BIAS],["linear"],transB=1),
    onnx.helper.make_node("Mul",["linear",SCALE],[OUTPUT])],"N16_plan_head",
    [onnx.helper.make_tensor_value_info(FEATURES,onnx.TensorProto.FLOAT16,[1,512])],
    [onnx.helper.make_tensor_value_info(OUTPUT,onnx.TensorProto.FLOAT16,[1,990])],
    [value for value in model.graph.initializer if value.name in (WEIGHT,BIAS,SCALE)])
  graph=onnx.helper.make_model(graph,opset_imports=model.opset_import,ir_version=model.ir_version)
  path=folder/"plan-check.onnx"
  onnx.save(graph,str(path))
  options=ort.SessionOptions()
  options.intra_op_num_threads=2
  session=ort.InferenceSession(str(path),sess_options=options,providers=["CPUExecutionProvider"])
  selected=np.linspace(0,len(features)-1,min(16,len(features)),dtype=int)
  actual=np.concatenate([session.run(None,{FEATURES:features[index:index+1].astype(np.float16)})[0][:,ROWS] for index in selected]).reshape(-1,len(VALID),8).astype(np.float32)
  with torch.no_grad():
    predicted=network(torch.from_numpy(features[selected]).float().to(device)).cpu().numpy()
  error=float(np.max(np.abs(actual-predicted)))
  if not np.isfinite(error) or error>.02:
    raise ValueError("N16 trajectory head FP16 parity failed: "+str(error))
  return {"max_error":error,"tolerance":.02,"passed":True}


def export(model,network):
  import numpy as np
  from onnx import numpy_helper
  changed=0
  for value in model.graph.initializer:
    if value.name in (WEIGHT,BIAS):
      array=numpy_helper.to_array(value).copy()
      replacement=(network.weight if value.name==WEIGHT else network.bias).detach().cpu().numpy().astype(array.dtype)
      changed+=int(np.count_nonzero(array[ROWS]!=replacement))
      array[ROWS]=replacement
      value.CopyFrom(numpy_helper.from_array(array,value.name))
  return changed
