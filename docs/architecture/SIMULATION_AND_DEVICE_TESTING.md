# 上上游模擬器與 C3X／C4 驗證

查核日期：2026-10-31。上上游 `commaai/openpilot/master` 的查核提交為 `afedebcfd4213a76b99b1f11b5310ed05cee04df`。下列來源固定到此提交，避免後續 master 移動造成判讀混淆。

## 查找結果

上上游提供 [MetaDrive bridge](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/openpilot/tools/sim/README.md)，目前兩個維護分支都已保留 `openpilot/tools/sim/`。它模擬道路、車輛、影像與感測訊息，讓 openpilot 的模型、規劃與控制形成軟體閉環。

它沒有模擬 C3X／C4 的整部裝置。C3X 是 `tizi`，C4 是 `mici`；主機的 `BIG=1/0` 只用於檢查對應 UI 版面，不能把 PC 變成相應的 Qualcomm、相機或 USB 硬體。

| 工具 | 適合驗證 | 必須另外驗證 |
| --- | --- | --- |
| MetaDrive bridge | 模擬影像→模型→規劃→控制→模擬車的閉環、程序健康與啟用流程 | 實際相機、GPU／USB、Panda safety、CCNC 車型封包 |
| process replay | 固定紀錄下的定位、規劃、控制等程序回歸 | 互動閉環、實機驅動與持續運行 |
| model replay | 固定影像下的模型輸出與推論回歸 | 所有自訂模型 runner、相機取像、USB 穩定度 |
| route replay＋UI | 真實路線的訊息與畫面重播 | 新版模型及控制器是否重新運算正確 |
| 本專案雙機種主機 UI 檢查 | C3X／C4 版面、中文、更新資訊及指定的啟動回歸 | 真正裝置開機與硬體效能 |
| test_onroad＋硬體測試 | 真正裝置的服務頻率、相機同步、模型時間、記憶體與 CPU | 真實車型整合與較長時間穩定度 |

上游的 [process replay 文件](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/openpilot/selfdrive/test/process_replay/README.md)、[model replay 程式](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/openpilot/selfdrive/test/process_replay/model_replay.py)與 [route replay 文件](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/openpilot/tools/replay/README.md)分別對應不同驗證目的，不應把播放舊模型輸出的畫面當成重新執行模型的證據。

## 目前兩分支與上游的缺口

1. **自動駕駛模擬測試尚未啟用。** 上游及兩分支的 `.github/workflows/tests.yaml` 都對 `simulator_driving` 設定 `if: false`，`test_sim_bridge.py` 的 `test_driving` 也有無條件 skip。來源：[上游 workflow](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/.github/workflows/tests.yaml)、[測試本體](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/openpilot/tools/sim/tests/test_sim_bridge.py)。綠色的其他 CI 不代表模擬駕駛已通過。
2. **預設沒有安裝 MetaDrive。** 上游與兩分支 `pyproject.toml` 中對應依賴已註解，候選來源是 `commaai/metadrive` 的 `minimal` 分支，且原依賴條件排除 aarch64。恢復使用前需要選定可工作的固定提交、Python 版本與圖形環境。不要直接加入未釘選的最新版。
3. **預設車型是 Honda Civic 2022。** `launch_openpilot.sh` 固定 `FINGERPRINT=HONDA_CIVIC_2022`，`simulated_car.py` 使用 Honda DBC 並發布模擬 Panda 狀態。這能測共用流程，不能證明 CCNC 的 CarState、CarController 或真實 safety 正確。來源：[啟動腳本](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/openpilot/tools/sim/launch_openpilot.sh)、[模擬車](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/openpilot/tools/sim/lib/simulated_car.py)。
4. **現有 Chestnut 實機測試限制 MICI。** 兩分支 `TestChestnutOnroad` 有 `requires MICI` 的 skip 條件，C3X 不會執行這組測試。C3X eGPU 需要獨立測試入口及能力檢查，不能只移除 skip。上游也限制 MICI，且上游已新增切斷 VBUS 後回退小模型的測試；兩分支目前尚無這段測試。來源：[上游 test_onroad](https://github.com/commaai/openpilot/blob/afedebcfd4213a76b99b1f11b5310ed05cee04df/openpilot/selfdrive/test/test_onroad.py)。
5. **模型 runner 覆蓋不完整。** 本專案另有 `modeld_tinygrad`／`modeld_v2`，現有 model replay 以名為 `modeld` 的 process config 執行，不能推定自動包含所有自訂模型。CPU runtime contract 與 CTM 載入測試也不代表 QCOM／Chestnut 實機推論通過。
6. **必須確認真的收集並執行測試。** `test_metadrive_bridge.py` 沒有 `unittest.main()`，直接以 `python <檔案>` 執行會載入定義而不執行測試；本專案 `tools/test_runner.py` 也把 sim 目錄排除於一般掃描。正式接入時需指定測試類別，檢查 executed／skipped 數量，不能只看 exit code。
7. **模型差異報告的 exit code 有限制。** 兩分支 `model_replay.py` 在 `CI` 環境中會把比較後的 `failed` 設為 False；驗收要讀取 `model_diff.txt` 並明訂允許差異，不能只看程式成功退出。不要用更新參考輸出消除未解釋的差異。

以上缺口由原始碼比對確認；本次未啟用 workflow、安裝模擬器或修改控制／GPU 行為。

## 主機試跑方式

優先使用 Ubuntu 24.04；Windows 可使用 WSL2 的 Ubuntu，圖形與模型後端是否可用仍需實測。開發環境步驟見 [本專案工具說明](../../tools/README.md)。MetaDrive 依賴需先在獨立環境驗證並釘選，本段不是目前可直接通過的安裝承諾。

完成儲存庫依賴、原生編譯與 MetaDrive 安裝後，在專用測試工作區的兩個終端執行：

```bash
# 終端 A：儲存庫根目錄；會設定模擬用 Params 並啟動 manager
source .venv/bin/activate
bash openpilot/tools/sim/launch_openpilot.sh
```

```bash
# 終端 B：同一儲存庫根目錄
source .venv/bin/activate
python openpilot/tools/sim/run_bridge.py --dual_camera
```

這是主機共用流程的試跑。兩個分支分別執行，並記錄分支、提交、實際 runner、模型 SHA、後端、frame drop、程序退出及啟用結果。需要比較兩套 UI 時可各次設定 `BIG=1`、`BIG=0`，但這不產生裝置硬體覆蓋。若設定 `CI=1`，目前啟動腳本會阻擋 UI，不能再以它驗證畫面。

目前可用下面指令明確載入模擬測試類別；預期結果仍為 skip，並非通過閉環驗收：

```bash
python -m unittest openpilot.tools.sim.tests.test_metadrive_bridge.TestMetaDriveBridge -v
```

不要以 `FINGERPRINT` 改成 CCNC 取代模擬車 adapter；CAN 產生、車輛狀態、控制回讀及 safety 契約也需要一起實作。

## C3X／C4 實機驗證入口

在專用測試裝置完成編譯、模型準備並停止一般執行中的 manager 後，可分別以相同提交執行：

```bash
python -m unittest openpilot.selfdrive.test.test_onroad.TestOnroad -v
python openpilot/selfdrive/test/process_replay/model_replay.py
```

這些測試會初始化硬體、啟動程序及設定測試參數。`TestOnroad` 使用模擬訊息輔助進入運作狀態，驗證實際裝置執行；不等於真實 CAN／車型路測。CPU 預算與程序清單目前是既有固定值，兩裝置及自訂 runner 是否適用仍需各自校準並記錄原因。

有 Chestnut 的 C4 可另執行既有測試與模型重播：

```bash
python -m unittest openpilot.selfdrive.test.test_onroad.TestChestnutOnroad -v
python openpilot/selfdrive/test/process_replay/model_replay.py --chestnut
```

C3X 的 `TestChestnutOnroad` 目前會 skip。model replay 是否使用預期後端須查看實際載入與輸出，並確認全程使用指定模型；不要把 fallback 成功當成大模型成功。上游裝置 CI 準備腳本會清理資料與改變裝置設定，不能直接當成一般使用者機器的安裝指令。

## 建議接入順序與驗收矩陣

1. 先修復並固定主機 MetaDrive 環境；解決停用原因、明確執行測試、加入有界 timeout 與清理，保留日誌及失敗畫面。測試至少要驗證必要程序、訊息頻率、持續 engaged、路徑完成及失敗退出。
2. 為每個實際使用的模型 runner 建立明確選擇與輸出驗證，區分模型載入成功、推論成功及閉環成功。
3. 保留 Honda 共用 smoke test，另外建立 CCNC adapter 或使用代表性 CCNC 紀錄做 car/controller 與 safety 回歸；兩分支各用自身 opendbc pin。
4. 建立 C3X／C4 專用裝置測試工作，按能力分開 QCOM 與 Chestnut。接入 C3X Chestnut 時需驗證驅動、供電、USB、warmup、持續推論及故障處理；上游 MICI VBUS 測試不能原樣套用。

| 維護分支 | PC 閉環／UI | C3X QCOM | C3X Chestnut（使用時） | C4 QCOM | C4 Chestnut（使用時） | 車型／safety |
| --- | --- | --- | --- | --- | --- | --- |
| hkg-enhanced | MetaDrive＋兩套 UI | 實機 | 實機＋待補測試入口 | 實機 | 實機 | 承諾支援車型逐組驗證 |
| ccnc-port | 共用 smoke＋CCNC 待接入 | 實機 | 實機＋待補測試入口 | 實機 | 實機 | CCNC CAN／controller／safety |

表格是驗收要求，不是已通過結果。每個格子記錄精確提交、裝置、模型、runner、後端、執行／跳過數、日誌及結論；無裝置或依賴時標示未驗證。長時間穩定度與真實車型測試另行記錄。
