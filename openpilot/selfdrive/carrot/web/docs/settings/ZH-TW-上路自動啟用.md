<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_START" param="AutoEngage" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 上路自動啟用

**選單:** 駕駛控制 \> 啟動·自動 \> 起步動作

---

<!-- CARROT:SETTING:BEGIN AutoEngage -->
<a id="AutoEngage"></a>

## 上路自動啟用

`AutoEngage`

1: 僅轉向, 2: 轉向開啟 + 巡航待機

<!-- CARROT:AUTO:BEGIN AutoEngage -->
<!-- CARROT:AUTO:SOURCE facts="c08687404a92c1a8535318a05201cdbf6249036f57108c744e467567ad2e79c1" semantic="5d795f951b628b849d1157749c4b492dddea109419cdb315856d2246614b812e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 駕駛控制 \> 啟動·自動 \> 起步動作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoEngage -->

<!-- CARROT:MANUAL:BEGIN AutoEngage -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

此設定選擇開始行車時的初始橫向控制及巡航待命狀態，本身不會立即開始轉向、加速或煞車。

- `0` — 不自動啟用橫向控制或巡航待命。
- `1` — 僅啟用橫向控制。
- `2` — 啟用橫向控制，並在支援車輛上啟用巡航待命。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

安全停妥後變更，並於下次行車確認結果。

| 預期行為 | 搭配使用的設定 |
|---|---|
| 開始行車即轉向，僅手動啟用巡航 | `AutoEngage=1`, `AlwaysLateral=1`, `AutoCruiseControl=0` |
| 開始行車即轉向，條件允許時自動巡航 | `AutoEngage=2`, `AlwaysLateral=1`, `AutoCruiseControl=1` |
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> `AlwaysLateral=0` 時，即使選擇 `1` 或 `2`，巡航未啟用時仍不會提供實際輔助轉向。若需要轉向獨立於巡航保持可用，請使用 `AlwaysLateral=1`。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoEngage -->

<!-- CARROT:SETTING:END AutoEngage -->
