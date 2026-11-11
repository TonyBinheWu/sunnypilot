"""Explicit local-only visual QA fixture. Never included in the IIS runtime package."""
from pathlib import Path

from formosalink.server.store import Store
from openpilot.sunnypilot.formosalink.agent import run
from openpilot.sunnypilot.formosalink.identity import create, read
from openpilot.sunnypilot.formosalink.protocol import fingerprint


def main():
  root = Path("build/formosalink-preview")
  origin = "http://127.0.0.1:8765"
  directory = root / "demo-device"
  try:
    identity, _, public = read(directory)
  except FileNotFoundError:
    identity, _, public = create(directory, origin)
  if identity["origin"] != origin:
    raise SystemExit("visual QA is restricted to loopback")
  store = Store(root / "formosalink.sqlite3")
  result = store.enroll(identity["device_id"], public, fingerprint(public))
  if result["state"] == "pending":
    store.pair(result["pair_code"], result["fingerprint"], "FormosaPilot · 台灣山海")
  run(directory, demo=True)


if __name__ == "__main__":
  main()
