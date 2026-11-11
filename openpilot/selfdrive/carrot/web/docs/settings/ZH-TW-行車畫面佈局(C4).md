<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_BRIGHT" param="ShowModelView" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 行車畫面佈局(C4)

**選單:** 顯示 \> 亮度與檢視

---

<!-- CARROT:SETTING:BEGIN ShowModelView -->
<a id="ShowModelView"></a>

## 行車畫面佈局(C4)

`ShowModelView`

選擇 C4 行車畫面的攝影機影片和車道線/行駛路徑圖形。車道線/路徑圖形包含前車標記。 不受亮度設定影響，行車中更改後約 5 秒內生效。 即使隱藏兩者，速度和警告仍會顯示。連線外部 HUD 時，優先遵循“外部 HUD 連線時本機攝影機”設定。

<!-- CARROT:AUTO:BEGIN ShowModelView -->
<!-- CARROT:AUTO:SOURCE facts="40f3c89cb19b2af448603676555c50f83711fa094460a45b95193aed0234d89e" semantic="0fbb289950310b907ca1e85a973172fac18f0381fcd7718d1a6f3ebf584a61ce" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 0 攝影機 + 車道線/路徑 (`0`)
- **範圍:** 0 攝影機 + 車道線/路徑 (`0`) ~ 3 隱藏兩者 (`3`)
- **步長:** `1`
- **選項:** `0` 0 攝影機 + 車道線/路徑, `1` 1 僅攝影機, `2` 2 僅車道線/路徑, `3` 3 隱藏兩者
- **選單:** 顯示 \> 亮度與檢視
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowModelView -->

<!-- CARROT:MANUAL:BEGIN ShowModelView -->
<!-- CARROT:REVIEW reviewed-for="c8040075196baa91f6b37ffa483d6e1197e44f8bd97dd6bfca9c50ab762b41de" reviewed-at="2026-10-08T09:28:59.208385+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 動作

選擇 C4 行車畫面的影片和圖形。車道線/路徑圖形包含前車標記。

- `0` — 在攝像頭影片上顯示車道線/路徑。
- `1` — 僅顯示攝像頭影片。
- `2` — 在黑色背景上顯示車道線/路徑。
- `3` — 隱藏影片和車道線/路徑，速度、警告和駕駛員狀態仍會顯示。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

不受亮度設定影響，進入行車模式後無需額外等待。行車中更改後約五秒內生效，無需重啟。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

不適用於 C3/C3X。連線外部 HUD 且 `ShowCameraWithCluster=0` 時，無論此處如何選擇，本機攝像頭影片和車道線/路徑都會隱藏。

不改變攝像頭拍攝、駕駛判斷或車輛控制。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ShowModelView -->

<!-- CARROT:SETTING:END ShowModelView -->
