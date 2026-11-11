<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_ONNX" param="OnnxBsdSmoothingMs" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 盲区保持时间

**菜单:** 驾驶控制 \> 转向 \> ONNX 车道与盲点

---

<!-- CARROT:SETTING:BEGIN OnnxBsdSmoothingMs -->
<a id="OnnxBsdSmoothingMs"></a>

## 盲区保持时间

`OnnxBsdSmoothingMs`

平滑盲区置信度；警告启用后会在低于启动阈值15个百分点时解除。

<!-- CARROT:AUTO:BEGIN OnnxBsdSmoothingMs -->
<!-- CARROT:AUTO:SOURCE facts="0d8cc9fb3523916cbc4b073249b1355c4c1b93935cf4cc9dc0272fc56ca3509b" semantic="fbbb637458a2aa850365acb0eff1f4fa744b9934ed8dfd981401753968ba6375" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `200ms`
- **范围:** `100ms` ~ `500ms`
- **步长:** `100`
- **显示单位:** `ms`
- **菜单:** 驾驶控制 \> 转向 \> ONNX 车道与盲点
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdSmoothingMs -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdSmoothingMs -->
<!-- CARROT:REVIEW reviewed-for="fbbb637458a2aa850365acb0eff1f4fa744b9934ed8dfd981401753968ba6375" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

提高此值会减慢盲区置信度平滑，降低则更快响应新结果。解除阈值比启动阈值低 15 个百分点，下限为零。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxBsdSmoothingMs -->

<!-- CARROT:SETTING:END OnnxBsdSmoothingMs -->
