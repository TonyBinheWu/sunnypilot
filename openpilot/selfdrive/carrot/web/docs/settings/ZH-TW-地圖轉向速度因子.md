<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CURVE" param="MapTurnSpeedFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 地圖轉向速度因子

**選單:** 駕駛控制 \> 速度與減速 \> 彎道與轉彎

---

<!-- CARROT:SETTING:BEGIN MapTurnSpeedFactor -->
<a id="MapTurnSpeedFactor"></a>

## 地圖轉向速度因子

`MapTurnSpeedFactor`

值越小，沿路線減速越多。

<!-- CARROT:AUTO:BEGIN MapTurnSpeedFactor -->
<!-- CARROT:AUTO:SOURCE facts="99561831bf75f1645ebd66957cb8c652151252bcd054566e51ca92dfd3c489b2" semantic="70911cfe4337b36f9b1812b46852781a33788b52e9f58c2bf5e64debf1f9fa80" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100%`
- **範圍:** `50%` ~ `300%`
- **步長:** `10`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 速度與減速 \> 彎道與轉彎
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MapTurnSpeedFactor -->

<!-- CARROT:MANUAL:BEGIN MapTurnSpeedFactor -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

數值越小，沿路線降低的速度越多。

- **調高：** 減少導航轉彎時的減速。
- **調低：** 增加依導航路線進行的減速。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同彎道與路線導引條件下，每次調整一項，比較入彎前的目標及過彎速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> 此設定僅在已連接依路線提供的轉彎資訊時生效。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MapTurnSpeedFactor -->

<!-- CARROT:SETTING:END MapTurnSpeedFactor -->
