<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_LIMIT" param="AutoRoadSpeedLimitOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 道路限速偏移 (-1)

**選單:** 駕駛控制 \> 速度與減速 \> 限速

---

<!-- CARROT:SETTING:BEGIN AutoRoadSpeedLimitOffset -->
<a id="AutoRoadSpeedLimitOffset"></a>

## 道路限速偏移 (-1)

`AutoRoadSpeedLimitOffset`

道路限速 + 設定值, -1: 不使用

<!-- CARROT:AUTO:BEGIN AutoRoadSpeedLimitOffset -->
<!-- CARROT:AUTO:SOURCE facts="af66f1f2beefa38a2fd0d1371a65dfa7a8017703bccadce5f8ef3350d475a176" semantic="4e35d5a4d2ce2702b10b336d7e982781e60ea48724b8f97f29540fa36a14137d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `-1km/h`
- **範圍:** `-1km/h` ~ `100km/h`
- **步長:** `1`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 速度與減速 \> 限速
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoRoadSpeedLimitOffset -->

<!-- CARROT:MANUAL:BEGIN AutoRoadSpeedLimitOffset -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

道路速限加上設定值。

- **調高：** 將修正值往正方向調整。
- **調低：** 將其往負方向調整。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在同一個道路速限變更路段，確認新的目標速度及切換時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `-1` 會停用依道路速限計算的目標速度。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoRoadSpeedLimitOffset -->

<!-- CARROT:SETTING:END AutoRoadSpeedLimitOffset -->
