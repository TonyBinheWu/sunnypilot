<!-- CARROT:GENERATED schema="1" locale="zh" group="BASIC_START" param="TeslaManualLaneSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉手动变道灯

**菜单:** 驾驶控制 \> 启动·自动 \> 起步动作

---

<!-- CARROT:SETTING:BEGIN TeslaManualLaneSignals -->
<a id="TeslaManualLaneSignals"></a>

## 特斯拉手动变道灯

`TeslaManualLaneSignals`

需开启特斯拉自动转向灯和数据共享。30km/h 以上结合驾驶员转向意图、持续接近车道线、连续 ONNX 虚线分类与相邻车道几何，仅请求左右灯，巡航未激活也可使用。实线、未知或过期结果禁止新自动请求，不限制真实拨杆。不能证明车道线颜色或同向车流，不增加转向权限。默认关闭，修改后重启，需封闭场地实车验证。

<!-- CARROT:AUTO:BEGIN TeslaManualLaneSignals -->
<!-- CARROT:AUTO:SOURCE facts="674105a72bf617da6635870fdade48405b1639bcf24f46efb717a65d0133fa03" semantic="669db437b176b1b2fdb9d4effef75f18f63f9ba24fa2385698d782ce9d784aec" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 启动·自动 \> 起步动作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaManualLaneSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaManualLaneSignals -->
<!-- CARROT:REVIEW reviewed-for="669db437b176b1b2fdb9d4effef75f18f63f9ba24fa2385698d782ce9d784aec" reviewed-at="2026-11-08T01:13:19.697893+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

开启后根据持续驾驶员扭矩和两侧边界接近，仅请求左右灯，巡航未激活也可使用；关闭时保留既有 ATC/App 灯光。左右均需至少 30km/h、新鲜连续 ONNX 虚线、可信相邻车道与道路边界余量，不写入转向 desire。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

需特斯拉自动转向灯、数据共享、支持的车辆 CAN、真实拨杆及灯光反馈，修改后重启。视觉盲点开关独立。人工输入、双闪、无效状态、证据丢失、远离边界、越线完成或 12 秒后，通过既有取消/OFF 握手结束。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

至少两次不同虚线完成时间相隔 0.2 秒，当前年龄不超过 0.8 秒；默认 400ms 推理间隔不变。完成时间不是拍摄时间，虚线不证明白线、同向或无障碍。不恢复导航转弯预告、不增加距离附加或掉头实现，不保证轮胎越线前亮灯；仍需封闭场地实车验收。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaManualLaneSignals -->

<!-- CARROT:SETTING:END TeslaManualLaneSignals -->
