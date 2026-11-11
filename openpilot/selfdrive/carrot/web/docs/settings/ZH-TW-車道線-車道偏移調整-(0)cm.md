<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANEMODE" param="AdjustLaneOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 車道線: 車道偏移調整 (0)cm

**選單:** 駕駛控制 \> 轉向 \> 車道模式

---

<!-- CARROT:SETTING:BEGIN AdjustLaneOffset -->
<a id="AdjustLaneOffset"></a>

## 車道線: 車道偏移調整 (0)cm

`AdjustLaneOffset`

向路緣/彎道內側修正

<!-- CARROT:AUTO:BEGIN AdjustLaneOffset -->
<!-- CARROT:AUTO:SOURCE facts="ac1fa2cf830fc808331d069ea2d7d14247a14dcf727bd48be469aa5e3fa29bc7" semantic="919b501dd31d3d3f258b212892e8fb3d2436b4872e6787e10d4fb65765fa6cfb" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0cm`
- **範圍:** `0cm` ~ `500cm`
- **步長:** `10`
- **顯示單位:** `cm`
- **選單:** 駕駛控制 \> 轉向 \> 車道模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AdjustLaneOffset -->

<!-- CARROT:MANUAL:BEGIN AdjustLaneOffset -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

朝道路邊緣／彎道內側修正。

- **調高：** 將修正值往正方向調整。
- **調低：** 將其往負方向調整。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同車道及彎道重複測試，每次調整一項，同時比較路徑追蹤、轉向反應及平順度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 不適當的數值可能降低轉向或縱向控制的穩定性與舒適度。每次只小幅調整一項，行為異常時恢復預設值。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AdjustLaneOffset -->

<!-- CARROT:SETTING:END AdjustLaneOffset -->
