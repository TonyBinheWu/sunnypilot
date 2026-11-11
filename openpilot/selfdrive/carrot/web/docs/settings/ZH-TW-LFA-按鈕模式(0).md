<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BUTTON_MODE" param="LfaButtonMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LFA 按鈕模式(0)

**選單:** 駕駛控制 \> 按鈕·預設 \> 按鈕模式

---

<!-- CARROT:SETTING:BEGIN LfaButtonMode -->
<a id="LfaButtonMode"></a>

## LFA 按鈕模式(0)

`LfaButtonMode`

0: 常規, 1: 減速並停止/前車就緒, 2: 胡蘿蔔巡航

<!-- CARROT:AUTO:BEGIN LfaButtonMode -->
<!-- CARROT:AUTO:SOURCE facts="3f6213a6235ebadd1f55eb0c25bc294584bdea3f0a74588d3d3d5cc07ce3982b" semantic="9c4b44838ae0dcff4397e38c706817d14778d81d616a5617a32fbc5b2d88e8ff" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 駕駛控制 \> 按鈕·預設 \> 按鈕模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LfaButtonMode -->

<!-- CARROT:MANUAL:BEGIN LfaButtonMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 一般
- `1` — 減速與停車、前車就緒
- `2` — CarrotCruise
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

停妥後選擇模式，分別確認短按、長按及取消行為。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LfaButtonMode -->

<!-- CARROT:SETTING:END LfaButtonMode -->
