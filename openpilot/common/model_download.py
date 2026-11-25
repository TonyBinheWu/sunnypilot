"""Report actual per-file transfer progress to optional model-selector clients."""
import hashlib


def notify(progress, phase, name, received=0, total=None):
  if progress is not None:
    progress(phase, name, received, total)


def copy_download(src, dst, offroad, limit, name, progress, size=None):
  if size is None:
    header = str(src.headers.get('Content-Length', ''))
    if header.isascii() and header.isdecimal() and len(header) <= 15 and 0 < int(header) <= limit:
      size = int(header)
  hasher = hashlib.sha256()
  received = 0
  notify(progress, 'downloading', name, received, size)
  while block := src.read(1 << 20):
    if not offroad() or received + len(block) > limit:
      raise ValueError('Model download interrupted')
    dst.write(block)
    hasher.update(block)
    received += len(block)
    notify(progress, 'downloading', name, received, size)
  if size is not None and received != size:
    raise ValueError('Incomplete model download')
  notify(progress, 'verifying', name, received, size)
  return hasher.hexdigest()
