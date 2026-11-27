"""Checked selected weight loading; no conversion or training jobs."""
import hashlib
import json
import os
import queue
import threading
from functools import lru_cache
from pathlib import Path
import numpy as np
from tinygrad import Device, Tensor, dtypes
from tinygrad.device import Buffer
from tinygrad.nn.state import safe_load
from tinygrad.uop.ops import KernelInfo, Ops, UOp
from .amd_gemm import pack, unpack
from .frozen import ASSETS, checked, manifest
from .transport import upload


_LEAF = 4096
_LANES = 64


@lru_cache(maxsize=1)
def _hash_kernel():
  stem = ASSETS/'gfx1200/weight_sha256'
  source = checked(stem.with_suffix('.cpp'), '32ae4eb358f9093bdc756e6787d148bc6440ce63438df71b6576a3862a35f354')
  binary = checked(stem.with_suffix('.hsaco'), '5122be76107cff16c3e3f5821079400cbd516e7e378a8813f5278e36fd4c4518')
  return source.decode(), binary


def _hash_program(out, data, nonce):
  source, binary = _hash_kernel()
  groups, leftover = divmod(data.numel()*4, _LEAF*_LANES)
  if (not groups or leftover or out.dtype != data.dtype or data.dtype != nonce.dtype or data.dtype != dtypes.uint32
      or out.numel() != groups*_LANES*8 or nonce.numel() != 4):
    raise ValueError('Invalid weight digest kernel buffers')
  sink = UOp.sink(out[0].store(data[0].load() ^ nonce[0].load()), UOp.special(groups, 'gidx0'),
                  UOp.special(_LANES, 'lidx0'), arg=KernelInfo(name='weight_sha256'))
  return UOp(Ops.PROGRAM, src=(sink, UOp(Ops.LINEAR, src=tuple(sink.toposort())),
                               UOp(Ops.SOURCE, arg=source), UOp(Ops.BINARY, arg=binary)))


_ZERO_NONCE = bytes(16)


def leaf_proofs(directory, index):
  """Per-leaf SHA-256 (leaf || 16 zero bytes) of weights.bin, built once by a pass that also checks the file digest.

  Startup then needs no CPU hashing: the GPU recomputes each proof from the uploaded bytes and compares them itself.
  """
  directory = Path(directory)
  weights, path, meta = directory/'weights.bin', directory/'leaf-proofs.bin', directory/'leaf-proofs.json'
  stat = weights.stat()
  identity = {'weights_sha256': index['sha256'], 'nbytes': index['nbytes'], 'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns,
              'leaf': _LEAF, 'nonce': 'zero16'}
  if path.exists() and meta.exists():
    recorded = json.loads(meta.read_text())
    if {k: recorded.get(k) for k in identity} == identity:
      data = path.read_bytes()
      if hashlib.sha256(data).hexdigest() == recorded['proofs_sha256']:
        return data
  digest, proofs = hashlib.sha256(), bytearray()
  with weights.open('rb') as source:
    while chunk := source.read(16*1024*1024):
      digest.update(chunk)
      view = memoryview(chunk)
      for i in range(0, len(chunk)-len(chunk)%_LEAF, _LEAF):
        proofs += hashlib.sha256(view[i:i+_LEAF].tobytes()+_ZERO_NONCE).digest()
  if digest.hexdigest() != index['sha256'] or stat.st_size != index['nbytes']:
    raise ValueError('FP8 weight content differs')
  data = bytes(proofs)
  for target, content in ((path, data), (meta, json.dumps(dict(identity, proofs_sha256=hashlib.sha256(data).hexdigest())).encode())):
    temporary = target.with_suffix('.tmp')
    temporary.write_bytes(content)
    os.replace(temporary, target)
  return data


def _verify_storage(storage, nbytes, proofs, tail):
  """Recompute every leaf proof on the GPU, compare there with the stored proofs, and read back one mismatch count."""
  from .transport import download
  device = storage.device
  if device.split(':')[0] != 'AMD' or Device[device].arch != 'gfx1200':
    raise ValueError('Weight digest kernel requires gfx1200')
  size = nbytes - nbytes%(_LEAF*_LANES)
  count = size//_LEAF*32
  if len(proofs) < count:
    raise ValueError('Stored leaf proofs are incomplete')
  nonce = Tensor(_ZERO_NONCE, device='CPU').bitcast(dtypes.uint32).to(device).realize()
  # Random initial proof contents: a kernel that did not run cannot match the stored proofs.
  out = Tensor(os.urandom(count), device='CPU').bitcast(dtypes.uint32).to(device).contiguous().realize()
  expected = Tensor(proofs[:count], device='CPU').bitcast(dtypes.uint32).to(device).contiguous().realize()
  data = Tensor(UOp.from_buffer(storage.view(size, 0).ensure_allocated(), dtypes.uint32))
  proof = Tensor.custom_kernel(out, data, nonce, fxn=_hash_program)[0]
  mismatches = int(download((proof != expected).cast(dtypes.int32).sum().reshape(1)).item())
  if mismatches:
    raise ValueError(f'GPU weight upload digest differs in {mismatches} proof words')
  if size < nbytes and storage.view(nbytes-size, size).ensure_allocated().as_memoryview() != tail:
    raise ValueError(f'GPU weight upload tail differs at offset {size}')


def _upload_bulk(source, nbytes, proofs):
  if nbytes <= 0 or os.fstat(source.fileno()).st_size != nbytes:
    raise ValueError('FP8 weight size differs')
  storage = Buffer(Device.DEFAULT, nbytes).ensure_allocated()
  # Large transfers reach ~330 MB/s over USB 3; verification runs once on the GPU after the last chunk.
  # A reader thread fills one staging buffer from disk while the other is uploaded.
  chunk = min(64*1024*1024, nbytes)
  free, filled = queue.Queue(), queue.Queue()
  for _ in range(2):
    free.put(memoryview(bytearray(chunk)))
  def reader():
    try:
      while True:
        staging = free.get()
        count = source.readinto(staging)
        filled.put((staging, count))
        if not count:
          return
    except BaseException as error:  # noqa: BLE001 - surfaced on the uploading thread
      filled.put((error, 0))
  threading.Thread(target=reader, name='weight-reader', daemon=True).start()
  offset = 0
  while True:
    staging, count = filled.get()
    if isinstance(staging, BaseException):
      raise staging
    if not count:
      break
    if offset + count > nbytes:
      raise ValueError('FP8 weight size differs')
    storage.view(count, offset).ensure_allocated().copy_from(Buffer('NPY', count, opaque=staging[:count]))
    Device[storage.device].synchronize()  # the staging memory returns to the reader
    free.put(staging)
    offset += count
  if offset != nbytes:
    raise ValueError('FP8 weight size differs')
  Device[storage.device].synchronize()
  source.seek(nbytes - nbytes%(_LEAF*_LANES))
  _verify_storage(storage, nbytes, proofs, source.read())
  return storage


def load_bulk(model, checkpoint, directory):
  checkpoint, directory = Path(checkpoint), Path(directory)
  index = json.loads((directory/'index.json').read_text())
  if index['format'] != 1:
    raise ValueError('Unsupported FP8 weight format')
  name = 'vlm.model.language_model.layers.0.mlp.fc1.weight'
  shard = json.loads((checkpoint/'model.safetensors.index.json').read_text())['weight_map'][name]
  value = upload(safe_load(checkpoint/shard)[name], dtypes.bfloat16)
  scale = (value.float().abs().max()/448).clamp(min_=1e-12).realize()
  value = (value.float()/scale).clamp(-448,448).cast(dtypes.fp8e4m3).realize()
  value = pack(value).realize()
  with (directory/'weights.bin').open('rb') as source:
    for kind, tensor in [('scale', scale), ('fp8', value)]:
      record = next(r for r in index['records'] if r['name'] == name and r['kind'] == kind)
      source.seek(record['offset'])
      if tensor.reshape(-1).bitcast(dtypes.uint8).numpy().tobytes() != source.read(record['nbytes']):
        raise ValueError(f'Target FP8 conversion/packing differs: {kind}')
  del value, scale
  proofs = leaf_proofs(directory, index)
  with (directory/'weights.bin').open('rb') as source:
    storage = _upload_bulk(source, index['nbytes'], proofs)
  for record in index['records']:
    kind = record['kind']
    dtype = {'scale':dtypes.float32,'fp8':dtypes.fp8e4m3,'bf16':dtypes.bfloat16}[kind]
    view = storage.view(record['nbytes'],record['offset']).ensure_allocated()
    value = Tensor(UOp.from_buffer(view,dtype)).reshape(record['shape'])
    if record['packed']:
      value = unpack(value)
    (model.weight_scales if kind == 'scale' else model.weights)[record['name']] = value
  model._bulk_storage = storage
  return index['sha256']


HASH_MULTIPLIER = 2654435761


def _word_hash(halves):
  """sum(word[i] * (i*HASH_MULTIPLIER+1)) mod 2^32 over little-endian 32-bit words of 16-bit values (zero-padded)."""
  words = np.concatenate([halves, np.zeros(len(halves)%2, np.uint16)]).view(np.uint32).astype(np.uint64)
  weights = (np.arange(len(words), dtype=np.uint64)*HASH_MULTIPLIER+1) & 0xffffffff
  return int((words*weights).sum(dtype=np.uint64) & 0xffffffff)


def _word_hash_gpu(value):
  halves = value.reshape(-1).bitcast(dtypes.uint16)
  if halves.numel() % 2:
    halves = halves.pad(((0,1),))
  words = halves.bitcast(dtypes.uint32)
  assert value.device == Device.DEFAULT  # arange builds on the default device
  weights = Tensor.arange(words.numel(), dtype=dtypes.uint32)*HASH_MULTIPLIER+1
  return (words*weights).sum(dtype=dtypes.uint32)


def restore_bf16(model, checkpoint):
  prefixes = ['vlm.model.visual.embeddings.patch_embedding.',
              'vlm.model.visual.encoder.layers.0.', 'vlm.model.visual.encoder.layers.1.',
              'expert.action_in_proj.', 'expert.action_out_proj.']
  names = sorted(name for name in model.weight_scales if name.startswith(tuple(prefixes)))
  if not names:
    raise ValueError('Missing mixed-precision restoration tensors')
  index = json.loads((Path(checkpoint)/'model.safetensors.index.json').read_text())['weight_map']
  shards, expected, restored = {}, [], []
  for name in names:
    shard = index[name]
    if shard not in shards:
      shards[shard] = safe_load(Path(checkpoint)/shard)
    source = shards[shard][name]
    assert source.dtype == dtypes.bfloat16 and source.shape == model.weights[name].shape
    value = upload(source,dtypes.bfloat16)
    expected.append(_word_hash(np.frombuffer(source.bitcast(dtypes.uint8).numpy().tobytes(),dtype=np.uint16)))
    restored.append(value)
    model.weights[name] = value
    del model.weight_scales[name]
  # One readback for all tensors: the position-weighted word hash is recomputed on the GPU from the uploaded bytes.
  from .transport import download
  got = download(Tensor.stack(*[_word_hash_gpu(v) for v in restored]).bitcast(dtypes.int32)).view(np.uint32).tolist()
  if got != expected:
    bad = [n for n,a,b in zip(names,got,expected) if a != b]
    raise ValueError(f'BF16 restoration differs: {bad[:4]}')
  return names


def reduce_head(model):
  raw = checked(ASSETS/'coc_vocab.json',manifest()['vocabulary_sha256'])
  vocab = sorted(set(json.loads(raw)))
  config = model.config
  def allowed(i):
    return (not config['traj_ids']['history_id0'] <= i < config['traj_ids']['history_id0']+config['history_vocab_size']
            and not config['traj_ids']['future_id0'] <= i < config['traj_ids']['future_id0']+config['future_vocab_size']
            and i != config['vlm_config']['text_config']['eos_token_id'])
  vocab = [i for i in vocab if allowed(i)]
  assert config['traj_ids']['future_start'] in vocab
  assert vocab and min(vocab) >= 0 and max(vocab) < model.weights['vlm.lm_head.weight'].shape[0]
  padded = vocab+[vocab[-1]]*((-len(vocab))%64)
  model.output_token_mapping = Tensor(padded,dtype=dtypes.int32).realize()
  model.weights['vlm.lm_head.weight'] = model.weights['vlm.lm_head.weight'][model.output_token_mapping].contiguous().realize()
  return len(vocab)
