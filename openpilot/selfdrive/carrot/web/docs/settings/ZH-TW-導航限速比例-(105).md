<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="AutoNaviSpeedSafetyFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 導航限速比例 (105)%

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedSafetyFactor -->
<a id="AutoNaviSpeedSafetyFactor"></a>

## 導航限速比例 (105)%

`AutoNaviSpeedSafetyFactor`

在限速攝影機處將速度降至 道路限速 \* 設定值

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedSafetyFactor -->
<!-- CARROT:AUTO:SOURCE facts="9e35e062b7c360d080b505808243421e1e08fe0e4e9d6e6442b10bc384766e08" semantic="eea3adb6e5ca418ecba31e8c96f61079f384473b7d7680324d8217bbc831c7c7" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `105%`
- **範圍:** `80%` ~ `120%`
- **步長:** `1`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedSafetyFactor -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedSafetyFactor -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

設定套用至測速照相及道路速限的目標速度比例。

- **調高：** 提高相對於道路速限的目標速度。
- **調低：** 降低相對於道路速限的目標速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同速限及測速照相類型下，每次調整一項，比較減速起點、完成位置及通過速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedSafetyFactor -->

<!-- CARROT:SETTING:END AutoNaviSpeedSafetyFactor -->
