<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_ONNX" param="OnnxBsdThreshold" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 盲区置信度阈值

**菜单:** 驾驶控制 \> 转向 \> ONNX 车道与盲点

---

<!-- CARROT:SETTING:BEGIN OnnxBsdThreshold -->
<a id="OnnxBsdThreshold"></a>

## 盲区置信度阈值

`OnnxBsdThreshold`

将在检测区域内的车辆判定为摄像头盲区警告所需的最低置信度。

<!-- CARROT:AUTO:BEGIN OnnxBsdThreshold -->
<!-- CARROT:AUTO:SOURCE facts="594780b0e097502140d82910454a871e3c8262def0ef84e50df16dd4c443b5d5" semantic="93b3cd562cb2ac377453782fc4a8fb383aa6da0af1741171fc90eac4b5696e07" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `94%`
- **范围:** `0%` ~ `100%`
- **步长:** `1`
- **显示单位:** `%`
- **菜单:** 驾驶控制 \> 转向 \> ONNX 车道与盲点
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdThreshold -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdThreshold -->
<!-- CARROT:REVIEW reviewed-for="93b3cd562cb2ac377453782fc4a8fb383aa6da0af1741171fc90eac4b5696e07" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

提高此值会要求盲区威胁类别具有更高置信度，降低则允许较低置信度触发警告。远处或后方车辆类别不会触发警告。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxBsdThreshold -->

<!-- CARROT:SETTING:END OnnxBsdThreshold -->
