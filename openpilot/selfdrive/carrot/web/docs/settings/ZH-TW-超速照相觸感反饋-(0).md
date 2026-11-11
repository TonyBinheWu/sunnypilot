<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_HYUNDAI" param="HapticFeedbackWhenSpeedCamera" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 超速照相觸感反饋 (0)

**選單:** 車輛與硬體 \> 現代·起亞

---

<!-- CARROT:SETTING:BEGIN HapticFeedbackWhenSpeedCamera -->
<a id="HapticFeedbackWhenSpeedCamera"></a>

## 超速照相觸感反饋 (0)

`HapticFeedbackWhenSpeedCamera`

0: 禁用, 1: 振動, 2: 儀表盤, 3: HUD 顯示

<!-- CARROT:AUTO:BEGIN HapticFeedbackWhenSpeedCamera -->
<!-- CARROT:AUTO:SOURCE facts="aaa1d3fa4390f8105e692599c3193e5dce771b7e21e7ee6279e3b2bef50675c5" semantic="e9e7ad9d957bc03d8cb260062ab40a0f6d2de683d9c3d9106ea39f476072aad3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 車輛與硬體 \> 現代·起亞
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HapticFeedbackWhenSpeedCamera -->

<!-- CARROT:MANUAL:BEGIN HapticFeedbackWhenSpeedCamera -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 停用
- `1` — 震動
- `2` — 儀表板
- `3` — HUD 顯示
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

確認車輛規格及線組配置，停妥後設定，並於下次行車確認 SCC 及車道警示行為。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 車型、年式、HDA 世代或線組位置不符，可能導致 SCC 或縱向控制行為錯誤。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HapticFeedbackWhenSpeedCamera -->

<!-- CARROT:SETTING:END HapticFeedbackWhenSpeedCamera -->
