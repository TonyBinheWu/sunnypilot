<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_CARROT" param="CarrotCruiseDecel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 胡蘿蔔巡航減速度(-1)

**選單:** 駕駛控制 \> 巡航與車距 \> Carrot巡航

---

<!-- CARROT:SETTING:BEGIN CarrotCruiseDecel -->
<a id="CarrotCruiseDecel"></a>

## 胡蘿蔔巡航減速度(-1)

`CarrotCruiseDecel`

胡蘿蔔巡航減速度設定，-1: 巡航關閉

<!-- CARROT:AUTO:BEGIN CarrotCruiseDecel -->
<!-- CARROT:AUTO:SOURCE facts="77784dcb6b60d848cd72ce34e293adfa25c0709c2851587a284be8c6a3ddcb52" semantic="ba7e233d65895feac8118c77053f75720240197ed3ffa0ecf87ea2f953e899d2" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `-1`
- **範圍:** `-1` ~ `200`
- **步長:** `10`
- **選單:** 駕駛控制 \> 巡航與車距 \> Carrot巡航
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotCruiseDecel -->

<!-- CARROT:MANUAL:BEGIN CarrotCruiseDecel -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

Carrot 巡航減速度設定。

- **正值調高：** 增加 Carrot Cruise 可請求的最大減速度。
- **正值調低：** 降低允許請求的減速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在支援車輛及適用行車模式下，每次調整一項，檢查目標速度及實際加速／減速請求。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 目前實作只適用於受支援的 Hyundai／Kia 控制器。`-1` 會解除巡航，而非提出 Carrot Cruise 減速請求。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CarrotCruiseDecel -->

<!-- CARROT:SETTING:END CarrotCruiseDecel -->
