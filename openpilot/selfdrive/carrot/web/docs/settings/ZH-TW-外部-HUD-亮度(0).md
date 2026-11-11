<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_BASIC" param="ClusterHudBrightness" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 外部 HUD 亮度(0)

**選單:** 顯示 \> 外部HUD \> 基本

---

<!-- CARROT:SETTING:BEGIN ClusterHudBrightness -->
<a id="ClusterHudBrightness"></a>

## 外部 HUD 亮度(0)

`ClusterHudBrightness`

0: 自動 1-100: 亮度

<!-- CARROT:AUTO:BEGIN ClusterHudBrightness -->
<!-- CARROT:AUTO:SOURCE facts="504f05640be9c2cc87ed402224a9125dbf7c2d24d0cb196a29ef962f35195b82" semantic="22a87e6cddc1752b7b1eeb6748de1b1b2c63a65f6e171b170e1ca2b1f17a1ece" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0%`
- **範圍:** `0%` ~ `100%`
- **步長:** `1`
- **顯示單位:** `%`
- **選單:** 顯示 \> 外部HUD \> 基本
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudBrightness -->

<!-- CARROT:MANUAL:BEGIN ClusterHudBrightness -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- `0` — 使用自動亮度；無法取得連接主螢幕的亮度時，使用外接 HUD 的預設值。
- `1`–`100` — 將外接 HUD 亮度固定為該百分比。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

連接外接 HUD 後變更，確認方向、亮度及地圖連線。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudBrightness -->

<!-- CARROT:SETTING:END ClusterHudBrightness -->
