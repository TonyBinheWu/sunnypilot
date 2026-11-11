<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleNaviCanControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 車輛導航 CAN 減速應用模式

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleNaviCanControl -->
<a id="VehicleNaviCanControl"></a>

## 車輛導航 CAN 減速應用模式

`VehicleNaviCanControl`

僅在外部導航未連線時應用。外部導航連線期間，即使沒有當前引導專案也不使用原車導航。 選擇何時使用原車導航 CAN 的攝影機和減速帶實際距離進行減速。路徑匹配是指 vNAVI 的未來事件與當前計算路線及路徑一致。 0：禁用 1：攝影機和減速帶始終應用 2：攝影機始終應用，減速帶僅在路徑匹配時應用 3：攝影機和減速帶僅在路徑匹配時應用 路徑資料超過兩秒未更新時按無路徑處理。車輛直接確認的當前攝影機狀態由 VehicleSpeedCameraControlMode 單獨控制。PV5 直接確認的區間測速狀態在模式 1～3 中保持有效。此為實驗功能，請僅在已驗證車輛上使用。 當前攝影機警告僅關聯限速相同且距離較近的候選；若只有同限速的遠處攝影機，則使用當前警告自身的虛擬距離。

<!-- CARROT:AUTO:BEGIN VehicleNaviCanControl -->
<!-- CARROT:AUTO:SOURCE facts="9174f881d199d4e82cb68f58c46826c7a5fe290a0dc334e0569318d304630831" semantic="f8d1712821a73e6fe7eba60cf61124d25e39d1cbafcd0c3129f9732ab42f4b13" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 禁用 (`0`)
- **範圍:** 禁用 (`0`) ~ 攝影機和減速帶按路徑 (`3`)
- **步長:** `1`
- **選項:** `0` 禁用, `1` 攝影機和減速帶始終應用, `2` 攝影機始終、減速帶按路徑, `3` 攝影機和減速帶按路徑
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviCanControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviCanControl -->
<!-- CARROT:REVIEW reviewed-for="9598e2a6ce6b00dcd5e8a0f1feae8f420e87990f1a27edc0aa0a46bbff15d34b" reviewed-at="2026-09-13T09:14:59.934316+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

外部導航連線期間僅使用外部導航，即使沒有當前引導專案也不使用原車導航。確認斷開連線或接收超時後，按各項設定恢復使用原車導航。

未連線外部導航時，0禁用；1不論路線引導狀態均使用攝像頭和減速帶；2始終使用攝像頭，僅在路線匹配時使用減速帶；3兩者均要求路線匹配。車輛直接確認的當前攝像頭狀態遵循車輛接收攝像頭減速設定。
當前攝像頭警告僅關聯限速相同且距離較近的候選。若只有同限速的遠處攝像頭，當前警告使用自身的虛擬距離，遠處攝像頭仍保留供後續接近時使用。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同時檢查外部導航連線狀態以及顯示的事件型別和剩餘距離。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviCanControl -->

<!-- CARROT:SETTING:END VehicleNaviCanControl -->
