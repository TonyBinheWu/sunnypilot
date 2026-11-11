"""Optional monitoring agent with a separate, device-guarded settings channel."""
import json
import logging
import random
import time

from openpilot.sunnypilot.formosalink.identity import default_directory, read
from openpilot.sunnypilot.formosalink.connection_status import acknowledge
from openpilot.sunnypilot.formosalink.service_policy import self_hosted_origin
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
  self_hosted_origin(identity["origin"])
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
      acknowledge(identity["origin"])
      sequence += 1
      if stop:
        stop.wait(SAMPLE_INTERVAL)
      else:
        time.sleep(SAMPLE_INTERVAL)
  finally:
    ws.close()


def connect_http(identity, private, sampler, stop=None, samples=60):
  self_hosted_origin(identity["origin"])
  import requests
  with requests.Session() as session:
    for sequence in range(samples):
      if stop and stop.is_set():
        return
      snapshot = sampler.sample(sequence)
      envelope = sign(private, identity["device_id"], "telemetry", snapshot)
      response = session.post(identity["origin"] + "/api/v1/agent/telemetry", json=envelope, timeout=15)
      response.raise_for_status()
      if len(response.content) > MAX_FRAME_BYTES or response.json() != {"type": "ack", "sequence": sequence}:
        raise ValueError("unexpected HTTPS acknowledgement")
      acknowledge(identity["origin"])
      if stop:
        stop.wait(SAMPLE_INTERVAL)
      else:
        time.sleep(SAMPLE_INTERVAL)


def run(directory=None, demo=False, stop=None):
  import threading
  from openpilot.sunnypilot.formosalink.management import start_management
  stop = stop or threading.Event()
  directory = directory or default_directory()
  if not demo:
    start_management(directory,stop)
    from openpilot.sunnypilot.formosalink.cameras import start as start_cameras
    start_cameras(directory,stop)
    from openpilot.sunnypilot.formosalink.profile import CARROT
    if CARROT:
      from openpilot.sunnypilot.formosalink.remote_web import start as start_web
      start_web(directory, stop)
  from openpilot.sunnypilot.formosalink.telemetry import DemoSampler, OpenpilotSampler
  sampler = DemoSampler() if demo else OpenpilotSampler()
  failures = 0
  while stop is None or not stop.is_set():
    try:
      identity, private, _ = read(directory or default_directory())
      try:
        connect_once(identity, private, sampler, stop)
      except Exception as exc:
        log.info("FormosaLink WebSocket unavailable (%s); using signed HTTPS telemetry", type(exc).__name__)
        connect_http(identity, private, sampler, stop)
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
