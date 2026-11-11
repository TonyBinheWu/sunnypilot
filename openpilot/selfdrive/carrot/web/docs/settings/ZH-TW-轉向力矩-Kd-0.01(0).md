<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_COEFF" param="LateralTorqueKd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 轉向力矩 Kd\*0.01(0)

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKd -->
<a id="LateralTorqueKd"></a>

## 轉向力矩 Kd\*0.01(0)

`LateralTorqueKd`

轉向微分增益，推薦 0

<!-- CARROT:AUTO:BEGIN LateralTorqueKd -->
<!-- CARROT:AUTO:SOURCE facts="fa7ef7915451b26171c2ef8a6d7e732cf60c32079b276fbec6366a37bc745a8a" semantic="f4b07835f8d82647a8e9661e9116ca1f5478c8d37cdf844014eb000c7d90ea9a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `10000`
- **步長:** `10`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKd -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKd -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

設定回應轉向誤差快速變化的微分項。

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
<!-- CARROT:MANUAL:END LateralTorqueKd -->

<!-- CARROT:SETTING:END LateralTorqueKd -->
