# 兩分支架構與模組維護入口

本目錄把目前的程式整理成可獨立審閱、成組升級的維護部件。這是依現有目錄與介面建立的模組邊界，尚未搬移執行程式或改變行車行為。

## 閱讀順序

1. [目前架構與資料流](CURRENT_ARCHITECTURE.md)：啟動、控制、模型、硬體與兩分支差異。
2. [模組部件目錄](COMPONENTS.md)：15 個部件的程式位置、輸入輸出、升級單位與驗證入口。
3. [升級與維護手冊](UPGRADE_GUIDE.md)：改動影響、升級順序、分支同步及回復方式。
4. [機器可讀模組地圖](module_map.json)：供維護工具讀取的路徑與相依關係。
5. [上上游模擬器與雙機種測試](SIMULATION_AND_DEVICE_TESTING.md)：MetaDrive、重播、實機測試及目前覆蓋缺口。
6. [2026-11-01 平台更新紀錄](PLATFORM_UPGRADE_2026_11.md)：AGNOS 20.1、依賴升級、CCNC 導航同步與驗證範圍。

## 分析快照

| 分支 | 已核對的遠端提交 | sunnypilot 版本 | openpilot 基底標示 | AGNOS |
| --- | --- | --- | --- | --- |
| hkg-enhanced | `ef3e9ec8cde918d71c64e2f8986ed550e6e44cb8` | 2026.003.002 | 0.11.2 | 19.9 |
| ccnc-port | `92888c97572fe0820c1edea5a5fa9789a01a5735` | 2026.003.002 | 0.11.2 | 19.9 |

分析日期：2026-10-31。快照是分析依據，後續版本以分支實際 Git 提交與版本標頭為準。支援政策與程式能力分別記錄；保留某車型的程式碼不等於承諾支援該車型。

## 2026-11-01 升級內容

本次維護版本為 `2026.003.003`，AGNOS 目標 `20.1`、openpilot 基底標示 `0.11.3`。已將導航目錄、訊息契約與程序設定同步至 CCNC；上表保留改動前的已提交快照。這不是完整合併 master，也不是實機驗證完成的聲明。

## 日常使用

在儲存庫根目錄執行，僅使用 Python 標準函式庫，不需啟動車輛程序：

```bash
python tools/maintenance/module_inventory.py --check
python tools/maintenance/module_inventory.py --diff HEAD~1
python tools/maintenance/module_inventory.py --diff origin/ccnc-port --profile hkg-enhanced
python tools/maintenance/module_inventory.py --diff HEAD~1 --json
python tools/maintenance/module_inventory.py --catalog
```

`--diff` 讀取參考提交到目前工作樹的已追蹤檔案差異，列出直接影響部件、依賴它們的部件與建議檢查；未歸類路徑也會明列。新增而尚未追蹤的檔案不在 Git diff 結果中，需另行檢視 `git status`。結果是保守的升級影響分析，不是測試已通過或實車安全性的證明。

模組地圖中的 `requires` 表示升級時要一起審閱的介面依賴，`optional_requires` 表示該分支啟用功能時的依賴。它們不是 Python import 的完整清單，也不是行車資料流的拓撲排序。

`--catalog` 從同一份 JSON 輸出兩分支完整部件目錄，更新模組地圖後可用它重新產生 `COMPONENTS.md`。JSON 差異報告的 `inactive_module_paths` 會列出目標分支未啟用功能的路徑，例如歷史版本中未啟用的導航目錄；目前兩分支均已納入導航。
