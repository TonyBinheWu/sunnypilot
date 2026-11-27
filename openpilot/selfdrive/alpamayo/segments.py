"""Immutable calibrated inputs and packed CPU rows for the 500 ms selected worker."""
import hashlib
import numpy as np

IMAGE = (1, 3, 432, 768)
IMAGE_BYTES = 3*432*768
ROWS = (720, 768)


class FrontImages(tuple):
  __slots__ = ()
  shape = (10, *IMAGE)
  dtype = np.dtype(np.uint8)

  def __new__(cls, owners):
    obj = super().__new__(cls, owners)
    if len(obj) != 10 or any(type(b) is not bytes or len(b) != IMAGE_BYTES for b in obj):
      raise ValueError('Expected ten immutable calibrated exposures')
    return obj

  def views(self):
    return tuple(np.frombuffer(b, np.uint8).reshape(IMAGE) for b in self)

  def __array__(self, dtype=None, copy=None):
    # Explicit dense export for saved fixtures. The live adapter and the canonical audit consume segments directly.
    if copy is False:
      raise ValueError('A dense image export requires a copy')
    return np.stack(self.views(), dtype=dtype)


class Patch(tuple):
  __slots__ = ()

  def __new__(cls, array):
    if array.shape != ROWS or array.dtype != np.uint8:
      raise ValueError('Expected 720 full byte patches')
    data = array.tobytes(order='C')
    return super().__new__(cls, (data, hashlib.sha256(data).digest()))


class PatchRows(tuple):
  __slots__ = ()
  dtype = np.dtype(np.uint8)

  def __new__(cls, patches):
    obj = super().__new__(cls, patches)
    if len(obj) not in (2, 10) or any(type(p) is not Patch for p in obj):
      raise ValueError('Expected two anchor or ten full patch sets')
    return obj

  @property
  def shape(self):
    return len(self)*ROWS[0], ROWS[1]

  def rows(self, begin, end):
    if begin % ROWS[0] or end-begin != ROWS[0] or not 0 <= begin < end <= self.shape[0]:
      raise ValueError('Expected one complete selected image')
    return np.frombuffer(self[begin//ROWS[0]][0], np.uint8).reshape(ROWS)
