<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CURVE" param="TurnSpeedControlMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 轉向速度控制模式

**選單:** 駕駛控制 \> 速度與減速 \> 彎道與轉彎

---

<!-- CARROT:SETTING:BEGIN TurnSpeedControlMode -->
<a id="TurnSpeedControlMode"></a>

## 轉向速度控制模式

`TurnSpeedControlMode`

0: 不使用, 1: 視覺, 2: 視覺 + 路線, 3: 路線 (始終)

<!-- CARROT:AUTO:BEGIN TurnSpeedControlMode -->
<!-- CARROT:AUTO:SOURCE facts="200c7a98733beafe26ce792204011f97eb3c4b95ae88d82d51b000c154e24f3f" semantic="0e0a5e58e9061594b9a41986ec433b7b6680c5f6ce99da897cd9b4e52ded8e38" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `1`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 彎道與轉彎
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TurnSpeedControlMode -->

<!-- CARROT:MANUAL:BEGIN TurnSpeedControlMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 不使用
- `1` — 視覺
- `2` — 視覺＋導航路線
- `3` — 導航路線（持續使用）
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同彎道與路線導引條件下，每次調整一項，比較入彎前的目標及過彎速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TurnSpeedControlMode -->

<!-- CARROT:SETTING:END TurnSpeedControlMode -->
