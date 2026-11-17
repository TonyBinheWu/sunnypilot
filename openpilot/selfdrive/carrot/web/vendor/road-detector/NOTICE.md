# Local road-observation models (2026-11-17)

This optional display-only pack is disabled by default. It recognizes **traffic cones and crosswalks only**. It contains no stop-line or motorcycle-waiting-area model. No camera image is sent to a third party. Independent Taiwan-road, rain/night and Android-box accuracy/latency have not been validated.

## Cone model and license declarations

- Author: **mancalazure**, [construction-ppe-safety](https://huggingface.co/mancalazure/construction-ppe-safety/tree/70cc801710f246765f70ada7248d9560ec749bb2), commit `70cc801710f246765f70ada7248d9560ec749bb2`.
- `cone.onnx` is the unmodified `best.onnx`. SHA-256 `1d5f3cf69883e89ba6e2b3836a0b21623044e9a682f1f00dfbacac97b99baf94`.
- The model card declares **CC-BY-4.0**, while its ONNX metadata explicitly declares **AGPL-3.0** and Ultralytics **8.4.114**. These are distinct declarations; this pack retains both notices and does not describe the weights as MIT/Apache or resolve the discrepancy by discarding AGPL obligations. Redistribution must retain attribution, license notices and corresponding source availability. There is no warranty or legal opinion here.
- Original card, original PyTorch weights, labels/data YAML and the matching Ultralytics source distribution are under `source/`. `ULTRALYTICS-AGPL-3.0.txt` and `CC-BY-4.0.txt` accompany the assets. Training data are not bundled; consult the original author for their provenance.
- Input: `images`, float32 `[1,3,640,640]`, stretched RGB divided by255. Output: `output0`, `[1,14,8400]`, YOLOv8 without objectness. Only class6 `Safety Cone` is admitted. The other nine PPE/person/vehicle classes are intentionally ignored.

## Crosswalk model, changes and corresponding source

- Author: **kairess**, [crosswalk-traffic-light-detection-yolov5](https://github.com/kairess/crosswalk-traffic-light-detection-yolov5/tree/5ba1e01d946e1a5cc9dcf396b3b8fc62ae2666d5), commit `5ba1e01d946e1a5cc9dcf396b3b8fc62ae2666d5`, **GPL-3.0** (`CROSSWALK-GPL-3.0.txt`).
- Original `runs/train/exp4/weights/best.pt` is bundled as `source/crosswalk-best.pt`, SHA-256 `7eb9e22c31e6eef68dce2cfd656fa27614e21203371cdf9255d942c86e29f127`. Corresponding original Python/YAML/scripts/license/documentation are bundled as `source/crosswalk-source.zip`; upstream images, video and training-output binaries are excluded. No source code has been relicensed.
- Change: exported the original YOLOv5s6 checkpoint to fixed-input **320px** ONNX opset12 with Torch2.9.0 CPU, ONNX1.19.1. `crosswalk.onnx` SHA-256 `9434014d541488e423e8b4d2f951d4151bf8ce24619a034e5ae988ad183f5ff7`. No retraining or precision quantization. Exporter source and pinned dependencies: [tools/carrot_road_models](https://github.com/TonyBinheWu/sunnypilot/tree/carrot-wip/tools/carrot_road_models).
- Reproduce from repository root in an isolated environment: `python tools/carrot_road_models/export_crosswalk.py --output crosswalk.onnx`. The exporter verifies source hashes, loads only explicit class definitions, uses `torch.load(weights_only=True)` with exact allowed globals, and checks ONNX plus blank-input PyTorch/ORT parity. It never uses unrestricted pickle loading.
- Input: `images`, float32 `[1,3,320,320]`, RGB /255, aspect-preserving letterbox with114 padding. Output: `output0`, `[1,6375,8]`. Confidence = objectness × class0 `Zebra_Cross`; class1/2 red/green signals are **not** used. A crosswalk bounding box provides an image notice, not its actual ground contour, measured width, distance or a stop line.

## Runtime and hashing

- [ONNX Runtime Web1.22.0](https://www.npmjs.com/package/onnxruntime-web/v/1.22.0): MIT, copyright Microsoft; `ORT-LICENSE` and `ORT-ThirdPartyNotices.txt`. WASM CPU, SIMD, one thread, no cross-origin isolation requirement, no WebGPU permission.
- [@noble/hashes1.8.0](https://www.npmjs.com/package/@noble/hashes/v/1.8.0): MIT, copyright Paul Miller; `HASHES-LICENSE`. ESM files are copied, with the bare `@noble/hashes/crypto` import changed to `./crypto.js` for the offline browser bundle. SHA-256 also works on private-LAN HTTP where WebCrypto.subtle is unavailable.
- `manifest.json` records every shipped file's bytes and hash, and each model's explicit preprocessing/head contract. Runtime checks model length and SHA-256 before constructing sessions. No arbitrary remote model URLs or runtime checkpoint deserialization.
- Loaded inference assets total about74MB; corresponding-source files are not fetched for inference. Models load only after explicit opt-in. Source files and notices can be obtained from the same `/vendor/road-detector/` tree and repository. Worker/decoder adapters are available in `web/src/features/drive/contents/vision/`; this component's GPL/AGPL notices remain applicable. Existing unrelated components retain their own licenses.

## Evidence and limitations

The original author's sample video frames0/50/150 gave nonempty class0 detections. Export/native ORT outputs matched with rtol0.001, atol0.01; largest absolute error at320px was0.000336. A separate CC0 Commons photograph by Ser Amantio di Nicolao (Traffic cones in the government center.jpg, 2023-02-28) gave cone detections. These inputs were local smoke tests only; test photos/video are not redistributed here. This is not an independent accuracy benchmark or evidence of safe road performance.

Positions use fresh calibrated full ROAD frames and flat-ground rays; slope, truncation, camera mismatch and detector errors affect them. Image observations expire after1.2s. Slow frames are discarded rather than kept as live targets. Leaving Vision, backgrounding, source changes or freezing the review clears/terminates recognition. Native radar remains unclassified. No occupancy, 360-degree perception, Tesla proprietary weights, automatic braking or control integration is provided.
