---
license: cc-by-4.0
library_name: ultralytics
pipeline_tag: object-detection
thumbnail: logo.png
tags:
- object-detection
- yolov8
- edge-ai
- ppe
- construction-safety
- triton
- zededa
- jetson
---

<p align="center">
  <img src="logo.png" alt="Work Safety AI - PPE Detection Model" width="520">
</p>

# Construction Site PPE Detector (YOLOv8n)

Detects **hard hats, hi-vis vests, masks, people, safety cones and site
equipment** for a worker-safety demo running on an NVIDIA Jetson Orin Nano under
ZEDEDA EVE-K. A rule engine turns detections into PPE-compliance alerts and an
on-device language model writes the shift summary; nothing but metadata leaves
the node.

- **Base:** `yolov8n`, fine-tuned on the Roboflow Universe
  `construction-site-safety` v28 dataset.
- **Classes (index order):** `0 Hardhat`, `1 Mask`, `2 NO-Hardhat`, `3 NO-Mask`,
  `4 NO-Safety Vest`, `5 Person`, `6 Safety Cone`, `7 Safety Vest`,
  `8 machinery`, `9 vehicle`.
- **Input:** 640x640 (stretch). **ONNX** (opset 12) served on Triton's
  onnxruntime GPU backend.

## TWO exports of the same weights -- pick the right one

This repo ships both, and they are **not interchangeable**. Loading the wrong
one produces no error, just garbage detections.

| file | input -> output | opset | exporter | consumer |
|---|---|---|---|---|
| `model-deepstream.onnx` | `input [batch,3,640,640]` -> `[1, 8400, 6]` | 18 | DeepStream-Yolo `export_yoloV8.py` | DeepStream `nvinfer` + `NvDsInferParseYolo` |
| `best.onnx` | `images` -> `output0 [1, 14, 8400]` | 12 | stock ultralytics (`nms=False`) | Triton onnxruntime, generic YOLOv8 tooling |

`[1, 14, 8400]` is 4 box coords + 10 class scores. **NMS is in neither graph** --
the consumer must run it.

## Files

- `model-deepstream.onnx` -- ONNX for DeepStream / `nvinfer`
- `best.onnx` -- ONNX for Triton / generic YOLOv8 tooling
- `best.pt` -- source PyTorch weights (ultralytics), for re-export
- `config.pbtxt` -- Triton model config (onnxruntime, GPU). Applies to
  `best.onnx` only; it is meaningless for the DeepStream graph.
- `labels.txt` -- class names in index order, one per line
- `data.yaml` -- the same class list plus dataset provenance
- `logo.png` -- card image

`data.yaml` `names` is authoritative for class order. Any consumer that keeps
its own copy of the class list must agree exactly, including case and the space
in `NO-Safety Vest`. Getting it wrong raises no error -- it silently mislabels
every detection.

## Honest limits

No validation metrics are published here, because none were measured against a
held-out set for this deployment -- quoting the upstream project's numbers for
this export would be misleading. What was observed in use, on one demo clip:

- **Roughly one false positive per six people** when "no hard hat" is inferred
  from the absence of a `Hardhat` box over a detected `Person`, usually from a
  briefly occluded hat or someone far back in frame. Raising the consecutive-
  frame confirmation count trades latency for quiet.
- **The `NO-Hardhat` class itself is weak.** It was trained on bare heads, so it
  misses caps, beanies and hoods. Inferring absence from the `Hardhat` class is
  more reliable in practice, and is what the demo does.
- **No forklift and no pallet class.** Heavy equipment arrives as `machinery` or
  `vehicle`. Say "equipment", not "forklift".
- **PPE-to-person association is by box containment**, so crowded frames will
  mis-assign a hat or vest to the wrong worker.
- **"No hard hat" only fires when hats are detected somewhere in frame.** Absence
  of detection is not evidence of non-compliance, so with a person-only model
  these rules go inert rather than wrong.

Validate against your own footage before quoting any accuracy figure.

## Licence

Weights are **CC BY 4.0**, inherited from the Roboflow Universe
`construction-site-safety` v28 dataset and the
`snehilsanyal/Construction-Site-Safety-PPE-Detection` project -- attribution
required.

Separately, the export toolchain is the YOLOv8 / ultralytics lineage, which is
**AGPL-3.0**. That affects code, not these weights, but get it cleared before
this appears in anything productised.

## Usage

```python
from ultralytics import YOLO
model = YOLO("best.pt")
model.predict("image.jpg")
```

## Regenerating

**Triton layout (this `best.onnx`):**

```bash
docker run --rm --platform linux/arm64 -v "$PWD":/work -w /work \
  ultralytics/ultralytics:latest-arm64 \
  yolo export model=best.pt format=onnx opset=12 imgsz=640 \
              nms=False dynamic=False simplify=False
```

`simplify=False` matters: simplification pulls in `onnxslim`, which is not in
the image, and the export dies with `ModuleNotFoundError`.

**DeepStream layout (for `nvinfer`, NOT this file):**

```bash
docker run --rm --platform linux/arm64 -v "$PWD":/work -w /work \
  ultralytics/ultralytics:latest-arm64 bash -c '
    pip install -q onnx onnxscript onnxslim
    git clone --depth 1 https://github.com/marcoslucianops/DeepStream-Yolo /tmp/dsy
    python3 /tmp/dsy/utils/export_yoloV8.py -w best.pt --dynamic
    python3 -c "import onnx; onnx.save(onnx.load(\"best.onnx\"), \"model.onnx\", save_as_external_data=False)"
  '
```

Recent torch writes split external-data ONNX -- a small `.onnx` plus a large
`.onnx.data`. The `onnx.save` line merges them; a bare `.onnx` without its
sidecar is a broken model.
