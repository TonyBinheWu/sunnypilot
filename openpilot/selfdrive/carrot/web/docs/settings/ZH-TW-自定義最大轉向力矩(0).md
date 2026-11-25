<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_LIMIT" param="CustomSteerMax" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自定義最大轉向力矩(0)

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制

---

<!-- CARROT:SETTING:BEGIN CustomSteerMax -->
<a id="CustomSteerMax"></a>

## 自定義最大轉向力矩(0)

`CustomSteerMax`

最大轉向力矩 — 在 270/384/409 中選擇不報錯的最大值 使用 ADAS ECU 的 EV6 HDA2 扭矩轉向在低於 11 m/s 時採用 384，達到 11 m/s 時採用 330。較低的正值可限制兩段輸出。

<!-- CARROT:AUTO:BEGIN CustomSteerMax -->
<!-- CARROT:AUTO:SOURCE facts="a6ae7a342c738446ad7504770db9e8e6755c8dd1f2a3b4997c9ee160d4ebd915" semantic="69a6e47badf874d2955d531c868fbb567fbe47091875499338aed77993a98279" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `30000`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerMax -->

<!-- CARROT:MANUAL:BEGIN CustomSteerMax -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

調整支援的 Hyundai／Kia 扭矩控制器之最大轉向扭矩限制。

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
<!-- CARROT:MANUAL:END CustomSteerMax -->

<!-- CARROT:SETTING:END CustomSteerMax -->
