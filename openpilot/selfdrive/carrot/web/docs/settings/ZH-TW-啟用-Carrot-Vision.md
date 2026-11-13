<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_DM" param="CarrotVisionEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 啟用 Carrot Vision

**選單:** 車輛與硬體 \> 駕駛員監控

---

<!-- CARROT:SETTING:BEGIN CarrotVisionEnabled -->
<a id="CarrotVisionEnabled"></a>

## 啟用 Carrot Vision

`CarrotVisionEnabled`

啟用網頁道路影像，支援停車觀看。有觀看會話時才請求鏡頭與專用編碼器，結束後釋放；獨立於駕駛員監控及外部 HUD。 同時使用影片可能增加裝置負載。

<!-- CARROT:AUTO:BEGIN CarrotVisionEnabled -->
<!-- CARROT:AUTO:SOURCE facts="b96c968da37b5006a3a34d64c6de201daca44322c62a8910d066935ac567c411" semantic="b2d518e8de1cb65052caf0bf8dd1cad8094210462341bdc7090b9f4156fdff5f" review="current" -->
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
<!-- CARROT:REVIEW reviewed-for="b2d518e8de1cb65052caf0bf8dd1cad8094210462341bdc7090b9f4156fdff5f" reviewed-at="2026-11-13T16:58:12Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

獨立於駕駛員監控及外部 HUD，支援行車及停車道路影像。停車時僅在觀看會話存在期間請求鏡頭與編碼器，其他鏡頭使用者仍遵循原有條件。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

開啟此設定並進入 App 或網頁的 Vision。車機更新並重新啟動一次後，可繼續使用 CarrotAssist 0.2.16，無須執行診斷鏡頭程序。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

停車觀看不啟動駕駛模型、控制或一般行車錄影，也不沿用舊行車指引；錄影回放保留紀錄資料。原有電量關機條件不變。舊 DisableDM 影像選項只遷移一次，不改變駕駛員監控或實驗模式。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CarrotVisionEnabled -->

<!-- CARROT:SETTING:END CarrotVisionEnabled -->
