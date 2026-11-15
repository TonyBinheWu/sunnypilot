<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_PATH" param="RainbowMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 彩虹道路（SP 風格）

**選單:** 顯示 \> 路徑顯示

---

<!-- CARROT:SETTING:BEGIN RainbowMode -->
<a id="RainbowMode"></a>

## 彩虹道路（SP 風格）

`RainbowMode`

橫向控制啟用時，在預測路徑上顯示 SP 風格的動態彩虹。0:關閉，1:開啟。僅改變顯示，不改變轉向、速度或路徑計算。不必重新啟動。

<!-- CARROT:AUTO:BEGIN RainbowMode -->
<!-- CARROT:AUTO:SOURCE facts="b6da2e2e9b2601921087ba99c26db3eb33759d9aaa6365058c2bcb8d8dceb1c4" semantic="1aba7ed0cb53ca634c206d22650345f906fe8d15486d15e502ccfad140063cfd" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 顯示 \> 路徑顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RainbowMode -->

<!-- CARROT:MANUAL:BEGIN RainbowMode -->
<!-- CARROT:REVIEW reviewed-for="1aba7ed0cb53ca634c206d22650345f906fe8d15486d15e502ccfad140063cfd" reviewed-at="2026-11-15T15:32:11.549173+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

開啟後，橫向控制啟用時，機器的預測路徑會使用 SP 風格的動態彩虹漸層。關閉或橫向控制未啟用時，使用原有路徑樣式。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在機器的開關選單操作，或在 Carrot Web / CarrotAssist 搜尋 `RainbowMode`。C3/C3X 與 C4 不必重新啟動即可套用；關閉後恢復原有路徑模式及顏色。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

此功能只改變路徑填色，不改變轉向、巡航速度、模型輸出或警示。網頁 / APK 的彩虹顯示另有 `vision_rainbow_lane` 設定。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END RainbowMode -->

<!-- CARROT:SETTING:END RainbowMode -->
