"""Direct, physically paired ccNC companion on the device's Wi-Fi or Ethernet address."""

from __future__ import annotations
import base64
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import ipaddress
import json
import os
import secrets
import socket
import ssl
import struct
import time
import uuid

PORT = 8787
GRANT = "FormosaLanAccess"
REQUEST = "FormosaLanPairRequest"
INFO = "FormosaLanPairInfo"
NETWORKS = tuple(map(ipaddress.ip_network, ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "169.254.0.0/16")))


def lan_address():
  import fcntl

  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    for name in sorted((n for _, n in socket.if_nameindex()), key=lambda n: not n.startswith(("wl", "ap"))):
      if not name.startswith(("wl", "ap", "eth", "en", "br")):
        continue
      try:
        raw = fcntl.ioctl(sock.fileno(), 0x8915, struct.pack("256s", name.encode()[:15]))
        addr = ipaddress.IPv4Address(raw[20:24])
        if any(addr in net for net in NETWORKS):
          return str(addr)
      except OSError:
        continue
  return None


def atomic_file(path, data):
  tmp = path.with_suffix(".tmp")
  with os.fdopen(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "wb") as f:
    f.write(data)
    f.flush()
    os.fsync(f.fileno())
  os.replace(tmp, path)


def certificate(directory):
  from cryptography import x509
  from cryptography.hazmat.primitives import hashes, serialization
  from cryptography.hazmat.primitives.asymmetric import ec
  from cryptography.x509.oid import NameOID

  directory.mkdir(parents=True, exist_ok=True, mode=0o700)
  path = directory / "local-tls.pem"
  if not path.exists():
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "FormosaLink ccNC")])
    now = datetime.now(UTC)
    cert = (
      x509.CertificateBuilder()
      .subject_name(name)
      .issuer_name(name)
      .public_key(key.public_key())
      .serial_number(x509.random_serial_number())
      .not_valid_before(now - timedelta(days=1))
      .not_valid_after(now + timedelta(days=3650))
      .sign(key, hashes.SHA256())
    )
    atomic_file(
      path,
      cert.public_bytes(serialization.Encoding.PEM)
      + key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()),
    )
  cert = x509.load_pem_x509_certificate(path.read_bytes())
  context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
  context.minimum_version = ssl.TLSVersion.TLSv1_2
  context.load_cert_chain(path)
  return context, cert.fingerprint(hashes.SHA256()).hex()


class LanDevice:
  def __init__(self, directory, params, grant, provider, device_id):
    self.params, self.grant, self.provider, self.device_id = params, grant, provider, device_id
    self.path = directory / "phones.json"
    self.request = self.address = None
    self.code, self.until, self.attempts = "", 0.0, 0
    self.commands = []
    self.cameras = {}
    try:
      stored = json.loads(self.path.read_bytes())
      self.phones = stored["phones"] if stored["grant"] == grant else []
    except (OSError, ValueError, TypeError, KeyError):
      self.phones = []

  def refresh(self, address, pin):
    request = self.params.get(REQUEST)
    if request and (request != self.request or address != self.address):
      self.request, self.address = request, address
      self.code = f"{secrets.randbelow(1_000_000):06}"
      self.until, self.attempts = time.monotonic() + 120, 0
      self.params.put(INFO, {"request": request, "address": address, "pin": pin, "code": self.code, "until": self.until}, block=True)
    now = time.monotonic()
    for name in list(self.cameras):
      if now - self.cameras[name][1] > 5:
        self.cameras.pop(name)[0].close()

  def paired(self, token):
    return bool(
      token
      and len(token) <= 100
      and self.params.get(GRANT) == self.grant
      and any(hmac.compare_digest(hashlib.sha256(token.encode()).hexdigest(), value) for value in self.phones)
    )

  def pair(self, code):
    if self.params.get(GRANT) != self.grant or not self.provider.guard() or not self.code or time.monotonic() >= self.until or self.attempts >= 5:
      return None
    self.attempts += 1
    if not isinstance(code, str) or not hmac.compare_digest(code, self.code):
      return None
    token = secrets.token_urlsafe(32)
    phones = self.phones[-15:] + [hashlib.sha256(token.encode()).hexdigest()]
    atomic_file(self.path, json.dumps({"grant": self.grant, "phones": phones}).encode())
    self.phones, self.code = phones, ""
    self.params.remove(REQUEST)
    self.params.remove(INFO)
    return {"token": token, "device": self.device_id}

  def state(self):
    return {
      "snapshot": self.provider.capture(),
      "commands": self.commands,
      "fresh": True,
      "received_at": datetime.now(UTC).timestamp(),
      "device": self.device_id,
      "product": "FormosaLink-ccnc",
    }

  def submit(self, body):
    if set(body) != {"key", "value", "expected_revision", "session"}:
      raise ValueError("setting_unavailable")
    now = datetime.now(UTC).timestamp()
    command = dict(body, id=str(uuid.uuid4()), device_id=self.device_id, created_at=now, expires_at=now + 10)
    receipt = self.provider.apply(command, self.device_id, time.monotonic() + 10)
    self.commands = ([receipt] + self.commands)[:32]
    return receipt

  def frame(self, camera):
    from openpilot.sunnypilot.formosalink.cameras import NativeCamera, save_lease, lan_lease_path
    from openpilot.sunnypilot.formosalink.stream_encoder import StreamEncoder
    from openpilot.sunnypilot.formosalink.media_protocol import jpeg_size

    save_lease([camera], 6, path=lan_lease_path())
    if camera not in self.cameras:
      from openpilot.sunnypilot.formosalink.road_overlay import RoadOverlay

      source = NativeCamera(camera, encoder=StreamEncoder(), overlay=RoadOverlay() if camera == "wide-road" else None)
      self.cameras[camera] = (source, time.monotonic())
    source, _ = self.cameras[camera]
    self.cameras[camera] = (source, time.monotonic())
    data, timestamp, hud = source()
    width, height = jpeg_size(data)
    return {
      "source": camera,
      "jpeg": base64.b64encode(data).decode(),
      "width": width,
      "height": height,
      "sampled_at": timestamp,
      "hud": hud,
      "sequence": time.monotonic_ns() // 1000,
      "stream": self.device_id,
    }

  def close(self):
    for camera, _ in self.cameras.values():
      camera.close()


class Handler(BaseHTTPRequestHandler):
  def log_message(self, format, *args):  # noqa: A002 - keyword accepted by BaseHTTPRequestHandler
    pass

  def send_json(self, status, value):
    data = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
    self.send_response(status)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Cache-Control", "no-store")
    self.send_header("Content-Length", str(len(data)))
    self.end_headers()
    self.wfile.write(data)

  def serve(self, post):
    if not isinstance(self.server, Server):
      raise RuntimeError("Missing FormosaLink LAN server")
    device = self.server.device
    # The Android client is native. Browser origins and cross-origin form submissions have no local privileges.
    if self.headers.get("Origin") or self.headers.get("Transfer-Encoding"):
      return self.send_json(403, {"detail": "forbidden"})
    try:
      data = {}
      if post:
        count = int(self.headers.get("Content-Length", "0"))
        if not 0 < count <= 8192 or self.headers.get_content_type() != "application/json":
          return self.send_json(400, {"detail": "invalid_request"})
        data = json.loads(self.rfile.read(count))
        if not isinstance(data, dict):
          raise ValueError()
      if post and self.path == "/v1/pair":
        result = device.pair(data.get("code"))
        return self.send_json(200 if result else 403, result or {"detail": "invalid_pair"})
      auth = self.headers.get("Authorization", "")
      if not auth.startswith("Bearer ") or not device.paired(auth[7:]):
        return self.send_json(401, {"detail": "unauthorized"})
      if not post and self.path == "/v1/state":
        return self.send_json(200, device.state())
      if post and self.path == "/v1/settings":
        result = device.submit(data)
        return self.send_json(200 if result["status"] == "applied" else 409, result if result["status"] == "applied" else {"detail": result["reason"]})
      if not post and self.path in ("/v1/frame/wide-road", "/v1/frame/driver"):
        try:
          return self.send_json(200, device.frame(self.path.rsplit("/", 1)[1]))
        except (ValueError, OSError, RuntimeError, TimeoutError):
          return self.send_json(503, {"detail": "camera_waiting"})
      return self.send_json(404, {"detail": "unknown"})
    except (ValueError, TypeError, KeyError):
      return self.send_json(400, {"detail": "invalid_request"})

  def do_GET(self):
    self.serve(False)

  def do_POST(self):
    self.serve(True)


class Server(HTTPServer):
  device: LanDevice
  tls: ssl.SSLContext
  allow_reuse_address = True

  def get_request(self):
    sock, address = self.socket.accept()
    sock.settimeout(2)
    try:
      return self.tls.wrap_socket(sock, server_side=True), address
    except OSError:
      sock.close()
      raise


def main():
  from openpilot.common.params import Params
  from openpilot.sunnypilot.formosalink.identity import default_directory, read
  from openpilot.sunnypilot.formosalink.device_settings import NativeSettingsProvider

  params = Params()
  directory = default_directory() / "lan"
  tls, pin = certificate(directory)
  grant = params.get(GRANT)
  if not grant:
    return
  device_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "formosa-lan:" + pin))
  try:
    cloud_id = read(directory.parent)[0]["device_id"]
  except (OSError, KeyError, ValueError):
    cloud_id = None

  class LocalSettings(NativeSettingsProvider):
    def allowed(self):
      return self.params.get(GRANT) == grant

  provider = LocalSettings(cloud_id)
  device = LanDevice(directory, params, grant, provider, device_id)
  try:
    while params.get(GRANT) == grant:
      address = lan_address()
      if not address:
        time.sleep(0.5)
        continue
      try:
        with Server((address, PORT), Handler) as server:
          server.device, server.tls, server.timeout = device, tls, 0.35
          while params.get(GRANT) == grant and lan_address() == address:
            device.refresh(address, pin)
            server.handle_request()
      except OSError:
        time.sleep(1)
  finally:
    device.close()
    params.remove(INFO)


if __name__ == "__main__":
  main()
