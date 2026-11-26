import json
import socket
import struct
import time
from unittest.mock import Mock

import pytest

from openpilot.common.remote_screen import ScreenSession


@pytest.fixture
def connection():
  state = [True]
  session = ScreenSession(lambda: state[0])
  session.listener = Mock()
  session.pin = "177436"
  session.last_rx = time.monotonic()
  session.expires = session.last_rx + 60
  session.peer, client = socket.socketpair()
  session.peer.setblocking(False)
  client.settimeout(1)
  yield session, client, state
  session.close()
  client.close()


def message(client, row):
  client.sendall(json.dumps(row).encode()+b"\n")


def pair(s, client):
  message(client, {"pin":s.pin})
  assert not s.tick() and s.auth
  s.tick()
  assert client.recv(3) == b"OK\n"


def test_frames_and_touch_require_local_pairing(connection):
  s, client, state = connection
  assert not s.wants_frame()
  pair(s,client)
  assert s.wants_frame()
  s.frame(b"image")
  s.tick()
  assert client.recv(13) == struct.pack(">II",9,0)+b"image"
  for action in ("down","move","up"):
    message(client,dict(type=action,epoch=0,x=.3,y=.6))
    assert s.tick() == [(action,.3,.6)]
  message(client,dict(type="up",epoch=0,x=.3,y=.6))
  assert s.tick() == []
  message(client,dict(type="down",epoch=0,x=.6,y=.1))
  assert s.tick()
  state[0] = False
  assert s.tick() == [("cancel",-1.,-1.)] and not s.auth and not s.listener


@pytest.mark.parametrize("case",["invalid_pin","peer_close","expired","local_takeover","invalid_position","stale_peer"])
def test_revoke(connection, case):
  s, client, _ = connection
  if case=="invalid_pin":
    message(client,{"pin":"000000"})
    assert not s.tick() and not s.auth and s.attempts==1
    return
  pair(s,client)
  if case=="peer_close": client.close()
  if case=="expired": s.expires=0
  if case=="stale_peer": s.last_rx=0
  if case=="invalid_position": message(client,dict(type="down",epoch=0,x=2,y=0))
  s.tick(physical=case=="local_takeover")
  assert not s.auth and not s.listener


def test_discard_input_from_previous_mode(connection):
  s, client, _ = connection
  pair(s,client)
  s.epoch=5
  for epoch in [0,None,False,4,6]:
    message(client,dict(type="down",epoch=epoch,x=.2,y=.3))
    assert not s.tick() and not s.down
  message(client,dict(type="down",epoch=5,x=.2,y=.3))
  assert s.tick()==[("down",.2,.3)]


def test_empty_capture_notice_keeps_stream_framed_and_paired(connection):
  s, client, _ = connection
  pair(s, client)
  s.frame(b"image")
  s.frame(b"")
  s.tick()
  assert client.recv(13) == struct.pack(">II", 9, 0) + b"image"
  s.epoch = 4
  s.frame(b"")
  s.tick()
  assert client.recv(8) == struct.pack(">II", 4, 4) and s.auth
  s.frame(b"new")
  s.tick()
  assert client.recv(11) == struct.pack(">II", 7, 4) + b"new"
