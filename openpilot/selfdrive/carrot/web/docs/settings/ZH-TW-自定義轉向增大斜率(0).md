<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaUp" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自定義轉向增大斜率(0)

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaUp -->
<a id="CustomSteerDeltaUp"></a>

## 自定義轉向增大斜率(0)

`CustomSteerDeltaUp`

力矩控制車輛 — 值越高方向盤轉動速度越快

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaUp -->
<!-- CARROT:AUTO:SOURCE facts="a2769a18dbd75d0f2a2319aa3fe6520796998dda60e5adebf823911b7fc6a8b5" semantic="22505d7f9d2fdc5441ecca4890ef75dd0dd73869c71f0347effa2d7f6d892664" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `50`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaUp -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaUp -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

扭矩控制車輛：數值越高，方向盤轉動速度越快。

- **調高：** 增加適用的轉向扭矩限制或變化速率。
- **調低：** 降低限制或變化速率。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在支援扭矩控制的車輛上，每次調整一項，確認一般行車及變換車道時的轉向扭矩增加與減少速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 不適當的數值可能降低轉向或縱向控制的穩定性與舒適度。每次只小幅調整一項，行為異常時恢復預設值。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CustomSteerDeltaUp -->

<!-- CARROT:SETTING:END CustomSteerDeltaUp -->
