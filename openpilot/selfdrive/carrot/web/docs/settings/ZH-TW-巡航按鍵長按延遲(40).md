<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BUTTON_UNIT" param="CruiseButtonLongDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航按鍵長按延遲(40)

**選單:** 駕駛控制 \> 按鈕·預設 \> 速度單位

---

<!-- CARROT:SETTING:BEGIN CruiseButtonLongDelay -->
<a id="CruiseButtonLongDelay"></a>

## 巡航按鍵長按延遲(40)

`CruiseButtonLongDelay`

長按按鈕後，功能觸發前的延遲時間。

<!-- CARROT:AUTO:BEGIN CruiseButtonLongDelay -->
<!-- CARROT:AUTO:SOURCE facts="04221bf7667e08a11823bb17fb1bad4b918f0093ce2c05cd172595d7abfec31a" semantic="7156b031dff48c8b2a99b76175c1620036d0ffbe8df7af1cc39a39690ddb9f59" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `40`
- **範圍:** `30` ~ `100`
- **步長:** `10`
- **選單:** 駕駛控制 \> 按鈕·預設 \> 速度單位
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonLongDelay -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonLongDelay -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

觸發長按操作前的等待時間。

- **調高：** 增加適用的時間或延遲。
- **調低：** 減少時間或延遲。

Volkswagen 的此延遲適用於獨立 +／- 按鈕。獨立 SET／RES 不論按住多久，均只在放開時作用一次，不會重複調速。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

分別確認單次按壓及長按的設定速度變化量與時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseButtonLongDelay -->

<!-- CARROT:SETTING:END CruiseButtonLongDelay -->
