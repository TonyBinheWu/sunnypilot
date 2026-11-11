<!-- CARROT:GENERATED schema="1" locale="zh" group="BASIC_START" param="TeslaAutoTurnSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉自动转向灯

**菜单:** 驾驶控制 \> 启动·自动 \> 起步动作

---

<!-- CARROT:SETTING:BEGIN TeslaAutoTurnSignals -->
<a id="TeslaAutoTurnSignals"></a>

## 特斯拉自动转向灯

`TeslaAutoTurnSignals`

仅适用于车辆 CAN 与真实拨杆有效的 Model 3/Y。不再导航提前打转弯灯，用实测航向和回正判定完成；仅已确认点亮的转弯可在新鲜权限下停车等待，保留变道准备亮灯。驾驶员优先，不增加转向或起步权限。默认关闭，修改后需重启。未经封闭场地实车验证，不应用于公共道路。

<!-- CARROT:AUTO:BEGIN TeslaAutoTurnSignals -->
<!-- CARROT:AUTO:SOURCE facts="b0b37580d3a0b62378714acbee08274a36c8ca5dd81310092a64459db41866e2" semantic="8b6946fdb18666d41bbb517905b3d386b2941ffcbbf16b84ab7bf6f7eb3920a6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 启动·自动 \> 起步动作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaAutoTurnSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaAutoTurnSignals -->
<!-- CARROT:REVIEW reviewed-for="8b6946fdb18666d41bbb517905b3d386b2941ffcbbf16b84ab7bf6f7eb3920a6" reviewed-at="2026-11-08T01:13:19.645605+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

转弯灯从既有转弯 desire 开始，不因导航准备或距离提前点亮；变道保留准备亮灯确认。完成需新鲜实测航向变化 20°、目标方向转向超过 30°，再以至少 1 km/h 移动且回正至 ±15°。仅已确认 TX/点亮的转弯可在新鲜横向权限和健康姿态下停车等待，不适用于新请求或变道。后续候选等待当前完成及有效转弯 desire，最多排队三秒，同方向保持 ID。60 秒上限、新 idle 模板与逐次 TX 回报、驾驶员优先和取消/OFF 确认均保留。反馈丢失则退出，取消未确认则本次运行禁止自动输出。PC 测试不能证明实车持续点亮。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

默认关闭，修改后需重启。要求受支持的 Model 3/Y、与自动巡航滚轮共用的 CAN1 拓展线检测（`0x3DF`）、有效且新鲜的真实拨杆输入及匹配的 Panda 固件。收到 CAN1 拨杆后优先使用该来源；输入陈旧或冲突时禁止自动输出。仍需独立的灯控模板及 UI/物理灯反馈；App 请求保持至既有动作完成。`blocked:*`、`waiting:*` 用于记录具体阻断原因，不是新增屏幕告警。不增加转向或起步权限。公共道路使用前必须在目标车辆的封闭场地验证左右灯、故障和人工接管；CAN 断线或设备断电时无法保证物理熄灯。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

执行：`openpilot/selfdrive/car/tesla_turn_signals.py`。意图：`openpilot/selfdrive/controls/lib/desire_helper.py`。安全层：`opendbc_repo/opendbc/safety/safety/safety_tesla_turn_signals.h`。诊断与限制见 Tesla 用户指南。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaAutoTurnSignals -->

<!-- CARROT:SETTING:END TeslaAutoTurnSignals -->
