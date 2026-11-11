<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_LIMIT" param="AutoRoadSpeedAdjust" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自動道路限速調整 (50)%

**選單:** 駕駛控制 \> 速度與減速 \> 限速

---

<!-- CARROT:SETTING:BEGIN AutoRoadSpeedAdjust -->
<a id="AutoRoadSpeedAdjust"></a>

## 自動道路限速調整 (50)%

`AutoRoadSpeedAdjust`

-1: 設定道路限速, 100: 新道路速度, 50: 中值, 0: 不改變

<!-- CARROT:AUTO:BEGIN AutoRoadSpeedAdjust -->
<!-- CARROT:AUTO:SOURCE facts="da21a0355e035d209b2640ea7864db0693a0cdb0751fea60b00fde6c86bd542e" semantic="c5639d7240a075f5e1e1594a87177824bc3d8bf0192fbf8b3dc2b51a26ea762a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0%`
- **範圍:** `-1%` ~ `100%`
- **步長:** `10`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 速度與減速 \> 限速
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoRoadSpeedAdjust -->

<!-- CARROT:MANUAL:BEGIN AutoRoadSpeedAdjust -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- `-1` — 道路速限改變時，立即採用新的道路速限目標速度。
- `0` — 保留既有巡航設定速度。
- `1`–`99` — 將既有設定速度與降低後的新道路速限混合計算；數值越高，越接近新速限。
- `100` — 直接套用降低後的新道路速限。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在同一個道路速限變更路段，確認新的目標速度及切換時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoRoadSpeedAdjust -->

<!-- CARROT:SETTING:END AutoRoadSpeedAdjust -->
