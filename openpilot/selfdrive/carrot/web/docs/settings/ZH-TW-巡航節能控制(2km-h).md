<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_CARROT" param="CruiseEcoControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航節能控制(2km/h)

**選單:** 駕駛控制 \> 巡航與車距 \> Carrot巡航

---

<!-- CARROT:SETTING:BEGIN CruiseEcoControl -->
<a id="CruiseEcoControl"></a>

## 巡航節能控制(2km/h)

`CruiseEcoControl`

為提高燃油效率臨時提高目標速度

<!-- CARROT:AUTO:BEGIN CruiseEcoControl -->
<!-- CARROT:AUTO:SOURCE facts="82a0a435baa39d2f4a489a78d8fca66035928009d1f2cb13dae5942d6bf9676f" semantic="246d47bc61ed89bbb5fb72086ee161e3d96147de49d94b9b9459f285b9fc06e3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `2km/h`
- **範圍:** `0km/h` ~ `10km/h`
- **步長:** `1`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 巡航與車距 \> Carrot巡航
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseEcoControl -->

<!-- CARROT:MANUAL:BEGIN CruiseEcoControl -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

暫時提高目標速度以改善燃油效率。

- **調高：** 節能控制可暫時提高目標速度的幅度較大。
- **調低：** 減少該增加幅度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在支援車輛及適用行車模式下，每次調整一項，檢查目標速度及實際加速／減速請求。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseEcoControl -->

<!-- CARROT:SETTING:END CruiseEcoControl -->
