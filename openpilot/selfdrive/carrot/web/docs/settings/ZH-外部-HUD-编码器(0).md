<!-- CARROT:GENERATED schema="1" locale="zh" group="HUD_SCREEN" param="ClusterHudEncoder" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 外部 HUD 编码器(0)

**菜单:** 显示 \> 外部HUD \> 画面·摄像头

---

<!-- CARROT:SETTING:BEGIN ClusterHudEncoder -->
<a id="ClusterHudEncoder"></a>

## 外部 HUD 编码器(0)

`ClusterHudEncoder`

0: Auto (Hardware H264 -\> Software H264 -\> JPEG) 1: JPEG 2: Hardware H264 3: Software H264 (ffmpeg/libx264)

<!-- CARROT:AUTO:BEGIN ClusterHudEncoder -->
<!-- CARROT:AUTO:SOURCE facts="4b7e1a46412320db427b40bc26d36e5004ac545af82c13ccb0bb97ded5f47bd0" semantic="e7f0467150d4fda3feb1928b6ea87dac5141cb3e8bea9565855221b17bb9f0e6" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `0`
- **范围:** `0` ~ `3`
- **步长:** `1`
- **菜单:** 显示 \> 外部HUD \> 画面·摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudEncoder -->

<!-- CARROT:MANUAL:BEGIN ClusterHudEncoder -->
<!-- CARROT:REVIEW reviewed-for="bfbf70df61e7ca677ecf0cdf6ba8f498aa2ce1b76fb9fc7641423889a6f5810c" reviewed-at="2026-10-16T21:40:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为



S3 Wi-Fi 确认固件 1.2.0 支持后自动选择 H.264。此设置选择硬件或软件编码器，不覆盖 Wi-Fi 编解码器选择。自动模式下两个 H.264 编码器初始化均失败时可回退 JPEG；旧 S3 固件使用 JPEG。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ClusterHudEncoder -->

<!-- CARROT:SETTING:END ClusterHudEncoder -->
