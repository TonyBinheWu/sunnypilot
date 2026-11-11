<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_COEFF" param="LateralTorqueKf" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 轉向力矩 Kf\*0.001(100)

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKf -->
<a id="LateralTorqueKf"></a>

## 轉向力矩 Kf\*0.001(100)

`LateralTorqueKf`

轉向前饋修正 — 推薦 85

<!-- CARROT:AUTO:BEGIN LateralTorqueKf -->
<!-- CARROT:AUTO:SOURCE facts="91289aede18a94dc3c060152f3d66f8fb08fa2044c794a047ddacb52eca11897" semantic="ea6d27099c3e8610130f74384cd9fe8bee6c2a22a6291c942b50541fc25fcd81" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100`
- **範圍:** `0` ~ `200`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKf -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKf -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

設定套用至預測轉向扭矩的前饋係數。

- **調高：** 增加此扭矩控制項的作用比重。
- **調低：** 降低該項的作用比重。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在扭矩控制車輛上，每次小幅調整一個係數，比較直路回正、平緩彎道及駕駛介入時的扭矩。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 不適當的數值可能降低轉向或縱向控制的穩定性與舒適度。每次只小幅調整一項，行為異常時恢復預設值。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LateralTorqueKf -->

<!-- CARROT:SETTING:END LateralTorqueKf -->
