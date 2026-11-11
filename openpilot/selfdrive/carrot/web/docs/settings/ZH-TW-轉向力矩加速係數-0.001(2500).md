<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_COEFF" param="LateralTorqueAccelFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 轉向力矩加速係數\*0.001(2500)

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數

---

<!-- CARROT:SETTING:BEGIN LateralTorqueAccelFactor -->
<a id="LateralTorqueAccelFactor"></a>

## 轉向力矩加速係數\*0.001(2500)

`LateralTorqueAccelFactor`

隨著值減小，力矩會增強到某一點然後變弱 — 請使用力矩最強點的值。

<!-- CARROT:AUTO:BEGIN LateralTorqueAccelFactor -->
<!-- CARROT:AUTO:SOURCE facts="f481f394fcebbbbd45eeae52776c3b686581f2353e6d3b52d57ff7a934b58aad" semantic="746c0daa75a2f8c2391948cd47d2956c33436ee89b75ae1080fe4a6a40d6d552" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `2500`
- **範圍:** `1000` ~ `6000`
- **步長:** `100`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 扭矩係數
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueAccelFactor -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueAccelFactor -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

設定將請求橫向加速度換算為轉向扭矩的係數。

此係數為非線性：降低數值會增強扭矩直到某個點，之後扭矩反而減弱。請在實際車輛上小幅調整，找出最強且可用的設定點。
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
<!-- CARROT:MANUAL:END LateralTorqueAccelFactor -->

<!-- CARROT:SETTING:END LateralTorqueAccelFactor -->
