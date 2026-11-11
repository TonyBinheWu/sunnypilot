<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="VehicleSpeedCameraControlMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 车辆接收测速摄像头减速（始终应用）

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN VehicleSpeedCameraControlMode -->
<a id="VehicleSpeedCameraControlMode"></a>

## 车辆接收测速摄像头减速（始终应用）

`VehicleSpeedCameraControlMode`

仅在外部导航未连接时应用。外部导航连接期间，即使没有当前引导项目也不使用原车导航。 选择如何将通过车辆 CAN 接收的测速摄像头执法速度用于自动减速。此设置不影响从 Carrot Navi 接收的测速摄像头信息。 0：禁用 1：无论加速踏板输入如何都始终应用 2：车辆接收的摄像头减速开始后，新踩下加速踏板会忽略当前事件，并将覆盖期间达到的最高车速保持为减速下限 3：踩下加速踏板期间暂停车辆接收的测速摄像头减速

<!-- CARROT:AUTO:BEGIN VehicleSpeedCameraControlMode -->
<!-- CARROT:AUTO:SOURCE facts="4494448e20ad7e5d036355b857a058668e938801e071061c25a00bcf87d65e40" semantic="751d90cd219472ee82418f090d5685fd521295720a7ff37eb36bf0b66f9d92e9" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 始终应用 (`1`)
- **范围:** 禁用 (`0`) ~ 加速时暂停 (`3`)
- **步长:** `1`
- **选项:** `0` 禁用, `1` 始终应用, `2` 加速踏板忽略减速, `3` 加速时暂停
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleSpeedCameraControlMode -->

<!-- CARROT:MANUAL:BEGIN VehicleSpeedCameraControlMode -->
<!-- CARROT:REVIEW reviewed-for="9b48b9341a4ad5213f5220c933fa0f581110bf68f4e799917977eb831c1e67bd" reviewed-at="2026-09-13T07:52:41.725083+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

外部导航连接期间仅使用外部导航，即使没有当前引导项目也不使用原车导航。确认断开连接或接收超时后，按各项设置恢复使用原车导航。

0禁用；1不受加速踏板影响；2在减速开始后重新踩下加速踏板时，将达到的最高速度作为下限保持至事件结束；3踩下加速踏板期间解除。此模式不控制外部导航减速。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同时检查外部导航连接状态以及显示的事件类型和剩余距离。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleSpeedCameraControlMode -->

<!-- CARROT:SETTING:END VehicleSpeedCameraControlMode -->
