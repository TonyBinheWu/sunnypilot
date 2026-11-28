import threading
import time

from openpilot.common import big_model_catalog as external
from openpilot.common import internal_models as internal
from openpilot.common import sunny_models as sunny
from openpilot.system.ui.lib.multilang import tr


LAT2V_INSTALL_TEXT = {
  'queued': 'Queued for download',
  'waiting_offroad': 'Queued · waiting for ignition off',
  'preparing': 'Preparing model on C4',
  'retry_download': 'Download interrupted · will retry',
  'waiting_egpu': 'Downloaded · waiting for powered 5 Gbps Chestnut',
  'verifying_gpu': 'Verifying on eGPU',
  'failed': 'Verification failed · select to retry',
}


class ModelChoices:
  def __init__(self, offroad, params):
    self.offroad = offroad
    self.params = params
    self.items = sunny.model_items()
    self.query = ""
    self.visible_models = set()
    self.group = 0
    self._filter()
    self.busy = False
    self.error = self.error_detail = None
    self.park_error = False
    self.lat2v_block = None
    self.lat2v_install = {}
    self.lat2v_supported = sunny.lat2v_supported()
    self.next_role = 0.
    self.role_value = ""
    self.next_refresh = 0.
    self.active = self.pending = (None, None)
    self.failed = False

  def status(self, big, key):
    if time.monotonic() >= self.next_refresh:
      self.next_refresh = time.monotonic() + 2
      self.load_errors = (sunny.failed_key(False), sunny.failed_key(True))
      self.active = tuple(sunny.key_for(bool(b), True) or default for b, default in enumerate((internal.active(), external.effective_id())))
      self.pending = tuple(sunny.key_for(bool(b)) or default for b, default in enumerate((internal.pending(), external.preferences()['selected'])))
      self.failed = bool(internal.state().get('failed'))
      self.lat2v_block = sunny.lat2v_park_block(self.params)
      self.lat2v_install = sunny.lat2v_install_status(self.lat2v_block)
    if key == sunny.LAT2V:
      if not self.lat2v_supported:
        return tr("Requires a comma four")
      if state := self.lat2v_install.get('state'):
        label = tr(LAT2V_INSTALL_TEXT[state])
        if detail := self.lat2v_install.get('detail'):
          return f"{label} · {detail}"
        progress = self.lat2v_install.get('progress', {})
        if progress.get('phase') == 'downloading' and progress.get('total'):
          return f"{label} · {100 * progress['received'] // progress['total']}%"
        return label
    if key == sunny.LAT2V and self.park_error and self.error == (big, key):
      return tr(sunny.LAT2V_PARK_MESSAGES[self.lat2v_block]) if self.lat2v_block else tr("Select again")
    if self.error == (big, key):
      return self.error_detail or tr("Selection failed")
    if self.busy == (big, key):
      return tr("Preparing…")
    if not big and self.failed and self.pending[0] == key and self.active[0] != key:
      return tr("Build failed")
    if self.active[big] == key and self.load_errors[big] == key:
      return tr("Load failed")
    if self.active[big] == key:
      return tr("This boot")
    if self.pending[big] == key:
      return tr("Next boot")
    if key == sunny.LAT2V and self.lat2v_block:
      return tr(sunny.LAT2V_PARK_MESSAGES[self.lat2v_block])
    return tr("Select")

  def next_group(self):
    self.group = (self.group + 1) % 4
    self._filter()

  def set_query(self, text):
    self.query = text.strip()[:64]
    self._filter()

  def _filter(self):
    query = self.query.casefold()
    catalog = sunny.catalog()
    self.visible_models = {(big, key) for big, key, name in self.items
                           if (self.group == 0 or self.group == (2 + int(big) if key in catalog else 1))
                           and (query in name.casefold() or query in key.casefold())}

  def group_text(self):
    return (tr("All models"), "carrot-wip", tr("sunnypilot small models"), tr("sunnypilot large models"))[self.group]

  def includes(self, big, key):
    return (big, key) in self.visible_models

  def can_choose(self, key):
    return self.offroad() and not self.busy and (key != sunny.LAT2V or
           (self.lat2v_supported and self.lat2v_block in (None, 'forced_offroad')))

  def choose(self, big, key):
    if not self.can_choose(key):
      return
    self.busy, self.error, self.error_detail = (big, key), None, None
    self.park_error = False
    def run():
      try:
        sunny.choose_model(big, key, self.offroad, params=self.params)
      except Exception as exc:
        self.park_error = isinstance(exc, sunny.Lat2vParkedError)
        self.error_detail = str(exc) if key == sunny.LAT2V and isinstance(exc, ValueError) else None
        self.error = (big, key)
      finally:
        self.next_refresh = 0.
        self.busy = False
    threading.Thread(target=run, name='model-selection', daemon=True).start()

  def toggle_primary(self):
    if self.offroad() and not self.busy:
      try:
        sunny.set_primary('auto' if sunny.internal_primary() else 'internal', self.offroad)
      except (OSError, ValueError):
        return
      self.next_role = 0.

  def primary_text(self):
    now = time.monotonic()
    if now >= self.next_role:
      self.next_role = now + 1.
      self.role_value = tr("Internal small model") if sunny.internal_primary() else tr("Prefer external large model")
    return self.role_value
