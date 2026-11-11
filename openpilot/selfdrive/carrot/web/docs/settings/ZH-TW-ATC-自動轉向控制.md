<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="AutoTurnControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC: 自動轉向控制

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControl -->
<a id="AutoTurnControl"></a>

## ATC: 自動轉向控制

`AutoTurnControl`

0: 關閉，1: 變道/轉彎，2: 變道/轉彎+速度，3: 速度。右轉前自動變道距離在詳細設定中調整，0米關閉，僅在模式1或2下工作。

<!-- CARROT:AUTO:BEGIN AutoTurnControl -->
<!-- CARROT:AUTO:SOURCE facts="0485f3de174eae3c28f416c4668530f0e5b13c3533234d6d7076b0e8364acc9b" semantic="e075079f91a03599fc073d2fd981a0d2f880dba4f6b9252ca9cc7782a5ecb64d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControl -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControl -->
<!-- CARROT:REVIEW reviewed-for="e075079f91a03599fc073d2fd981a0d2f880dba4f6b9252ca9cc7782a5ecb64d" reviewed-at="2026-11-02T22:15:29.548185+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

0關閉ATC，1控制變道和轉彎，2同時控制速度，3僅控制速度。右轉距離附加功能在模式1或2下於設定距離內請求右轉向燈。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

在ATC詳細設定中選擇右轉前自動變道距離。增大距離會更早檢查條件，減小距離則靠近轉彎後檢查。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

重啟時舊模式4轉換為模式1。沒有單獨距離設定時使用250米，已明確設定的值予以保留。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END AutoTurnControl -->

<!-- CARROT:SETTING:END AutoTurnControl -->
