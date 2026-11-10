"""Independent signed HTTPS settings channel. No executable remote actions."""
import json
import logging
import math
import os
import threading
import time
from pathlib import Path

from openpilot.sunnypilot.formosalink.identity import read
from openpilot.sunnypilot.formosalink.protocol import canonical, sign
from openpilot.sunnypilot.formosalink.management_protocol import COMMAND_TTL, MAX_MANAGEMENT_BYTES


class ManagementClient:
  def __init__(self, identity, private, provider, directory):
    self.identity, self.private, self.provider = identity, private, provider
    self.path = Path(directory) / "setting-receipts.json"
    self.receipts = []
    try:
      saved = json.loads(self.path.read_text())
      if isinstance(saved,list) and len(saved)<=32:
        self.receipts = saved
    except (OSError, ValueError):
      pass
    self.catalog_revision = None

  def persist(self):
    temporary = self.path.with_suffix(".tmp")
    descriptor = os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(descriptor,"wb") as output:
      output.write(canonical(self.receipts))
      output.flush()
      os.fsync(output.fileno())
    os.replace(temporary,self.path)

  def once(self, session):
    snapshot = self.provider.capture()
    snapshot["receipts"] = self.receipts
    catalog_revision = snapshot["catalog_revision"]
    if self.catalog_revision == catalog_revision:
      snapshot["catalog"] = None
    started = time.monotonic()
    response = session.post(self.identity["origin"]+"/api/v1/agent/sync",
                            json=sign(self.private,self.identity["device_id"],"sync",snapshot),timeout=10,stream=True)
    try:
      response.raise_for_status()
      raw = bytearray()
      for chunk in response.iter_content(8192):
        raw.extend(chunk)
        if len(raw)>MAX_MANAGEMENT_BYTES:
          raise ValueError("oversized settings response")
      result = json.loads(raw)
    finally:
      response.close()
    if not isinstance(result,dict) or set(result)!={"server_time","command","acknowledged","needs_catalog"}:
      raise ValueError("invalid settings response")
    self.catalog_revision = None if result["needs_catalog"] else catalog_revision
    self.receipts = [x for x in self.receipts if x["id"] not in result["acknowledged"]]
    command = result["command"]
    if command:
      if not isinstance(command,dict) or any(type(value) not in (int,float) or not math.isfinite(value) for value in (result["server_time"],command.get("expires_at"),command.get("created_at"))):
        raise ValueError("invalid command")
      remaining = command["expires_at"]-result["server_time"]
      if not 0 < remaining <= COMMAND_TTL or command["expires_at"]-command["created_at"]>COMMAND_TTL:
        raise ValueError("invalid command expiry")
      existing = next((x for x in self.receipts if x["id"]==command["id"]),None)
      if not existing:
        if len(self.receipts)>=32:
          raise ValueError("receipt journal full")
        # Persist a rejection before I/O: a crash can never replay the write.
        receipt = {"id":command["id"],"status":"rejected","reason":"write_failed"}
        self.receipts.append(receipt)
        self.persist()
        self.receipts[-1] = self.provider.apply(command,self.identity["device_id"],started+remaining)
    self.persist()


def run_management(directory, stop):
  import requests
  from openpilot.sunnypilot.formosalink.device_settings import NativeSettingsProvider
  provider = None
  while not stop.is_set():
    try:
      identity, private, _ = read(directory)
      if provider is None:
        provider = NativeSettingsProvider()
      client = ManagementClient(identity,private,provider,directory)
      with requests.Session() as session:
        while not stop.is_set():
          client.once(session)
          stop.wait(5)
    except Exception as exc:
      logging.getLogger("formosalink").info("Settings sync unavailable (%s)",type(exc).__name__)
      stop.wait(10)


def start_management(directory, stop):
  thread = threading.Thread(target=run_management,args=(directory,stop),name="formosalink-settings",daemon=True)
  thread.start()
  return thread
