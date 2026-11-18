"""Reconstruct class-independent visible surface candidates on a research workstation.

Input is a rectified ROAD image and its optical intrinsics at that image size.
Output is in camera optical coordinates (right, down, forward), never a control input.
"""

import argparse
import json
from pathlib import Path

import numpy as np

MODEL = "depth-anything/Depth-Anything-V2-Metric-Outdoor-Small-hf"
REVISION = "fd2c22027eaf20374204f14099b8341e1925ad39"


def surface_voxels(depth, camera, cell=0.2, stride=4):
  """One vote per sampled pixel per endpoint cell. Missing cells stay unknown."""
  h, w = depth.shape
  fx, fy, cx, cy = [float(camera[k]) for k in ("fx", "fy", "cx", "cy")]
  if camera.get("width") != w or camera.get("height") != h or camera.get("rectified") is not True:
    raise ValueError("rectified frame size must match its intrinsics")
  if not np.isfinite([fx, fy, cx, cy]).all() or min(fx, fy) <= 0 or not 0 <= cx < w or not 0 <= cy < h:
    raise ValueError("invalid intrinsics")
  if not 0.1 <= cell <= 1 or not 1 <= stride <= 32:
    raise ValueError("invalid voxel or sampling size")
  v, u = np.mgrid[0:h:stride, 0:w:stride]
  z = depth[::stride, ::stride]
  valid = np.isfinite(z) & (z >= 1) & (z <= 60)
  xyz = np.stack(((u - cx) * z / fx, (v - cy) * z / fy, z), axis=-1)[valid]
  xyz = xyz[(np.abs(xyz[:, 0]) <= 30) & (np.abs(xyz[:, 1]) <= 10)]
  cells, counts = np.unique(np.floor(xyz / cell).astype(np.int32), axis=0, return_counts=True)
  return cells, counts


def distance_band(depth, camera, surface, cell=0.2):
  """Projective signed distances in observed surface neighbourhoods, in metres.

  A large depth jump within a pixel neighbourhood is an occlusion boundary.
  Leave ambiguous samples unknown instead of smoothing across the foreground.
  """
  if not len(surface):
    return surface, np.empty(0, dtype=np.float32)
  h, w = depth.shape
  offsets = np.mgrid[-1:2, -1:2, -2:3].reshape(3, -1).T
  cells = np.unique((surface[:, None] + offsets[None, :]).reshape(-1, 3), axis=0)
  xyz = (cells + 0.5) * cell
  valid = (xyz[:, 2] >= 1) & (xyz[:, 2] <= 60)
  cells, xyz = cells[valid], xyz[valid]
  u = np.rint(camera["cx"] + camera["fx"] * xyz[:, 0] / xyz[:, 2]).astype(int)
  v = np.rint(camera["cy"] + camera["fy"] * xyz[:, 1] / xyz[:, 2]).astype(int)
  inside = (u >= 1) & (u < w - 1) & (v >= 1) & (v < h - 1)
  u, v = u[inside], v[inside]
  samples = np.stack([depth[v, u], depth[v - 1, u], depth[v + 1, u], depth[v, u - 1], depth[v, u + 1]])
  signed = samples[0] - xyz[inside, 2]
  keep = np.isfinite(samples).all(axis=0) & (np.ptp(samples, axis=0) <= 2 * cell) & (np.abs(signed) <= 2 * cell)
  return cells[inside][keep].astype(np.int32), signed[keep].astype(np.float32)


def main():
  from PIL import Image
  import torch
  from transformers import AutoImageProcessor, AutoModelForDepthEstimation

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("image", type=Path)
  parser.add_argument("intrinsics", type=Path)
  parser.add_argument("output", type=Path)
  parser.add_argument("--cell", type=float, default=0.2)
  parser.add_argument("--occupancy-head", type=Path, help="evaluated local research weights from occupancy_head")
  args = parser.parse_args()
  with Image.open(args.image) as source:
    rgb = source.convert("RGB")
  processor = AutoImageProcessor.from_pretrained(MODEL, revision=REVISION, use_fast=False)
  network = AutoModelForDepthEstimation.from_pretrained(MODEL, revision=REVISION, use_safetensors=True).eval()
  if network.config.depth_estimation_type != "metric" or network.config.max_depth != 80:
    raise ValueError("expected outdoor metric depth weights")
  with torch.inference_mode():
    prediction = network(**processor(images=rgb, return_tensors="pt"))
    depth = (
      processor.post_process_depth_estimation(prediction, target_sizes=[(rgb.height, rgb.width)])[0]["predicted_depth"]
      .cpu()
      .numpy()
    )
  camera = json.loads(args.intrinsics.read_text(encoding="utf-8"))
  cells, hits = surface_voxels(depth, camera, args.cell)
  band, distances = distance_band(depth, camera, cells, args.cell)
  metadata = dict(
    distance_field="projective-Z, metres, positive toward camera",
    schema="formosa-visible-surfaces/v1",
    model=MODEL,
    revision=REVISION,
    frame="camera_optical_RDF",
    camera=camera,
    cell_m=args.cell,
    unobserved="unknown",
    ground_truth=False,
    control_eligible=False,
  )
  extra = {}
  if args.occupancy_head:
    import hashlib
    from .occupancy_head import CELL, features, predict

    if args.cell != CELL:
      raise ValueError("head requires its trained voxel size")
    xyz = (band + 0.5) * args.cell
    queries = features(xyz[:, 2] + distances, xyz[:, 2], xyz[:, 0] / xyz[:, 2], xyz[:, 1] / xyz[:, 2])
    extra["occupancy_probability"] = predict(args.occupancy_head, queries)
    metadata["occupancy_head_sha256"] = hashlib.sha256(args.occupancy_head.read_bytes()).hexdigest()
  with args.output.open("xb") as out:
    np.savez_compressed(
      out, cells=cells, hits=hits, band_cells=band, projective_distance_m=distances, metadata=json.dumps(metadata), **extra
    )
  print(f"{len(cells)} surface candidate cells")


if __name__ == "__main__":
  main()
