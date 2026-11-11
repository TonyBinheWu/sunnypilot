<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_DM" param="CarrotVisionEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 啟用 Carrot Vision

**選單:** 車輛與硬體 \> 駕駛員監控

---

<!-- CARROT:SETTING:BEGIN CarrotVisionEnabled -->
<a id="CarrotVisionEnabled"></a>

## 啟用 Carrot Vision

`CarrotVisionEnabled`

獨立於駕駛員監控啟用網頁道路影片，可與外部HUD同時使用。同時使用影片可能增加裝置負載。

<!-- CARROT:AUTO:BEGIN CarrotVisionEnabled -->
<!-- CARROT:AUTO:SOURCE facts="ba8efc21d43470721fb0b25e78207cf3fc376ab9e137cfda4e6d6577ec185399" semantic="06ceb617dbe739cddd0239009397024736b16a64f730822966da6da92c24437d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 關閉 (`0`)
- **範圍:** 關閉 (`0`) ~ 開啟 (`1`)
- **步長:** `1`
- **選項:** `0` 關閉, `1` 開啟
- **選單:** 車輛與硬體 \> 駕駛員監控
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotVisionEnabled -->

<!-- CARROT:MANUAL:BEGIN CarrotVisionEnabled -->
<!-- CARROT:REVIEW reviewed-for="196e1f296cc743239e491c11d519cea88fbf7bde06ad6f1fe40b377fe6758e07" reviewed-at="2026-09-28T07:45:03.024967+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

啟用後可使用網頁道路影片，關閉後停止。此設定獨立於駕駛員監控。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

需要網頁道路影片時啟用。啟用USB儀表盤時無法使用Carrot Vision。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

舊DisableDM的影片選擇僅遷移一次到此設定。遷移不會關閉駕駛員監控或開啟實驗模式。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CarrotVisionEnabled -->

<!-- CARROT:SETTING:END CarrotVisionEnabled -->
