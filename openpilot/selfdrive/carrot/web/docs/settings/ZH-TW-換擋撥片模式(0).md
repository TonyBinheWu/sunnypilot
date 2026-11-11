<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BUTTON_MODE" param="PaddleMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 換擋撥片模式(0)

**選單:** 駕駛控制 \> 按鈕·預設 \> 按鈕模式

---

<!-- CARROT:SETTING:BEGIN PaddleMode -->
<a id="PaddleMode"></a>

## 換擋撥片模式(0)

`PaddleMode`

動能回收撥片後, 0: 巡航開啟, 1: 巡航就緒, 2: 減速並巡航就緒, 3: 胡蘿蔔巡航

<!-- CARROT:AUTO:BEGIN PaddleMode -->
<!-- CARROT:AUTO:SOURCE facts="dc2f6a5c8e5e835994c6204c6dd3bb1048e5de752eca4111874305fe23468135" semantic="513264e6a1d57186ce13925ba169f9b25c61b0d5d02385d078e00fd84cb40d9d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `1`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 駕駛控制 \> 按鈕·預設 \> 按鈕模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END PaddleMode -->

<!-- CARROT:MANUAL:BEGIN PaddleMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 巡航開啟
- `1` — 巡航待命
- `2` — 減速與巡航待命
- `3` — CarrotCruise
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

停妥後選擇模式，分別確認短按、長按及取消行為。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END PaddleMode -->

<!-- CARROT:SETTING:END PaddleMode -->
