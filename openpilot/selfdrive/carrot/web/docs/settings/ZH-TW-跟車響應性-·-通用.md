<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="LeadAccelResponse" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 跟車響應性 · 通用

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN LeadAccelResponse -->
<a id="LeadAccelResponse"></a>

## 跟車響應性 · 通用

`LeadAccelResponse`

車距級別選擇使用通用值時應用。級別越低越從容，越高響應越快。0關閉加速增強，5為最大響應。所有響應級別均應用速度TF。 先確定通用值或車距專用值，再應用模式限制：節能最高2，安全最高3，普通和高速保留所選值。較低值和0不會提高，也不會改寫儲存的設定。 額外餘量保持條件在TF距離（車速×TF＋停車距離）的1.2倍以內適用，在1.2至1.5倍之間逐步解除，達到1.5倍後無論前車速度如何都會回收餘量。 不單獨記憶制動開始時的車距，也不在停車後保持該距離。

<!-- CARROT:AUTO:BEGIN LeadAccelResponse -->
<!-- CARROT:AUTO:SOURCE facts="308009f2ce8b2e886495e5de13bcf18e9c1c356e18e265305381559935e0565a" semantic="46d9ff7041e6f7680369b13cd90e72cfa05423b6ad5dbae8d537cadcb8858d89" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 0 從容跟隨 (`0`)
- **範圍:** 0 從容跟隨 (`0`) ~ 5 最大跟隨（測試） (`5`)
- **步長:** `1`
- **選項:** `0` 0 從容跟隨, `1` 1 最柔和, `2` 2 平緩跟隨, `3` 3 均衡跟隨, `4` 4 快速跟隨, `5` 5 最大跟隨（測試）
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadAccelResponse -->

<!-- CARROT:MANUAL:BEGIN LeadAccelResponse -->
<!-- CARROT:REVIEW reviewed-for="642da0e45e37822a53a84280a2fa8db34ece932cf62dd49a24ca1d9ba737377a" reviewed-at="2026-10-05T01:00:23.824710+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

應用於選擇使用通用值的巡航車距級別。級別越低恢復越從容，越高跟隨越快，同時調整加速增強和額外車距恢復。

確定通用值或車距專用響應後，節能最高2，安全最高3。普通和高速保留所選值，不提高較低值和0，也不改寫儲存值。

0～4級的額外餘量保持受距離範圍限制。基準D為車速×基本TF＋設定停車距離，不包括額外餘量。

- 不超過1.2D：使用現有保持與回收條件。
- 1.2D至1.5D：逐步降低保持餘量和補充速度，並放寬低速回收限制。
- 達到1.5D：即使前車正在遠離或已經停止，也按所選級別的速度回收餘量。

不會立即清空餘量或直接增加加速度。基本TF、停車距離、制動限制及5級不增加額外餘量的規則保持不變。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

所有響應級別均基於速度倍率和駕駛模式修正後的TF。已移除4～5級跳過速度TF的特例。保留必要制動及現有加速限制。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LeadAccelResponse -->

<!-- CARROT:SETTING:END LeadAccelResponse -->
