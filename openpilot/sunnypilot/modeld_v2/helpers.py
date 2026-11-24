"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import bisect
import builtins
import dataclasses
import io
import itertools
import json
import math
import mmap
import pickle
import re
import struct

MAGIC = b"SPTGPLN1"
ALIGNMENT = 256
METADATA_TYPES = ("slice", "tuple", "list", "dict", "set", "frozenset", "complex")
RUNTIME_ENVIRONMENT = ("GMMU", "AMD_AQL", "AMD_DISABLE_SDMA", "GRAPH_ONE_KERNEL")


def _patch_system_flock_acquire():
  try:
    from tinygrad.runtime.support.system import System
    original_flock_acquire = System.flock_acquire
    acquired_locks: dict[str, int] = {}

    def flock_acquire(name: str) -> int:
      if name in acquired_locks:
        return acquired_locks[name]
      lock_file_descriptor = original_flock_acquire(name)
      acquired_locks[name] = lock_file_descriptor
      return lock_file_descriptor
    System.flock_acquire = flock_acquire
  except (ImportError, AttributeError):
    pass
_patch_system_flock_acquire()


def patch_fetch_fw() -> None:
  try:
    import zstandard
  except ImportError:
    return
  zstandard.decompress = lambda data, *_: zstandard.ZstdDecompressor().stream_reader(data).read()  # ty: ignore[invalid-assignment]


class ArtifactMismatch(RuntimeError):
  pass


class _MetadataUnpickler(pickle.Unpickler):
  def find_class(self, module, name):
    if module == "builtins" and name in METADATA_TYPES:
      return getattr(builtins, name)
    raise pickle.UnpicklingError(f"{module}.{name} is not allowed in model metadata")


def flatten(value) -> list:
  if isinstance(value, (tuple, list)):
    return [tensor for item in value for tensor in flatten(item)]
  return [] if value is None else [value]


def read_parts(path: str) -> tuple[dict, dict]:
  with open(path, "rb") as file:
    data = memoryview(mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_COPY))
  if bytes(data[:len(MAGIC)]) != MAGIC:
    raise ValueError(f"{path} is not a plain tinygrad model, recompile it with compile_modeld.py")
  start = len(MAGIC) + 8 + struct.unpack_from("<Q", data, len(MAGIC))[0]
  header, blob = json.loads(bytes(data[len(MAGIC) + 8:start])), data[start + -start % ALIGNMENT:]
  parts = {tuple(e["key"]) if isinstance(e["key"], list) else e["key"]: (e["header"], blob[slice(*e["blob"])]) for e in header["parts"]}
  return parts, _MetadataUnpickler(io.BytesIO(bytes(blob[slice(*header["extras"])]))).load()


def load_model(path: str, device_map: dict | None = None, verify: bool = True, extend=None) -> dict:
  parts, extras = read_parts(path)
  if extend is not None:
    parts.update(extend(parts, extras))
  shared: dict = {}
  return extras | {key: PlainJit(header, blob, device_map, verify, shared) for key, (header, blob) in parts.items()}


def _dtype(text: str):
  from tinygrad.dtype import DType, dtypes
  match = re.fullmatch(r'dtypes\.([a-z][a-z0-9]*)(?:\.vec\(([1-9][0-9]*)\))?', text)
  dtype = getattr(dtypes, match[1], None) if match else None
  if not isinstance(dtype, DType):
    raise ValueError(f'Unknown tinygrad dtype {text!r}')
  return dtype.vec(int(match[2])) if match[2] else dtype


def _device(recorded: str, device_map: dict | None) -> str:
  from tinygrad import Device
  device_map = device_map or {}
  return Device.canonicalize(device_map.get(recorded, device_map.get(recorded.split(":", 1)[0], recorded)))


def _upload(buffer, data: memoryview, chunk: int = 16 << 20) -> None:
  from tinygrad.device import Buffer
  source, chunk = Buffer("NPY", len(data), opaque=memoryview(bytearray(data)) if data.readonly else data), min(chunk, len(data))
  for offset in sorted({*range(0, len(data) - chunk, chunk), len(data) - chunk}):
    buffer.view(chunk, offset).ensure_allocated().copy_from(source.view(chunk, offset).ensure_allocated())


def _allocate_buffers(header: dict, blob: memoryview, device_map: dict | None, shared: dict) -> list:
  import numpy as np
  from tinygrad.device import Buffer
  written = {call["args"][i]["buffer"] for call in header["calls"] for i in (call["outs"] if call["kind"] == "program" else (0,))
             if "buffer" in call["args"][i]}
  entries = [(_device(entry["device"], device_map), blob[slice(*entry["init"])] if "init" in entry else None, entry) for entry in header["buffers"]]
  keys = [(device, entry["dtype"], np.frombuffer(data, np.uint8).ctypes.data, len(data)) if data and index not in written else object()
          for index, (device, data, entry) in enumerate(entries)]
  for device in {key[0] for key in keys if isinstance(key, tuple) and key not in shared}:
    if shared.setdefault(("mapped", device), Buffer(device, 1).ensure_allocated().get_storage().host is not None):
      continue
    spans = [(entry["init"], entry["nbytes"], key) for (_, _, entry), key in zip(entries, keys, strict=True)
             if isinstance(key, tuple) and key[0] == device and key not in shared]
    files = getattr(blob, "starts", [0])  # a part read from several files (frame_fusion's) is uploaded a block per file
    for _, group in itertools.groupby(sorted(spans, key=lambda span: span[0][0]), key=lambda span: bisect.bisect_right(files, span[0][0])):
      group = list(group)
      start, end = min(span[0] for span, _, _ in group), max(span[1] for span, _, _ in group)
      _upload(block := Buffer(device, end - start).ensure_allocated(), blob[start:end])
      shared |= {key: block.view(nbytes, span[0] - start).ensure_allocated() for span, nbytes, key in group}
  buffers = []
  for (device, data, entry), key in zip(entries, keys, strict=True):
    if key not in shared:
      shared[key] = Buffer(device, entry["nbytes"], initial_value=pickle.PickleBuffer(data) if data else None).ensure_allocated()
    buffers.append(shared[key])
  return buffers


def _fields(what, /, **values):  # a tinygrad dataclass built or replaced with the fields it has today: a dropped field is fine, a new required one is not
  known = {field.name for field in dataclasses.fields(what)}
  values = {name: value for name, value in values.items() if name in known}
  return what(**values) if isinstance(what, type) else dataclasses.replace(what, **values)


def _program_uop(call: dict, lib: bytes):
  from tinygrad.helpers import Target
  from tinygrad.uop.ops import KernelInfo, Ops, ProgramInfo, UOp
  parameters = []
  for name, compact_slot, dtype, shape in call["signature"]:
    parameter = UOp.param(call["globals"][compact_slot], _dtype(dtype), math.prod(shape))
    image = (shape[0], shape[1]) if len(shape) == 3 and shape[2] == 4 else None
    parameters.append(parameter.replace(arg=_fields(parameter.arg, name=name, image=image)))
  info = _fields(ProgramInfo, global_size=tuple(call["global_size"]), local_size=tuple(call["local_size"]), params=tuple(parameters),
                 globals=tuple(call["globals"]), outs=tuple(call["outs"]), ins=tuple(call["ins"]), target=_fields(Target, **call["target"]))
  return UOp(Ops.PROGRAM, src=(UOp(Ops.SINK, arg=KernelInfo(name=call["name"])), UOp(Ops.LINEAR, src=tuple(parameters)),
                               UOp(Ops.SOURCE, arg=""), UOp(Ops.BINARY, arg=lib)), arg=info)


def _input_tensors(kwargs: dict) -> list:  # in _prepare_jit_inputs' order
  from tinygrad import Tensor
  tensors = [t for _, t in sorted(kwargs.items()) if t.__class__ is Tensor]
  for value in kwargs.values():
    tensors += [t for t in (value.values() if isinstance(value, dict) else value if isinstance(value, (tuple, list)) else ())
                if t.__class__ is Tensor and not any(t is y for y in tensors)]
  return tensors


class _Jit:
  def __init__(self, captured, input_names: list, buffers: list):
    self.captured, self.input_names, self.buffers = captured, input_names, buffers

  def __call__(self, *args, **kwargs):
    import tinygrad.engine.jit as jit
    from tinygrad.uop.ops import Ops
    # same names, no variables: the binding is the tensors' own uops, without _prepare_jit_inputs' graph rewrites
    if not args and self.__dict__.get("_names") == sorted(kwargs):
      tensors = _input_tensors(kwargs)
      if all(t.uop.is_realized for t in tensors):
        return self.captured([t.uop.src[0] if t.uop.op is Ops.UNSHARD else t.uop for t in tensors], {})
    input_uops, var_vals, names, _ = jit._prepare_jit_inputs(args, kwargs)
    if names != self.input_names:
      raise ValueError(f"expected inputs {self.input_names}, got {names}")
    if not args and not var_vals:
      self._names = sorted(kwargs)
    return self.captured(input_uops, var_vals)


class PlainJit(_Jit):
  def __init__(self, header: dict, blob: memoryview, device_map: dict | None = None, verify: bool = True, shared: dict | None = None):
    import numpy as np
    import tinygrad.engine.jit as jit
    from tinygrad import Tensor
    from tinygrad.device import Buffer
    from tinygrad.dtype import dtypes
    from tinygrad.uop.ops import Ops, UOp

    inputs = {spec["slot"]: spec for spec in header["inputs"]}
    buffers = _allocate_buffers(header, blob, device_map, {} if shared is None else shared)
    bases = [UOp.from_buffer(buffer, _dtype(entry["dtype"])) for buffer, entry in zip(buffers, header["buffers"], strict=True)]

    def argument(described: dict):
      if "input" in described:
        spec = inputs[described["input"]]
        return UOp.param(described["input"], _dtype(spec["dtype"]), spec["numel"], _device(spec["device"], device_map))
      base, dtype, offset, nbytes = bases[described["buffer"]], _dtype(described["dtype"]), described["offset"], described["nbytes"]
      if offset == 0 and nbytes == header["buffers"][described["buffer"]]["nbytes"] and dtype == base.dtype:
        return base
      return (base if base.dtype.itemsize == 1 else base.bitcast(dtypes.uint8)).shrink(((offset, offset + nbytes),)).bitcast(dtype)

    calls = []
    for call in header["calls"]:
      arguments = [argument(described) for described in call["args"]]
      if call["kind"] == "program":
        calls.append(_program_uop(call, bytes(blob[slice(*call["lib"])])).call(*arguments))
      else:
        calls.append(arguments[0].store_call(arguments[1]))
    # allocate gpu buffers
    stand_ins = {slot: UOp.from_buffer(Buffer(_device(spec["device"], device_map), spec["numel"] * _dtype(spec["dtype"]).itemsize).ensure_allocated(),
                                       _dtype(spec["dtype"])) for slot, spec in inputs.items()}
    input_uops = tuple(stand_ins.get(slot, next(iter(stand_ins.values()), None)) for slot in range(max(stand_ins, default=-1) + 1))
    linear = jit.compile_linear(UOp(Ops.LINEAR, src=tuple(calls)), beam=0, input_uops=input_uops, cache=False)

    returned = [Tensor(argument(t)).reshape(tuple(t["shape"])) for t in header["returns"]["tensors"]]
    ret = {"NoneType": None, "Tensor": returned[0] if returned else None, "tuple": tuple(returned), "list": returned}[header["returns"]["kind"]]
    super().__init__(jit.CapturedJit(ret, linear, header["input_names"], []), header["input_names"], buffers)

    if not verify or not (check := header.get("check")):
      return
    def array(stored):
      return np.frombuffer(blob[slice(*stored["data"])], dtype=np.dtype(stored["dtype"])).reshape(stored["shape"]).copy()
    kwargs: dict = {}
    for path, stored, device in check["inputs"]:
      tensor = Tensor(array(stored), device=_device(device, device_map)).realize()
      kwargs[path[0]] = tensor if len(path) == 1 else {**kwargs.get(path[0], {}), path[1]: tensor}
    result = self(**kwargs)
    outputs = kwargs[check["output_container"]].values() if check["output_container"] else flatten(result)
    for index, (got, stored) in enumerate(zip([t.numpy() for t in outputs], check["outputs"], strict=True)):
      expected = array(stored)
      if got.shape != expected.shape or not np.allclose(got, expected, rtol=1e-3, atol=1e-3, equal_nan=True):
        raise ArtifactMismatch(f"output {index} differs from the compile-time reference frame; recompile the model")
