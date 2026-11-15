# Local front-camera display detector

MediaPipe Tasks Vision 0.10.21, Copyright The MediaPipe Authors, Apache-2.0.
The unmodified module and SIMD/non-SIMD WASM files are pinned in `manifest.json`;
the worker is built from this module by `web/build.mjs`. See [LICENSE](LICENSE).

EfficientDet-Lite0 int8 version 1 is the pretrained Google-hosted model linked
from the [official Object Detector documentation](https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector).
EfficientDet code and models originate from [Google AutoML](https://github.com/google/automl/tree/master/efficientdet),
under Apache-2.0. The artifact URL and exact SHA-256 are retained in the manifest.
It has a 320x320 input and COCO categories, not a surround-view driving model.

Runtime sources: [MediaPipe v0.10.21](https://github.com/google-ai-edge/mediapipe/tree/v0.10.21),
[published package](https://www.npmjs.com/package/@mediapipe/tasks-vision/v/0.10.21).
Published CDN SHA-256 metadata was checked before vendoring the runtime files.

Carrot uses only person, bicycle, car, motorcycle, bus and truck classes, with
a minimum model score of 0.5. Scores are not calibrated driving confidence.
The camera image is processed in a CPU worker on the viewing browser/WebView;
no model/runtime CDN or image upload is needed during use. The first enabled
session loads one local WASM variant and the model from the connected device.
No image preprocessing/training artifacts or third-party test photos are shipped.

Positions use a flat-ground intersection of the observed box bottom centre and
fresh camera calibration. They are approximate, not learned 3D depth, object
dimensions, headings, motion tracks or calibrated radar-camera fusion. Radar
observations retain their native origin and remain unclassified. This detector
has no connection to control/actuation or vehicle alerts.
