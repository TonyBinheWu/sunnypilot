"""Self-hosted companion policy, independent of upstream remote services."""
import os
from pathlib import Path
import signal
from urllib.parse import urlsplit

from openpilot.sunnypilot.formosalink.protocol import validate_origin

LEGACY_PROCESSES = frozenset(("manage_sunnylinkd", "sunnylink_registration_manager", "statsd_sp", "backup_manager", "sunnylink_uploader"))


def self_hosted_origin(origin):
  origin = validate_origin(origin)
  host = (urlsplit(origin).hostname or "").rstrip(".").lower()
  if any(host == domain or host.endswith("."+domain) for domain in ("sunnylink.ai", "sunnypilot.ai")):
    raise ValueError("FormosaLink requires a self-hosted server")
  return origin


def disable_legacy(params):
  # Background monitoring is enabled by default; pairing is still required.
  if not params.get_bool("FormosaLinkEnabled"):
    params.put_bool("FormosaLinkEnabled", True)
  # Preserve old IDs, credentials and all independent FormosaLink state.
  for key in ("SunnylinkEnabled", "EnableSunnylinkUploader"):
    if params.get_bool(key):
      params.put_bool(key, False)


def stop_legacy_daemon(params, proc_root=Path("/proc")):
  """Stop only the verified legacy supervisor's dedicated process group."""
  try:
    pid = int(params.get("SunnylinkdPid") or 0)
    if pid <= 1:
      return False
    args = (proc_root / str(pid) / "cmdline").read_bytes().split(b"\0")
    module = b"openpilot.sunnypilot.sunnylink.athena.manage_sunnylinkd"
    if module not in args or os.getpgid(pid) != pid:
      return False
    os.killpg(pid, signal.SIGTERM)
    return True
  except (OSError, TypeError, ValueError):
    return False


class OptionalCloudOnboarding:
  # Cloud pairing remains an explicit, independent action in FormosaLink.
  completed = True

  def render(self, rect):
    return None
