<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="AutoNaviSpeedCtrlEnd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 導航減速結束點 (6秒)

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedCtrlEnd -->
<a id="AutoNaviSpeedCtrlEnd"></a>

## 導航減速結束點 (6秒)

`AutoNaviSpeedCtrlEnd`

基於 速度 x 時間 的減速完成時間

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedCtrlEnd -->
<!-- CARROT:AUTO:SOURCE facts="25aa1b685b7f0fb667c16bff1a7b12e6d38331ffb59a2d2110048018d506a316" semantic="310d348eaca8548ab5ee44af0a5126ab993dcc4265cbb669485438b669022d38" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `6s`
- **範圍:** `3s` ~ `20s`
- **步長:** `1`
- **顯示單位:** `s`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedCtrlEnd -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedCtrlEnd -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

設定在測速照相或速限位置之前達到目標速度的時間基準。

- **調高：** 在目標點前更遠處達到目標速度，較早完成減速。
- **調低：** 在更接近目標點的位置達到目標速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同速限及測速照相類型下，每次調整一項，比較減速起點、完成位置及通過速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedCtrlEnd -->

<!-- CARROT:SETTING:END AutoNaviSpeedCtrlEnd -->
