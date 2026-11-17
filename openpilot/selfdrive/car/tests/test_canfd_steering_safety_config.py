"""The actual interface must transmit the selected protocol/AOL authorization."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from openpilot.cereal import car
from opendbc.car.hyundai.values import HyundaiFlags, HyundaiSafetyFlags


@pytest.mark.parametrize('angle',[False,True])
@pytest.mark.parametrize('aol',[0,1,2])
def test_actual_interface_serializes_separate_authorization_flags(angle,aol):
  path=Path('opendbc_repo/opendbc/car/hyundai/interface.py')
  tree=ast.parse(path.read_text(encoding='utf-8'))
  nodes=[n for n in ast.walk(tree) if isinstance(n,ast.If) and
         any(isinstance(x,ast.Attribute) and x.attr in ('CANFD_ALWAYS_LATERAL','CANFD_ANGLE_CONTROL') for x in ast.walk(n))]
  # Select just the two assignments, not their enclosing CAN-FD branch.
  nodes=[n for n in nodes if len(n.body)==1 and isinstance(n.body[0],ast.AugAssign)]
  assert len(nodes)==2
  cp=car.CarParams.new_message(flags=int(HyundaiFlags.CANFD|(HyundaiFlags.ANGLE_CONTROL if angle else 0)))
  cp.safetyConfigs=[{'safetyModel':'hyundaiCanfd','safetyParam':int(HyundaiSafetyFlags.LONG|HyundaiSafetyFlags.CAMERA_SCC)}]
  ns={'ret':cp,'params':NS(get_int=lambda key:aol),'HyundaiFlags':HyundaiFlags,'HyundaiSafetyFlags':HyundaiSafetyFlags}
  exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
  with car.CarParams.from_bytes(cp.to_bytes()) as parsed:
    flags=parsed.safetyConfigs[0].safetyParam
    assert bool(flags & HyundaiSafetyFlags.CANFD_ALWAYS_LATERAL)==(aol>0)
    assert bool(flags & HyundaiSafetyFlags.CANFD_ANGLE_CONTROL)==angle
    assert flags & HyundaiSafetyFlags.LONG and flags & HyundaiSafetyFlags.CAMERA_SCC
