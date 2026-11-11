<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="LeadAccelResponseTF1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF1 跟車響應性

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN LeadAccelResponseTF1 -->
<a id="LeadAccelResponseTF1"></a>

## TF1 跟車響應性

`LeadAccelResponseTF1`

巡航車距1級的跟車響應性。-1使用通用值，0～5僅應用於此車距級別。可設定相同的基本TF和不同的響應。 先確定通用值或車距專用值，再應用模式限制：節能最高2，安全最高3，普通和高速保留所選值。較低值和0不會提高，也不會改寫儲存的設定。 額外餘量保持條件在TF距離（車速×TF＋停車距離）的1.2倍以內適用，在1.2至1.5倍之間逐步解除，達到1.5倍後無論前車速度如何都會回收餘量。 不單獨記憶制動開始時的車距，也不在停車後保持該距離。

<!-- CARROT:AUTO:BEGIN LeadAccelResponseTF1 -->
<!-- CARROT:AUTO:SOURCE facts="5eaa3eefcac91655098f0d0b0a86cf6395524928b50407dccb71df8337816fbf" semantic="095edb40730e0a41998e0ade9729636a60de3f36b5e93f22b4eaf6a85acb84f3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 使用通用值 (`-1`)
- **範圍:** 使用通用值 (`-1`) ~ 5 最大跟隨（測試） (`5`)
- **步長:** `1`
- **選項:** `-1` 使用通用值, `0` 0 從容跟隨, `1` 1 最柔和, `2` 2 平緩跟隨, `3` 3 均衡跟隨, `4` 4 快速跟隨, `5` 5 最大跟隨（測試）
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadAccelResponseTF1 -->

<!-- CARROT:MANUAL:BEGIN LeadAccelResponseTF1 -->
<!-- CARROT:REVIEW reviewed-for="92118c8853805bdcfe52a1837ccd9c3dd6925e1d8ee95a39b9ae408011a0f056" reviewed-at="2026-10-05T01:00:23.807350+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

巡航車距1級使用通用響應或單獨設定。級別越高跟隨越快，越低恢復車距越從容。

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

<!-- CARROT:MANUAL:END LeadAccelResponseTF1 -->

<!-- CARROT:SETTING:END LeadAccelResponseTF1 -->
