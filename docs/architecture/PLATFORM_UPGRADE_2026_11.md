# 2026-11-01 平台、套件與導航更新

平台更新基準：兩分支 `2026.003.003`。本頁記錄平台更新與後續 eGPU 修正；裝置的安裝與實機驗證需另行確認。

## hkg-enhanced 2026.003.006：暖機失敗後的參數缺失

原廠線紀錄顯示，大模型在暖機輸出讀回時拋出 `AMD failed with -1`，隨後讀取未註冊的 `ChestnutRetry` 再次拋出 `UnknownKeyName`，使 modeld 在載入小模型之前退出。這與前幾次已進入推論後成功回退小模型的故障路徑不同。

補回 sunnypilot master 的 `ChestnutRetry` 定義：`BOOL`，於 `CLEAR_ON_MANAGER_START | CLEAR_ON_IGNITION_ON` 清除。此狀態不在 `CLEAR_ON_OFFROAD_TRANSITION` 或 `CLEAR_ON_ONROAD_TRANSITION` 清除，才能讓既有的 `OnroadCycleRequested` 流程每次點火僅重試一次，而不反覆切換。

新增兩個原生 Params 回歸，分別檢查參數讀寫／清除生命週期，以及直接執行標準與 sunnypilot 模型執行器的載入失敗分支。這不模擬真實 GPU；上游單次重試與回退策略未另行改寫，也沒有放寬 USB 或定位檢查。

Linux 原生驗證已在修正前重現 `UnknownKeyName: ChestnutRetry`；補上參數並重建後，完整 Params、更新說明與 eGPU 啟動測試共 28 項通過，`scons --minimal` 建置成功。C3X／C4 CI 矩陣新增上述兩項原生 Params 回歸；主機驗證結果不代表實體 GPU 已恢復穩定。

`AMD failed with -1` 的傳輸原因仍未確定；原廠線亦重現，只能排除「僅先前那條非原廠線造成」的說法，不能證明所有線材、供電或平台均正常。此修正處理其後的程式崩潰，不代表已修復 eGPU 鏈路本身。

## hkg-enhanced 2026.003.005：eGPU 上游差異與修正

比對基準為 [sunnypilot master `6f7a2c94`](https://github.com/sunnypilot/sunnypilot/tree/6f7a2c94c10dffcf9a83b120ab1e6985e4496868)。此處僅同步 eGPU 韌體與啟動流程，不代表完整合併 master。

| 部件 | 修正前 hkg-enhanced | sunnypilot master／此次處理 |
| --- | --- | --- |
| tinygrad | `92b742f711c7d216fd3ed7a46a30a959e3c43bd4` | 相同，保留釘選；沒有可直接套用的較新 USB 後端差異 |
| Chestnut 韌體 | `ed4e39b7` | 同步 `8516b768` 及完整 `firmware_wrapped.bin`，來源為上游 [a742df61](https://github.com/sunnypilot/sunnypilot/commit/a742df61827f8b34eee1af99bbb881201163e472) |
| 韌體更新啟動條件 | 缺少更新中等待條件；第一次更新也受重試間隔限制 | 同步 `Chestnut.flashing`、首次即時更新與初始 USB 清單，以及最長 30 秒的啟動等待 |
| AGNOS | `20.1` | 上游此基準為 `19.9`；保留使用者指定的 `20.1`，此組合仍需 C3X／C4 實機驗證 |

上游韌體提交僅說明版本更新，沒有承諾修復 `AMD failed with -7`。目前紀錄可確認 USB 傳輸逾時及同時段的短暫定位輸入異常，尚不能證明逾時由韌體版本造成。更新韌體後的穩定性需在同一台 C3X、相同供電與模型負載下重新驗證。

裝置沿用既有的非行車韌體更新程序；本次沒有操作實機或直接執行刷寫。啟動等待採上游的 30 秒上限，並不代表等待整個最長 600 秒的刷寫預算。超過等待上限後，模型仍依既有韌體產品字串判斷是否使用 eGPU。

主機回歸：`python -m unittest tools.diagnostics.test_chestnut_startup -v` 共 6 項通過，涵蓋首次更新、非行車限制、同時執行與重試預算、啟動等待及逾時、正確版本傳入刷寫程序、韌體校驗與產品字串。這些測試不涵蓋真實 USB、電源、AGNOS 或 GPU 推論。

實機驗證需分別記錄 C3X 與 C4 的韌體更新結果、模型啟動、冷啟動／車輛啟動期間供電、持續推論及小模型回退；保留故障當分鐘的完整 rlog。接管警示及定位輸入檢查維持原設定。

## 更新內容

* 參考 `commaai/openpilot@afedebcfd4213a76b99b1f11b5310ed05cee04df` 的 [launch_env.sh](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/launch_env.sh)、[版本標頭](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/openpilot/common/version.h)及 [AGNOS manifest](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/openpilot/common/hardware/comma/agnos.json)，將兩分支 AGNOS 目標改為 20.1，openpilot 基底標示改為 0.11.3。這是指定項目移植，並非完整合併 master。
* 同步官方映像 URL、hash、hash_raw、ondevice_hash 及替代下載資料。保留 C3X／C4 裝置識別與原有相容路徑；既有 AGNOS updater 程式與該上游提交一致。
* `uv lock --upgrade --python 3.12` 更新 42 項套件，新增 7 項、移除 2 項，見 [完整明細](DEPENDENCY_UPGRADE.json)。保留 Python 3.12 範圍、pycapnp 2.1.0、目前的 msgq／ZeroMQ 架構及所有子模組釘選。上游的新 msgq-ipc 套件架構未混入舊 msgq pin。
* `ccnc-port` 同步 HKG 的 `selfdrive/navigation`、navd／mapsd 註冊、NavigationEnabled／NavDestination、navInstruction／navRoute schema 名稱與服務定義。保留訊息 ordinal 82／83。預設關閉，只在行車且 NavigationEnabled 為 true 時執行；mapd 保持原用途。
* 兩分支版本標頭、README 與繁體中文 CHANGELOG 同步更新。HKG 的新版 Ruff 字串檢查修正不改變測試內容。

## 驗證結果

在 Ubuntu 22.04 WSL 的兩個獨立暫存 checkout，使用 Python 3.12.13 與各分支既有 opendbc pin 驗證：

| 檢查 | hkg-enhanced | ccnc-port |
| --- | --- | --- |
| 新鎖定套件實際安裝 | 通過 | 通過 |
| Ruff 0.17.3 | 通過 | 通過 |
| SCons 最小原生建置 | 通過 | 通過 |
| 導航資料流、啟停條件、更新說明 | 27 項通過 | 27 項通過 |
| C3X tizi／BIG=1 更新資訊 | 3 項通過 | 3 項通過 |
| C4 mici／BIG=0 更新資訊 | 3 項通過 | 3 項通過 |
| HKG 雙機種識別、AGNOS manifest 與 UI frame 檢查 | 每 profile 5 項通過 | 無這套 HKG 專屬工具 |
| 主要升級套件 API／加密往返 | 通過 | 通過 |

套件 smoke 包含 pycapnp 版本、NumPy／Pillow、ZeroMQ 載入、PyJWT、Crypto AES／RSA、dateutil、Hugging Face API 與本專案 AESCipher 載入。導航整合測試使用本機 HTTP tile server，涵蓋失敗與恢復；不是外部導航服務的線上驗收。

最小建置因環境缺少 LLVM 而跳過 tinygrad 模型編譯；本次沒有完成模型編譯／GPU 推論、完整測試矩陣或 GitHub Actions 驗證。UI 是 headless 主機檢查，真實字型效果、捲動、AGNOS 安裝／開機、QCOM／Chestnut 與實車行為仍需 C3X、C4 各自驗證。裝置更新由正常 updater 執行；本次沒有對任何裝置刷寫。

## Toyota 後續範圍確認

維護者已提供 StarPilot 並選擇保留原有扭力上限；`hkg-enhanced` 加入 [Honda／Toyota 低速控制調校](../LOW_SPEED_STEERING_TUNE.md)。此項不修改 opendbc／Panda safety，`ccnc-port` 不加入此車種功能。
