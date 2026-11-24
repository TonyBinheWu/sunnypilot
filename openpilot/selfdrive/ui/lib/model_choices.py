import threading
import time

from openpilot.common import big_model_catalog as external
from openpilot.common import internal_models as internal
from openpilot.system.ui.lib.multilang import tr


class ModelChoices:
  def __init__(self, offroad):
    self.offroad = offroad
    self.items = [(False, key, model[0]) for key, model in internal.MODELS.items()]
    self.items += [(True, key, model['name']) for key, model in external.available().items()]
    self.busy = False
    self.error = None
    self.next_refresh = 0.
    self.active = self.pending = (None, None)
    self.failed = False

  def status(self, big, key):
    if time.monotonic() >= self.next_refresh:
      self.next_refresh = time.monotonic() + 2
      self.active = (internal.active(), external.effective_id())
      self.pending = (internal.pending(), external.preferences()['selected'])
      self.failed = bool(internal.state().get('failed'))
    if self.error == (big, key):
      return tr("Selection failed")
    if self.busy == (big, key):
      return tr("Preparing…")
    if not big and self.failed and self.pending[0] == key and self.active[0] != key:
      return tr("Build failed")
    if self.active[big] == key:
      return tr("This boot")
    if self.pending[big] == key:
      return tr("Next boot")
    return tr("Select")

  def choose(self, big, key):
    if self.busy or not self.offroad():
      return
    self.busy, self.error = (big, key), None
    def run():
      try:
        if big:
          if self.offroad():
            external.select(key)
        else:
          internal.select(key, self.offroad)
      except (OSError, ValueError, KeyError, TimeoutError):
        self.error = (big, key)
      finally:
        self.next_refresh = 0.
        self.busy = False
    threading.Thread(target=run, name='model-selection', daemon=True).start()
