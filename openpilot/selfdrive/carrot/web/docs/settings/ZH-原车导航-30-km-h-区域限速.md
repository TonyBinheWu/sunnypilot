<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="VehicleNaviSchoolZoneControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 原车导航 30 km/h 区域限速

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN VehicleNaviSchoolZoneControl -->
<a id="VehicleNaviSchoolZoneControl"></a>

## 原车导航 30 km/h 区域限速

`VehicleNaviSchoolZoneControl`

仅在外部导航未连接时应用。外部导航连接期间，即使没有当前引导项目也不使用原车导航。 收到已确认的原车导航 30 km/h 限速区域进入信号后，将目标车速限制在 30 km/h，直到收到离开信号。此实验功能也可能适用于非学校区域的 30 km/h 限速路段，目前尚不支持 PV5。

<!-- CARROT:AUTO:BEGIN VehicleNaviSchoolZoneControl -->
<!-- CARROT:AUTO:SOURCE facts="b169ebc79b89e43850a19206419ec6467311c63af3d7d202ba735992feafe4d1" semantic="15eb22197321d7512c27030134cd141a289a4cd2499931c4f1406a9fe2630761" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviSchoolZoneControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviSchoolZoneControl -->
<!-- CARROT:REVIEW reviewed-for="15eb22197321d7512c27030134cd141a289a4cd2499931c4f1406a9fe2630761" reviewed-at="2026-09-13T07:52:41.292784+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

外部导航连接期间仅使用外部导航，即使没有当前引导项目也不使用原车导航。确认断开连接或接收超时后，按各项设置恢复使用原车导航。

开启后，支持车辆在原车导航确认的30 km/h区域限制目标速度；关闭后不使用此区域限制。也可能适用于非学校区域，不支持PV5。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同时检查外部导航连接状态以及显示的事件类型和剩余距离。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviSchoolZoneControl -->

<!-- CARROT:SETTING:END VehicleNaviSchoolZoneControl -->
