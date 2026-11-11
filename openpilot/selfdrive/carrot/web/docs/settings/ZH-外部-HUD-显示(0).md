<!-- CARROT:GENERATED schema="1" locale="zh" group="HUD_BASIC" param="ClusterHud" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 外部 HUD 显示(0)

**菜单:** 显示 \> 外部HUD \> 基本

---

<!-- CARROT:SETTING:BEGIN ClusterHud -->
<a id="ClusterHud"></a>

## 外部 HUD 显示(0)

`ClusterHud`

0: 关闭 1: TURZX 9.2 英寸 适用于直接连接本机的 USB HUD。连接到 Jetson USB 的 HUD 自动运行，不受此设置影响。熄火后关闭屏幕；HUD 调试设置控制常亮。支持的 Jetson 运行时在推理期间通过 USB 接收 HUD、导航和信号灯信息；旧接收器更新前保留 Wi-Fi。Jetson 目标输出为 10 FPS。

<!-- CARROT:AUTO:BEGIN ClusterHud -->
<!-- CARROT:AUTO:SOURCE facts="38b537c8b45f6a307b87edb23883362b07124339c529169a48752f7136bfd487" semantic="9edf824457ea89ad8d62580c7ca4d5e4fc5c4e9c21e0b81860547c9d4b2bb10e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 显示 \> 外部HUD \> 基本
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHud -->

<!-- CARROT:MANUAL:BEGIN ClusterHud -->
<!-- CARROT:REVIEW reviewed-for="17e8e51b49d27978d564c982b7216d47db6b18c9d4a636e239f4306d3b9cdf96" reviewed-at="2026-10-16T21:40:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

启用或关闭直接 USB 或已注册的 S3 HUD。连接到 Jetson 的 HUD 不受此设置影响，会自动运行。

最新 C4 和 S3 固件 1.2.0 自动使用 H.264；旧固件或未收到功能确认时使用 JPEG。目标为 15 FPS，eGPU 启用时最高 10 FPS；实际速度取决于画面和无线连接。

通过[安装、固件与注册指南](https://upload.shind0.synology.me/models/carrot-s3/index.html)将 S3 更新一次至 1.2.0。保留 Wi-Fi/C4 注册，在同一 2.4GHz 网络自动重连。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ClusterHud -->

<!-- CARROT:SETTING:END ClusterHud -->
