<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_ONNX" param="OnnxBsdEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ONNX 摄像头盲点识别

**菜单:** 驾驶控制 \> 转向 \> ONNX 车道与盲点

---

<!-- CARROT:SETTING:BEGIN OnnxBsdEnabled -->
<a id="OnnxBsdEnabled"></a>

## ONNX 摄像头盲点识别

`OnnxBsdEnabled`

开启广角摄像头的 ONNX 车辆侧方盲点识别。它与车道识别独立，默认关闭，不影响车辆自身提供的盲点信息。

<!-- CARROT:AUTO:BEGIN OnnxBsdEnabled -->
<!-- CARROT:AUTO:SOURCE facts="fd71c1e06be9fd2bc9705166473dd13e855d222081b3cbe4ac7cc9e72c130563" semantic="96272d6cd431cbf5a7da6b15e4a4e61a939dbe4357ffcbbc432c06e64be4efbd" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> ONNX 车道与盲点
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdEnabled -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdEnabled -->
<!-- CARROT:REVIEW reviewed-for="96272d6cd431cbf5a7da6b15e4a4e61a939dbe4357ffcbbc432c06e64be4efbd" reviewed-at="2026-10-20T08:49:07+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

开启后加载广角摄像头 BSD 模型，交替检查已配置且模型估算车道宽度至少为 2 米的左右区域。关闭后卸载 BSD 模型并清除旧检测结果，车道识别继续运行。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

先开启 `ShareData` 以运行视觉服务，再在 Carrot Web 的 ONNX 详情页面使用此开关。服务约每秒检查一次设置。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

不影响车辆自身的 BSD。原来使用车道与盲点识别的用户如需继续摄像头 BSD，必须单独开启此开关。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END OnnxBsdEnabled -->

<!-- CARROT:SETTING:END OnnxBsdEnabled -->
