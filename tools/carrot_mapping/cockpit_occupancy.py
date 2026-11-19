"""Train/export the optional front-camera visible occupancy network. All model files stay outside git.

Depth features come from the pinned outdoor RGB backbone. Independent, rectified
lidar returns supervise a conditional distribution for the first surface along a ray.
Integrating it across each 1 m depth interval gives that cell's occupied probability.
"""

import argparse
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import numpy as np

from .depth_surface import MODEL, REVISION
from .kitti_reference import calibration, reference

HEIGHT, WIDTH = 126, 224
ROWS, COLS = 36, 64
HALF_X = 0.34
HALF_Y = HALF_X * HEIGHT / WIDTH


def ray_grid():
  y, x = np.mgrid[:ROWS, :COLS].astype(np.float32)
  return (2 * (x + 0.5) / COLS - 1) * HALF_X, (2 * (y + 0.5) / ROWS - 1) * HALF_Y


def prepare_image(image, fx, fy, cx, cy):
  from PIL import Image

  box = (cx - fx * HALF_X, cy - fy * HALF_Y, cx + fx * HALF_X, cy + fy * HALF_Y)
  if box[0] < 0 or box[1] < 0 or box[2] > image.width or box[3] > image.height:
    raise ValueError("camera does not cover virtual sensor")
  pixels = np.asarray(image.convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR, box=box))
  rgb = ((pixels / 255 - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])).astype(np.float32)
  return rgb.transpose(2, 0, 1)[None]


def prepare_drive(archive, calib, depth_onnx, output, step):
  import onnxruntime as ort
  from PIL import Image

  options = ort.SessionOptions()
  options.intra_op_num_threads = 2
  sess = ort.InferenceSession(str(depth_onnx), options, providers=["CPUExecutionProvider"])
  with ZipFile(calib) as z:
    c, v = calibration(z, "calib_cam_to_cam.txt"), calibration(z, "calib_velo_to_cam.txt")
  P, rect = c["P_rect_02"].reshape(3, 4), c["R_rect_00"].reshape(3, 3)
  R, t = rect @ v["R"].reshape(3, 3), rect @ v["T"]
  rx, ry = ray_grid()
  u, v = np.rint(P[0, 2] + P[0, 0] * rx).astype(int), np.rint(P[1, 2] + P[1, 1] * ry).astype(int)
  depths, labels = [], []
  with ZipFile(archive) as z:
    frames = sorted(n for n in z.namelist() if "/image_02/data/" in n and n.endswith(".png"))[::step]
    if not frames:
      raise ValueError("no rectified camera frames")
    for name in frames:
      with Image.open(BytesIO(z.read(name))) as image:
        rgb = prepare_image(image, P[0, 0], P[1, 1], P[0, 2], P[1, 2])
        cloud = np.frombuffer(z.read(name.replace("/image_02/", "/velodyne_points/")[:-4] + ".bin"), dtype="<f4").reshape(-1, 4)
        gt = reference(cloud, P, R, t, image.size)
      neighbourhood = np.stack([gt[v + dv, u + du] for du in (-1, 0, 1) for dv in (-1, 0, 1)])
      valid = np.isfinite(neighbourhood)
      low = np.where(valid, neighbourhood, np.inf).min(0)
      high = np.where(valid, neighbourhood, -np.inf).max(0)
      label = np.where(
        valid.any(0) & ((high - low) < 0.75) & (low >= 2) & (high <= 45),
        np.where(valid, neighbourhood, 0).sum(0) / np.maximum(valid.sum(0), 1),
        np.nan,
      )
      depths.append(sess.run(["depth"], {"rgb": rgb})[0][0, 0])
      labels.append(label)
  with output.open("xb") as f:
    np.savez_compressed(
      f, depth=np.array(depths), label=np.array(labels, dtype=np.float32), drive=Path(frames[0]).parents[2].name, frames=frames
    )


def models():
  import torch
  from torch import nn
  from torch.nn import functional as F

  class Head(nn.Module):
    def __init__(self):
      super().__init__()
      self.layers = nn.Sequential(
        nn.Conv2d(8, 24, 3, padding=1),
        nn.SiLU(),
        nn.Conv2d(24, 24, 3, padding=2, dilation=2),
        nn.SiLU(),
        nn.Conv2d(24, 16, 3, padding=3, dilation=3),
        nn.SiLU(),
        nn.Conv2d(16, 2, 1),
      )
      rx, ry = ray_grid()
      self.register_buffer("ray", torch.from_numpy(np.stack([rx, ry]))[None])
      self.register_buffer("bins", torch.arange(2.0, 45.0).reshape(1, -1, 1, 1) + 0.5)

    def parameters_at_rays(self, depth):
      s = torch.clamp(depth, 1, 80)
      nearby = F.avg_pool2d(F.pad(s, (1, 1, 1, 1), mode="replicate"), 3, stride=1)
      # Provide per-frame relative scale and contrast as features. A road reference
      # is a scale cue only; the network can reject it on slopes or occlusion.
      lower = s[:, :, 29:35, 15:49]
      scale = torch.clamp((lower * self.ray[:, 1:2, 29:35, 15:49]).mean((2, 3), keepdim=True), 0.25, 4)
      aligned = s * 1.65 / scale
      context = F.avg_pool2d(F.pad(s, (4, 4, 4, 4), mode="replicate"), 9, stride=1)
      f = torch.cat(
        [
          torch.log(s) / 3,
          s / 30,
          (s - nearby) / 10,
          self.ray.expand(len(s), -1, -1, -1) * 4,
          aligned / 30,
          (s - context) / context,
          s / s.mean((2, 3), keepdim=True),
        ],
        1,
      )
      a = self.layers(f)
      return aligned * torch.exp(torch.tanh(a[:, :1]) * 1.8), 0.22 + F.softplus(a[:, 1:])

    def forward(self, depth):
      median, scale = self.parameters_at_rays(depth)
      lower = torch.sigmoid((self.bins - 0.5 - median) / scale)
      upper = torch.sigmoid((self.bins + 0.5 - median) / scale)
      return upper - lower, 1 - upper

  class Depth(nn.Module):
    def __init__(self, local):
      super().__init__()
      from transformers import AutoModelForDepthEstimation

      self.backbone = AutoModelForDepthEstimation.from_pretrained(
        local or MODEL, revision=REVISION, use_safetensors=True, attn_implementation="eager"
      )
      if self.backbone.config.depth_estimation_type != "metric" or self.backbone.config.max_depth != 80:
        raise ValueError("expected outdoor metric model")

    def forward(self, rgb):
      return F.interpolate(self.backbone(rgb).predicted_depth[:, None], size=(ROWS, COLS), mode="bilinear", align_corners=False)

  return Depth, Head


def train(files, output):
  import torch
  from torch.nn import functional as F

  _, Head = models()
  torch.manual_seed(31)
  depths, labels, drives = [], [], set()
  for file in files:
    with np.load(file, allow_pickle=False) as data:
      drive = str(data["drive"].item())
      if not drive or drive in drives:
        raise ValueError("training inputs must be distinct named drives")
      drives.add(drive)
      depths.extend(data["depth"])
      labels.extend(data["label"])
  depth = torch.from_numpy(np.array(depths))[:, None]
  gt = torch.from_numpy(np.array(labels))[:, None]
  head = Head().train()
  optim = torch.optim.AdamW(head.parameters(), lr=0.001, weight_decay=0.001)
  for epoch in range(75):
    for ix in torch.randperm(len(depth)).split(8):
      mu, sigma = head.parameters_at_rays(depth[ix])
      known = gt[ix].isfinite()
      error = (gt[ix][known] - mu[known]) / sigma[known]
      if not known.any():
        continue
      # KITTI roof-mount height is used only for sampling balance during training.
      # It never supplies the vehicle calibration or an inference-time ground label.
      raised = (1.65 - head.ray[:, 1:2] * gt[ix])[known] > 0.5
      weights = 1.0 + 2.0 * raised.float()
      loss = ((sigma[known].log() + F.softplus(error) + F.softplus(-error)) * weights).sum() / weights.sum()
      if not torch.isfinite(loss):
        raise ValueError("nonfinite occupancy loss")
      optim.zero_grad()
      loss.backward()
      optim.step()
  torch.save(head.state_dict(), output)


def evaluate(archive, calib, examples, model):
  """Score the final ONNX file against independent lidar, before vehicle-height clipping."""
  import onnxruntime as ort
  from PIL import Image

  options = ort.SessionOptions()
  options.intra_op_num_threads = 2
  session = ort.InferenceSession(str(model), options, providers=["CPUExecutionProvider"])
  with ZipFile(calib) as z:
    P = calibration(z, "calib_cam_to_cam.txt")["P_rect_02"].reshape(3, 4)
  returns = admitted = correct = 0
  raised_returns = raised_selected = raised_correct = 0
  rx, ry = ray_grid()
  ranged = in_range = 0
  rows, cols = np.indices(ry.shape)
  distances = []
  with np.load(examples, allow_pickle=False) as samples, ZipFile(archive) as z:
    for name, gt in zip(samples["frames"], samples["label"], strict=True):
      with Image.open(BytesIO(z.read(str(name)))) as image:
        rgb = prepare_image(image, P[0, 0], P[1, 1], P[0, 2], P[1, 2])
      occ_batch, free_batch = session.run(None, {"rgb": rgb})
      occupied, free = occ_batch[0], free_batch[0]
      known = np.isfinite(gt)
      selected = known & (occupied.max(axis=0) >= 0.22)
      estimate = occupied.argmax(axis=0) + 2.5
      returns += int(known.sum())
      admitted += int(selected.sum())
      correct += int((selected & (estimate == np.floor(gt) + 0.5)).sum())
      raised = known & (1.65 - ry * gt >= 0.5) & (1.65 - ry * gt <= 6)
      raised_returns += int(raised.sum())
      raised_selected += int((raised & selected).sum())
      raised_correct += int((raised & selected & (estimate == np.floor(gt) + 0.5)).sum())
      # Compare the same sparse uncertainty strokes shown by the renderer against lidar.
      peak = occupied.max(axis=0)
      near = (free <= 0.75).argmax(axis=0) + 2
      far = (free <= 0.25).argmax(axis=0) + 3
      interval = (
        known
        & (peak >= 0.065)
        & (peak < 0.22)
        & (1.65 - ry * estimate >= 0.5)
        & (cols % 4 == 2)
        & (rows % 4 == 2)
        & (free[0] >= 0.75)
        & (free[-1] <= 0.25)
        & (far - near <= 8)
        & (np.abs(rx * far) <= 17)
      )
      for endpoint in [near, far]:
        interval &= (1.65 - ry * endpoint >= -0.65) & (1.65 - ry * endpoint <= 6)
      ranged += int(interval.sum())
      in_range += int((interval & (gt >= near) & (gt <= far)).sum())
      distances.extend(np.abs(estimate[selected] - gt[selected]).tolist())
    return dict(
      drive=str(samples["drive"].item()),
      frames=len(samples["frames"]),
      lidar_rays=returns,
      admitted=admitted,
      correct_bin=correct,
      precision=correct / max(admitted, 1),
      recall=correct / max(returns, 1),
      iou=correct / max(returns + admitted - correct, 1),
      median_error_m=float(np.median(distances)) if distances else None,
      elevated_lidar_rays=raised_returns,
      elevated_admitted=raised_selected,
      elevated_correct_bin=raised_correct,
      range_strokes_with_lidar=ranged,
      range_strokes_containing_lidar=in_range,
    )


def export_graph(local, output, head_file=None):
  import torch

  Depth, Head = models()
  net = Depth(local).eval()
  names = ["depth"]
  if head_file:
    head = Head().eval()
    head.load_state_dict(torch.load(head_file, map_location="cpu", weights_only=True))
    net = torch.nn.Sequential(net, head).eval()
    names = ["occupied", "visible_free"]
  with torch.inference_mode():
    torch.onnx.export(
      net,
      (torch.zeros(1, 3, HEIGHT, WIDTH),),
      str(output),
      input_names=["rgb"],
      output_names=names,
      opset_version=17,
      dynamo=False,
      external_data=False,
    )


if __name__ == "__main__":
  p = argparse.ArgumentParser(description=__doc__)
  sub = p.add_subparsers(dest="command", required=True)
  e = sub.add_parser("export")
  e.add_argument("output", type=Path)
  e.add_argument("--head", type=Path)
  e.add_argument("--local-depth", type=Path)
  d = sub.add_parser("prepare")
  d.add_argument("archive", type=Path)
  d.add_argument("calib", type=Path)
  d.add_argument("depth", type=Path)
  d.add_argument("output", type=Path)
  d.add_argument("--step", type=int, default=3)
  t = sub.add_parser("train")
  t.add_argument("output", type=Path)
  t.add_argument("files", nargs="+", type=Path)
  a = sub.add_parser("evaluate")
  for name in ["archive", "calib", "examples", "model"]:
    a.add_argument(name, type=Path)
  q = sub.add_parser("quantize")
  q.add_argument("source", type=Path)
  q.add_argument("output", type=Path)
  args = p.parse_args()
  if args.command == "export":
    export_graph(args.local_depth, args.output, args.head)
  elif args.command == "prepare":
    if args.step < 1:
      p.error("positive frame step required")
    prepare_drive(args.archive, args.calib, args.depth, args.output, args.step)
  elif args.command == "train":
    train(args.files, args.output)
  elif args.command == "quantize":
    from onnxruntime.quantization import quantize_dynamic, QuantType

    quantize_dynamic(args.source, args.output, weight_type=QuantType.QInt8, op_types_to_quantize=["MatMul"], per_channel=True)
  else:
    import json

    print(json.dumps(evaluate(args.archive, args.calib, args.examples, args.model), indent=2))
