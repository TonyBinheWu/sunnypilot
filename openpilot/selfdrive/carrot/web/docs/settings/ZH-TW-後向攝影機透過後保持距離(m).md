<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="AutoNaviRearCameraHoldDistance" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 後向攝影機透過後保持距離(m)

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN AutoNaviRearCameraHoldDistance -->
<a id="AutoNaviRearCameraHoldDistance"></a>

## 後向攝影機透過後保持距離(m)

`AutoNaviRearCameraHoldDistance`

外部導航報告後向測速或後向闖紅燈及測速攝影機（TMAP 75/76）時，透過攝影機後繼續在此距離內保持目標速度上限。在最後50米記錄位置，即使提示消失或切換到下一專案，仍按行駛距離跟蹤。單位為米；0關閉額外保持。增大數值會保持更遠，停車不消耗距離。斷開連線、偏離路線或導航會話變化時清除。原車CAN無法識別後向型別，因此此距離不適用於原車警告。倒計時結束不代表保持結束。

<!-- CARROT:AUTO:BEGIN AutoNaviRearCameraHoldDistance -->
<!-- CARROT:AUTO:SOURCE facts="c45ffd6886e02f3f876e507d9b9343e907648c86024976d48a28c2d58b54fc62" semantic="8b904f46c8e8a1e5c6c381366357034716287800c77b9036e8dc99eac2ec8689" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100`
- **範圍:** `0` ~ `300`
- **步長:** `10`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviRearCameraHoldDistance -->

<!-- CARROT:MANUAL:BEGIN AutoNaviRearCameraHoldDistance -->
<!-- CARROT:REVIEW reviewed-for="8b904f46c8e8a1e5c6c381366357034716287800c77b9036e8dc99eac2ec8689" reviewed-at="2026-09-13T09:14:59.726525+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

外部導航報告後向測速或後向闖紅燈及測速攝像頭（TMAP 75/76）時，透過後繼續保持目標速度上限。增大數值會保持更遠，減小會更早解除，0關閉額外保持。

在最後50米記錄位置並按行駛距離跟蹤。提示消失或切換到下一專案後仍保持，停車不消耗距離。其他控制要求更低速度時仍優先採用更低速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

顯示和儲存單位為米。倒計時在攝像頭處結束，後向測速保持距離單獨顯示。外部連線斷開、偏離路線、新會話、行駛距離重置或關閉攝像頭控制時清除保持狀態。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

原車CAN無法識別後向型別，因此不應用此額外距離。設定距離並不保證實際裝置已經結束測量。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviRearCameraHoldDistance -->

<!-- CARROT:SETTING:END AutoNaviRearCameraHoldDistance -->
