<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="VehicleNaviDecelCancelEarlyWarning" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 减速中止：提前警告修正 \[实验\]

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<a id="VehicleNaviDecelCancelEarlyWarning"></a>

## 减速中止：提前警告修正 \[实验\]

`VehicleNaviDecelCancelEarlyWarning`

实验功能，仅在减速中止请求开启时有效。原车导航测速警告通常在摄像头前约 6.1m×限速（60km/h 约 366m）开始，但在部分地区或车辆上会更早开始（60km/h 约 460m），导致箱式、固定、移动区间预告无法匹配而被视为未识别类型。开启后将匹配窗口的远端最多扩大至 1.35 倍，使这类警告也能识别类型。⚠ 风险：窗口扩大后，附近的移动摄像头（移动测速区间）预告可能被错误匹配到其他警告。此时若开启了“减速中止：移动测速区间”或导航减速模式（AutoNaviSpeedCtrlMode）为 2 及以下（忽略移动区间），则有较低概率跳过实际测速摄像头的减速。开启后务必在实际驾驶中确认其行为。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<!-- CARROT:AUTO:SOURCE facts="475c0a918e24154bef14ab734f4773549c0c842a36df05f029c1f1622d319889" semantic="ca6595f1bd5ba33a43b5c946ad4d3a7cb99440c06da4c111043f7d1654d3b7c6" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelEarlyWarning -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelEarlyWarning -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelEarlyWarning -->
