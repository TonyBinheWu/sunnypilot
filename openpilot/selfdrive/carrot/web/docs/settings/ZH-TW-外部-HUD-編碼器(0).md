<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_SCREEN" param="ClusterHudEncoder" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 外部 HUD 編碼器(0)

**選單:** 顯示 \> 外部HUD \> 畫面·攝影機

---

<!-- CARROT:SETTING:BEGIN ClusterHudEncoder -->
<a id="ClusterHudEncoder"></a>

## 外部 HUD 編碼器(0)

`ClusterHudEncoder`

0: Auto (Hardware H264 -\> Software H264 -\> JPEG) 1: JPEG 2: Hardware H264 3: Software H264 (ffmpeg/libx264)

<!-- CARROT:AUTO:BEGIN ClusterHudEncoder -->
<!-- CARROT:AUTO:SOURCE facts="907ca59ed180916f67903e66e169ae9366e26b060c242070fd8e6d5e97e6736a" semantic="e7f0467150d4fda3feb1928b6ea87dac5141cb3e8bea9565855221b17bb9f0e6" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 顯示 \> 外部HUD \> 畫面·攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudEncoder -->

<!-- CARROT:MANUAL:BEGIN ClusterHudEncoder -->
<!-- CARROT:REVIEW reviewed-for="bfbf70df61e7ca677ecf0cdf6ba8f498aa2ce1b76fb9fc7641423889a6f5810c" reviewed-at="2026-10-16T21:40:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為



S3 Wi-Fi 確認韌體 1.2.0 支援後自動選擇 H.264。此設定選擇硬體或軟體編碼器，不覆蓋 Wi-Fi 編解碼器選擇。自動模式下兩個 H.264 編碼器初始化均失敗時可回退 JPEG；舊 S3 韌體使用 JPEG。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ClusterHudEncoder -->

<!-- CARROT:SETTING:END ClusterHudEncoder -->
