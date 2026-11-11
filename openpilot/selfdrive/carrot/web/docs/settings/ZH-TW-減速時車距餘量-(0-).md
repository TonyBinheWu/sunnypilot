<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="TFollowDecelBoost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 減速時車距餘量 (0%)

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN TFollowDecelBoost -->
<a id="TFollowDecelBoost"></a>

## 減速時車距餘量 (0%)

`TFollowDecelBoost`

根據減速強度在基礎目標車距上只增加一次餘量，持續減速時不會重複累加。數值越高餘量越大，減速減弱時逐漸釋放。0%關閉額外餘量，已施加的餘量會逐漸解除。減速時仍保留基礎車距縮短暫停功能。

<!-- CARROT:AUTO:BEGIN TFollowDecelBoost -->
<!-- CARROT:AUTO:SOURCE facts="57f922cca3bb4476d27241721d0967c7419c5edf6058edb2492c2282ceacf61e" semantic="a003496b606637110045bb4c8096e6fd7af91b9b8c2778f41be61772125c46ca" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0%`
- **範圍:** `0%` ~ `100%`
- **步長:** `10`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowDecelBoost -->

<!-- CARROT:MANUAL:BEGIN TFollowDecelBoost -->
<!-- CARROT:REVIEW reviewed-for="a003496b606637110045bb4c8096e6fd7af91b9b8c2778f41be61772125c46ca" reviewed-at="2026-09-09T08:56:50.274086+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 工作方式

根據減速強度在基礎目標車距上只增加一次餘量，持續制動時不會重複累加。數值越高額外空間越大，數值越低越小。

減速減弱時逐漸釋放額外餘量，減速增強時及時更新。關閉設定後已施加的餘量逐漸解除，但保留制動期間基礎車距縮短暫停功能。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

用於調整減速時的車距餘量，不改變基礎跟車時間設定。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:MANUAL:END TFollowDecelBoost -->

<!-- CARROT:SETTING:END TFollowDecelBoost -->
