<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="AutoTurnControlSpeedTurn" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC: 轉向速度(20)

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlSpeedTurn -->
<a id="AutoTurnControlSpeedTurn"></a>

## ATC: 轉向速度(20)

`AutoTurnControlSpeedTurn`

(APN) 0: 不使用, 轉向速度

<!-- CARROT:AUTO:BEGIN AutoTurnControlSpeedTurn -->
<!-- CARROT:AUTO:SOURCE facts="216705c05bce23de39e91ba3a6470a02264f1f9b79055c04890640a346884236" semantic="faad48b2a790f2c99af8ac2842c96d8e3a430972367fdf5e0eb2fa6ebfc3f18f" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `20km/h`
- **範圍:** `0km/h` ~ `100km/h`
- **步長:** `5`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlSpeedTurn -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlSpeedTurn -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

（APN）0：不使用；轉彎速度。

- **調高：** 提高適用的速度或速度門檻。
- **調低：** 降低速度或門檻。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在車道線清楚且附近無車流處測試，確認打方向燈後的等待、車道檢查及完成時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `0` 會停用 ATC 轉彎目標速度。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoTurnControlSpeedTurn -->

<!-- CARROT:SETTING:END AutoTurnControlSpeedTurn -->
