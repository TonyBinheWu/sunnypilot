"""Read kernel PPP link state without waiting for serial modem queries."""
import errno
import socket
import struct
import time


def sample_link(interface="ppp0"):
  import fcntl
  request = struct.pack("256s", interface.encode("ascii")[:15])
  try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
      flags = struct.unpack_from("H", fcntl.ioctl(sock, 0x8913, request), 16)[0]
      address = socket.inet_ntoa(fcntl.ioctl(sock, 0x8915, request)[20:24])
    connected = bool(flags & 1 and flags & 0x40 and address != "0.0.0.0")
    return {"connected":connected, "ip_address":address if connected else "", "data_checked_at":time.monotonic()}
  except OSError as exc:
    if exc.errno in (errno.ENODEV, errno.ENXIO, errno.EADDRNOTAVAIL):
      return {"connected":False, "ip_address":"", "data_checked_at":time.monotonic()}
    return {}
