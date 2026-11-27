"""Decode the checked, unlinked numerical PROGRAMs for the two-image encoder."""

import gzip
import hashlib
import json
from pathlib import Path
import struct

from tinygrad import Device, dtypes
from tinygrad.codegen import to_program_cache, to_program_config, to_program_key
from tinygrad.codegen.opt import Opt, OptOps
from tinygrad.dtype import AddrSpace, ConstFloat, DType, Invalid
from tinygrad.helpers import Target
from tinygrad.renderer import Estimates
from tinygrad.uop.ops import AxisType, KernelInfo, Ops, ParamArg, ProgramInfo, UOp

from ..frozen import ASSETS, TINYGRAD_REVISION, checked

ASSET = Path(__file__).with_name('gfx1200.json.gz')
PROGRAMS = 38
SHA256 = '28a0d728b515818771a98bd19d52a55a6ebc33995d18af364d37f110f2b35003'
TARGET = Target('AMD', 'LLVM', 'gfx1200', 'USB')
CLASSES = {c.__name__: c for c in (Opt, Estimates, Target, KernelInfo, ParamArg, ProgramInfo)}
ENUMS = {c.__name__: c for c in (Ops, AxisType, AddrSpace, OptOps)}
DTYPES = {d.name: d for d in (*dtypes.all, *dtypes.weaks, *(v for v in vars(type(dtypes)).values() if isinstance(v, DType)))}


def require(condition, message):
  if not condition:
    raise ValueError(message)


class PairPrograms:
  def __init__(self, renderer):
    require(Device.DEFAULT == 'AMD' and renderer.target == TARGET, 'Vision pair requires USB+AMD:LLVM:gfx1200')
    plan = json.loads(gzip.decompress(checked(ASSET, SHA256)))
    require(plan['pin'] == TINYGRAD_REVISION and plan['target'] == str(TARGET), 'Vision pair compiler pin or target differs')
    checked(ASSETS / 'manifest.json', plan['manifest_sha'])
    require(plan['config'] == {v.key: v.value for v in to_program_config}, 'Vision pair compiler configuration differs')
    self.renderer, self.table = renderer, plan['table']
    nodes, binaries = [], {k: bytes.fromhex(v) for k, v in plan['blobs'].items()}
    require(all(b.startswith(b'\x7fELF') and hashlib.sha256(b).hexdigest() == k for k, b in binaries.items()), 'Invalid vision binary')

    def value(v):
      if not isinstance(v, dict):
        return v
      if 'node' in v:
        return nodes[v['node']]
      if 'dtype' in v:
        return DTYPES[v['dtype']]
      if 'enum' in v:
        name, member = v['enum']
        return ENUMS[name][member]
      if 'tuple' in v:
        return tuple(value(i) for i in v['tuple'])
      if 'float64' in v:
        f = struct.unpack('>d', bytes.fromhex(v['float64']))[0]
        return ConstFloat(f) if v['const'] else f
      if v == {'invalid': True}:
        return Invalid
      if 'class' in v:
        obj = CLASSES[v['class']](**{k: value(i) for k, i in v['fields'].items()})
        require(not isinstance(obj, ParamArg) or (obj.buffer is None and not obj.bind_on_realize), 'Storage in frozen vision program')
        return obj
      raise ValueError('Unknown vision program field')

    for name, sources, argument in plan['nodes']:
      op = Ops[name]
      require(op not in (Ops.GETADDR, Ops.PYLITERAL), 'Address or Python literal in vision program')
      arg = binaries[argument['blob']] if op is Ops.BINARY else value(argument)
      require(op is not Ops.BUFFER or arg.addrspace in (AddrSpace.LOCAL, AddrSpace.REG), 'Runtime buffer in vision program')
      nodes.append(UOp(op, src=tuple(nodes[i] for i in sources), arg=arg))
    self.programs = {k: nodes[i] for k, i in plan['programs'].items()}
    require(len(self.programs) == PROGRAMS and set(self.table.values()) == set(self.programs), 'Incomplete vision pair programs')
    for key, p in self.programs.items():
      require(
        p.op is Ops.PROGRAM and isinstance(p.arg, ProgramInfo) and p.arg.target == TARGET and p.key.hex() == key,
        'Vision PROGRAM or ABI identity differs',
      )

  def __call__(self, linear):
    calls = []
    for c in linear.src:
      require(c.op is Ops.CALL, 'Unexpected vision operation')
      if isinstance(c.body.arg, ProgramInfo):
        require(c.body.key.hex() in self.programs, 'Unknown compiled vision layer')
      else:
        key = self.table.get(c.body.key.hex())
        require(key is not None, 'Vision operation differs from frozen recipe')
        program = self.programs[key]
        prior = to_program_cache.get(to_program_key(c.body, self.renderer))
        require(prior is None or prior.key == program.key, 'Existing compiled vision operation differs')
        c = c.replace(src=(program, *c.src[1:]))
      calls.append(c)
    return UOp(Ops.LINEAR, src=tuple(calls))
