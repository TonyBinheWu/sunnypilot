<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_COEFF" param="LateralTorqueKiV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 轉向力矩 Ki\*0.01(10)

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKiV -->
<a id="LateralTorqueKiV"></a>

## 轉向力矩 Ki\*0.01(10)

`LateralTorqueKiV`

轉向累積誤差修正 — 推薦 20

<!-- CARROT:AUTO:BEGIN LateralTorqueKiV -->
<!-- CARROT:AUTO:SOURCE facts="b10b1e303c642ab70498b5e1f360528cd62b4ef5c3d13184cfaba09eaedf1058" semantic="1009f0b89dab98fe24e61983fa04ccf3c2daebed428a26b892370ecf0301a095" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `10`
- **範圍:** `0` ~ `200`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKiV -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKiV -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

設定修正累積轉向誤差的積分項。

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
<!-- CARROT:MANUAL:END LateralTorqueKiV -->

<!-- CARROT:SETTING:END LateralTorqueKiV -->
