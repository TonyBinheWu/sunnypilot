"""Shared camera input and output contract for the official YOLOX-Nano ONNX export."""
from pathlib import Path

import numpy as np

from .gpu_workstation import WorkstationGpuModel

MODEL_SHA256 = "c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d"
INPUT = 416
NAMES = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


def decode(output, grids, strides):
  predictions = output[0]
  if predictions.shape != (3549, 85):
    raise ValueError("unexpected YOLOX-Nano output")
  labels = predictions[:, 5:].argmax(axis=1)
  scores = predictions[:, 4] * predictions[np.arange(len(labels)), 5 + labels]
  indices = np.flatnonzero((scores >= .5) & (scores <= 1) & np.isin(labels, list(NAMES)))
  indices = indices[np.argsort(-scores[indices], kind="stable")]
  centers = (predictions[indices, :2] + grids[indices]) * strides[indices]
  sizes = np.exp(np.clip(predictions[indices, 2:4], -12, 8)) * strides[indices]
  mins, maxs = centers - sizes / 2, centers + sizes / 2
  keep, result = [], []
  for i, index in enumerate(indices):
    if not np.isfinite(mins[i]).all() or not np.isfinite(maxs[i]).all():
      continue
    same = [k for k in keep if labels[indices[k]] == labels[index]]
    if same:
      overlap = np.maximum(0, np.minimum(maxs[i], maxs[same]) - np.maximum(mins[i], mins[same])).prod(axis=1)
      union = sizes[i].prod() + sizes[same].prod(axis=1) - overlap
      if np.any(overlap > .45 * union):
        continue
    keep.append(i)
    result.append({"kind": NAMES[labels[index]], "score": float(scores[index]),
                   "box": [float(v) for v in (*mins[i], *maxs[i])]})
    if len(result) == 24:
      break
  return result


def output_grid():
  grids, strides = [], []
  for stride in (8, 16, 32):
    side = INPUT // stride
    grids.append(np.indices((side, side))[::-1].reshape(2, -1).T)
    strides.append(np.full((side * side, 1), stride))
  return np.concatenate(grids), np.concatenate(strides)


def model_input(rgba):
  if len(rgba) != INPUT * INPUT * 4:
    raise ValueError("expected a letterboxed 416x416 RGBA frame")
  pixels = np.frombuffer(rgba, np.uint8).reshape(INPUT, INPUT, 4)
  return np.ascontiguousarray(pixels[:, :, 2::-1].transpose(2, 0, 1)[None], dtype=np.float32)


class WorkstationObjects(WorkstationGpuModel):
  def __init__(self, path: Path, profile_prefix: Path, adapter: int = 0):
    super().__init__(path, MODEL_SHA256, profile_prefix, adapter)
    self.grids, self.strides = output_grid()

  def detect(self, rgba):
    (raw,) = self.session.run(None, {"images": model_input(rgba)})
    self.verify_profile()
    return decode(raw, self.grids, self.strides)
