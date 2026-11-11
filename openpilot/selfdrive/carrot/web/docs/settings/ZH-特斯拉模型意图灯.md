<!-- CARROT:GENERATED schema="1" locale="zh" group="BASIC_START" param="TeslaModelDesireSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉模型意图灯

**菜单:** 驾驶控制 \> 启动·自动 \> 起步动作

---

<!-- CARROT:SETTING:BEGIN TeslaModelDesireSignals -->
<a id="TeslaModelDesireSignals"></a>

## 特斯拉模型意图灯

`TeslaModelDesireSignals`

独立且默认关闭的变道预测灯：需特斯拉自动转向灯、数据共享、横向控制激活、30km/h 以上、连续模型变道概率及新鲜 ONNX 虚线和相邻车道证据。可能提前或错误亮灯，不使用导航转弯预告，不实现掉头，也不增加转向权限。修改后重启，需封闭场地验证。

<!-- CARROT:AUTO:BEGIN TeslaModelDesireSignals -->
<!-- CARROT:AUTO:SOURCE facts="4d36ecd6b0a1ee03ae8f32d4c48b11a60c07da43abdb62250a41a998f83e0caa" semantic="bca04977c235f3a14fba9b7ea53e0b0d380d401a15291409e8f45d1bfb0bedc7" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 启动·自动 \> 起步动作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaModelDesireSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaModelDesireSignals -->
<!-- CARROT:REVIEW reviewed-for="bca04977c235f3a14fba9b7ea53e0b0d380d401a15291409e8f45d1bfb0bedc7" reviewed-at="2026-11-08T01:13:19.722451+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

开启后，优势变道概率在至少四个不同模型帧中持续 0.2 秒时请求灯光；关闭时不使用该预测。需横向控制激活、至少 30km/h 及手动灯相同的新鲜 ONNX 虚线/相邻车道证据，不生成转向请求。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

需特斯拉自动转向灯、数据共享和支持的 CAN/真实拨杆/灯光反馈，修改后重启。与手动及路径选项独立，既有 ATC/App 意图优先。证据丢失、完成、回退或 12 秒时取消；连续预测不能在中立预测和持续熄灯确认前重放已消费的观察。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

可能提前或误亮。需两次不同虚线结果跨度 0.2 秒、完成年龄不超过 0.8 秒，而非总拍摄年龄；默认 400ms 推理不变。不证明颜色、同向或无障碍，不增加导航转弯预告、转弯预测或掉头实现。PC 测试不等于实车验收。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaModelDesireSignals -->

<!-- CARROT:SETTING:END TeslaModelDesireSignals -->
