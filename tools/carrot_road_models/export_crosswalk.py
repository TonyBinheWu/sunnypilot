# SPDX-License-Identifier: GPL-3.0-or-later
# Export adapter for kairess/crosswalk-traffic-light-detection-yolov5.
# Uses only allowlisted class definitions and weights_only=True checkpoint load.
import ast,sys,types,hashlib,json,warnings,argparse,tempfile,zipfile
from pathlib import Path
import torch,torch.nn as nn,numpy as np,onnx,onnxruntime as ort
sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(2)
parser=argparse.ArgumentParser(description='Reproduce fixed-320 crosswalk ONNX from bundled GPL source')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
vendor=Path(__file__).resolve().parents[2]/'openpilot/selfdrive/carrot/web/vendor/road-detector'
source_root=vendor/'source'
manifest=json.loads((vendor/'manifest.json').read_text())
for name in ['crosswalk-best.pt','crosswalk-source.zip']:
 record=next(f for f in manifest['files'] if f['path']=='source/'+name)
 if hashlib.sha256((source_root/name).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('source integrity: '+name)
temporary=tempfile.TemporaryDirectory(prefix='carrot-road-export-')
root=Path(temporary.name)
with zipfile.ZipFile(source_root/'crosswalk-source.zip') as archive:
 for item in archive.infolist():
  path=(root/'crosswalk-source'/item.filename).resolve()
  if not path.is_relative_to(root.resolve()):raise ValueError('archive path')
  if item.is_dir():continue
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(archive.read(item))
assert hashlib.sha256((source_root/'crosswalk-best.pt').read_bytes()).hexdigest()=='7eb9e22c31e6eef68dce2cfd656fa27614e21203371cdf9255d942c86e29f127'
pkg=types.ModuleType('models');pkg.__path__=[];sys.modules['models']=pkg
common=types.ModuleType('models.common');sys.modules[common.__name__]=common
common.__dict__.update(torch=torch,nn=nn,warnings=warnings)
yolo=types.ModuleType('models.yolo');sys.modules[yolo.__name__]=yolo
yolo.__dict__.update(torch=torch,nn=nn,check_version=lambda *a,**k:True)
for module,name,wanted in [(common,'common.py',{'Conv','Bottleneck','C3','SPPF','Concat'}),(yolo,'yolo.py',{'Model','Detect'})]:
 source=root/'crosswalk-source/models'/name
 tree=ast.parse(source.read_text(encoding='utf-8'))
 nodes=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name in wanted]
 assert len(nodes)==len(wanted)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),module.__dict__)
allowed=[getattr(common,n) for n in ['Conv','Bottleneck','C3','SPPF','Concat']]+[yolo.Model,yolo.Detect,nn.Upsample,nn.BatchNorm2d,nn.Sequential,nn.ModuleList,nn.SiLU,nn.Conv2d,nn.MaxPool2d]
with torch.serialization.safe_globals(allowed):ckpt=torch.load(source_root/'crosswalk-best.pt',map_location='cpu',weights_only=True)
model=ckpt['model'].float().eval()
assert model.names==['Zebra_Cross','R_Signal','G_Signal'],model.names
for m in model.modules():
 if isinstance(m,yolo.Detect):m.inplace=False
class Wrapper(nn.Module):
 def __init__(self):super().__init__();self.model=model
 def forward(self,x):return self.model(x)[0]
wrapped=Wrapper().eval();x=torch.zeros(1,3,320,320)
with torch.no_grad():reference=wrapped(x).numpy()
print('classes',model.names,'output',reference.shape,flush=True)
torch.onnx.export(wrapped,x,str(args.output),input_names=['images'],output_names=['output0'],opset_version=12,dynamo=False,external_data=False)
m=onnx.load(args.output);onnx.checker.check_model(m)
assert all(n.domain in ('','ai.onnx') for n in m.graph.node)
onnx.helper.set_model_props(m,{'names':json.dumps(model.names),'source':'kairess/crosswalk-traffic-light-detection-yolov5@5ba1e01d946e1a5cc9dcf396b3b8fc62ae2666d5','source_sha256':'7eb9e22c31e6eef68dce2cfd656fa27614e21203371cdf9255d942c86e29f127','preprocess':'RGB,320x320,letterbox,114,divide255','license':'GPL-3.0'})
onnx.save(m,args.output)
opts=ort.SessionOptions();opts.intra_op_num_threads=2
session=ort.InferenceSession(str(args.output),sess_options=opts,providers=['CPUExecutionProvider'])
actual=session.run(None,{'images':x.numpy()})[0]
np.testing.assert_allclose(actual,reference,rtol=.001,atol=.01)
print('ORT parity on blank input passed; smoke only, not accuracy validation.')
print('SHA256',hashlib.sha256((args.output).read_bytes()).hexdigest())

print('Fixed 320 input; output [1,6375,8]. No deployment accuracy claim.')
temporary.cleanup()
