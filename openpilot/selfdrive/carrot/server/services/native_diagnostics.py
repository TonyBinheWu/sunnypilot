"""On-demand native observations; no logs, identifiers, tokens or uploads."""
import math
import re
import threading
import time

from .self_diagnostics import diagnose, RepairTickets


class NativeDiagnostics:
  def __init__(self):
    self.lock = threading.RLock()
    self.sm = None
    self.tickets = RepairTickets()
    self.cached = None

  def snapshot(self):
    with self.lock:
      now = time.monotonic()
      # Concurrent tabs share a very short read cache, never the write gate.
      if self.cached and 0 <= now - self.cached[0] < .5:
        return self.cached[1]
      facts, missing, p = {}, [], None
      try:
        from openpilot.common.forced_offroad import fresh
        if self.sm is None:
          from openpilot.cereal import messaging
          self.sm = messaging.SubMaster(['deviceState', 'carState', 'carControl', 'selfdriveState', 'managerState', 'liveCalibration'])
        self.sm.update(0)
        sm = self.sm
        def valid(name, age): return fresh(sm, name, age, time.monotonic())
        def number(value):
          value = float(value)
          return round(value, 1) if math.isfinite(value) else None
        facts['device'] = {'fresh': valid('deviceState', 2)}
        if facts['device']['fresh']:
          state = sm['deviceState']
          facts['device'].update(started=bool(state.started), thermal=str(state.thermalStatus), freeSpace=number(state.freeSpacePercent), memory=number(state.memoryUsagePercent))
        # card marks its Event invalid when CAN is invalid. A diagnostic must
        # still read that *fresh failure observation*, while repair admission
        # continues requiring the full valid/P/zero-speed control policy.
        elapsed = time.monotonic() - sm.logMonoTime.get('carState', 0) / 1e9
        received = bool(sm.seen.get('carState') and 0 <= elapsed <= .5)
        facts['car'] = {'fresh': received, 'messageValid': bool(sm.valid.get('carState'))}
        if facts['car']['fresh']:
          state = sm['carState']
          facts['car'].update(canValid=bool(state.canValid), canTimeout=bool(state.canTimeout))
        facts['alert'] = {'fresh': valid('selfdriveState', 1)}
        if facts['alert']['fresh']:
          state = sm['selfdriveState']
          kind = str(state.alertType)
          facts['alert'].update(type=kind if re.fullmatch(r'[A-Za-z0-9_./-]{0,100}', kind) else '', level=str(state.alertStatus))
        facts['manager'] = {'fresh': valid('managerState', 3)}
        if facts['manager']['fresh']:
          state = sm['managerState']
          facts['manager'].update(rebootRequired=bool(state.rebootRequired), failed=[str(p.name)[:80] for p in state.processes if p.shouldBeRunning and not p.running][:12])
        facts['calibration'] = {'fresh': valid('liveCalibration', 5)}
        if facts['calibration']['fresh']:
          facts['calibration']['status'] = str(sm['liveCalibration'].calStatus)
      except Exception:
        missing.append('native_state')
      try:
        from .params import Params, HAS_PARAMS
        p = Params() if HAS_PARAMS and Params else None
        if p is None:
          raise RuntimeError('params unavailable')
        facts['visionEnabled'] = bool(p.get_bool('CarrotVisionEnabled'))
        formosa = {'enabled': bool(p.get_bool('FormosaLinkEnabled')), 'remoteWeb': bool(p.get_bool('FormosaLinkRemoteWeb'))}
        if formosa['enabled']:
          from openpilot.sunnypilot.formosalink.identity import default_directory, read
          from openpilot.sunnypilot.formosalink.connection_status import is_online
          try:
            identity = read(default_directory())
            formosa.update(paired=True, online=is_online(identity['origin']))
          except (OSError, ValueError, KeyError, TypeError):
            formosa.update(paired=False, online=False)
        facts['formosa'] = formosa
      except Exception:
        missing.append('settings')
      try:
        from ..features.egpu_model import build_status_payload
        status = build_status_payload()
        facts['model'] = {key: status.get(key) for key in ('available', 'state', 'error_code', 'progress')}
      except Exception:
        missing.append('model_status')
      facts['unavailable'] = missing
      report = {'ok': True, 'version': 1, 'collectedAt': time.time(), 'facts': facts, **diagnose(facts)}
      report['repairAllowed'] = False
      report['repairReason'] = 'vehicle_unavailable'
      if p is not None and self.sm is not None:
        try:
          from ..features.intro.routes import _check_setup_state
          _check_setup_state(p, self.sm)
          report.update(repairAllowed=True, repairReason='')
        except Exception as exc:
          report['repairReason'] = getattr(exc, 'code', 'vehicle_unavailable')
      report['ticket'] = self.tickets.issue(report['actions'])
      self.cached = (now, report)
      return report


service = NativeDiagnostics()
