<!-- CARROT:GENERATED schema="1" locale="zh" group="BASIC_START" param="TeslaModelPathSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉模型路径灯

**菜单:** 驾驶控制 \> 启动·自动 \> 起步动作

---

<!-- CARROT:SETTING:BEGIN TeslaModelPathSignals -->
<a id="TeslaModelPathSignals"></a>

## 特斯拉模型路径灯

`TeslaModelPathSignals`

独立且默认关闭的路径预测灯：需特斯拉自动转向灯、数据共享、横向控制激活、30km/h 以上、相对车道曲率连续预测越线及新鲜 ONNX 虚线和相邻车道证据。可能提前或错误亮灯；不恢复导航转弯提前亮灯，不增加掉头逻辑或转向权限。修改后重启，需封闭场地验证。

<!-- CARROT:AUTO:BEGIN TeslaModelPathSignals -->
<!-- CARROT:AUTO:SOURCE facts="b0763e0a0c7b77c6e41879f1214d58889fcef2d0bb9f3669c866936269c2b6e8" semantic="edf04a247afa9d6aaf6f0a28c3a2a9441df5e3bfed9758d06e290ced61ea05b0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 启动·自动 \> 起步动作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaModelPathSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaModelPathSignals -->
<!-- CARROT:REVIEW reviewed-for="edf04a247afa9d6aaf6f0a28c3a2a9441df5e3bfed9758d06e290ced61ea05b0" reviewed-at="2026-11-08T01:13:19.741652+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

开启后，根据相对弯曲车道边界的连续模型路径越线预测请求灯光；关闭时不使用该预测。需至少四个不同帧持续 0.2 秒、横向控制激活、至少 30km/h 及新鲜 ONNX 虚线/相邻车道证据，不改变模型或转向命令。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

需特斯拉自动转向灯、数据共享和支持的 CAN/真实拨杆/灯光反馈，修改后重启。与手动和意图选项独立，ATC/App 优先。证据/状态失效、回退、完成或 12 秒后由原执行器取消；重新触发前需中立预测和持续熄灯确认。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

可能提前或误亮，不保证识别每次越线。需两次不同虚线跨度 0.2 秒、完成年龄最多 0.8 秒，而非拍摄年龄；默认 400ms 间隔不变。虚线不证明颜色、同向或无障碍。不增加导航转弯预告、转弯预测或掉头逻辑；封闭场地实车验收仍未完成。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaModelPathSignals -->

<!-- CARROT:SETTING:END TeslaModelPathSignals -->
