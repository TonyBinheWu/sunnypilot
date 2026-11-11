import ast
from itertools import product
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import pytest

from openpilot.sunnypilot.formosalink.management_protocol import validate_snapshot
from openpilot.sunnypilot.formosalink.profile import CarrotStatusProvider
from openpilot.sunnypilot.formosalink.stream_encoder import nv12_bytes


def test_remote_web_requires_fresh_parked_device_and_independent_local_consent():
  path=Path('openpilot/sunnypilot/formosalink/remote_web.py')
  tree=ast.parse(path.read_text(encoding='utf-8'))
  cls=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='NativePermission')
  cls.body=[node for node in cls.body if isinstance(node,ast.FunctionDef) and node.name=='__call__']
  namespace={}
  exec(compile(ast.Module(body=[cls],type_ignores=[]),str(path),'exec'),namespace)
  guard=namespace['NativePermission']()
  now=time.monotonic()
  class State(dict):
    def update(self,timeout):pass
  sm=State(deviceState=SimpleNamespace(started=False),pandaStates=[SimpleNamespace(ignitionCan=False,ignitionLine=False)])
  sm.seen=sm.valid={'deviceState':True,'pandaStates':True}
  sm.logMonoTime={'deviceState':int(now*1e9),'pandaStates':int(now*1e9)}
  guard.sm=sm
  for enabled,consent,offroad,started,ignition in product((False,True),repeat=5):
    values={'FormosaLinkEnabled':enabled,'FormosaLinkRemoteWeb':consent,'IsOffroad':offroad}
    guard.params=SimpleNamespace(get_bool=lambda key:values.get(key,False))
    sm['deviceState'].started=started;sm['pandaStates'][0].ignitionLine=ignition
    assert guard() is (enabled and consent and offroad and not started and not ignition)
  values.update(FormosaLinkEnabled=True,FormosaLinkRemoteWeb=True,IsOffroad=True)
  sm['deviceState'].started=False;sm['pandaStates'][0].ignitionLine=False
  assert guard() is True
  sm.logMonoTime['pandaStates']=int((now-10)*1e9)
  assert guard() is False


def test_carrot_driver_enum_and_nv12_padding(monkeypatch):
  from openpilot.sunnypilot.formosalink.cameras import NativeCamera
  calls=[]
  monkeypatch.setitem(sys.modules,'msgq.visionipc',SimpleNamespace(VisionIpcClient=lambda *args:calls.append(args),
                      VisionStreamType=SimpleNamespace(VISION_STREAM_WIDE_ROAD=1,VISION_STREAM_DRIVER=2)))
  NativeCamera('wide-road');NativeCamera('driver')
  assert calls==[('camerad',1,True),('camerad',2,True)]
  # Carrot VisionBuf may expose only stride/height; UV begins after the Y plane.
  frame=SimpleNamespace(width=2,height=2,stride=4,data=bytes([1,2,0,0,3,4,0,0,5,6,0,0]))
  assert nv12_bytes(frame)==bytes([1,2,3,4,5,6])


def test_carrot_health_uses_its_own_schema_without_sunnypilot_settings():
  provider=CarrotStatusProvider.__new__(CarrotStatusProvider)
  class State(dict):
    def update(self,timeout):pass
  sm=State(deviceState=SimpleNamespace(started=False,deviceType='tizi'))
  sm.seen=sm.valid={'deviceState':True}
  sm.logMonoTime={'deviceState':time.monotonic_ns()}
  provider.params=SimpleNamespace(get_bool=lambda key:key=='IsOffroad')
  provider.sm=sm;provider.session='00000000-0000-4000-8000-000000000000'
  snapshot=validate_snapshot(provider.capture())
  assert snapshot['offroad'] and not snapshot['remote_enabled']
  assert snapshot['catalog']==[] and snapshot['info']['device_model']=='tizi'
