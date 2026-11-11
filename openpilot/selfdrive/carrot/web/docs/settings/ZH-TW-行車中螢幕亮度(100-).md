<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_BRIGHT" param="ShowCustomBrightness" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 行車中螢幕亮度(100%)

**選單:** 顯示 \> 亮度與檢視

---

<!-- CARROT:SETTING:BEGIN ShowCustomBrightness -->
<a id="ShowCustomBrightness"></a>

## 行車中螢幕亮度(100%)

`ShowCustomBrightness`

行車開始約10秒後的螢幕亮度比例 0: 根據環境亮度自動調節 100: 始終最大亮度

<!-- CARROT:AUTO:BEGIN ShowCustomBrightness -->
<!-- CARROT:AUTO:SOURCE facts="d00c11a594d39b5de825e24001ccf50f629cd758e77b455eece2edb0b6734c5a" semantic="fc03de2baf9a00998b9705313c1101cb5d556a9067d5a4ab5b539596ebe94454" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100%`
- **範圍:** `0%` ~ `100%`
- **步長:** `5`
- **顯示單位:** `%`
- **選單:** 顯示 \> 亮度與檢視
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowCustomBrightness -->

<!-- CARROT:MANUAL:BEGIN ShowCustomBrightness -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 依環境亮度自動調整
- `100` — 固定使用最高亮度
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

行車亮度穩定後，檢查攝影機／模型顯示的可見度及眩光。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowCustomBrightness -->

<!-- CARROT:SETTING:END ShowCustomBrightness -->
