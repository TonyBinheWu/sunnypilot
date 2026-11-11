<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_ONNX" param="ShareData" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ONNX 车道与盲点识别

**菜单:** 驾驶控制 \> 转向 \> ONNX 车道与盲点

---

<!-- CARROT:SETTING:BEGIN ShareData -->
<a id="ShareData"></a>

## ONNX 车道与盲点识别

`ShareData`

开启后在 comma 设备上识别车道类型。仅在单独开启 OnnxBsdEnabled 后运行摄像头 BSD；该开关默认关闭，并在已配置且模型估算宽度至少 2m 的左右区域间轮流检查。关闭本设置会停止视觉服务并保留车辆原有 BSD。即使已开启，也会等待 onroad 初始化及模型、CAN、Panda 就绪并稳定 0.5 秒后启动，无需启用巡航。Offroad 时停止，下次 onroad 重新等待。

<!-- CARROT:AUTO:BEGIN ShareData -->
<!-- CARROT:AUTO:SOURCE facts="459450eb0e36fa5aa24a48b8b62eabaa54b52dc5fec9b1b224933a9042a38ed2" semantic="0ea20987779bff6e6de29f186065d105a554022ef87fd4b93b59b42d499ee336" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> ONNX 车道与盲点
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShareData -->

<!-- CARROT:MANUAL:BEGIN ShareData -->
<!-- CARROT:REVIEW reviewed-for="0ea20987779bff6e6de29f186065d105a554022ef87fd4b93b59b42d499ee336" reviewed-at="2026-10-20T08:49:07+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

开启后 comma 设备使用摄像头图像识别实线、虚线；同时开启 `OnnxBsdEnabled` 后才检测盲点。关闭后停止视觉服务，车辆原有 BSD 保持有效。

- 有摄像头图像时持续识别车道线类型。
- 开启 `OnnxBsdEnabled` 后，摄像头盲区检测交替检查已配置区域且模型估计车道宽度至少为 2 米的左右侧，不受车速和变道方向限制。

开启后仍须等待 onroad 初始化及模型、CAN、Panda 就绪状态持续 0.5 秒，无需开启巡航。Offroad 时停止，下次 onroad 时再次等待。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

通过 Carrot Web 中的此开关启用或关闭。保留已有设置值。满足启动条件后，设置和 mici 显示会在几秒后更新。

mici 的 VISION 卡片显示左右车道线类型、最近一次处理耗时和 BSD 状态。隐藏摄像头画面后，卡片和 BSD 警告仍可见。
仅原车检测时盲区墙为黄色，仅视觉检测时为蓝色，两者同时检测时为浅红色。左右侧分别显示信号来源。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

更新中包含 OpenCV，设备正常启动时自动安装到本地可写目录，无需单独运行 pip。

BSD 待机表示当前没有检查该侧。未检出不代表整个盲区安全；关闭服务后，最后的结果会在有效期结束时消失。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END ShareData -->

<!-- CARROT:SETTING:END ShareData -->
