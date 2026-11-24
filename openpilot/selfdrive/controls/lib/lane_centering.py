"""Blend the driving path toward the midpoint of two observed lane boundaries."""
import numpy as np


def lane_midpoint(model, path_x):
  if (len(model.laneLines) < 3 or len(model.laneLineProbs) < 3 or len(model.laneLineStds) < 3 or
      not all(.7 <= model.laneLineProbs[i] <= 1 for i in (1, 2)) or
      not all(0 <= model.laneLineStds[i] <= .25 for i in (1, 2))):
    return None
  sides = []
  for line in (model.laneLines[1], model.laneLines[2]):
    if (len(line.x) != len(path_x) or len(line.y) != len(path_x) or len(path_x) < 2 or
        not np.isfinite(line.x).all() or not np.isfinite(line.y).all() or not (np.diff(line.x) > 0).all()):
      return None
    sides.append(np.interp(path_x, line.x, line.y, left=np.nan, right=np.nan))
  left, right = sides
  width = right - left
  usable = (width >= 2.5) & (width <= 4.5)
  # Permit a slight difference between the initial model/lane sample origins.
  near = (path_x >= 1.) & (path_x <= 25.)
  if not near.any() or not usable[near].all() or not (left[near][0] < 0 < right[near][0]):
    return None
  return np.where(usable, .5 * (right + left), np.nan)
