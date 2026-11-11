<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="LeadAccelResponseTF4" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF4 跟車響應性

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN LeadAccelResponseTF4 -->
<a id="LeadAccelResponseTF4"></a>

## TF4 跟車響應性

`LeadAccelResponseTF4`

巡航車距4級的跟車響應性。-1使用通用值，0～5僅應用於此車距級別。可設定相同的基本TF和不同的響應。 先確定通用值或車距專用值，再應用模式限制：節能最高2，安全最高3，普通和高速保留所選值。較低值和0不會提高，也不會改寫儲存的設定。 額外餘量保持條件在TF距離（車速×TF＋停車距離）的1.2倍以內適用，在1.2至1.5倍之間逐步解除，達到1.5倍後無論前車速度如何都會回收餘量。 不單獨記憶制動開始時的車距，也不在停車後保持該距離。

<!-- CARROT:AUTO:BEGIN LeadAccelResponseTF4 -->
<!-- CARROT:AUTO:SOURCE facts="34d81746afd3cda856dbbbc55170272885a1d6a7b9df56e351b9a73d4c2b98d4" semantic="98a6de3affc56a6d1146a72fe4af4fe954aaf9bca912ea89256434a150b6a595" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 使用通用值 (`-1`)
- **範圍:** 使用通用值 (`-1`) ~ 5 最大跟隨（測試） (`5`)
- **步長:** `1`
- **選項:** `-1` 使用通用值, `0` 0 從容跟隨, `1` 1 最柔和, `2` 2 平緩跟隨, `3` 3 均衡跟隨, `4` 4 快速跟隨, `5` 5 最大跟隨（測試）
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadAccelResponseTF4 -->

<!-- CARROT:MANUAL:BEGIN LeadAccelResponseTF4 -->
<!-- CARROT:REVIEW reviewed-for="86649c8bc61cf3c79e9166987b9b53dcf40b9e0456bbfdf0e5093eb888a42174" reviewed-at="2026-10-05T01:00:23.810402+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

巡航車距4級使用通用響應或單獨設定。級別越高跟隨越快，越低恢復車距越從容。

確定通用值或車距專用響應後，節能最高2，安全最高3。普通和高速保留所選值，不提高較低值和0，也不改寫儲存值。

0～4級的額外餘量保持受距離範圍限制。基準D為車速×基本TF＋設定停車距離，不包括額外餘量。

- 不超過1.2D：使用現有保持與回收條件。
- 1.2D至1.5D：逐步降低保持餘量和補充速度，並放寬低速回收限制。
- 達到1.5D：即使前車正在遠離或已經停止，也按所選級別的速度回收餘量。

不會立即清空餘量或直接增加加速度。基本TF、停車距離、制動限制及5級不增加額外餘量的規則保持不變。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

兩個車距級別可使用相同基本TF和不同響應。加速增強與額外車距恢復使用同一響應值，並保留速度TF倍率。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LeadAccelResponseTF4 -->

<!-- CARROT:SETTING:END LeadAccelResponseTF4 -->
