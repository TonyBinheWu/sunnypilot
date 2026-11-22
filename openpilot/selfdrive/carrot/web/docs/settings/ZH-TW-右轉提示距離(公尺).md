<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="AutoTurnControlRightLaneChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 右轉提示距離（公尺）

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlRightLaneChange -->
<a id="AutoTurnControlRightLaneChange"></a>

## 右轉提示距離（公尺）

`AutoTurnControlRightLaneChange`

支援的方向燈配件會在這個距離內檢查右轉或右側分岔提示。0 公尺關閉，最遠 500 公尺。適用於 ATC 模式 1 或 2，且自動方向燈設為模式 2。變換車道由駕駛確認。

<!-- CARROT:AUTO:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:AUTO:SOURCE facts="196ae9618be670c447fdd300768bc92ea372f99cf6b69f5addc7d95c0bb42089" semantic="517c131dc727f1d4463382c4d3c83de1677184ce198f650ff90d5937e35160e1" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `500`
- **步長:** `50`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlRightLaneChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:REVIEW reviewed-for="517c131dc727f1d4463382c4d3c83de1677184ce198f650ff90d5937e35160e1" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

支援的方向燈配件會在這個距離內檢查右轉或右側分岔提示。0 公尺關閉，最遠 500 公尺。適用於 ATC 模式 1 或 2，且自動方向燈設為模式 2。變換車道由駕駛確認。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoTurnControlRightLaneChange -->

<!-- CARROT:SETTING:END AutoTurnControlRightLaneChange -->
