<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="DynamicTFollowLC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 變道響應 (100%)

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN DynamicTFollowLC -->
<a id="DynamicTFollowLC"></a>

## 變道響應 (100%)

`DynamicTFollowLC`

保持基礎 TF，僅在正常選出的前車已確認錯開且間距充足時有限放寬。以變道開始時正常選出的 leadOne/leadTwo 為基準。任一前車變化或消失後，本次變道不再額外放寬。制動只使用當前正常選出的前車，不將側方雷達候選點或開始時的歷史車輛新增為額外製動障礙物。100 不額外放寬，數值越低放寬越多，80 及以下上限相同，最多 0.25 秒且不超過 4 米。

<!-- CARROT:AUTO:BEGIN DynamicTFollowLC -->
<!-- CARROT:AUTO:SOURCE facts="b5c95f4e18dfdd3907d294e438c93cf28aa19c38fe23a02d9e1269fbfd23db07" semantic="50c56f4f2de5df94d98f4e119aa5b15e7798602f30b9dfa55b943d4e48280693" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100%`
- **範圍:** `20%` ~ `100%`
- **步長:** `5`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DynamicTFollowLC -->

<!-- CARROT:MANUAL:BEGIN DynamicTFollowLC -->
<!-- CARROT:REVIEW reviewed-for="50c56f4f2de5df94d98f4e119aa5b15e7798602f30b9dfa55b943d4e48280693" reviewed-at="2026-09-09T03:21:39.061398+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

以變道開始時正常選出的 leadOne/leadTwo 為基準。任一前車變化或消失後，本次變道不再額外放寬。制動只使用當前正常選出的前車，不將側方雷達候選點或開始時的歷史車輛新增為額外製動障礙物。

數值越高，額外放寬越少，最大值關閉放寬；數值越低，確認錯開後的放寬越多，但不超過原有上限。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

先確認預設值下的行為。缺少正常選出的第二前車或姿態資訊時，不額外放寬。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:MANUAL:END DynamicTFollowLC -->

<!-- CARROT:SETTING:END DynamicTFollowLC -->
