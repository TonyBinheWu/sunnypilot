<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="VehicleSpeedCameraDistanceTime" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 车辆测速摄像头虚拟距离时间（6.0秒）

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN VehicleSpeedCameraDistanceTime -->
<a id="VehicleSpeedCameraDistanceTime"></a>

## 车辆测速摄像头虚拟距离时间（6.0秒）

`VehicleSpeedCameraDistanceTime`

仅在外部导航未连接时应用。外部导航连接期间，即使没有当前引导项目也不使用原车导航。 当车辆仅发送测速摄像头执法速度而没有距离时，创建虚拟减速距离。保存值以0.1秒为单位：60表示6.0秒，62表示6.2秒。虚拟距离（米）= 执法速度（km/h）× 设置时间（秒），因此在50 km/h时，62会生成310米。设置值越小，虚拟距离越短，因此可能会更早或更强地开始减速。更改后的值会在行驶中约1秒内生效。 支持的CAN-FD车辆在没有与当前警告匹配的近处距离时也适用。新警告或限速变化会重新开始计算；距离耗尽后，只要警告仍有效就保持限速，不会反复延长虚拟距离。

<!-- CARROT:AUTO:BEGIN VehicleSpeedCameraDistanceTime -->
<!-- CARROT:AUTO:SOURCE facts="fbca2d7f9bb6186f315d72928d22d693e031527f07467b31256877020041f006" semantic="b3ca6436f7051d2fd82ae24a9dc3974abf6b5ee32c633d085c3eb4bee630c364" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `60`
- **范围:** `10` ~ `200`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleSpeedCameraDistanceTime -->

<!-- CARROT:MANUAL:BEGIN VehicleSpeedCameraDistanceTime -->
<!-- CARROT:REVIEW reviewed-for="b3ca6436f7051d2fd82ae24a9dc3974abf6b5ee32c633d085c3eb4bee630c364" reviewed-at="2026-09-13T09:14:59.940344+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

外部导航连接期间仅使用外部导航，即使没有当前引导项目也不使用原车导航。确认断开连接或接收超时后，按各项设置恢复使用原车导航。

当车辆只提供执法速度而不提供距离时计算虚拟距离。增大数值会延长虚拟距离，减小数值会缩短距离，可能更早或更强地减速。
支持的CAN-FD车辆在没有与当前警告匹配的近处距离时也使用此设置。新警告或限速变化会重新开始计算，并随行驶距离减少。距离耗尽后，只要警告仍有效就保持限速，不会反复延长虚拟距离。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同时检查外部导航连接状态以及显示的事件类型和剩余距离。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleSpeedCameraDistanceTime -->

<!-- CARROT:SETTING:END VehicleSpeedCameraDistanceTime -->
