<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="LaneLineCheck" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 變道車道判斷

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN LaneLineCheck -->
<a id="LaneLineCheck"></a>

## 變道車道判斷

`LaneLineCheck`

0: 顏色+型別(黃線阻止), 1: 僅型別(虛線/實線), 2: 僅型別+實線扭矩override

<!-- CARROT:AUTO:BEGIN LaneLineCheck -->
<!-- CARROT:AUTO:SOURCE facts="5c110b602bbb0277fc480eb105d9af012b956530bd724eab8fd4a006e44c26bd" semantic="5977a88be710cace4de2e0c770c5dc27e274c2c55f3693f68730b76f98956e5e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneLineCheck -->

<!-- CARROT:MANUAL:BEGIN LaneLineCheck -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 顏色＋類型（阻擋時顯示黃色）
- `1` — 僅類型
- `2` — 類型＋駕駛施加扭矩時顯示實線
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在車道線清楚且附近無車流處測試，確認打方向燈後的等待、車道檢查及完成時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

攝影機或車輛可能誤判標線，允許越過實線也不代表跨越實線安全或合法。請參閱[變換車道說明（英文）](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/lane-change.md)。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneLineCheck -->

<!-- CARROT:SETTING:END LaneLineCheck -->
