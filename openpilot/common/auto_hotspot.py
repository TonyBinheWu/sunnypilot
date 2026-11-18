"""Policy for explicitly enabled SIM-backed sharing; no network mutations here."""
import ipaddress
import json
from pathlib import Path


def cellular_ready(now, path=Path('/dev/shm/modem')):
  try:
    state=json.loads(path.read_text())
    ip=ipaddress.IPv4Address(state.get('ip_address', ''))
    return (state.get('sim_state')=='READY' and state.get('connected') is True
            and 0 <= now-float(state['seconds_since_boot']) <= 15
            and not ip.is_unspecified and not ip.is_loopback and not ip.is_multicast and not ip.is_link_local)
  except (OSError, ValueError, TypeError, KeyError):
    return False


class AutoHotspotPolicy:
  def __init__(self):
    self.owned=False
    self.paused=False
    self.next_attempt=0.
    self.failures=0

  def manual(self, active):
    self.paused=not active
    if not active:
      self.owned=False

  def step(self, *, enabled, cellular, active, now, radio_busy=False):
    if not enabled:
      stop=self.owned and active
      self.owned=False;self.paused=False;self.failures=0;self.next_attempt=0.
      return 'stop' if stop else 'disabled'
    if self.paused:
      return 'manual_pause'
    if active and (cellular or self.owned):
      self.owned=True;self.failures=0
      return 'share'
    if not cellular:
      return 'waiting_cellular'
    if radio_busy:
      return 'radio_busy'
    if now < self.next_attempt:
      return 'connecting'
    self.owned=True
    self.next_attempt=now+min(60,10*2**min(self.failures,3))
    self.failures+=1
    return 'activate'
