"""Optional telemetry-only agent; intentionally accepts no remote commands."""
import json
import logging
import random
import time

from openpilot.sunnypilot.formosalink.identity import default_directory, read
from openpilot.sunnypilot.formosalink.protocol import MAX_FRAME_BYTES, SAMPLE_INTERVAL, VERSION, canonical, sign

log = logging.getLogger("formosalink")


def send_snapshot(ws, snapshot):
  ws.send(canonical(snapshot).decode())
  raw = ws.recv()
  if not isinstance(raw, str) or len(raw.encode()) > MAX_FRAME_BYTES:
    raise ValueError("invalid acknowledgement")
  ack = json.loads(raw)
  if ack != {"type": "ack", "sequence": snapshot["sequence"]}:
    raise ValueError("unexpected server message; commands are unsupported")


def connect_once(identity, private, sampler, stop=None):
  import websocket
  url = identity["origin"].replace("https://", "wss://", 1).replace("http://", "ws://", 1)
  ws = websocket.create_connection(url + "/api/v1/agent/ws", timeout=15, suppress_origin=True,
                                   enable_multithread=True)
  try:
    ws.send(canonical(sign(private, identity["device_id"], "connect")).decode())
    raw = ws.recv()
    if not isinstance(raw, str) or len(raw.encode()) > MAX_FRAME_BYTES:
      raise ValueError("invalid handshake")
    ready = json.loads(raw)
    if ready != {"type": "ready", "version": VERSION, "sample_interval": SAMPLE_INTERVAL}:
      raise ValueError("unsupported handshake")
    sequence = 0
    while stop is None or not stop.is_set():
      send_snapshot(ws, sampler.sample(sequence))
      sequence += 1
      if stop:
        stop.wait(SAMPLE_INTERVAL)
      else:
        time.sleep(SAMPLE_INTERVAL)
  finally:
    ws.close()


def run(directory=None, demo=False, stop=None):
  from openpilot.sunnypilot.formosalink.telemetry import DemoSampler, OpenpilotSampler
  sampler = DemoSampler() if demo else OpenpilotSampler()
  failures = 0
  while stop is None or not stop.is_set():
    try:
      identity, private, _ = read(directory or default_directory())
      connect_once(identity, private, sampler, stop)
      failures = 0
    except Exception as exc:
      # No credentials, pairing codes, request bodies or private keys in logs.
      log.warning("FormosaLink disconnected (%s); retrying", type(exc).__name__)
      failures = min(failures + 1, 6)
      delay = min(60, 2 ** failures) + random.uniform(0, 2)
      if stop:
        stop.wait(delay)
      else:
        time.sleep(delay)


def main():
  logging.basicConfig(level=logging.INFO)
  run()


if __name__ == "__main__":
  main()
