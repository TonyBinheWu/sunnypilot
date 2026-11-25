import numpy as np
import pytest

from openpilot.common import sunny_models as sunny


def test_choices_keep_named_aliases_and_freeze_boot(tmp_path, monkeypatch):
  monkeypatch.setenv('CARROT_BIG_MODEL_DIR', str(tmp_path))
  small = [k for k,v in sunny.catalog().items() if not v['big']]
  big = [k for k,v in sunny.catalog().items() if v['big']]
  assert (len(small), len(big)) == (79,25)
  assert len({v['sha256'] for v in sunny.catalog().values()}) == 101
  sunny.save('small', small[0])
  sunny.save('big', big[-1])
  sunny.freeze_boot()
  sunny.save('small', small[-1])
  sunny.save('assistant', True)
  sunny.freeze_boot()
  assert sunny.key_for(False, True) == small[0] and sunny.key_for(True, True) == big[-1]
  assert sunny.key_for(False) == small[-1] and not sunny.prefs(True).get('assistant')
  with pytest.raises(ValueError):
    sunny.select(False, small[-1], lambda:False)


def test_bad_download_does_not_replace_cache(tmp_path):
  import hashlib
  src, dst = tmp_path/'payload', tmp_path/'cache'
  src.write_bytes(b'new')
  dst.write_bytes(b'old')
  sha = hashlib.sha256(b'new').hexdigest()
  with pytest.raises(ValueError):
    sunny.download(src.as_uri(), '0'*64, dst, lambda:True, 3)
  assert dst.read_bytes() == b'old'
  with pytest.raises(ValueError):
    sunny.download(src.as_uri(), sha, dst, lambda:False, 3)
  sunny.download(src.as_uri(), sha, dst, lambda:True, 3)
  assert dst.read_bytes() == b'new'


@pytest.mark.parametrize('known_size', [True, False])
def test_download_counts_received_chunks_and_verifies_before_publication(tmp_path, monkeypatch, known_size):
  import hashlib
  from io import BytesIO
  payload = b'a' * (1 << 20) + b'end'
  source = BytesIO(payload)
  source.headers = {'Content-Length': str(len(payload))} if known_size else {}
  monkeypatch.setattr(sunny.urllib.request, 'urlopen', lambda *_, **__: source)
  dst = tmp_path/'weights'
  records = []
  def progress(*row):
    assert not dst.exists()
    records.append(row)
  sunny.download('https://example.invalid', hashlib.sha256(payload).hexdigest(), dst, lambda: True, 2 << 20, progress)
  total = len(payload) if known_size else None
  assert [r[2:] for r in records if r[0] == 'downloading'] == [(0, total), (1 << 20, total), (len(payload), total)]
  assert records[-1][:2] == ('verifying', 'weights')
  assert dst.read_bytes() == payload


def test_primary_migrates_previous_role_without_changing_catalog_selections(tmp_path, monkeypatch):
  monkeypatch.setenv('CARROT_BIG_MODEL_DIR', str(tmp_path))
  assert not sunny.internal_primary()
  sunny.save('assistant', True)
  sunny.freeze_boot()
  assert sunny.internal_primary(boot=True)
  sunny.save('primary', 'auto')
  assert not sunny.internal_primary() and sunny.internal_primary(boot=True)
  sunny.save('primary', 'internal')
  assert sunny.internal_primary()


def test_legacy_pedal_and_disengagement_layouts_are_distinct():
  from openpilot.selfdrive.modeld.fill_model_msg import LegacyMeta, Meta
  a=np.arange(55)
  assert a[LegacyMeta.HARD_BRAKE_5].tolist() == [6,13,20,27,34]
  assert a[LegacyMeta.GAS_PRESS].tolist() == [7,14,21,28,35]
  assert not hasattr(LegacyMeta, 'BRAKE_PRESS')
  assert a[Meta.HARD_BRAKE_5].tolist() == [6,12,18,24,30]
