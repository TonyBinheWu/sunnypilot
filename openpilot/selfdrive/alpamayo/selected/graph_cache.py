"""Persist captured TinyJit graphs so restarts skip graph scheduling.

A capture records the compiled command linear (after code generation and command building, before linking). Each buffer
is stored as an owner: a named persistent runtime buffer, a JIT output, fresh scratch or host command memory, or a small
constant. Loading rebinds the owners to the live runtime; linking on the first call resolves the addresses. Entries are keyed by graph name,
the selected sources, the checkpoint and the compiler; any mismatch or unresolved owner falls back to a normal capture.
"""
import hashlib
import io
import os
import pickle
import sys
import time
from pathlib import Path

from tinygrad import Tensor
import tinygrad.engine.jit as tinyjit
import tinygrad.engine.realize as realize
from tinygrad.engine.jit import CapturedJit, TinyJit, _TinyJit, _prepare_jit_inputs
from tinygrad.uop.ops import Ops, UOp

SCHEMA = 2
CONSTANT_LIMIT = 1 << 20  # unnamed held buffers above this size must be registered runtime state
_ROOTS: dict = {}
_DIRECTORY: Path | None = None
_KEY = ''
STATS = {'loaded': 0, 'captured': 0, 'failed': 0, 'load_ms': 0.0}


def configure(directory, roots, key_parts):
  """Enable the cache. `roots` name the objects whose Tensor attributes own persistent buffers."""
  global _DIRECTORY, _ROOTS, _KEY
  _DIRECTORY, _ROOTS = Path(directory), dict(roots)
  _DIRECTORY.mkdir(parents=True, exist_ok=True)
  digest = hashlib.sha256()
  for part in key_parts:
    digest.update(repr(part).encode())
  # Graph construction code: the selected runtime package plus the shared model and attention modules.
  sources = Path(__file__).resolve().parents[1]
  for path in sorted([*sources.joinpath('selected').rglob('*.py'), sources/'model.py', sources/'amd_attention.py']):
    digest.update(str(path.relative_to(sources)).encode())
    digest.update(path.read_bytes())
  _KEY = digest.hexdigest()[:24]
  for stale in _DIRECTORY.glob('*.pkl'):  # entries from other sources, checkpoints or compilers never load again
    if not stale.stem.endswith(_KEY):
      stale.unlink(missing_ok=True)


def _path(name):
  stem = name if len(name) <= 80 and name.replace('-', '').replace('_', '').isalnum() else hashlib.sha256(name.encode()).hexdigest()[:32]
  return _DIRECTORY / f'{stem}-{_KEY}.pkl'


def disable():
  global _DIRECTORY
  _DIRECTORY = None


def _walk(obj, path, out, seen, depth):
  if id(obj) in seen or depth > 6:
    return
  seen.add(id(obj))
  if isinstance(obj, Tensor):
    base = obj.uop.base
    if base.op is Ops.BUFFER and base not in out:
      out[base] = path
    return
  if isinstance(obj, dict):
    for k, v in list(obj.items()):
      if isinstance(k, (str, int, tuple)):
        _walk(v, path + (('item', k),), out, seen, depth + 1)
  elif isinstance(obj, (list, tuple)):
    for i, v in enumerate(obj):
      _walk(v, path + (('item', i),), out, seen, depth + 1)
  elif hasattr(obj, '__dict__') and type(obj).__module__.startswith(('openpilot.selfdrive.alpamayo', 'alpamayo')):
    for k, v in list(vars(obj).items()):
      _walk(v, path + (('attr', k),), out, seen, depth + 1)


def _registry():
  out, seen = {}, set()
  for name, root in _ROOTS.items():
    _walk(root, (('root', name),), out, seen, 0)
  return out


def _resolve(path):
  obj = None
  for kind, key in path:
    obj = _ROOTS[key] if kind == 'root' else getattr(obj, key) if kind == 'attr' else obj[key]
  if not isinstance(obj, Tensor) or obj.uop.base.op is not Ops.BUFFER:
    raise KeyError('Graph owner is not a buffer: ' + repr(path))
  return obj.uop.base


class _Ref:
  def __init__(self, uop):
    self.uop = uop


def _strip(ret):
  if isinstance(ret, Tensor):
    return _Ref(ret.uop)
  if isinstance(ret, (tuple, list)):
    return type(ret)(_strip(x) for x in ret)
  if ret is None:
    return None
  raise TypeError('Unsupported JIT return for graph cache')


def _dress(ret):
  if isinstance(ret, _Ref):
    return Tensor(ret.uop)
  if isinstance(ret, (tuple, list)):
    return type(ret)(_dress(x) for x in ret)
  return ret


def _ret_buffers(ret, out):
  if isinstance(ret, _Ref):
    base = ret.uop.base
    if base.op is Ops.BUFFER and base not in out:
      out[base] = len(out)
  elif isinstance(ret, (tuple, list)):
    for x in ret:
      _ret_buffers(x, out)
  return out


def _written(programs):
  """Base buffers written by the program calls of a code-generated linear."""
  out = set()
  for call in programs.src:
    c = call.src[0] if call.op is Ops.AFTER else call
    if c.op is Ops.CALL and c.src and c.src[0].op is Ops.PROGRAM:
      for i in c.src[0].arg.outs:
        arg = c.src[1+i]
        out.add(arg.base if arg.op is not Ops.BUFFER else arg)
  return out


def save(name, lowered, ret, names, info, programs=None):
  registry = _registry()
  ret = _strip(ret)
  outputs = _ret_buffers(ret, {})
  if programs is not None:
    written = _written(programs)
    unwritten = [u for u in outputs if u not in registry and u not in written]
    if unwritten:
      # A returned buffer the graph does not write is persistent state; a fresh allocation would lose its contents.
      raise ValueError(f'{len(unwritten)} returned buffer(s) not written by the graph')
  arenas = {u.src[0] for call in lowered.src for u in call.toposort() if u.op is Ops.SHRINK and u.src[0].op is Ops.BUFFER}
  owners = {'path': 0, 'out': 0, 'new': 0, 'data': 0}

  class Pickler(pickle.Pickler):
    def persistent_id(self, obj):
      if type(obj) is not UOp or obj.op is not Ops.BUFFER or getattr(obj.arg, 'buffer', None) is None:
        return None  # kernel-local LDS/register buffers are part of the program
      if obj in registry:
        owners['path'] += 1
        return ('path', registry[obj])
      if obj in outputs:
        owners['out'] += 1
        return ('out', outputs[obj], obj.device, obj.max_numel(), obj.dtype)
      if obj in arenas or obj.device == 'CPU' or not obj.arg.buffer.is_allocated():  # link writes host command memory
        owners['new'] += 1
        return ('new', obj.device, obj.max_numel(), obj.dtype)
      nbytes = obj.max_numel() * obj.dtype.itemsize
      if nbytes > CONSTANT_LIMIT or not isinstance(obj.device, str):
        raise ValueError(f'Unregistered {nbytes} byte buffer in graph {name}')
      owners['data'] += 1
      return ('data', obj.device, obj.max_numel(), obj.dtype, bytes(obj.arg.buffer.as_buffer()))

  data = io.BytesIO()
  Pickler(data, protocol=pickle.HIGHEST_PROTOCOL).dump((SCHEMA, lowered, ret, names, info))
  path = _path(name)
  tmp = path.with_suffix('.tmp')
  tmp.write_bytes(data.getvalue())
  os.replace(tmp, path)
  print(f'graph cache: saved {name} ({len(lowered.src)} calls, {data.tell()/1e6:.1f} MB, owners {owners})', file=sys.stderr, flush=True)


def load(name):
  path = _path(name)
  if not path.exists():
    return None
  outputs = {}

  class Unpickler(pickle.Unpickler):
    def persistent_load(self, pid):
      kind = pid[0]
      if kind == 'path':
        return _resolve(pid[1])
      if kind == 'out':
        if pid[1] not in outputs:
          outputs[pid[1]] = UOp.new_buffer(pid[2], pid[3], pid[4])
        return outputs[pid[1]]
      if kind == 'new':
        return UOp.new_buffer(pid[1], pid[2], pid[3])
      if kind == 'data':
        u = UOp.new_buffer(pid[1], pid[2], pid[3])
        u.buffer.ensure_allocated().copyin(memoryview(bytearray(pid[4])))
        return u
      raise pickle.UnpicklingError('Unknown graph owner')

  schema, lowered, ret, names, info = Unpickler(io.BytesIO(path.read_bytes())).load()
  if schema != SCHEMA:
    return None
  return lowered, _dress(ret), names, info


class CachedJit:
  """TinyJit with a persistent graph. `name` must identify the function and every closure value that shapes the graph."""

  def __init__(self, fxn, name):
    self.fxn, self.name = fxn, name
    self.jit = TinyJit(fxn)
    self.loaded = None
    self.tried = False

  def reset(self):
    self.jit.reset()
    self.loaded = None
    self.tried = False

  def __get__(self, obj, objtype):
    from functools import partial
    return partial(self.__call__, obj)

  def _load(self, args, kwargs):
    started = time.monotonic()
    entry = load(self.name)
    if entry is None:
      return None
    lowered, ret, names, info = entry
    input_uops, var_vals, live_names, live_info = _prepare_jit_inputs(args, kwargs)
    if live_names != names or live_info != info:
      raise ValueError('graph cache input signature differs')
    jit = _TinyJit(None, captured=CapturedJit(ret, lowered, names, info))
    STATS['loaded'] += 1
    STATS['load_ms'] += (time.monotonic()-started)*1e3
    return jit

  def __call__(self, *args, **kwargs):
    if self.loaded is not None:
      return self.loaded(*args, **kwargs)
    if _DIRECTORY is not None and not self.tried and self.jit.cnt in (0, 1):
      self.tried = True
      try:
        self.loaded = self._load(args, kwargs)
      except Exception as exc:  # noqa: BLE001 - any stale or unresolvable entry is recaptured
        STATS['failed'] += 1
        print(f'graph cache: {self.name} not loaded ({type(exc).__name__}: {exc})', file=sys.stderr, flush=True)
        self.loaded = None
      if self.loaded is not None:
        return self.loaded(*args, **kwargs)
    if _DIRECTORY is None or self.jit.cnt != 1:
      return self.jit(*args, **kwargs)
    recorded = []
    def record(linear, beam=None, validate=False, input_uops=None, profile=None, cache=False):
      programs = realize.lower_and_compile(linear)
      compiled = realize.hcq_compile(programs, input_uops, bool(realize.PROFILE or realize.DEBUG >= 2) if profile is None else profile,
                                     cache=cache)
      recorded.append((compiled, programs))
      return compiled
    tinyjit.compile_linear = record
    try:
      ret = self.jit(*args, **kwargs)
    finally:
      tinyjit.compile_linear = realize.compile_linear
    captured = self.jit.captured
    if captured is not None and recorded:
      try:
        compiled, programs = max(recorded, key=lambda r: len(r[1].src))
        save(self.name, compiled, captured.ret, captured.expected_names, captured.expected_input_info, programs)
        STATS['captured'] += 1
      except Exception as exc:  # noqa: BLE001 - an unsupported graph still runs; it just is not persisted
        print(f'graph cache: {self.name} not saved ({type(exc).__name__}: {exc})', file=sys.stderr, flush=True)
    return ret
