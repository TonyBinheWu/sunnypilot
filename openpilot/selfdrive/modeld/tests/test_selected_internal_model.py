from pathlib import Path

from openpilot.common import internal_models as models


def test_selection_takes_effect_only_after_boot_and_verified_compile(tmp_path, monkeypatch):
  monkeypatch.setenv('CARROT_BIG_MODEL_DIR', str(tmp_path))
  key = 'rebel'
  boot = ['one']
  monkeypatch.setattr(models.library, 'boot_id', lambda: boot[0])
  monkeypatch.setattr(models, 'verify', lambda path, oid: path.is_file())
  models.prepare_boot()
  models.directory().mkdir(exist_ok=True)
  models.artifact(key, '.onnx').write_bytes(b'graph')
  models.select(key, lambda: True)
  assert models.pending() == key and models.active() == 'cd210'
  boot[0] = 'two'
  def compile_model(command, *, cwd, check, env):
    assert command[-1] == 'sunny_internal_model' and env['SUNNY_COMPILE_INTERNAL'] == key and check
    artifact = models.artifact(key, '.pkl')
    Path(str(artifact) + '.chunkmanifest').write_text('2')
    Path(str(artifact) + '.chunk01of02').write_bytes(b'compiled')
    Path(str(artifact) + '.chunk02of02').touch()
  monkeypatch.setattr(models.subprocess, 'run', compile_model)
  models.prepare_boot()
  assert models.active() == key
  boot[0] = 'three'
  models.artifact(key, '.onnx').unlink()
  models.prepare_boot()
  assert models.active() == 'cd210' and models.state()['failed']


def test_onroad_download_cannot_change_boot_preference(tmp_path, monkeypatch):
  import pytest
  monkeypatch.setenv('CARROT_BIG_MODEL_DIR', str(tmp_path))
  with pytest.raises(ValueError):
    models.select('mrlv2', lambda: False)
  assert models.pending() == 'cd210'
