import threading
import time

from openpilot.common import big_model_catalog as external
from openpilot.common import internal_models as internal
from openpilot.common import sunny_models as sunny
from openpilot.system.ui.lib.multilang import tr


class ModelChoices:
  def __init__(self, offroad):
    self.offroad = offroad
    self.items = [(False, key, model[0]) for key, model in internal.MODELS.items()]
    self.items += [(True, key, model['name']) for key, model in external.available().items()]
    self.items += [(row["big"], key, row["name"]) for key, row in reversed(sunny.catalog().items())]
    self.group = 0
    self.busy = False
    self.error = None
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
    if self.error == (big, key):
      return tr("Selection failed")
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
    return tr("Select")

  def next_group(self):
    self.group = (self.group + 1) % 4

  def group_text(self):
    return (tr("All models"), "carrot-wip", tr("sunnypilot small models"), tr("sunnypilot large models"))[self.group]

  def includes(self, big, key):
    return self.group == 0 or self.group == (2 + int(big) if key in sunny.catalog() else 1)

  def choose(self, big, key):
    if self.busy or not self.offroad():
      return
    self.busy, self.error = (big, key), None
    def run():
      try:
        if key in sunny.catalog():
          sunny.select(big, key, self.offroad)
        elif big:
          if self.offroad():
            external.select(key)
            sunny.save("big", None)
        else:
          internal.select(key, self.offroad)
          sunny.save("small", None)
      except Exception:
        self.error = (big, key)
      finally:
        self.next_refresh = 0.
        self.busy = False
    threading.Thread(target=run, name='model-selection', daemon=True).start()

  def toggle_primary(self):
    if self.offroad() and not self.busy:
      sunny.save('primary', 'auto' if sunny.internal_primary() else 'internal')
      self.next_role = 0.

  def primary_text(self):
    now = time.monotonic()
    if now >= self.next_role:
      self.next_role = now + 1.
      self.role_value = tr("Internal small model") if sunny.internal_primary() else tr("Prefer external large model")
    return self.role_value
