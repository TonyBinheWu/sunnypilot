import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from openpilot.system.manager import boot_prebuilt as boot


def commit(root, *paths):
  boot.git(root, 'add', '--', *paths)
  boot.git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.org', 'commit', '-qm', 'fixture')


@pytest.fixture
def released(tmp_path, monkeypatch):
  root = tmp_path / 'builder'
  root.mkdir()
  boot.git(root, 'init', '-q')
  (root / '.gitignore').write_text(boot.RECEIPT + '\n' + boot.REPAIR + '\n')
  (root / 'source').write_bytes(b'input')
  commit(root, '.gitignore', 'source')
  files = set(boot.REQUIRED)
  for m in ('driving', 'dmonitoring_model'):
    files.update(boot.MODELS + m + '_tinygrad.pkl' + s for s in ('.chunk01of02', '.chunk02of02'))
  for name in files:
    dest = root / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    content = b'2' if name.endswith('chunkmanifest') else name.encode()
    if name.endswith('02of02'):
      content = b''  # a valid final padding chunk
    if name.endswith('.json'):
      content = json.dumps({'openpilot.selfdrive.modeld.modeld': {'default': {'WARP_DEV': 'QCOM'}}}).encode()
    dest.write_bytes(content)
    dest.chmod(0o644 if '.' in dest.name else 0o755)
  targets = tmp_path / 'targets'
  targets.write_text('\n'.join(files))
  monkeypatch.setattr(boot, 'identity', lambda p: {'source': boot.source_tree(p), 'os': 'fixture'})
  boot.record(root, targets, publish=True)
  commit(root, boot.BUNDLE)
  device = tmp_path / 'device'
  subprocess.run(['git', 'clone', '-q', str(root), str(device)], check=True)
  return device


def test_offline_install_then_same_boot_without_rereading_models(released, monkeypatch):
  root = released
  boot.prepare(root)
  camera = root / 'openpilot/system/camerad/camerad'
  assert camera.stat().st_mode & 0o111
  assert (root / (boot.MODELS + 'driving_tinygrad.pkl.chunk02of02')).read_bytes() == b''
  monkeypatch.setattr(boot, 'digest', lambda _p: pytest.fail('unchanged file rehashed'))
  boot.prepare(root)
  # An inactive staged checkout can be atomically renamed into service.
  active = root.rename(root.parent / 'active')
  boot.prepare(active)


@pytest.mark.parametrize('fault', ['missing', 'corrupt', 'permissions'])
def test_changed_output_requests_native_repair(released, fault):
  root = released
  boot.prepare(root)
  name = boot.MODELS + 'driving_tinygrad.pkl.chunk01of02'
  p = root / name
  if fault == 'missing':
    p.unlink()
  elif fault == 'corrupt':
    s = p.stat()
    p.write_bytes(b'x' * s.st_size)
    os.utime(p, ns=(s.st_atime_ns, s.st_mtime_ns))
  else:
    p.chmod(0o600)
  with pytest.raises(ValueError, match='rebuilding'):
    boot.prepare(root)
  assert (root / boot.REPAIR).read_text().splitlines() == [name]


def test_new_source_without_matching_release_builds_once(released, tmp_path):
  root = released
  boot.prepare(root)
  files = boot.read_json(root / boot.RECEIPT)['files']
  (root / 'source').write_text('next revision')
  commit(root, 'source')
  with pytest.raises(ValueError, match='does not match'):
    boot.prepare(root)
  targets = tmp_path / 'new-build-targets'
  targets.write_text('\n'.join(files))
  boot.record(root, targets)
  boot.prepare(root)


def test_release_preserves_versioned_assets_regenerated_by_scons(released, tmp_path):
  root = released
  boot.prepare(root)
  files = set(boot.read_json(root / boot.RECEIPT)['files'])
  name = 'openpilot/selfdrive/assets/fonts/Pretendard-Medium.fnt'
  font = root / name
  font.parent.mkdir(parents=True, exist_ok=True)
  font.write_text('versioned')
  commit(root, name)
  font.write_text('locally generated')
  targets = tmp_path / 'targets-with-generated-data'
  targets.write_text('\n'.join(files | {name}))
  boot.record(root, targets, publish=True)
  assert name not in boot.read_json(root / boot.BUNDLE / 'manifest.json')['files']
  assert name in boot.read_json(root / boot.RECEIPT)['files']
  assert font.read_text() == 'locally generated'


@pytest.mark.parametrize('fault', ['bad-blob', 'wrong-hardware', 'new-header', 'edited-source', 'symlink'])
def test_rejects_unverified_build_before_recording(released, monkeypatch, fault):
  root = released
  if fault == 'bad-blob':
    manifest = boot.read_json(root / boot.BUNDLE / 'manifest.json')
    blob = root / boot.BUNDLE / (manifest['files']['openpilot/system/camerad/camerad'][0] + '.gz')
    blob.write_bytes(gzip.compress(b'bad'))
    commit(root, boot.BUNDLE)
  elif fault == 'wrong-hardware':
    monkeypatch.setattr(boot, 'identity', lambda p: {'source': boot.source_tree(p), 'os': 'different'})
  elif fault == 'new-header':
    (root / 'new.h').write_text('new')
  elif fault == 'edited-source':
    (root / 'source').write_text('edited')
  else:
    (root / 'openpilot').symlink_to(root.parent, target_is_directory=True)
  with pytest.raises((ValueError, subprocess.CalledProcessError)):
    boot.prepare(root)
  assert not (root / boot.RECEIPT).exists()


def test_scons_inventory_and_repair_exercise_up_to_date_multi_target_actions(tmp_path):
  scons = shutil.which('scons')
  assert scons
  repo = Path(boot.__file__).resolve().parents[3]
  script = (repo / 'SConstruct').read_text()
  progress = script[script.index('# progress output'):script.index('# ********** Cython')]
  repair = script[script.index('if repair_path :='):]
  (tmp_path / 'SConstruct').write_text('import os, sys\nfrom pathlib import Path\n' + progress + """
def generate(target, source, env):
  for t in target:
    Path(str(t)).write_text('built')
Command(['openpilot/one', 'openpilot/two'], 'input', generate)
""" + repair)
  (tmp_path / 'input').write_text('source')
  inventory = tmp_path / 'targets.txt'
  env = dict(os.environ, CARROT_BUILD_TARGETS=str(inventory))
  for _ in range(2):
    subprocess.run([scons, '-Q'], cwd=tmp_path, env=env, check=True, capture_output=True)
    assert set(inventory.read_text().splitlines()) == {'openpilot/one', 'openpilot/two'}
  (tmp_path / 'openpilot/two').write_text('damaged')
  repair_file = tmp_path / 'repair'
  repair_file.write_text('openpilot/two\n')
  subprocess.run([scons, '-Q'], cwd=tmp_path, env=dict(env, CARROT_BUILD_REPAIR=str(repair_file)), check=True)
  assert (tmp_path / 'openpilot/two').read_text() == 'built'
