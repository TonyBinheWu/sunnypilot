"""Opt-in recording quota. Only known recordings, never follows symlinks.

The existing emergency free-space policy stays independent of this quota.
"""
from dataclasses import dataclass
import json
import errno
import os
from pathlib import Path
import re
import shutil
import time

SETTINGS = Path('/data/carrot/state/web_settings.json')
STATUS = Path('/data/carrot/state/recording_quota_status.json')
SCREEN_ROOTS = tuple(Path('/data/media/0') / name for name in ('videos', 'screenrecord', 'screen_recordings', 'screenrecords', 'ScreenRecords'))
SCREEN_NAME = re.compile(r'^\d{8}-\d{6}(?:[-_][\w-]+)?\.(?:mp4|mkv|avi|mov|ts|hevc)$', re.I)
SEGMENT_NAME = re.compile(r'^.+--\d+$')
ROUTE_FILES = {'rlog', 'rlog.zst', 'qlog', 'qlog.zst', 'fcamera.hevc', 'ecamera.hevc', 'dcamera.hevc', 'qcamera.ts'}


@dataclass
class Recording:
  root: Path
  paths: list[Path]
  device: int
  size: int
  newest: float
  protected: bool


def preserved(path):
  try:
    return os.getxattr(path, 'user.preserve') == b'1'
  except AttributeError:
    return False
  except OSError as error:
    if error.errno in (errno.ENODATA, errno.ENOTSUP, errno.EOPNOTSUPP):
      return False
    raise


def open_files(proc=Path('/proc')):
  """Protect ffmpeg/logger handles, including stalled recordings older than the grace period."""
  result = set()
  for process in proc.iterdir():
    if not process.name.isdigit():
      continue
    try:
      if os.geteuid() != 0 and process.stat().st_uid != os.geteuid():
        continue
      for fd in (process / 'fd').iterdir():
        try:
          st = fd.stat()
          result.add((st.st_dev, st.st_ino))
        except PermissionError:
          raise
        except OSError:
          pass  # descriptor closed while taking this snapshot
    except OSError:
      if process.exists():
        # AGNOS recordings are written by these native processes. Fail closed
        # if a writer is opaque. Unrelated non-dumpable helpers (e.g. sd-pam)
        # must not disable the entire quota for an unprivileged device user.
        name = (process / 'comm').read_text().strip()
        if name in {'ffmpeg', 'loggerd', 'encoderd', 'loggerd.cc', 'encoderd.cc'}:
          raise
  return result


def inspect(path, opened, now, grace=120):
  """All descendants must be ordinary entries. A marker protects the complete route."""
  size, newest, protected = 0, 0., False
  paths = [path]
  if path.is_dir():
    paths += list(path.rglob('*'))
  for entry in paths:
    if entry.is_symlink():
      raise ValueError('recording contains a symlink')
    st = entry.stat()
    newest = max(newest, st.st_mtime)
    protected |= preserved(entry) or entry.name.endswith(('.lock', '.preserve')) or entry.name in {'.preserve', '.protected'}
    protected |= (st.st_dev, st.st_ino) in opened
    protected |= getattr(os, 'geteuid', lambda: 0)() != 0 and st.st_uid != os.geteuid()
    if entry.is_file():
      if st.st_nlink != 1:  # do not account/delete aliases of another file
        protected = True
      size += st.st_size
    elif not entry.is_dir():
      raise ValueError('recording contains a non-regular entry')
  return size, newest, protected or newest > now - grace


def inventory(log_root, screen_roots, opened, now):
  groups = {}
  root = Path(log_root).resolve(strict=True)
  for entry in root.iterdir():
    if entry.is_symlink() or not entry.is_dir() or not SEGMENT_NAME.fullmatch(entry.name):
      continue
    if not any((entry / name).is_file() for name in ROUTE_FILES) and not any(p.name.endswith('.lock') for p in entry.iterdir()):
      continue
    size, newest, protect = inspect(entry, opened, now)
    dev = entry.stat().st_dev
    key = (dev, str(root), entry.name.rsplit('--', 1)[0])
    if key not in groups:
      groups[key] = Recording(root, [], dev, 0, 0., False)
    group = groups[key]
    group.paths.append(entry)
    group.size += size
    group.newest = max(group.newest, newest)
    group.protected |= protect
  seen = {root}
  for candidate in screen_roots:
    folder = Path(candidate)
    if not folder.exists():
      continue
    if folder.is_symlink():
      continue
    folder = folder.resolve(strict=True)
    if folder in seen or root in folder.parents:
      continue
    seen.add(folder)
    for entry in folder.iterdir():
      if entry.is_symlink() or not entry.is_file() or not SCREEN_NAME.fullmatch(entry.name):
        continue
      size, newest, protect = inspect(entry, opened, now)
      protect |= preserved(folder) or (folder / '.lock').exists() or (folder / '.preserve').exists() or (folder / '.protected').exists()
      protect |= (folder / (entry.name + '.lock')).exists() or (folder / (entry.name + '.preserve')).exists()
      dev = entry.stat().st_dev
      groups[(dev, str(folder), entry.name)] = Recording(folder, [entry], dev, size, newest, protect)
  return list(groups.values())


def enforce_quota(log_root, screen_roots, percent, *, now=None, opened=None, capacity=None, max_deletes=4):
  """Shared budget per filesystem; oldest complete route or recording first."""
  if type(percent) is not int or percent not in range(10, 100, 10):
    return {'enabled': False, 'groups': [], 'deleted': 0}
  now = time.time() if now is None else now
  live_handles = opened is None
  opened = open_files() if live_handles else opened
  items = inventory(log_root, screen_roots, opened, now)
  devices = {}
  for item in items:
    state = devices.setdefault(item.device, {'usedBytes': 0, 'totalBytes': (capacity(item.root) if capacity else shutil.disk_usage(item.root).total), 'items': []})
    state['usedBytes'] += item.size
    state['items'].append(item)
  deleted = 0
  reports = []
  for dev, state in devices.items():
    total, used = state['totalBytes'], state['usedBytes']
    if not isinstance(total, (int, float)) or total <= 0:
      raise ValueError('invalid filesystem capacity')
    limit = total * percent / 100
    if used >= limit:
      target = total * max(0, percent - 2) / 100
      for item in sorted(state['items'], key=lambda row: row.newest):
        if used <= target or deleted >= max_deletes:
          break
        if item.protected:
          continue
        # Recheck every member before deleting any member. Never delete outside
        # its fixed recording root, an active/changed recording or a linked tree.
        safe = True
        fresh = open_files() if live_handles else opened
        for path in item.paths:
          if path.parent != item.root or path.resolve() != path or not path.exists():
            safe = False
            break
          size, modified, protected = inspect(path, fresh, now)
          if protected or modified > item.newest:
            safe = False
            break
          if path.is_file() and ((path.parent / (path.name + '.lock')).exists() or (path.parent / (path.name + '.preserve')).exists()):
            safe = False
            break
        if not safe:
          continue
        for path in item.paths:
          if path.is_dir():
            shutil.rmtree(path)
          else:
            path.unlink()
        used -= item.size
        deleted += 1
    reports.append({'device': dev, 'totalBytes': total, 'recordingBytes': used,
                    'usedPercent': round(100 * used / total, 2) if total else None,
                    'overQuota': used >= limit, 'protectedRecordings': sum(i.protected for i in state['items'])})
  return {'enabled': True, 'percent': percent, 'groups': reports, 'deleted': deleted, 'updatedAt': now}


class QuotaRunner:
  def __init__(self):
    self.next_run = 0.

  def tick(self, log_root):
    if time.monotonic() < self.next_run:
      return
    self.next_run = time.monotonic() + 30
    try:
      settings = json.loads(SETTINGS.read_text())
      if not isinstance(settings, dict):
        return
      percent = int(settings.get('recording_quota_percent', '0'))
    except (OSError, ValueError, TypeError):
      return
    try:
      result = enforce_quota(log_root, SCREEN_ROOTS, percent)
    except Exception as error:
      result = {'enabled': percent > 0, 'error': 'scan_failed', 'updatedAt': time.time()}
      from openpilot.common.swaglog import cloudlog
      cloudlog.warning(f'recording quota skipped: {type(error).__name__}')
    try:
      STATUS.parent.mkdir(parents=True, exist_ok=True)
      temp = STATUS.with_suffix('.tmp')
      temp.write_text(json.dumps(result))
      temp.replace(STATUS)
    except OSError:
      pass
