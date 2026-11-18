"""Prepare research occupancy examples from local KITTI synchronized raw and calibration ZIPs."""

import argparse
from io import BytesIO
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

import numpy as np

from .depth_surface import MODEL, REVISION


def calibration(archive, name):
  text = archive.read(next(n for n in archive.namelist() if n.endswith("/" + name))).decode()
  return {k: np.fromstring(v, sep=" ") for k, v in (row.split(":", 1) for row in text.splitlines()) if k != "calib_time"}


def reference(cloud, P, R, t, size):
  xyz = cloud[:, :3] @ R.T + t
  uvz = xyz @ P[:, :3].T + P[:, 3]
  uvz = uvz[(uvz[:, 2] >= 1) & (uvz[:, 2] <= 60)]
  u, v = np.rint(uvz[:, :2] / uvz[:, 2:]).astype(int).T
  w, h = size
  valid = (u >= 0) & (u < w) & (v >= 0) & (v < h)
  gt = np.full((h, w), np.inf, dtype=np.float32)
  np.minimum.at(gt, (v[valid], u[valid]), uvz[valid, 2])
  gt[~np.isfinite(gt)] = np.nan
  return gt


def main():
  from PIL import Image
  import torch
  from transformers import AutoImageProcessor, AutoModelForDepthEstimation

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("sync_zip", type=Path)
  parser.add_argument("calib_zip", type=Path)
  parser.add_argument("output", type=Path)
  parser.add_argument("--step", type=int, default=10)
  args = parser.parse_args()
  if args.step < 1:
    parser.error("frame step must be positive")
  args.output.mkdir(exist_ok=True, parents=True)
  with ZipFile(args.calib_zip) as archive:
    c = calibration(archive, "calib_cam_to_cam.txt")
    v = calibration(archive, "calib_velo_to_cam.txt")
  P = c["P_rect_02"].reshape(3, 4)
  rect = c["R_rect_00"].reshape(3, 3)
  R, t = rect @ v["R"].reshape(3, 3), rect @ v["T"]
  proc = AutoImageProcessor.from_pretrained(MODEL, revision=REVISION, use_fast=False)
  model = AutoModelForDepthEstimation.from_pretrained(MODEL, revision=REVISION, use_safetensors=True).eval()
  with ZipFile(args.sync_zip) as archive, torch.inference_mode():
    names = sorted(n for n in archive.namelist() if "/image_02/data/" in n and n.endswith(".png"))
    if not names:
      raise ValueError("no rectified left colour images")
    for name in names[:: args.step]:
      drive = PurePosixPath(name).parents[2].name
      frame = PurePosixPath(name).stem
      velo = name.replace("/image_02/data/", "/velodyne_points/data/").replace(".png", ".bin")
      points = np.frombuffer(archive.read(velo), dtype="<f4").reshape(-1, 4)
      image = Image.open(BytesIO(archive.read(name))).convert("RGB")
      gt = reference(points, P, R, t, image.size)
      outputs = model(**proc(images=image, return_tensors="pt"))
      estimate = proc.post_process_depth_estimation(outputs, target_sizes=[gt.shape])[0]["predicted_depth"].numpy()
      with (args.output / (drive + "-" + frame + ".npz")).open("xb") as out:
        np.savez_compressed(
          out, drive=drive, reference_m=gt, depth_m=estimate, fx=P[0, 0], fy=P[1, 1], cx=P[0, 2], cy=P[1, 2]
        )
  print(f"{len(names[:: args.step])} labeled research frames")


if __name__ == "__main__":
  main()
