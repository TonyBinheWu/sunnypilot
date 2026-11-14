"""Lazy, read-only learner subscriber for the web/Android status page."""
import copy
import threading

from openpilot.common.steering_learning import LearningReader, section


class LearningService:
  def __init__(self):
    self._lock = threading.Lock()
    self._stop = threading.Event()
    self._thread = None
    self._snapshot = {'ok': True, 'delay': section('liveDelay'), 'torque': section('liveTorqueParameters')}

  def _run(self):
    try:
      from openpilot.cereal import messaging
      from openpilot.common.params import Params
      sm = messaging.SubMaster(['liveDelay', 'liveTorqueParameters'])
      reader = LearningReader(Params())
      while not self._stop.is_set():
        sm.update(0)
        snapshot = reader.snapshot(sm)
        with self._lock:
          self._snapshot = snapshot
        self._stop.wait(.5)
    except Exception:
      with self._lock:
        self._snapshot = {'ok': False, 'delay': section('liveDelay'), 'torque': section('liveTorqueParameters')}

  def snapshot(self):
    with self._lock:
      if self._thread is None:
        self._thread = threading.Thread(target=self._run, name='steering-learning-view', daemon=True)
        self._thread.start()
      return copy.deepcopy(self._snapshot)

  def close(self):
    self._stop.set()


service = LearningService()
