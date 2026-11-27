"""Direct, physically paired ccNC companion on the device's Wi-Fi or Ethernet address."""

from __future__ import annotations
import base64
from contextlib import ExitStack
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import ipaddress
import json
import os
import re
import secrets
import select
import socket
import ssl
import struct
import time
import uuid

PORT = 8787
DISCOVERY_GROUP = "239.255.87.87"
DISCOVERY_QUERY = re.compile(rb"FormosaLink-ccNC/1 FIND ([0-9a-f]{32})")
IP_PKTINFO = getattr(socket, "IP_PKTINFO", 8)  # Linux in_pktinfo
GRANT = "FormosaLanAccess"
REQUEST = "FormosaLanPairRequest"
INFO = "FormosaLanPairInfo"
NETWORKS = tuple(map(ipaddress.ip_network, ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "169.254.0.0/16")))


def lan_interface():
  import fcntl

  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    for name in sorted((n for _, n in socket.if_nameindex()), key=lambda n: not n.startswith(("wl", "ap"))):
      if not name.startswith(("wl", "ap", "eth", "en", "br")):
        continue
      try:
        interface = struct.pack("256s", name.encode()[:15])
        addr = ipaddress.IPv4Address(fcntl.ioctl(sock.fileno(), 0x8915, interface)[20:24])
        if any(addr in net for net in NETWORKS):
          mask = socket.inet_ntoa(fcntl.ioctl(sock.fileno(), 0x891b, interface)[20:24])
          return socket.if_nametoindex(name), ipaddress.IPv4Interface((str(addr), mask))
      except OSError:
        continue
  return None


def discovery_socket(link, port=PORT):
  index, interface = link
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, IP_PKTINFO, 1)
    sock.bind(("", port))
    membership = struct.pack("=4s4si", socket.inet_aton(DISCOVERY_GROUP), interface.ip.packed, index)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    sock.setblocking(False)
    return sock
  except OSError:
    sock.close()
    raise


def answer_discovery(sock, link, pin):
  index, interface = link
  data, metadata, flags, peer = sock.recvmsg(96, socket.CMSG_SPACE(12))
  query = DISCOVERY_QUERY.fullmatch(data)
  if not query or flags & socket.MSG_TRUNC or ipaddress.IPv4Address(peer[0]) not in interface.network:
    return
  for level, kind, value in metadata:
    if level == socket.IPPROTO_IP and kind == IP_PKTINFO and len(value) == 12 and struct.unpack_from("=i", value)[0] == index:
      # Return only the public TLS identity, on the same link as the request.
      route = struct.pack("=i4s4s", index, interface.ip.packed, bytes(4))
      sock.sendmsg([b"FormosaLink-ccNC/1 HERE " + query[1] + b" " + pin.encode("ascii")], [(level, kind, route)], 0, peer)
      break


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
    if (self.params.get(GRANT) != self.grant or not self.provider.guard() or self.params.get(REQUEST) != self.request
        or not self.code or time.monotonic() >= self.until or self.attempts >= 5):
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
  device_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "formosa-lan:" + pin))
  try:
    cloud_id = read(directory.parent)[0]["device_id"]
  except (OSError, KeyError, ValueError):
    cloud_id = None

  class LocalSettings(NativeSettingsProvider):
    def __init__(self, access):
      super().__init__(cloud_id)
      self.access = access

    def allowed(self):
      return self.params.get(GRANT) == self.access

  while True:
    link = lan_interface()
    grant = params.get(GRANT)
    if not link:
      time.sleep(0.5)
      continue
    address = str(link[1].ip)
    try:
      with ExitStack() as stack:
        server = device = None
        if grant:
          device = LanDevice(directory, params, grant, LocalSettings(grant), device_id)
          stack.callback(params.remove, INFO)
          stack.callback(device.close)
          server = stack.enter_context(Server((address, PORT), Handler))
          server.device, server.tls, server.timeout = device, tls, 0
        discovery = None
        next_try = 0.0
        while params.get(GRANT) == grant and lan_interface() == link:
          if discovery is None and time.monotonic() >= next_try:
            next_try = time.monotonic() + 5
            try:
              discovery = stack.enter_context(discovery_socket(link))
            except OSError:
              pass
          if device is not None:
            device.refresh(address, pin)
          readers = [s for s in (server, discovery) if s is not None]
          ready, _, _ = select.select(readers, [], [], 0.35)
          if discovery is not None and discovery in ready:
            try:
              answer_discovery(discovery, link, pin)
            except OSError:
              pass
          if server is not None and server in ready:
            server.handle_request()
    except OSError:
      time.sleep(1)


if __name__ == "__main__":
  main()
