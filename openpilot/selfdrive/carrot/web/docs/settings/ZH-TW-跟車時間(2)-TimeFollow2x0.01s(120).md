<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="TFollowGap2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 跟車時間(2): TimeFollow2x0.01s(120)

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN TFollowGap2 -->
<a id="TFollowGap2"></a>

## 跟車時間(2): TimeFollow2x0.01s(120)

`TFollowGap2`

巡航車距2級的基本跟車時間。50=0.50秒。應用速度TF倍率及駕駛、減速修正。

<!-- CARROT:AUTO:BEGIN TFollowGap2 -->
<!-- CARROT:AUTO:SOURCE facts="c640bfd245e9848ce4b896b8feba03217cddde66468d18a3f69f7e4c3e4de242" semantic="4352d22a167ac26fa0a74811c302d3a719e21aaf91e7e7767b23e77fec61b555" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `120`
- **範圍:** `40` ~ `300`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap2 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap2 -->
<!-- CARROT:REVIEW reviewed-for="4352d22a167ac26fa0a74811c302d3a719e21aaf91e7e7767b23e77fec61b555" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

巡航車距2級的基本跟車時間。增大則基本車距變長，減小則變短。應用速度TF倍率及駕駛、減速修正。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

儲存值50表示0.50秒。不同車距級別可設定相同基本TF和不同前車響應。路徑上的橫條及米數表示動態修正後的跟車目標距離。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap2 -->

<!-- CARROT:SETTING:END TFollowGap2 -->
