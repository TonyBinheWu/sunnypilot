<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_AUX" param="SpeedFromPCM" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 來自 PCM 的速度 (原廠 SCC)

**選單:** 車輛與硬體 \> 車輛輔助

---

<!-- CARROT:SETTING:BEGIN SpeedFromPCM -->
<a id="SpeedFromPCM"></a>

## 來自 PCM 的速度 (原廠 SCC)

`SpeedFromPCM`

PCM 車輛速度控制。0: 彎道/攝影機減速 + 縱向控制，1: 使用原廠設定速度且不連續傳送按鈕，2: 彎道/攝影機減速，3: 本田/豐田（豐田/雷克薩斯使用原廠設定速度，不切換縱向控制模式）

<!-- CARROT:AUTO:BEGIN SpeedFromPCM -->
<!-- CARROT:AUTO:SOURCE facts="f3ba0ace6fdbe399e58b2bd9346097481361d57c35fe433aa6a331aa0b48d10d" semantic="826f2d40ddf5f91d56d0f427bee488abab5c3cb4e0d0c3487843d985b45560cc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `2`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 車輛與硬體 \> 車輛輔助
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SpeedFromPCM -->

<!-- CARROT:MANUAL:BEGIN SpeedFromPCM -->
<!-- CARROT:REVIEW reviewed-for="826f2d40ddf5f91d56d0f427bee488abab5c3cb4e0d0c3487843d985b45560cc" reviewed-at="2026-10-09T18:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### ??

豐田/雷克薩斯的 `3` 使用原廠 SET/RES 設定速度作為基本控制目標，並顯示原廠儀表設定速度。`1` 也使用原廠設定速度；`0` 和 `2` 保留現有 Carrot 速度選擇。本田的 `3` 行為不變。此設定本身不切換縱向控制器或雷達可用性。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END SpeedFromPCM -->

<!-- CARROT:SETTING:END SpeedFromPCM -->
