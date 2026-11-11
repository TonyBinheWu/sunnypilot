<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="AutoNaviRearCameraHoldDistance" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 后向摄像头通过后保持距离(m)

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN AutoNaviRearCameraHoldDistance -->
<a id="AutoNaviRearCameraHoldDistance"></a>

## 后向摄像头通过后保持距离(m)

`AutoNaviRearCameraHoldDistance`

外部导航报告后向测速或后向闯红灯及测速摄像头（TMAP 75/76）时，通过摄像头后继续在此距离内保持目标速度上限。在最后50米记录位置，即使提示消失或切换到下一项目，仍按行驶距离跟踪。单位为米；0关闭额外保持。增大数值会保持更远，停车不消耗距离。断开连接、偏离路线或导航会话变化时清除。原车CAN无法识别后向类型，因此此距离不适用于原车警告。倒计时结束不代表保持结束。

<!-- CARROT:AUTO:BEGIN AutoNaviRearCameraHoldDistance -->
<!-- CARROT:AUTO:SOURCE facts="d3e82bb4fcb9e00276325e16a3004084c841a80e45b3172572f2e2278b23000a" semantic="8b904f46c8e8a1e5c6c381366357034716287800c77b9036e8dc99eac2ec8689" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `100`
- **范围:** `0` ~ `300`
- **步长:** `10`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviRearCameraHoldDistance -->

<!-- CARROT:MANUAL:BEGIN AutoNaviRearCameraHoldDistance -->
<!-- CARROT:REVIEW reviewed-for="8b904f46c8e8a1e5c6c381366357034716287800c77b9036e8dc99eac2ec8689" reviewed-at="2026-09-13T09:14:59.726525+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

外部导航报告后向测速或后向闯红灯及测速摄像头（TMAP 75/76）时，通过后继续保持目标速度上限。增大数值会保持更远，减小会更早解除，0关闭额外保持。

在最后50米记录位置并按行驶距离跟踪。提示消失或切换到下一项目后仍保持，停车不消耗距离。其他控制要求更低速度时仍优先采用更低速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

显示和保存单位为米。倒计时在摄像头处结束，后向测速保持距离单独显示。外部连接断开、偏离路线、新会话、行驶距离重置或关闭摄像头控制时清除保持状态。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

原车CAN无法识别后向类型，因此不应用此额外距离。设置距离并不保证实际设备已经结束测量。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviRearCameraHoldDistance -->

<!-- CARROT:SETTING:END AutoNaviRearCameraHoldDistance -->
