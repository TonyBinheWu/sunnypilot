<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaUpLC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 變道自定義轉向增大斜率(0)

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaUpLC -->
<a id="CustomSteerDeltaUpLC"></a>

## 變道自定義轉向增大斜率(0)

`CustomSteerDeltaUpLC`

力矩控制車輛 — 變道期間臨時應用轉向增大斜率

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaUpLC -->
<!-- CARROT:AUTO:SOURCE facts="3fdde3578232ada1652ea736a1f9f80a7daa1433e6cc9f43dcfdaa1054ff82e8" semantic="4c4f646026bac5f61b4baffbdf4b28f1bd790783dd022d744209c74a30c33e3e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `50`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaUpLC -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaUpLC -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

扭矩控制車輛：變換車道時暫時套用 SteerDeltaUp。

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
<!-- CARROT:MANUAL:END CustomSteerDeltaUpLC -->

<!-- CARROT:SETTING:END CustomSteerDeltaUpLC -->
