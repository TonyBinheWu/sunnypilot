import os
from pathlib import Path

from openpilot.system.loggerd.recording_quota import enforce_quota, inventory, QuotaRunner


def old(path, data=b'x'*100, age=1000):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_bytes(data)
  os.utime(path, (age, age))
  os.utime(path.parent, (age, age))
  return path


def test_shared_budget_removes_oldest_complete_route_before_new_screen_recording(tmp_path):
  root=tmp_path/'routes'; root.mkdir()
  screen=tmp_path/'videos';screen.mkdir()
  old(root/'one--0'/'rlog.zst',age=100)
  old(root/'one--1'/'fcamera.hevc',age=110)
  newest=old(screen/'20260101-000000.mp4',age=200)
  result=enforce_quota(root,[screen],20,now=2000,opened=set(),capacity=lambda _:1000)
  assert result['deleted']==1
  assert not (root/'one--0').exists() and not (root/'one--1').exists()
  assert newest.exists()
  assert result['groups'][0]['recordingBytes']==100


def test_active_segment_protects_its_entire_route(tmp_path):
  root=tmp_path/'routes';root.mkdir()
  old(root/'one--0'/'rlog.zst')
  old(root/'one--1'/'rlog.zst')
  old(root/'one--1'/'rlog.lock')
  result=enforce_quota(root,[],10,now=2000,opened=set(),capacity=lambda _:1000)
  assert result['deleted']==0 and result['groups'][0]['overQuota']
  assert (root/'one--0').exists()


def test_recent_writes_open_handles_and_preserve_markers_are_skipped(tmp_path):
  root=tmp_path/'routes';root.mkdir();screen=tmp_path/'videos';screen.mkdir()
  recent=old(screen/'20260101-000000.mp4',age=1990)
  opened=old(screen/'20260101-000001.mp4')
  saved=old(screen/'20260101-000002.mp4')
  old(screen/(saved.name+'.preserve'))
  st=opened.stat()
  result=enforce_quota(root,[screen],10,now=2000,opened={(st.st_dev,st.st_ino)},capacity=lambda _:1000)
  assert result['deleted']==0
  assert all(p.exists() for p in [recent,opened,saved])


def test_imported_video_boot_crash_and_symlink_are_never_quota_candidates(tmp_path):
  root=tmp_path/'routes';root.mkdir();screen=tmp_path/'videos';screen.mkdir()
  old(root/'boot'/'rlog.zst');old(root/'crash'/'rlog.zst')
  personal=old(screen/'family.mp4')
  external=old(tmp_path/'outside.mp4')
  try:
    (screen/'20260101-000000.mp4').symlink_to(external)
  except OSError:
    pass
  result=enforce_quota(root,[screen],10,now=2000,opened=set(),capacity=lambda _:1000)
  assert result['deleted']==0 and personal.exists() and external.exists()
  assert (root/'boot').exists() and (root/'crash').exists()


def test_disabled_or_invalid_quota_performs_no_scan(tmp_path):
  for value in [0,True,-1,101,'10',15]:
    assert enforce_quota(tmp_path/'missing',[],value)['enabled'] is False


def test_cleanup_is_bounded_and_duplicate_roots_do_not_double_count(tmp_path):
  root=tmp_path/'routes';root.mkdir();screen=tmp_path/'videos';screen.mkdir()
  for i in range(5):old(screen/f'20260101-00000{i}.mp4',age=100+i)
  result=enforce_quota(root,[screen,screen],10,now=2000,opened=set(),capacity=lambda _:1000,max_deletes=1)
  assert result['deleted']==1 and result['groups'][0]['recordingBytes']==400
  assert not (screen/'20260101-000000.mp4').exists()


def test_preserved_xattr_protects_complete_route(tmp_path,monkeypatch):
  from openpilot.system.loggerd import recording_quota as module
  root=tmp_path/'routes';root.mkdir()
  saved=old(root/'one--0'/'rlog.zst')
  old(root/'one--1'/'rlog.zst')
  monkeypatch.setattr(module,'preserved',lambda p:p==saved)
  assert enforce_quota(root,[],10,now=2000,opened=set(),capacity=lambda _:1000)['deleted']==0


def test_invalid_status_settings_do_not_crash_original_deleter(tmp_path,monkeypatch):
  from openpilot.system.loggerd import recording_quota as module
  settings=tmp_path/'settings.json';settings.write_text('[]')
  monkeypatch.setattr(module,'SETTINGS',settings)
  QuotaRunner().tick(tmp_path)


def test_changed_recording_is_rechecked_before_deletion(tmp_path,monkeypatch):
  from openpilot.system.loggerd import recording_quota as module
  root=tmp_path/'routes';root.mkdir();file=old(root/'one--0'/'rlog.zst')
  real=module.inventory
  def scanning(*args):
    result=real(*args)
    os.utime(file,(1999,1999))
    return result
  monkeypatch.setattr(module,'inventory',scanning)
  assert enforce_quota(root,[],10,now=2000,opened=set(),capacity=lambda _:1000)['deleted']==0
  assert file.exists()


def test_empty_new_segment_lock_protects_older_segments_of_same_route(tmp_path):
  root=tmp_path/'routes';root.mkdir()
  old(root/'one--0'/'rlog.zst')
  old(root/'one--1'/'logger.lock')
  result=enforce_quota(root,[],10,now=2000,opened=set(),capacity=lambda _:1000)
  assert result['deleted']==0 and (root/'one--0').exists()


def test_link_inside_recording_aborts_scan_without_deleting_any_recording(tmp_path):
  import pytest
  root=tmp_path/'routes';root.mkdir()
  original=old(root/'one--0'/'rlog.zst')
  outside=old(tmp_path/'outside.txt')
  try:
    (original.parent/'linked.txt').symlink_to(outside)
  except OSError:
    pytest.skip('symlinks unavailable on this host')
  with pytest.raises(ValueError,match='symlink'):
    enforce_quota(root,[],10,now=2000,opened=set(),capacity=lambda _:1000)
  assert original.exists() and outside.exists()


def test_opaque_recorders_fail_closed_but_system_helpers_do_not_disable_quota(tmp_path,monkeypatch):
  import pytest
  from openpilot.system.loggerd.recording_quota import open_files
  proc=tmp_path/'proc';process=proc/'123';process.mkdir(parents=True)
  descriptor=process/'fd';descriptor.mkdir()
  comm=process/'comm';comm.write_text('(sd-pam)')
  original=Path.iterdir
  def entries(path):
    if path==descriptor:
      raise PermissionError('opaque process')
    return original(path)
  monkeypatch.setattr(Path,'iterdir',entries)
  assert open_files(proc)==set()
  comm.write_text('ffmpeg')
  with pytest.raises(PermissionError):
    open_files(proc)


def test_real_open_recording_is_retained_even_when_its_mtime_is_old(tmp_path):
  import pytest
  if not Path('/proc/self/fd').exists():
    pytest.skip('requires Linux procfs')
  root=tmp_path/'routes';root.mkdir()
  recording=old(root/'one--0'/'rlog.zst')
  with recording.open('rb'):
    result=enforce_quota(root,[],10,now=2000,capacity=lambda _:1000)
  assert result['deleted']==0 and recording.exists()
