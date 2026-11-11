<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_LONGTUNE" param="LongActuatorDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 縱向執行器延遲(20)x0.01

**選單:** 駕駛控制 \> 巡航與車距 \> 加減速調校

---

<!-- CARROT:SETTING:BEGIN LongActuatorDelay -->
<a id="LongActuatorDelay"></a>

## 縱向執行器延遲(20)x0.01

`LongActuatorDelay`

縱向延遲值 (值越高越早開始加減速) — HKG: 推薦 20

<!-- CARROT:AUTO:BEGIN LongActuatorDelay -->
<!-- CARROT:AUTO:SOURCE facts="51afae4d30b6b3d4305549299e32133a03da8ec73bf26679c16be961af7aa9e2" semantic="83f945e2bbe7928bc6258df845c0f2c9ea2701fa8ecf7a6225873c62d3a181cc" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `20`
- **範圍:** `0` ~ `200`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加減速調校
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongActuatorDelay -->

<!-- CARROT:MANUAL:BEGIN LongActuatorDelay -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

補償加速或煞車請求與車輛反應之間的延遲。

- **調高：** 假設縱向控制延遲較大，較早請求目標變更。
- **調低：** 減少縱向控制的提前補償。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同目標速度切換條件下，每次小幅調整一項，比較超調、振盪及反應延遲。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 不適當的數值可能降低轉向或縱向控制的穩定性與舒適度。每次只小幅調整一項，行為異常時恢復預設值。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LongActuatorDelay -->

<!-- CARROT:SETTING:END LongActuatorDelay -->
