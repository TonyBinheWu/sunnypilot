<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleNaviSchoolZoneControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 原車導航 30 km/h 區域限速

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleNaviSchoolZoneControl -->
<a id="VehicleNaviSchoolZoneControl"></a>

## 原車導航 30 km/h 區域限速

`VehicleNaviSchoolZoneControl`

僅在外部導航未連線時應用。外部導航連線期間，即使沒有當前引導專案也不使用原車導航。 收到已確認的原車導航 30 km/h 限速區域進入訊號後，將目標車速限制在 30 km/h，直到收到離開訊號。此實驗功能也可能適用於非學校區域的 30 km/h 限速路段，目前尚不支援 PV5。

<!-- CARROT:AUTO:BEGIN VehicleNaviSchoolZoneControl -->
<!-- CARROT:AUTO:SOURCE facts="a797ce7985fc785f64f3ad7e7e3f10eb8c417b0a73a7edade7790cf2b4542da7" semantic="15eb22197321d7512c27030134cd141a289a4cd2499931c4f1406a9fe2630761" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviSchoolZoneControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviSchoolZoneControl -->
<!-- CARROT:REVIEW reviewed-for="15eb22197321d7512c27030134cd141a289a4cd2499931c4f1406a9fe2630761" reviewed-at="2026-09-13T07:52:41.292784+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

外部導航連線期間僅使用外部導航，即使沒有當前引導專案也不使用原車導航。確認斷開連線或接收超時後，按各項設定恢復使用原車導航。

開啟後，支援車輛在原車導航確認的30 km/h區域限制目標速度；關閉後不使用此區域限制。也可能適用於非學校區域，不支援PV5。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同時檢查外部導航連線狀態以及顯示的事件型別和剩餘距離。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviSchoolZoneControl -->

<!-- CARROT:SETTING:END VehicleNaviSchoolZoneControl -->
