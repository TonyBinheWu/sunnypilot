"""Small deterministic checks. Observations are not proof of a root cause."""
import secrets
import threading
import time


def diagnose(facts):
  checks = []
  def add(code, level='info', **evidence):
    checks.append({'code': code, 'level': level, 'evidence': evidence})
  device = facts.get('device') or {}
  if not device.get('fresh'):
    add('device_unknown', 'unknown')
  else:
    started = device.get('started') is True
    add('onroad' if started else 'offroad')
    if device.get('thermal') in ('red', 'danger'):
      add('thermal_high', 'error', thermal=device['thermal'])
    if isinstance(device.get('freeSpace'), (int, float)) and device['freeSpace'] <= 5:
      add('storage_low', 'error', percent=device['freeSpace'])
    if isinstance(device.get('memory'), (int, float)) and device['memory'] >= 95:
      add('memory_high', 'warn', percent=device['memory'])
    car = facts.get('car') or {}
    if started:
      if not car.get('fresh'):
        add('vehicle_unknown', 'unknown')
      elif car.get('canTimeout') or car.get('canValid') is False:
        add('can_timeout' if car.get('canTimeout') else 'can_invalid', 'error')
      elif car.get('messageValid') is False or car.get('canValid') is not True:
        add('vehicle_unknown', 'unknown')
      else:
        add('can_ok')
  alert = facts.get('alert') or {}
  if alert.get('fresh'):
    kind = alert.get('type', '').split('/', 1)[0].lower()
    if any(term in kind for term in ('lagging', 'commissue', 'processtiming', 'controlstim')):
      add('processing_delay', 'error', alert=kind[:80])
    elif 'camera' in kind and any(term in kind for term in ('malfunction', 'error', 'lagging', 'frame')):
      add('camera_error', 'error', alert=kind[:80])
    elif kind and alert.get('level') in ('critical', 'userPrompt'):
      add('active_alert', 'warn', alert=kind[:80])
  manager = facts.get('manager') or {}
  if manager.get('fresh'):
    failed = manager.get('failed', [])[:12]
    if failed:
      add('process_stopped', 'error', processes=failed)
    if manager.get('rebootRequired'):
      add('restart_required', 'warn')
  else:
    add('manager_unknown', 'unknown')
  calibration = facts.get('calibration') or {}
  if calibration.get('fresh') and calibration.get('status') in ('uncalibrated', 'invalid', 'recalibrating'):
    add('calibration_needed', 'warn', status=calibration['status'])
  if facts.get('visionEnabled') is False:
    add('vision_disabled')
  formosa = facts.get('formosa') or {}
  if formosa.get('enabled'):
    if not formosa.get('paired'):
      add('formosa_unpaired', 'warn')
    elif not formosa.get('online'):
      add('formosa_offline', 'warn')
    if not formosa.get('remoteWeb'):
      add('remote_web_disabled')
  model = facts.get('model') or {}
  if model.get('available'):
    state = model.get('state')
    if state in ('error', 'recovery_stopped'):
      add('model_error', 'error', state=state, error=model.get('error_code'))
    elif state in ('checking', 'downloading', 'verifying', 'compiling', 'installing', 'waiting_for_network', 'recovering'):
      add('model_busy', 'info', state=state, progress=model.get('progress'))
  if facts.get('unavailable'):
    add('partial_data', 'unknown', sources=facts['unavailable'][:8])
  actions = []
  if any(row['code'] == 'vision_disabled' for row in checks):
    actions.append('enable_vision')
  if any(row['code'] in ('processing_delay', 'camera_error', 'process_stopped', 'restart_required', 'memory_high') for row in checks):
    actions.append('reboot')
  return {'checks': checks, 'actions': actions}


class RepairTickets:
  """Single-use, short-lived admission; a repair always refreshes the Park gate."""
  def __init__(self, clock=time.monotonic):
    self.clock, self.lock, self.pending = clock, threading.RLock(), {}

  def issue(self, actions):
    with self.lock:
      now = self.clock()
      self.pending = {key: value for key, value in self.pending.items() if now - value[0] <= 60}
      while len(self.pending) >= 32:
        self.pending.pop(next(iter(self.pending)))
      token = secrets.token_urlsafe(24)
      self.pending[token] = (now, frozenset(actions))
      return token

  def consume(self, token, action):
    with self.lock:
      value = self.pending.pop(token, None) if isinstance(token, str) else None
      if not value or not 0 <= self.clock() - value[0] <= 60 or action not in value[1]:
        raise ValueError('report_expired')
