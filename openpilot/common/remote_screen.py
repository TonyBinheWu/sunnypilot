"""A locally armed, single-client socket owned by the native UI on Linux."""
import hmac
import json
import math
import os
import secrets
import socket
import struct
import time

ADDRESS = bytes([0]) + b"carrot-device-screen-v1"
MAX_FRAME = 1024*1024


class ScreenSession:
  def __init__(self, parked, address=ADDRESS, *, continue_paired=None):
    self.parked, self.address = parked, address
    self.continue_paired = continue_paired or parked
    self.epoch = 0
    self.listener = self.peer = None
    self.auth = self.down = self.cancel = False
    self.pin = ""
    self.output = b""
    self.input = bytearray()
    self.attempts = 0

  def arm(self):
    if self.listener or not self.parked():
      return
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
      listener.bind(self.address)
      listener.listen(1)
      listener.setblocking(False)
    except OSError:
      listener.close()
      return
    self.listener = listener
    self.pin = f"{secrets.randbelow(1_000_000):06d}"
    self.expires = time.monotonic()+90
    self.attempts = 0

  def close_peer(self):
    if self.peer:
      self.peer.close()
    self.peer = None
    self.input.clear()
    self.output = b""
    self.cancel |= self.down
    self.down = self.auth = False

  def close(self):
    self.close_peer()
    if self.listener:
      self.listener.close()
    self.listener, self.pin = None, ""

  def tick(self, physical=False):
    events = []
    now = time.monotonic()
    if self.listener and (physical or now >= self.expires or not (self.continue_paired() if self.auth else self.parked())):
      self.close()
    if self.cancel:
      events.append(("cancel", -1., -1.))
      self.cancel = False
    if not self.listener:
      return events
    try:
      if not self.peer:
        self.peer, _ = self.listener.accept()
        self.peer.setblocking(False)
        if hasattr(socket, "SO_PEERCRED"):
          _, uid, _ = struct.unpack("3i", self.peer.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
          if uid != os.geteuid():
            self.close_peer()
            return events
        self.last_rx = now
      if now - self.last_rx > (4 if self.auth else 3):
        self.close() if self.auth else self.close_peer()
        return events
      if self.down and now-self.last_touch > 2:
        self.down = False
        events.append(("cancel", -1., -1.))
      if self.output:
        self.output = self.output[self.peer.send(self.output):]
      data = self.peer.recv(2048)
      if not data:
        self.close() if self.auth else self.close_peer()
        return events
      self.input.extend(data)
      if len(self.input) > 4096:
        raise ValueError("oversize input")
      while b"\n" in self.input:
        line, _, rest = self.input.partition(b"\n")
        self.input = bytearray(rest)
        msg = json.loads(line)
        if not isinstance(msg, dict):
          raise ValueError("invalid input")
        if not self.auth:
          pin = msg.get("pin")
          self.attempts += 1
          if not isinstance(pin, str) or not pin.isascii() or not hmac.compare_digest(pin, self.pin):
            self.close() if self.attempts >= 5 else self.close_peer()
            return events
          self.auth, self.pin = True, ""
          self.expires, self.last_frame = now + 4*3600, 0.
          self.output = b"OK\n"
        elif msg.get("type") in ("down", "up", "move", "cancel"):
          if type(msg.get("epoch")) is not int or msg["epoch"] != self.epoch:
            continue
          action = msg["type"]
          x, y = msg.get("x"), msg.get("y")
          if not all(type(n) in (int,float) and math.isfinite(n) and 0 <= n <= 1 for n in (x,y)):
            raise ValueError("invalid coordinates")
          if (action == "down") == self.down:
            continue
          self.last_touch = now
          self.down = action in ("down","move")
          events.append((action, x, y))
        elif msg.get("type") != "ping":
          raise ValueError("invalid event")
        self.last_rx = now
    except BlockingIOError:
      pass
    except (OSError, ValueError, UnicodeError, RecursionError):
      self.close() if self.auth else self.close_peer()
    return events if self.auth else [e for e in events if e[0]=="cancel"]

  def wants_frame(self):
    return self.auth and not self.output and time.monotonic()-self.last_frame >= .2

  def frame(self, image):
    if self.auth and 0 < len(image) <= MAX_FRAME-4:
      self.output = struct.pack(">II", len(image)+4, self.epoch) + image
      self.last_frame = time.monotonic()
