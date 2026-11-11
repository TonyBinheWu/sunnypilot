<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="AutoTurnControlTurnEnd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC: 速度控制剩餘時間(3)

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlTurnEnd -->
<a id="AutoTurnControlTurnEnd"></a>

## ATC: 速度控制剩餘時間(3)

`AutoTurnControlTurnEnd`

(APN) NOO 完成時間距離 (速度 × 時間)

<!-- CARROT:AUTO:BEGIN AutoTurnControlTurnEnd -->
<!-- CARROT:AUTO:SOURCE facts="f04ab1f254e10a643fbb81944550088c6a4411379591b82a9c1496e646ab7ed0" semantic="55ebb6f698365577e35dd91320b04f3f559583fa75f0b6bffd5f11af27bea89d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `6`
- **範圍:** `0` ~ `30`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlTurnEnd -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlTurnEnd -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

（APN）NOO 完成時間對應的距離（速度 × 時間）。

- **調高：** 增加適用的時間或延遲。
- **調低：** 減少時間或延遲。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在車道線清楚且附近無車流處測試，確認打方向燈後的等待、車道檢查及完成時機。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoTurnControlTurnEnd -->

<!-- CARROT:SETTING:END AutoTurnControlTurnEnd -->
