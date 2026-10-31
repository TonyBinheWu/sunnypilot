# HKG 開機與 UI 故障拍照診斷

適用 `hkg-enhanced` 的 C3X（tizi）與 C4（mici）。此變更收集故障證據，不宣稱修復卡死根因。

## 使用者操作

更新並在停車狀態重新開機。若建置、manager 啟動／執行或 UI 程序異常退出，獨立診斷畫面會顯示程序、結束碼／訊號、例外訊息、檔案與行號，以及版本與錯誤 ID。

先接管並安全停車，再拍第一頁。點螢幕可切換完整 traceback；長訊息請多拍幾頁。畫面不自動翻頁、關閉或重新開機。中文字型可用時顯示繁體中文提示；不可用時使用內建 ASCII 字型，避免因翻譯或字型資源缺失再次退出。

沒有 Python traceback 時，只顯示實際取得的結束碼／訊號，不捏造行號；SIGKILL 不等於已證實記憶體不足。

## 本機紀錄

- 最新摘要：`/data/diagnostics/hkg/latest-error.json`
- 每次啟動：`/data/diagnostics/hkg/session-*/`
- `build.log` / `manager.log` 與 `.log.1`：每檔上限 1 MiB，每個階段最多兩檔。
- `ui-<pid>.trace`：UI 的 Python 例外或 faulthandler 原生崩潰堆疊。
- `ui-error.json` / `build-error.json` / `manager-error.json`：分階段報告。
- `display.log`：診斷畫面本身的錯誤。

保留最近五次啟動。`/data` 無法建立目錄時嘗試 `/tmp/hkg-diagnostics`，此備援不保證重開機後保留。原始本機日誌可能含裝置識別或環境資訊，傳送前應遮蔽；程式不自動上傳。

## 保護範圍與限制

UI 仍正常執行時，不會啟動第二個畫面。只觀察真正退出的 UI，不以計時逾時殺死或重啟 UI，也不修改轉向、縱向、Panda、模型與相機控制。既有程序健康檢查與警告保留。正常關機／重啟由明確標記區分，外部 SIGTERM/SIGINT 轉送給原程序。

診斷程式只使用標準函式庫收集證據，顯示程式只額外依賴 pyray，不載入主 UI 的 application、widgets、Params 或 cereal。主機端 headless 繪圖與故障注入不等同裝置實測。

以下狀況仍可能只看到逗號：AGNOS 在執行這份啟動腳本之前卡住、核心／顯示驅動死鎖、斷電，或 UI/manager 活著但永久阻塞。這不是將 AGNOS 的開機 logo 改成核心 panic console。若更新後仍只有逗號，需保存本機啟動日誌及核心／供電紀錄，不能解讀成沒有錯誤。

## 離線驗證

```sh
python3 tools/diagnostics/test_boot_diagnostics.py
```

CI 另在 tizi/mici 主機設定下執行原有雙裝置回歸，並輸出獨立故障畫面截圖。故障注入只在子程序／暫存目錄進行，不接觸車輛或 CAN。
