<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaDownLC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 變道自定義轉向減小斜率(0)

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaDownLC -->
<a id="CustomSteerDeltaDownLC"></a>

## 變道自定義轉向減小斜率(0)

`CustomSteerDeltaDownLC`

力矩控制車輛 — 變道期間臨時應用轉向減小斜率 使用 ADAS ECU 的 EV6 HDA2 扭矩轉向以每 10 ms 3 個單位的固定速率收回扭矩，駕駛接管時同樣適用。

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaDownLC -->
<!-- CARROT:AUTO:SOURCE facts="76cfe4b6f59763b4ddd53a5274d8d35fda688f9ed25647f03375a648b1fde9aa" semantic="24f993369a8dc843e97c8b377086b40d1cb55d05c6cdf714f2e9f859ab68ba73" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `50`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaDownLC -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaDownLC -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

扭矩控制車輛：變換車道時暫時套用 SteerDeltaDown。

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
<!-- CARROT:MANUAL:END CustomSteerDeltaDownLC -->

<!-- CARROT:SETTING:END CustomSteerDeltaDownLC -->
