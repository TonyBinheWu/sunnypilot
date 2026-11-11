"""Translate hardware status for display without changing hardware protocol values."""
import re

from openpilot.system.ui.lib.multilang import tr, tr_noop

MESSAGES = (
  tr_noop("not detected"), tr_noop("multiple devices"), tr_noop("firmware mismatch"), tr_noop("startup failed"),
  tr_noop("loading"), tr_noop("reboot to compile"), tr_noop("active"), tr_noop("model not compiled"), tr_noop("ready"),
  tr_noop("USB not connected"), tr_noop("GPU check timed out"), tr_noop("12V / PCIe not ready"),
  tr_noop("GPU incompatible"), tr_noop("USB disconnected during GPU check"), tr_noop("USB link errors"),
  tr_noop("not checked"), tr_noop("no errors"), tr_noop("not connected"),
)


def localize_hardware_status(message: str) -> str:
  if message in MESSAGES:
    return tr(message)
  slow = re.fullmatch(r"slow USB \((\d+) Mbps\)", message)
  if slow:
    return tr("Slow USB ({speed} Mbps)").format(speed=slow[1])
  link = re.fullmatch(r"USB link (\d+) Mbps", message)
  if link:
    return tr("USB link {speed} Mbps").format(speed=link[1])
  return message  # Keep unrecognized diagnostic details intact.
