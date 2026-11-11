<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_CARROT" param="CarrotCruiseAtcDecel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 胡蘿蔔巡航 ATC 減速度(-1)

**選單:** 駕駛控制 \> 巡航與車距 \> Carrot巡航

---

<!-- CARROT:SETTING:BEGIN CarrotCruiseAtcDecel -->
<a id="CarrotCruiseAtcDecel"></a>

## 胡蘿蔔巡航 ATC 減速度(-1)

`CarrotCruiseAtcDecel`

胡蘿蔔巡航 ATC 減速度設定，-1: 不改變

<!-- CARROT:AUTO:BEGIN CarrotCruiseAtcDecel -->
<!-- CARROT:AUTO:SOURCE facts="1a10721a0e61261fd85411c2bca855475fb384522e85421feb7859d7b9f78d12" semantic="a6733fcd86fb76d04b17b6518d26eb29a1989d9fad23e0faca06bbe22b4919a0" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `-1`
- **範圍:** `-1` ~ `200`
- **步長:** `10`
- **選單:** 駕駛控制 \> 巡航與車距 \> Carrot巡航
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotCruiseAtcDecel -->

<!-- CARROT:MANUAL:BEGIN CarrotCruiseAtcDecel -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

Carrot 巡航 ATC 減速度設定。

- **正值調高：** 增加 ATC 期間 Carrot Cruise 可請求的最大減速度。
- **正值調低：** 降低 ATC 的減速度上限。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在支援車輛及適用行車模式下，每次調整一項，檢查目標速度及實際加速／減速請求。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 目前實作只適用於受支援 Hyundai／Kia 控制器的 ATC 減速。`-1` 會維持既有減速請求。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CarrotCruiseAtcDecel -->

<!-- CARROT:SETTING:END CarrotCruiseAtcDecel -->
