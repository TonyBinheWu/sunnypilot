<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SYS_SOUND" param="SoundLanguageVolume" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 語音播報音量

**選單:** 系統 \> 聲音

---

<!-- CARROT:SETTING:BEGIN SoundLanguageVolume -->
<a id="SoundLanguageVolume"></a>

## 語音播報音量

`SoundLanguageVolume`

導航轉彎、減速及1–10倒數語音的音量倍率。100%維持原音量，並與一般音量及環境音調節相乘。約1秒內生效，無需重啟。警告音與啟用音效維持各自的音量控制。

<!-- CARROT:AUTO:BEGIN SoundLanguageVolume -->
<!-- CARROT:AUTO:SOURCE facts="9088be142e431e8282644996e17afbfc55c8a9520657595472010f4376ead89b" semantic="32c48f4cfc1ecf1e4753492b38495b772d329d24d3954eff9db073bc90a47934" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100%`
- **範圍:** `5%` ~ `300%`
- **步長:** `5`
- **顯示單位:** `%`
- **選單:** 系統 \> 聲音
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SoundLanguageVolume -->

<!-- CARROT:MANUAL:BEGIN SoundLanguageVolume -->
<!-- CARROT:REVIEW reviewed-for="32c48f4cfc1ecf1e4753492b38495b772d329d24d3954eff9db073bc90a47934" reviewed-at="2026-11-13T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

調整導航轉彎、減速及數字倒數語音。機器端乘以一般音量及環境音調節，網頁端乘以網頁音量。警告音與啟用音效維持原有控制。增益後的機器端取樣限制在輸出範圍內。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

停車時逐步調高，確認導航播報清楚。約一秒內生效，無需重新啟動。網頁音量靜音時，網頁語音仍然靜音。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END SoundLanguageVolume -->

<!-- CARROT:SETTING:END SoundLanguageVolume -->
