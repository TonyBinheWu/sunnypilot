<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="TFollowGap4" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 跟車時間(4): TimeFollow4x0.01s(160)

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN TFollowGap4 -->
<a id="TFollowGap4"></a>

## 跟車時間(4): TimeFollow4x0.01s(160)

`TFollowGap4`

巡航車距4級的基本跟車時間。50=0.50秒。應用速度TF倍率及駕駛、減速修正。

<!-- CARROT:AUTO:BEGIN TFollowGap4 -->
<!-- CARROT:AUTO:SOURCE facts="6fe67509b5568ac8045614bcd2d28ad3b328274c2320a52bf1d1a3ed83f3dcfd" semantic="a772a1a64ce8b511e296150a40a883a31e7950a6c45ae92c5a364b37c775e817" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `160`
- **範圍:** `40` ~ `300`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap4 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap4 -->
<!-- CARROT:REVIEW reviewed-for="a772a1a64ce8b511e296150a40a883a31e7950a6c45ae92c5a364b37c775e817" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

巡航車距4級的基本跟車時間。增大則基本車距變長，減小則變短。應用速度TF倍率及駕駛、減速修正。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

儲存值50表示0.50秒。不同車距級別可設定相同基本TF和不同前車響應。路徑上的橫條及米數表示動態修正後的跟車目標距離。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap4 -->

<!-- CARROT:SETTING:END TFollowGap4 -->
