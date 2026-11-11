<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="TFollowGap3" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 跟車時間(3): TimeFollow3x0.01s(140)

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN TFollowGap3 -->
<a id="TFollowGap3"></a>

## 跟車時間(3): TimeFollow3x0.01s(140)

`TFollowGap3`

巡航車距3級的基本跟車時間。50=0.50秒。應用速度TF倍率及駕駛、減速修正。

<!-- CARROT:AUTO:BEGIN TFollowGap3 -->
<!-- CARROT:AUTO:SOURCE facts="e71759b0d8c78965cf4a59b566b4c0e7dc7dc4390f8ccb0c58f9bbbc17245ea6" semantic="9716f07b3b27c698d4848f5f0616674737d977a27f883067bb593444a3008774" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `140`
- **範圍:** `40` ~ `300`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap3 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap3 -->
<!-- CARROT:REVIEW reviewed-for="9716f07b3b27c698d4848f5f0616674737d977a27f883067bb593444a3008774" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

巡航車距3級的基本跟車時間。增大則基本車距變長，減小則變短。應用速度TF倍率及駕駛、減速修正。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

儲存值50表示0.50秒。不同車距級別可設定相同基本TF和不同前車響應。路徑上的橫條及米數表示動態修正後的跟車目標距離。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap3 -->

<!-- CARROT:SETTING:END TFollowGap3 -->
