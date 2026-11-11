<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="TFollowGap1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 跟車時間(1): TimeFollow1x0.01s(110)

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN TFollowGap1 -->
<a id="TFollowGap1"></a>

## 跟車時間(1): TimeFollow1x0.01s(110)

`TFollowGap1`

巡航車距1級的基本跟車時間。50=0.50秒。應用速度TF倍率及駕駛、減速修正。

<!-- CARROT:AUTO:BEGIN TFollowGap1 -->
<!-- CARROT:AUTO:SOURCE facts="c05eace2b07e8ed7324fa61e4256cee353b47c04970e860f94d1fc8ebd0ee736" semantic="ed3db450ac23993e30fe62a41b6390389aef7f0343a5afe4ff667f18b0fc589a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `110`
- **範圍:** `40` ~ `300`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap1 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap1 -->
<!-- CARROT:REVIEW reviewed-for="ed3db450ac23993e30fe62a41b6390389aef7f0343a5afe4ff667f18b0fc589a" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

巡航車距1級的基本跟車時間。增大則基本車距變長，減小則變短。應用速度TF倍率及駕駛、減速修正。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

儲存值50表示0.50秒。不同車距級別可設定相同基本TF和不同前車響應。路徑上的橫條及米數表示動態修正後的跟車目標距離。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap1 -->

<!-- CARROT:SETTING:END TFollowGap1 -->
