# 推送前模擬紀錄 / Pre-push simulation / プッシュ前の検証

日期：2026-11-09，Asia/Taipei。完整日誌與 JSON 位於工作區 `build/formosalink-prepush/final/`，不納入程式發布包。

## 測試範圍與結果

使用兩個獨立 Linux x86_64 快照、原分支各自釘選的 opendbc、官方 MetaDrive bridge 與實際大模型 ONNX CUDA 推論。每個場景有界執行 70 秒，初始速度 5 m/s。C3X 使用 `BIG=1 / tizi`，C4 使用 `BIG=0 / mici`；這些是 PC 版面／組態設定，**不是 Qualcomm、相機、Panda 或整機的硬體模擬**。

| 分支 | PC 設定 | 共用原生 UI／組態檢查 | FormosaLink 唯讀採樣 | 大模型閉環 | 場景結果 |
| --- | --- | --- | --- | --- | --- |
| hkg-enhanced | C3X | 4／4 通過 | 110 筆；105 筆有效；通過 | 可執行，約 8.37 Hz | 車道包絡超限；未通過 |
| hkg-enhanced | C4 | 4／4 通過 | 110 筆；105 筆有效；通過 | 可執行，約 8.72 Hz | 本次有界場景通過 |
| ccnc-port | C3X | 4／4 通過 | 110 筆；107 筆有效；通過 | 可執行，約 8.34 Hz | 車道包絡超限；未通過 |
| ccnc-port | C4 | 4／4 通過 | 110 筆；107 筆有效；通過 | 可執行，約 9.65 Hz | 車道包絡超限；未通過 |

四輪均無世界碰撞，控制輸出無非有限數，但這不能抵銷越線或推論頻率不足。FormosaLink 觀察器只訂閱真實模擬訊息，不寫入 Params、CAN 或控制輸出。共用原生檢查涵蓋 AGNOS 對應與 manifest、版面選擇、實際 UI frame 輸出及代理預設停用。

另以加入 FormosaLink 前的 HKG 提交 `5adaceb` 重跑 C3X 相同場景，移除代理的 manager／Params 入口，且不執行觀察器：同樣發生越線，最大車道中心偏差約 2.22 m、約 8.57 Hz、無碰撞。因此存在獨立於新代理的主機模型／場景驗證缺口；此單次比較不是統計上的完整不退化證明。

## 相依性及證據限制

- HKG opendbc：`1c51731784729da5ebaf24b3c34106bd27aaf94b`。
- CCNC opendbc：`23330cb5ab3ff9668421603dac22a4e98060b67c`。
- 原生快照使用既有主機專用 adapter：SConstruct、LLVM helper、modeld ONNX 接口、modeld SConscript 及 `openpilot/tools/sim/`。這些 Windows 工作區的模擬／訓練變更不包含在本次 FormosaLink 提交與推送內。
- 初輪環境錯誤保留：Windows 複製後的符號連結被展開為文字；CCNC 有 271 個 LFS 指標未還原成實體檔。已在隔離快照修復，模型與素材依既有 SHA-256 驗證。沒有降低場景驗收條件。
- CCNC 不含 HKG 專有停車標記，故改用獨立的共用檢查 `formosalink.tests.ui_profile_check`；原 HKG 專有檢查仍保留，並未為 CCNC 移植這項功能。
- 預設模擬車是 Honda 共用流程，不能宣稱已驗證 CCNC 真實 CAN、車型介面、Panda safety 或 C3X／C4 的實機推論後端。
- 本次推送交付的是預設停用的唯讀代理及自架平台，未變更控制器、safety、模型或 AGNOS；**不代表大模型場景或實車駕駛驗收通過，也不發布裝置韌體／模型更新**。

## English

Both branches were tested in isolated native PC builds with their own pinned opendbc. All four C3X/C4 layout/configuration profiles passed four common native checks and the production telemetry adapter's read-only simulator observation. Real CUDA model closed loops ran in all profiles; only the bounded HKG/C4 scenario passed its lane-envelope checks. The other three scenarios failed and remain recorded as failures. The pre-FormosaLink HKG baseline also failed the same C3X scenario without the agent or observer. Host-only adapters are not part of this push. These results do not certify physical hardware, real CCNC CAN behavior or driving safety.

## 日本語

両ブランチを個別のネイティブ PC 環境と各自の opendbc で検証しました。C3X／C4 の 4 組すべてで共通 UI・構成チェックと読み取り専用の状態取得が通過しました。実際の CUDA モデルの閉ループは動作しましたが、車線条件に合格したのは今回の HKG／C4 のみです。他の 3 組は不合格として記録しています。FormosaLink 導入前の HKG 基準も、agent や観測処理なしで C3X の同じ場面に失敗しました。実機や CCNC の実 CAN、安全性の合格を意味しません。主機専用の adapter、訓練、モデル変更は今回のプッシュに含めません。
