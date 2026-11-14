<!-- CARROT:GENERATED schema="1" locale="zh" group="TESLA_FEATURES" param="TeslaAutoSpeedLimit" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉自动滚轮调速

**菜单:** 驾驶控制 \> 特斯拉专用 \> 特斯拉功能

---

<!-- CARROT:SETTING:BEGIN TeslaAutoSpeedLimit -->
<a id="TeslaAutoSpeedLimit"></a>

## 特斯拉自动滚轮调速

`TeslaAutoSpeedLimit`

默认关闭，修改后需完整重启。支持的 Tesla 需额外车辆 CAN 及 alpha 纵向控制；巡航与 carrotpilot 已激活时，按原车 DAS 限速以每次1km/h或1mph调整巡航设定速度。关闭不配置自动滚轮发送及对应 Panda 权限，手动滚轮保留。此前自动启用的车辆现在也必须打开此开关。导航／Carrot 速度控制激活时暂停。手动滚轮暂停自动调速；1秒内先向一侧再向反侧滚动，或退出后重新激活可恢复。保留刹车、输入过期及无反馈保护；不代表实车或道路验收。

<!-- CARROT:AUTO:BEGIN TeslaAutoSpeedLimit -->
<!-- CARROT:AUTO:SOURCE facts="fc60933750cb754328e33e03676340a2f82194b50eaf37ee07c8416ee9bcd1dc" semantic="911d5260e6889f09c0ae7b64773f4b55f394fc435d0c6b998249abe3deeb2be0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 特斯拉专用 \> 特斯拉功能
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaAutoSpeedLimit -->

<!-- CARROT:MANUAL:BEGIN TeslaAutoSpeedLimit -->
<!-- CARROT:REVIEW reviewed-for="911d5260e6889f09c0ae7b64773f4b55f394fc435d0c6b998249abe3deeb2be0" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

支持的 Tesla 需额外车辆 CAN 及 alpha 纵向控制；巡航作用中，按原车 DAS 限速以显示单位逐步调整设定速度。关闭时不设置自动滚轮发送及相应 Panda 权限，保留手动滚轮及其他控制路径。导航/Carrot 速度控制优先，并保留刹车、过期输入及无确认回馈保护。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

在 Tesla 专用群组开启后完整重启。此前自动启用的车辆现在也须明确开启。手动滚轮会暂停自动调节；1秒内先向一方再向反方向滚动，或解除再重新启用巡航可恢复。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

仅跟随原车限速，不会自动启用巡航。软件检查不代表实车或道路验收。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TeslaAutoSpeedLimit -->

<!-- CARROT:SETTING:END TeslaAutoSpeedLimit -->
