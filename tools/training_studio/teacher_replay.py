"""Append immutable, label-only simulation replay before a teacher dataset is frozen."""
import hashlib
from pathlib import Path
import shutil

from tools.training_studio.store import read_json,write_json


def append_replay(data,source_manifest):
  import numpy as np
  data,source_manifest=Path(data),Path(source_manifest)
  manifest=read_json(data/'manifest.json');source=read_json(source_manifest)
  if (source_manifest.parent/'not-for-training.json').exists():raise ValueError('reference dataset is quarantined; do not train on its draft labels')
  identity=hashlib.sha256(source_manifest.read_bytes()).hexdigest()
  used=manifest.get('replay_manifest_sha256s',[])
  if identity in used: return 0
  if (not source.get('data_source','').startswith('simulation')
      or source.get('reference_controls_used_only_for_supervision') is not True
      or source.get('ground_truth_given_to_inference') is not False):
    raise ValueError('teacher replay requires label-only simulation provenance')
  additions=[];files=[];seen={(r['sha256'],r['split']) for r in manifest['samples']}
  for row in source['samples']:
    seed,split=row['seed'],row['split']
    if not ((split=='train' and 1000<=seed<7000) or (split=='validation' and 8000<=seed<9500)):
      raise ValueError('teacher replay seed/split leakage')
    relative=Path(row['file'])
    if relative.is_absolute() or '..' in relative.parts or '\\' in row['file']:
      raise ValueError('invalid replay packet path')
    packet=(source_manifest.parent/relative).resolve()
    if not packet.is_relative_to(source_manifest.parent.resolve()): raise ValueError('replay packet escaped its dataset')
    if hashlib.sha256(packet.read_bytes()).hexdigest()!=row['sha256']: raise ValueError('replay packet checksum mismatch')
    with np.load(packet,allow_pickle=False) as item:
      if hashlib.sha256(item['image_frames'].tobytes()).hexdigest()!=row['pixel_sha256']: raise ValueError('replay image checksum mismatch')
      if item['future_xyz'].shape!=(1,64,3) or item['future_rot'].shape!=(1,64,3,3): raise ValueError('invalid replay reference dimensions')
      if not np.isfinite(item['future_xyz']).all() or not np.isfinite(item['future_rot']).all(): raise ValueError('nonfinite replay reference')
    key=(row['sha256'],split)
    if key in seen: continue
    seen.add(key)
    target=Path('replay')/identity[:16]/relative
    additions.append({**row,'file':target.as_posix()});files.append((packet,data/target))
  rows=manifest['samples']+additions
  train={r['seed'] for r in rows if r['split']=='train'};validation={r['seed'] for r in rows if r['split']=='validation'}
  if train&validation: raise ValueError('replay seeds overlap across splits')
  if {r['pixel_sha256'] for r in rows if r['split']=='train'} & {r['pixel_sha256'] for r in rows if r['split']=='validation'}:
    raise ValueError('replay images overlap across splits')
  for source_path,target in files:
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
      if hashlib.sha256(target.read_bytes()).hexdigest()!=hashlib.sha256(source_path.read_bytes()).hexdigest():
        raise ValueError('refusing to overwrite a different replay packet')
    else: shutil.copyfile(source_path,target)
  manifest.update(samples=rows,replay_manifest_sha256s=[*used,identity])
  write_json(data/'manifest.json',manifest)
  return len(additions)
