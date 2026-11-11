<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_START" param="AlwaysLateral" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 全時橫向控制

**選單:** 駕駛控制 \> 啟動·自動 \> 起步動作

---

<!-- CARROT:SETTING:BEGIN AlwaysLateral -->
<a id="AlwaysLateral"></a>

## 全時橫向控制

`AlwaysLateral`

即使巡航未啟用，也允許橫向控制。 系統啟動後，首次確認所需輸入就緒前不執行轉向。一旦透過，此啟動檢查不再阻斷；現有行駛中安全處理保持不變。 Tesla 在實際靜止時可以轉向；低速移動時仍遵守最低轉向速度限制。 有車輛 CAN 擴充套件的 Tesla，每次獨立三指觸屏立即切換此設定，不再切換實驗模式。關閉不等於解除已啟用巡航中的轉向控制。 確認持續的 CAN 控制器錯誤或反覆出現的 Casper 前方安全系統故障時，會發出警報並停止全時轉向；故障解除前不能重新啟用。 0: 關閉, 1: 開啟

<!-- CARROT:AUTO:BEGIN AlwaysLateral -->
<!-- CARROT:AUTO:SOURCE facts="f7b8b1197532013ba78c4e5b2fdade46b5598a8b95eeaa943816edadaf8a82e5" semantic="3f6deea9c6bbfe6632488bcb5dfc98a7d569ea9227268d6d99cf4f6fc8019ea0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 啟動·自動 \> 起步動作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AlwaysLateral -->

<!-- CARROT:MANUAL:BEGIN AlwaysLateral -->
<!-- CARROT:REVIEW reviewed-for="3f6deea9c6bbfe6632488bcb5dfc98a7d569ea9227268d6d99cf4f6fc8019ea0" reviewed-at="2026-11-09T00:00:00+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 工作方式

- **開啟：** 前進擋且橫向控制已啟用時，巡航關閉或行駛中踩剎車取消巡航後仍可轉向。
- **關閉：** 僅在駕駛控制啟用時轉向。

此設定不改變加速或制動，也不會自行開啟橫向控制。
支援的 Tesla 車型在前進擋且橫向控制已啟用時，完全靜止也可保持轉向控制。車輛移動時仍受最低轉向速度限制；轉向故障或橫向控制關閉時不會轉向。

系統啟動後，首次確認模型、車輛引數、姿態等必需輸入有效且就緒前，不允許轉向。一旦透過，此啟動檢查即結束；之後的輸入暫時異常或橫向控制關閉再開啟，不會重新觸發該檢查。現有行駛中安全處理保持不變。啟動等待時間結束本身不能透過此檢查。
確認持續的 CAN 控制器錯誤或反覆出現的 Casper 前方安全系統故障時，會發出警報並停止全時轉向；故障解除前不能重新啟用。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AlwaysLateral -->

<!-- CARROT:SETTING:END AlwaysLateral -->
