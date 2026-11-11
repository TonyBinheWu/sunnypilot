<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_DEVICE" param="CommaPedalEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Comma Pedal纵向控制

**菜单:** 车辆与硬件 \> 设备硬件

---

<!-- CARROT:SETTING:BEGIN CommaPedalEnabled -->
<a id="CommaPedalEnabled"></a>

## Comma Pedal纵向控制

`CommaPedalEnabled`

允许在未配备ACC的车辆上通过Comma Pedal设备进行纵向控制。仅适用于CC\_ONLY\_CAR车辆，且车辆的Cruise ready必须关闭。Cruise ready开启时原厂巡航优先，无法使用Comma Pedal控制。

<!-- CARROT:AUTO:BEGIN CommaPedalEnabled -->
<!-- CARROT:AUTO:SOURCE facts="52fbfd486cb2c70e588edda2a559bcc4e10fda08634e2344e3940a2c079963f4" semantic="5cbde9f56254e3cc6a7304e4b3cf2da6b07f9ec7b1a494bfc3889cd0e17da671" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 车辆与硬件 \> 设备硬件
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CommaPedalEnabled -->

<!-- CARROT:MANUAL:BEGIN CommaPedalEnabled -->
<!-- CARROT:REVIEW reviewed-for="5cbde9f56254e3cc6a7304e4b3cf2da6b07f9ec7b1a494bfc3889cd0e17da671" reviewed-at="2026-11-03T12:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 动作

仅在具有明确踏板配置的 CC_ONLY_CAR 车辆上，检测到设备且满足安全条件时允许踏板控制。当前配置适用于 Kia Ray EV。原厂 Cruise ready 或巡航激活、输入无效、制动或驾驶员踩下加速踏板时阻止踏板输出。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

设置位于车辆与硬件 → 设备硬件。确认车辆和踏板配置后修改设置并重启，以应用车辆参数及 Panda 固件更新。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

CarrotPilot 实车运行、制动和停车保持仍需单独验证。贡献者报告的加速受限问题尚未解决。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CommaPedalEnabled -->

<!-- CARROT:SETTING:END CommaPedalEnabled -->
