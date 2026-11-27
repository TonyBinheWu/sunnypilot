"""Prepare the exact BF16 subset needed alongside the separate selected FP8 weights."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import tempfile

from .frozen import ASSETS

INDEX = 'model.safetensors.index.json'
SHARD = 'selected-bf16.safetensors'


def digest(path):
  with path.open('rb') as f:
    return hashlib.file_digest(f, 'sha256').hexdigest()


def write_compact(source, output, expected):
  if digest(source/INDEX) != expected['checkpoint_weight_index_sha256'] or digest(source/'config.json') != expected['checkpoint_config_sha256']:
    raise ValueError('Require the pinned original checkpoint and configuration')
  weights = json.loads((source/INDEX).read_text())['weight_map']
  # Parity probe, CPU position embedding, and tensors restored to BF16 in the selected recipe.
  names = sorted(n for n in weights if n == 'vlm.model.language_model.layers.0.mlp.fc1.weight' or n.startswith((
    'vlm.model.visual.embeddings.', 'vlm.model.visual.encoder.layers.0.', 'vlm.model.visual.encoder.layers.1.',
    'expert.action_in_proj.', 'expert.action_out_proj.')))
  records = {}
  for name, pinned in expected['checkpoint_shards'].items():
    path = source/name
    if digest(path) != pinned:
      raise ValueError(f'Original checkpoint hash mismatch: {name}')
    with path.open('rb') as f:
      size, = struct.unpack('<Q', f.read(8))
      header = json.loads(f.read(size))
    for n in names:
      if weights[n] == name:
        entry = header[n]; start, end = entry['data_offsets']
        records[n] = (path, 8+size+start, end-start, entry)
  offset, compact = 0, {}
  for n in names:
    _, _, length, entry = records[n]
    compact[n] = dict(dtype=entry['dtype'], shape=entry['shape'], data_offsets=[offset, offset+length]); offset += length
  raw = json.dumps(compact, separators=(',', ':')).encode(); raw += b' '*(-len(raw)%8)
  with (output/SHARD).open('xb') as dest:
    dest.write(struct.pack('<Q', len(raw))); dest.write(raw)
    for n in names:
      path, pos, length, _ = records[n]
      with path.open('rb') as f:
        f.seek(pos); data = f.read(length)
      if len(data) != length:
        raise ValueError(f'Short read: {n}')
      dest.write(data)
  (output/INDEX).write_text(json.dumps({'metadata': {'total_size': offset}, 'weight_map': dict.fromkeys(names, SHARD)}, sort_keys=True, separators=(',', ':'))+'\n')
  for name in ('config.json', 'tokenizer.json', 'tokenizer_config.json', 'processor_config.json', 'chat_template.jinja', 'generation_config.json', 'LICENSE'):
    shutil.copyfile(source/name, output/name)
  return {'index_sha256': digest(output/INDEX), 'shards': {SHARD: digest(output/SHARD)}}


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('source', type=Path); parser.add_argument('output', type=Path); args = parser.parse_args()
  if args.output.exists():
    raise FileExistsError(args.output)
  expected = json.loads((ASSETS/'artifacts.json').read_text())
  with tempfile.TemporaryDirectory(dir=args.output.parent) as tmp:
    package = Path(tmp)/'checkpoint'; package.mkdir()
    if write_compact(args.source, package, expected) != expected['compact_checkpoint']:
      raise ValueError('Compact checkpoint bytes differ from the pinned recipe')
    package.rename(args.output)


if __name__ == '__main__':
  main()
