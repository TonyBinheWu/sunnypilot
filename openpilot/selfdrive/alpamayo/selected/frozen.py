"""Exact gfx1200 GPU objects. No HIP compiler or executable deserialization."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path

ASSETS = Path(__file__).with_name('assets')
TINYGRAD_REVISION = '89846dcfb383a98ee01cfec3bba440ae7dcf9b1e'


def checked(path, digest):
  data = path.read_bytes()
  if hashlib.sha256(data).hexdigest() != digest:
    raise ValueError(f'Kernel asset hash mismatch: {path.name}')
  return data


@lru_cache(None)
def manifest():
  value = json.loads((ASSETS/'manifest.json').read_text())
  if value['tinygrad_revision'] != TINYGRAD_REVISION or value['target'] != 'gfx1200' or len(value['objects']) != 48:
    raise ValueError('Unsupported selected kernel manifest')
  return value


@lru_cache(None)
def object_pair(kind, args):
  records = [r for r in manifest()['objects'] if r['kind'] == kind and tuple(r['args']) == tuple(args)]
  if len(records) != 1:
    raise ValueError(f'No exact frozen kernel for {kind} {args}')
  record = records[0]
  stem = ASSETS/'gfx1200'/record['source_sha256']
  source = checked(stem.with_suffix('.cpp'), record['source_sha256']).decode()
  binary = checked(stem.with_suffix('.hsaco'), record['binary_sha256'])
  if len(binary) != record['bytes'] or binary[:4] != b'\x7fELF':
    raise ValueError('Invalid frozen GPU object')
  return source, binary


def verify_assets():
  for record in manifest()['objects']:
    object_pair(record['kind'], tuple(record['args']))
  checked(ASSETS/'coc_vocab.json', manifest()['vocabulary_sha256'])


def program(sink, kind, args):
  from tinygrad.uop.ops import Ops, UOp
  text, binary = object_pair(kind, tuple(args))
  return UOp(Ops.PROGRAM, src=(sink, UOp(Ops.LINEAR, src=tuple(sink.toposort())),
                              UOp(Ops.SOURCE, arg=text), UOp(Ops.BINARY, arg=binary)))
