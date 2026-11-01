# 升級與維護手冊

搭配 [架構](CURRENT_ARCHITECTURE.md)、[部件](COMPONENTS.md)與[模組地圖](module_map.json)使用。

## 每次改動的固定步驟

1. 記錄兩分支 HEAD、版本、AGNOS、所有 gitlink 及待移植上游提交。先確認工作樹是否有使用者修改。
2. 在目標分支獨立工作樹準備變更，使用 `module_inventory.py --diff <參考提交>` 找直接與間接影響。這不會自動同步另一個分支。
3. 寫清楚此次觸及的部件、保留的分支差異、相容性成組更新，以及回復的提交。
4. 完成部件的針對性驗證，再執行跨部件 CI。主機 CI、模型載入、裝置開機、GPU 實際推論與行車驗證分別記錄。
5. 共用修正分別套用到另一分支並審閱 diff；保留專屬功能，不以整個目錄覆蓋另一分支。
6. 有可發布的使用者變更時更新版本與繁體中文 CHANGELOG，依 [發布流程](../DEVICE_RELEASE_NOTES.md)核對更新前後的畫面與版號。

## 成組升級單位

| 改動 | 一起審閱的內容 | 不可只更新的部分 |
| --- | --- | --- |
| AGNOS／硬體 | launch_env、manifest、相容入口、硬體層、USB、原生依賴、兩機種開機 | 版本字串 |
| 訊息或 Params | schema、services、發布／訂閱端、健康檢查、遷移、預設與清除旗標 | 新增欄位或 UI 開關 |
| 模型／tinygrad | runtime pin、模型產物／SHA、格式、adapter、shape／dtype、warp、快取、warmup、fallback | tinygrad 或模型檔其中一個 |
| HKG／CCNC 車型 | fingerprint、DBC、CarState、CarController、interface、safety、能力判斷、初始化 | 控制器、旗標常數或 Panda 其中一個 |
| MADS／控制 | engagement 狀態、警示、CarParamsSP、橫縱向啟用、制動／油門介入 | UI 顯示的 engaged 狀態 |
| 導航模型 | navd、mapsd、schema／VisionIPC、兩種 runner、模型輸入與模型產物 | 導航畫面或 navd 單一檔案 |
| 中文 UI | 兩套介面、翻譯來源、PO／POT、字型、測量／換行／繪製、兩機種截圖 | 只有翻譯文字 |
| 發行更新 | 版本、CHANGELOG、build metadata、updated、當前／待安裝資訊、兩種 UI、打包 | GitHub Release 描述 |

## 建議升級順序

先建立可回復的基準與通過的測試，再依「硬體／建置 → 訊息與設定 → 子模組與模型契約 → 車型與 safety → 狀態與控制 → 導航／地圖 → UI／雲端 → 發行」分批整合。這是審閱順序；有明確成組相容性要求的提交仍須一起交付，不能為了分批而讓中間版本無法啟動或控制器與 safety 不一致。

不要把上游 `master`、導航開發分支、HKG、CCNC 同時整批合併。每次升級要能回答：改了哪個介面、哪個分支／機種／後端受影響、用哪個測試證明仍相容。

## 分支同步策略

* 共用層：保持可追蹤的相同修正，例如更新說明、通用 UI 修正、已驗證的 runtime contract。
* 車種層：opendbc／safety 與 CCNC 儀表功能各自保留，先對照符號意義再移植；不要複製數字常數。
* HKG 專屬層：DEC、藍色路徑、停車標記、開機診斷先視為獨立功能包。CCNC 要導入時逐包建立能力與測試。
* CCNC 專屬層：車型、儀表訊息、相機偏移校正與翻譯差異分別審閱，不當成 HKG 的通用替換。

建議後續逐步集中 branch／device／runner 的能力描述，但目前尚未建立單一執行時 profile 系統。第一步先集中純能力判斷，第二步加入相同介面的回歸測試，最後才移動控制與啟動程式。不要先改目錄再補契約。

## 發布驗證矩陣

每個維護分支都要分別記錄下列結果：

| 層次 | C3X | C4 |
| --- | --- | --- |
| 主機介面 | tizi／BIG=1 的版本、中文與捲動畫面 | mici／BIG=0 的版本、中文與捲動畫面 |
| QCOM 裝置 | 安裝、開機、模型載入與持續推論 | 安裝、開機、模型載入與持續推論 |
| Chestnut 裝置（使用時） | USB 枚舉、載入、持續推論、失敗處理 | USB 枚舉、載入、持續推論、失敗處理 |
| 車型 | 本分支承諾範圍的辨識、控制器與 safety | 本分支承諾範圍的辨識、控制器與 safety |
| 更新 | 舊版→新版、當前／待安裝說明、重新開機 | 舊版→新版、當前／待安裝說明、重新開機 |

使用 `C3X and C4 update compatibility`、HKG 額外的 `C4 and C3X compatibility`、完整 tests、Model runtime contract、CTM 載入及版本說明工作作為 CI 證據。主機測試不替代實機 GPU、Panda 韌體或行車驗證。既有 simulator driving 工作目前停用，不能列成已通過。

重播固定的共同基底為 `3323aafb5422cee72653206dc83a56e66c61799d`。升級基底時審閱參考資料與路線，不以本次待驗證程式直接覆寫預期輸出。

## 回復與故障定位

回復時記錄並對應主程式、子模組、模型／快取及 AGNOS。還原 Git 提交不會自動還原已更新的作業系統或已下載模型。若改了 schema／Params，先確認舊程式可讀取的範圍，再選擇回復方式。

| 現象 | 優先部件 | 必要證據 |
| --- | --- | --- |
| 無法開機／UI 不啟動 | platform、observability、ui | 開機階段、traceback、裝置型號、程式與 AGNOS 版本 |
| 模型無法載入／後端切換 | model_registry、inference、platform | 模型 SHA、runtime pin、runner、USB 狀態與推論錯誤 |
| CAN 被拒／扭力設定未生效 | vehicle_safety、engagement | fingerprint、CP／CP_SP flags、所有 safetyConfig、Panda 簽章與 CAN 紀錄 |
| 導航只有畫面、未影響模型 | navigation、inference | navInstruction／map 串流是否存在，以及 runner 是否實際接收 |
| 中文缺字／重疊／更新資訊錯版 | ui、release | 兩機種截圖、語言、字型、當前／待安裝描述與 CHANGELOG |
| CI 報告與實際測試狀態不同 | validation | 精確 head SHA、push／PR／pull_request_target 事件、目標分支與工作日誌 |

## 文件與地圖維護

新增部件時同步維護 `module_map.json` 與部件目錄，執行 `--check`。新增 schema、持久參數、程序或子模組時，更新架構資料流與升級單位。檔案被多個部件匹配是保守分析的預期行為；沒有匹配到的檔案要人工審閱，不能視為沒有風險。
