import os
import re


MODEL_STAGES = ("USB eGPU model", "USB eGPU big model")
PREPARATION = ("Preparing runtime packages", "Building settings registry", "registering device")
DOWNLOAD = re.compile(r"Downloading( precompiled model)? ([0-9]{1,3})%")


class BootStatus:
  def __init__(self):
    self.context = ""
    self.detail = ""
    self.progress = None

  def update(self, text):
    text = text.strip()
    if not text:
      return
    if text.isascii() and text.isdecimal():
      self.progress = min(100, int((text.lstrip("0") or "0")[:3]))
    elif text in MODEL_STAGES:
      self.context, self.detail, self.progress = text, "", None
    elif match := DOWNLOAD.fullmatch(text):
      self.detail = "Downloading precompiled model" if match[1] else "Downloading model"
      self.progress = min(100, int(match[2]))
    else:
      self.detail = text
      if text in PREPARATION:
        self.context = ""
      if self.context or text in PREPARATION:
        self.progress = None


class StatusInput:
  """Read whole lines from the producer pipe without waiting for a partial line."""
  def __init__(self, fd):
    self.fd = fd
    os.set_blocking(fd, False)
    self.pending = b""
    self.eof = False

  def poll(self, status):
    if self.eof:
      return
    try:
      chunk = os.read(self.fd, 65536)
    except BlockingIOError:
      return
    self.eof = not chunk
    parts = chunk.split(b"\n")
    for part in parts[:-1]:
      status.update((self.pending + part[:2048])[:2048].decode("utf-8", "replace"))
      self.pending = b""
    self.pending = (self.pending + parts[-1][:2048])[:2048]
    if self.eof:
      status.update(self.pending.decode("utf-8", "replace"))
      self.pending = b""


def fit_lines(text, width, measure):
  """At most two lines, keeping the start of long compiler commands visible."""
  lines = []
  rest = " ".join(text.split())
  for i in range(2):
    if not rest or measure(rest) <= width:
      return (*lines, rest) if rest else tuple(lines)
    suffix = "..." if i else ""
    lo, hi = 0, len(rest)
    while lo < hi:
      mid = (lo+hi+1)//2
      if measure(rest[:mid].rstrip()+suffix) <= width:
        lo = mid
      else:
        hi = mid-1
    stop = lo
    if i == 0 and (word := rest.rfind(" ", 0, lo+1)) > 0:
      stop = word
    lines.append(rest[:stop].rstrip()+suffix)
    rest = rest[stop:].lstrip()
  return tuple(lines)
