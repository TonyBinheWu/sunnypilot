<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="VehicleNaviCanControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 车辆导航 CAN 减速应用模式

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN VehicleNaviCanControl -->
<a id="VehicleNaviCanControl"></a>

## 车辆导航 CAN 减速应用模式

`VehicleNaviCanControl`

仅在外部导航未连接时应用。外部导航连接期间，即使没有当前引导项目也不使用原车导航。 选择何时使用原车导航 CAN 的摄像头和减速带实际距离进行减速。路径匹配是指 vNAVI 的未来事件与当前计算路线及路径一致。 0：禁用 1：摄像头和减速带始终应用 2：摄像头始终应用，减速带仅在路径匹配时应用 3：摄像头和减速带仅在路径匹配时应用 路径数据超过两秒未更新时按无路径处理。车辆直接确认的当前摄像头状态由 VehicleSpeedCameraControlMode 单独控制。PV5 直接确认的区间测速状态在模式 1～3 中保持有效。此为实验功能，请仅在已验证车辆上使用。 当前摄像头警告仅关联限速相同且距离较近的候选；若只有同限速的远处摄像头，则使用当前警告自身的虚拟距离。

<!-- CARROT:AUTO:BEGIN VehicleNaviCanControl -->
<!-- CARROT:AUTO:SOURCE facts="7bef370d049ff35577439801a948010fcfd73596b55caa961cc3321c8a795139" semantic="f8d1712821a73e6fe7eba60cf61124d25e39d1cbafcd0c3129f9732ab42f4b13" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 禁用 (`0`)
- **范围:** 禁用 (`0`) ~ 摄像头和减速带按路径 (`3`)
- **步长:** `1`
- **选项:** `0` 禁用, `1` 摄像头和减速带始终应用, `2` 摄像头始终、减速带按路径, `3` 摄像头和减速带按路径
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviCanControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviCanControl -->
<!-- CARROT:REVIEW reviewed-for="9598e2a6ce6b00dcd5e8a0f1feae8f420e87990f1a27edc0aa0a46bbff15d34b" reviewed-at="2026-09-13T09:14:59.934316+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

外部导航连接期间仅使用外部导航，即使没有当前引导项目也不使用原车导航。确认断开连接或接收超时后，按各项设置恢复使用原车导航。

未连接外部导航时，0禁用；1不论路线引导状态均使用摄像头和减速带；2始终使用摄像头，仅在路线匹配时使用减速带；3两者均要求路线匹配。车辆直接确认的当前摄像头状态遵循车辆接收摄像头减速设置。
当前摄像头警告仅关联限速相同且距离较近的候选。若只有同限速的远处摄像头，当前警告使用自身的虚拟距离，远处摄像头仍保留供后续接近时使用。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同时检查外部导航连接状态以及显示的事件类型和剩余距离。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviCanControl -->

<!-- CARROT:SETTING:END VehicleNaviCanControl -->
