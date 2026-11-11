<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BUTTON_MODE" param="CruiseButtonMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航按鈕模式(0)

**選單:** 駕駛控制 \> 按鈕·預設 \> 按鈕模式

---

<!-- CARROT:SETTING:BEGIN CruiseButtonMode -->
<a id="CruiseButtonMode"></a>

## 巡航按鈕模式(0)

`CruiseButtonMode`

0: 常規, 1: 使用者1, 2: 使用者2, 3: 使用者3 (使用速度表)

<!-- CARROT:AUTO:BEGIN CruiseButtonMode -->
<!-- CARROT:AUTO:SOURCE facts="752f312ead838389182384ba88df2284c67489f893d4895b99fbc4d4d7751a77" semantic="f106c313d9301e43d396835fadab742302d3dc37007a00554bf7f574204238c1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 駕駛控制 \> 按鈕·預設 \> 按鈕模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonMode -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 一般
- `1` — 自訂 1
- `2` — 自訂 2
- `3` — 自訂 3（使用速度表）

Volkswagen 的獨立 SET 會設定目前儀表速度；RES 恢復煞車前儲存的速度，否則保留既有設定速度，尚未初始化時則使用目前速度。此模式適用於獨立 +／- 按鈕。手動啟用仍由實體 SET／RES 按鈕放開時觸發。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

停妥後選擇模式，分別確認短按、長按及取消行為。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseButtonMode -->

<!-- CARROT:SETTING:END CruiseButtonMode -->
