<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SYS_SOUND" param="SoundVolumeAdjust" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 音量調節 (100%)

**選單:** 系統 \> 聲音

---

<!-- CARROT:SETTING:BEGIN SoundVolumeAdjust -->
<a id="SoundVolumeAdjust"></a>

## 音量調節 (100%)

`SoundVolumeAdjust`

調節一般提示音的音量。DM 首次聲音警告的增益至少為 70%，最終警告始終為 100%，不會因音量設定或環境噪聲調節而降低。

<!-- CARROT:AUTO:BEGIN SoundVolumeAdjust -->
<!-- CARROT:AUTO:SOURCE facts="e4680b13f5bad36c76b8bdb6e845b8de12c1b9b0c2cee3a0d4df8056093e9dbc" semantic="dd82113cc6e9e733b3f10f9f9d9e6a61149a0ef90764fad9174d6f5fa06129d6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0%`
- **範圍:** `5%` ~ `200%`
- **步長:** `5`
- **顯示單位:** `%`
- **選單:** 系統 \> 聲音
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SoundVolumeAdjust -->

<!-- CARROT:MANUAL:BEGIN SoundVolumeAdjust -->
<!-- CARROT:REVIEW reviewed-for="dd82113cc6e9e733b3f10f9f9d9e6a61149a0ef90764fad9174d6f5fa06129d6" reviewed-at="2026-09-28T23:41:56.696170+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

控制一般警告和提示音的音量倍率。 提高數值會增大一般提示音，降低數值會減小音量。

DM 首次聲音警告的增益至少為 70%，最終警告始終為 100%，不會因音量設定或環境噪聲調節而降低。該規則適用於模式 0 和 1，以及攝像頭或操作監測。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

停車時播放提示音，分別確認語言、一般音量及啟用和退出時的音量。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

聲音警告之前的畫面預警保持靜音。使用相同音源的導航提示不適用 DM 音量規則。

百分比表示軟體輸出增益，並非實測揚聲器聲壓。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SoundVolumeAdjust -->

<!-- CARROT:SETTING:END SoundVolumeAdjust -->
