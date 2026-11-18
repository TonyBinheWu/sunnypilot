"""Train an experimental visible-surface occupancy head against independent range measurements.

Each NPZ has depth_m (front RGB network), reference_m (rectified aligned optical-Z
range, NaN for missing), fx/fy/cx/cy and a recording group 'drive'. Train and
evaluate on distinct drives. Hidden/unmeasured voxels have no target.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

SCHEMA = "formosa-projective-occupancy/v1"
CELL = 0.2


def features(estimate, query_z, ray_x, ray_y):
  return np.stack([np.clip((estimate - query_z) / 2, -4, 4), estimate / 60, ray_x, ray_y], axis=-1).astype(np.float32)


def samples(paths):
  groups = set()
  inputs = []
  labels = []
  for path in paths:
    with np.load(path, allow_pickle=False) as data:
      est, gt = data["depth_m"], data["reference_m"]
      if est.ndim != 2 or est.shape != gt.shape or est.size > 4_000_000:
        raise ValueError("invalid aligned depth maps")
      groups.add(str(data["drive"].item()))
      fx, fy, cx, cy = [float(data[n].item()) for n in ("fx", "fy", "cx", "cy")]
      if not np.isfinite([fx, fy, cx, cy]).all() or min(fx, fy) <= 0:
        raise ValueError("invalid optical intrinsics")
      v, u = np.nonzero(np.isfinite(est) & np.isfinite(gt) & (est >= 1) & (est <= 60) & (gt >= 1) & (gt <= 60))
      # Uniform metric grid around the RGB estimate, independent of the label.
      # Every eighth measured ray bounds resources for large scans.
      v, u = v[::8], u[::8]
      pred, truth = est[v, u], gt[v, u]
      for delta in range(-12, 13):
        q = (np.floor(pred / CELL) + delta + 0.5) * CELL
        known = (q > 0) & (q <= truth + CELL / 2)
        inputs.append(features(pred[known], q[known], (u[known] - cx) / fx, (v[known] - cy) / fy))
        labels.append((np.abs(q[known] - truth[known]) <= CELL / 2).astype(np.float32))
  if not labels or sum(len(v) for v in labels) == 0:
    raise ValueError("no reference measurements")
  return np.concatenate(inputs), np.concatenate(labels), groups


def predict(path, inputs):
  with np.load(path, allow_pickle=False) as weights:
    if weights["schema"].item() != SCHEMA or weights["cell_m"].item() != CELL:
      raise ValueError("incompatible occupancy head")
    w1, b1, w2, b2 = [weights[k] for k in ("w1", "b1", "w2", "b2")]
    if (w1.shape, b1.shape, w2.shape, b2.shape) != ((16, 4), (16,), (1, 16), (1,)) or not all(
      np.isfinite(a).all() for a in (w1, b1, w2, b2)
    ):
      raise ValueError("invalid occupancy weights")
    logits = (np.maximum(0, inputs @ w1.T + b1) @ w2.T + b2).ravel()
    return 1 / (1 + np.exp(-np.clip(logits, -40, 40)))


def fit(train, test, output, epochs=12):
  import torch
  from torch import nn

  x, y, train_drives = samples(train)
  vx, vy, test_drives = samples(test)
  if not train_drives.isdisjoint(test_drives) or "" in train_drives | test_drives:
    raise ValueError("training and evaluation require separate named drives")
  if not 0 < y.sum() < len(y) or not 0 < vy.sum() < len(vy):
    raise ValueError("both occupied and visible empty measurements required")
  torch.manual_seed(23)
  model = nn.Sequential(nn.Linear(4, 16), nn.ReLU(), nn.Linear(16, 1))
  optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
  tx, ty = torch.from_numpy(x), torch.from_numpy(y)
  # Train for probability on the sampled grid. Select the decision threshold
  # on training data only, never by looking at the held-out drive.
  loss_fn = nn.BCEWithLogitsLoss()
  for _ in range(epochs):
    for idx in torch.randperm(len(tx)).split(4096):
      loss = loss_fn(model(tx[idx]).squeeze(1), ty[idx])
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()
  with torch.inference_mode():
    scores = torch.sigmoid(model(tx)).numpy().ravel()

  def metrics(scores, labels, threshold):
    selected = scores >= threshold
    positive = labels.astype(bool)
    tp = int((selected & positive).sum())
    return dict(
      iou=tp / max(1, int((selected | positive).sum())),
      recall=tp / max(1, int(positive.sum())),
      precision=tp / max(1, int(selected.sum())),
      queries=len(labels),
      positives=int(positive.sum()),
    )

  threshold = float(max(np.linspace(0.01, 0.99, 99), key=lambda t: metrics(scores, y, t)["iou"]))
  with Path(output).open("xb") as out:
    np.savez_compressed(
      out,
      schema=SCHEMA,
      cell_m=CELL,
      threshold=threshold,
      w1=model[0].weight.detach().numpy(),
      b1=model[0].bias.detach().numpy(),
      w2=model[2].weight.detach().numpy(),
      b2=model[2].bias.detach().numpy(),
    )
  return dict(
    schema=SCHEMA,
    threshold=threshold,
    held_out=metrics(predict(output, vx), vy, threshold),
    train_frames=len(train),
    test_frames=len(test),
    train_groups=len(train_drives),
    test_groups=len(test_drives),
    sha256=hashlib.sha256(Path(output).read_bytes()).hexdigest(),
    control_eligible=False,
  )


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--train", type=Path, nargs="+", required=True)
  parser.add_argument("--test", type=Path, nargs="+", required=True)
  parser.add_argument("--output", type=Path, required=True)
  args = parser.parse_args()
  print(json.dumps(fit(args.train, args.test, args.output), indent=2))
