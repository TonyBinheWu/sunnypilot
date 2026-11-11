<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_COEFF" param="LateralTorqueCustom" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自定義轉向力矩(0)

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數

---

<!-- CARROT:SETTING:BEGIN LateralTorqueCustom -->
<a id="LateralTorqueCustom"></a>

## 自定義轉向力矩(0)

`LateralTorqueCustom`

使用自定義力矩 (TorqueAccelFactor, FrictionFactor)

<!-- CARROT:AUTO:BEGIN LateralTorqueCustom -->
<!-- CARROT:AUTO:SOURCE facts="fe29946227575d1cbd1dfc4d2b50074a2abd53d28034ea8155281622db219d0b" semantic="931515b55fa1df2997b5da0e909ee948b8e957adb02298be36935346c8429d94" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `1`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueCustom -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueCustom -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- **開啟：** 使用自訂的加速度、摩擦與 PID 係數進行扭矩控制。
- **關閉：** 使用車輛介面與即時學習提供的預設扭矩係數。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在扭矩控制車輛上，每次小幅調整一個係數，比較直路回正、平緩彎道及駕駛介入時的扭矩。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 自訂扭矩係數只適用於扭矩控制車輛；須啟用此設定，才會使用自訂加速度與摩擦係數。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LateralTorqueCustom -->

<!-- CARROT:SETTING:END LateralTorqueCustom -->
