# 2026-11-01 平台、套件與導航更新

工作樹版本：兩分支均為 `2026.003.003`。本頁記錄此版本的改動與主機驗證；裝置的安裝與實機驗證需另行確認。

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
