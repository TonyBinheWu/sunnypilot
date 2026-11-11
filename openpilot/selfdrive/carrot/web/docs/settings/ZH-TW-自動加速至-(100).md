<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_LIMIT" param="AutoSpeedUptoRoadSpeedLimit" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自動加速至: (100)%

**選單:** 駕駛控制 \> 速度與減速 \> 限速

---

<!-- CARROT:SETTING:BEGIN AutoSpeedUptoRoadSpeedLimit -->
<a id="AutoSpeedUptoRoadSpeedLimit"></a>

## 自動加速至: (100)%

`AutoSpeedUptoRoadSpeedLimit`

當前方有車時自動加速，最高至 (道路限速 x 比例)

<!-- CARROT:AUTO:BEGIN AutoSpeedUptoRoadSpeedLimit -->
<!-- CARROT:AUTO:SOURCE facts="fb4fdfc08c591e81f9c784cc7dc5ac82f362d84c7ae325350ef0b1db1a3c9d71" semantic="c05370fd34043aeafdf056f429b15308e3f72dadec462c9d4d3b6c332b0d48d1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0%`
- **範圍:** `0%` ~ `200%`
- **步長:** `10`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 速度與減速 \> 限速
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoSpeedUptoRoadSpeedLimit -->

<!-- CARROT:MANUAL:BEGIN AutoSpeedUptoRoadSpeedLimit -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- `0` — 停用依前車狀態自動提高設定速度。
- **正值：** 60 m 內的前車速度接近目前設定速度時，以每次 5 km/h 提高設定速度，最高為道路速限乘以此倍率。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在同一個道路速限變更路段，確認新的目標速度及切換時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoSpeedUptoRoadSpeedLimit -->

<!-- CARROT:SETTING:END AutoSpeedUptoRoadSpeedLimit -->
