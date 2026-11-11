<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_COEFF" param="LateralTorqueKpV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 轉向力矩 Kp\*0.01(100)

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKpV -->
<a id="LateralTorqueKpV"></a>

## 轉向力矩 Kp\*0.01(100)

`LateralTorqueKpV`

轉向響應速度 (瞬時反應) — 推薦 140

<!-- CARROT:AUTO:BEGIN LateralTorqueKpV -->
<!-- CARROT:AUTO:SOURCE facts="9a9f6c6061dcf7310f170d9cadfb9248de8feeac7d692e7c499448393af3596e" semantic="03a3a5b716a1a1c2a0bb05b45da9e8adcadcf2e1c1a3232e2fbc606fc1ab928a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100`
- **範圍:** `0` ~ `200`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKpV -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKpV -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

設定立即回應轉向誤差的比例項。

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
<!-- CARROT:MANUAL:END LateralTorqueKpV -->

<!-- CARROT:SETTING:END LateralTorqueKpV -->
