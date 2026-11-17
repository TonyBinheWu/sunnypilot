# FormosaPilot Training Studio

這是實際讀取資料與工作狀態的本機工具。資料與模型不會發布到公開網站；服務只監聽 `127.0.0.1:8890`。

## 已實作的流程

1. 車主在原生 FormosaLink 畫面或已登入的裝置網頁，分別同意訓練資料用途。
2. 裝置在停車、有網路時，分塊續傳已完成的 `rlog` 與 `fcamera.hevc`／`ecamera.hevc`。排除車內影片、音訊及授權之前開始的片段。可使用行動數據。
3. FormosaLink 在網站外的私有目錄接收檔案，逐塊驗證裝置簽章、nonce、授權版本、offset 與 SHA-256。完整雙鏡頭片段才會進入訓練資料索引。
4. 經管理者註冊的專用 Ed25519 訓練工作站，只能下載完整的已貢獻資料。此通道與一般裝置監看、診斷分享分開。
5. 工作程序驗證檔案、複製不可變資料快照，按完整行程固定分成 train／validation／test。新資料自動建立新版本，歷史資料同時重播。
6. 從固定 N16 ONNX 提取真實特徵，以合格的 Alpamayo 2 Edge 教師產生控制與 3D 軌跡偽標籤，在 DGX 蒸餾並匯出完整 N16 ONNX。
7. 訓練曲線、失敗紀錄、版本、資料快照及發布資格都可在儀表板查看。訓練版本不會自動上車或發布。
8. 綁定該模型雜湊的閉迴路與 RX 9060 驗收通過後，操作者可按「推送版本」，建立含模型、固定 tinygrad runtime 及報告的 GitHub prerelease。

**目前的實際範圍：**固定的 N16 Nav 基底、action／residual 層，以及教師有效時間範圍內的 3D 位置、速度、yaw／yaw rate 輸出列，共 **1,422,036 個可訓練參數**。視覺骨幹、未觀測到的長時域軌跡列與其他輸出維持原始權重。這不是 0.5B–1B 骨幹擴容或全模型訓練。尚未加入 Action Expert latent 蒸餾。

目前只收取可對齊的無導航路線循道樣本；變換車道與需要側向間隙的指示訊號會排除。有路線的訓練還需要記錄實際 `mapsd` 地圖／47 維導航輸入，不能由 rlog 杜撰地圖。共用控制頭改動後的導航模式也需要另外回歸驗證。

## 啟動

Windows 使用既有隔離 WSL workspace 與 Python 環境：

```powershell
./scripts/run_training_studio.ps1 -FetchModel
```

打開 [Training Studio](http://127.0.0.1:8890)。按「啟動持續訓練」後，工作程序會持續監看，沒有資料時保持等待。這個版本使用既有 `build/official-sim/workspace.json`，不更動車載控制程序。

Linux／DGX 也可直接啟動：

```bash
python -m tools.training_studio.server --root /private/training-studio --port 8890
```

Windows 啟動器將程式複製到既有 WSL workspace。設定及資料庫在該 workspace 的 `build/training-studio/`，不是 Windows 同名目錄。前景啟動或服務中斷時，正在訓練的版本會標成 interrupted，不會自動重跑 optimizer。重試會另建版本，保留先前產物。

## N16 來源與提取

- repository：`commaai/openpilot_driving_models`
- revision：`eed9e515dccd5aa9be969a2d6c57eb469174a97d`
- path：`96244b1f-6c4e-4adc-848d-eccd0b44b182/12800/big_driving_supercombo.onnx`
- SHA-256：`01effc679eb46d6036ce0302673a87fe2dcfcc95a679daeeb929679e53c3647a`
- size：814,591,107 bytes

```bash
python -m tools.training_studio.engine fetch-model --root build/training-studio
```

`models/base.json` 保存驗證結果及實際輸入／輸出契約。這是 `carrot-wip` 的 N16 Nav，並未改用先前模擬流程的 Light speed／Cinque Terre 模型。initializer 元素數包含常數，不能直接視為模型可訓練參數數量。

## 車機／網頁與正式服務部署

`integrate` 對另一個 checkout 套用狹窄 hooks，保留現有 Carrot、診斷、相機與導航功能。預設只列出預計變更，`--write` 才寫入，原檔先備份到目前專案的 `build/training-studio-integration/`。

```powershell
python -m tools.training_studio.integrate --checkout C:/path/to/sunnypilot-carrot-wip --write
```

車機需要取得更新後的分支程式並重啟，才有訓練授權按鈕及背景上傳器。監看、停車設定、支援日誌或 GitHub 登入都不會自動開啟訓練資料授權。

產生工作站專用金鑰，私鑰只保留在 runtime 目錄。輸出的 UUID／public key 可給接收服務註冊：

```bash
python -m tools.training_studio.collector register-key --root build/training-studio --origin https://formosapilot.dinglu-t.com
```

IIS 只能存放公開前端及受 `App_Data` 隱藏規則保護的程式安裝包。私有資料目錄、SQLite、訓練原始資料及 `training-workers.json` 都必須在網站外。

`deploy_collection` 會先核對正式站的現有來源與 Carrot HEAD 是否一致，再複製本功能需要的檔案；不會發布舊分支的整套前端來覆蓋新功能。

```powershell
python -m tools.training_studio.deploy_collection --checkout C:/path/to/sunnypilot-carrot-wip --website \\192.168.20.145\htdocs\FormosaPilot --worker-registration build/training-studio-worker-registration.json --write
```

**SMB 檔案部署不等於後端已更新。** 既有 IIS 後端使用 `C:\ProgramData\FormosaLink-code` 私有副本，需要在 IIS 主機的系統管理員 PowerShell 執行一次已備妥的腳本：

```powershell
& '\\192.168.20.145\htdocs\FormosaPilot\App_Data\enable-training.ps1'
```

若原服務使用其他資料目錄，傳入 `-DataDirectory`。腳本合併訓練工作站 public key，再使用既有 setup-server 更新私有程式副本與服務，不替使用者同意上傳，不替車輛選擇模型。

256 KiB 原始分塊經 base64 與簽章包裝後仍低於既有 IIS 512 KiB 請求上限。預設每裝置容量 20 GiB，可用 `FORMOSA_TRAINING_DEVICE_QUOTA_GIB` 調整；剩餘磁碟不足 2 GiB 加新檔大小時停止接受新檔，不默默刪除資料。撤回阻止後續上傳，不宣稱能從已訓練權重回溯移除資料。

## 匯入已取得授權的既有檔案

```bash
python -m tools.training_studio.import_segment /recordings/route--0 \
  --inbox build/training-studio/inbox \
  --route-group complete-route-identifier \
  --authorized-for-training
```

同一趟行程的所有分段必須使用同一個 `route-group`。不能用逐影格或逐分段亂數分組，否則會產生資料洩漏。

## DGX Spark

runtime 的 `config.json` 支援 `remote` 設定：

```json
{
  "remote": {
    "host": "user@dgx-host",
    "ssh_command": ["ssh", "-o", "BatchMode=yes"],
    "workspace": "/home/user/formosa-training",
    "image": "a-pinned-existing-nvidia-image@sha256:..."
  },
  "training_device": "cuda"
}
```

```bash
python -m tools.training_studio.remote setup --root build/training-studio
```

套件安裝在獨立的 `/studio/deps`，不變更現有 Alpamayo 容器環境。每版建立自己的 `studio-n16-*` 訓練容器，沒有網路、使用同一固定映像與 GPU，且受 12 GiB 容器記憶體上限約束。只停止本工具建立的容器。模型快取按 SHA-256 去重；下載回來的完整 candidate 必須再次通過雜湊驗證。

`worker-readiness.json` 是實際 GPU／套件探測結果，不能當成訓練吞吐或車載效能量測。資料解析與特徵提取預設在工作站 CPU 上執行；DGX 負責可微分的學生輸出頭訓練。要將特徵提取搬到 CUDA，需先確認該主機的 ONNXRuntime CUDA provider，不能把 CPU fallback 誤報成 GPU 加速。

## 教師資格

使用既有 Edge 前向雙鏡頭推論服務，或在已安裝官方 pinned `alpamayo2_edge` 的 DGX 環境執行 `python -m tools.training_studio.teacher_service --model /work/model --receipt /work/model-receipt.json`。服務預設只監聽 loopback 8767；透過 SSH port forward 連接，並將 `teacher_url` 指向該埠。此入口保留真實影像時間戳、容許最多 35 ms 採樣誤差；不以複製影格補缺失視野。新服務預設不具駕駛資格，仍須通過下述閉迴路關卡。`config.json` 設定 `teacher_url`，並指定 `teacher_qualification` 的本機路徑。

```bash
python -m tools.training_studio.qualify_teacher \
  --batch build/official-sim/training/edge-evaluation/ACTUAL-PASSING-BATCH \
  --output build/training-studio/teacher-qualification.json
```

工具只接受既有真實閉迴路批次的 pass 狀態、完整情境、相同教師 provenance、沒有參考控制／號誌真值輸入的結果。教師版本或 adapter 改變，需要重新取得資格。資格不成立時保留失敗，不用 scripted labels 替代 NVIDIA 偽標籤。

教師輸出為偽標籤，非 Ground Truth。所有原始輸出保存在私有 run 目錄；文字不確定性只是額外拒收條件。正式發布報告不包含影像、rlog、教師推理文字或本機資料路徑。

## 編譯、驗收與發布

設定 `compiler_command` 為參數陣列。此命令必須在具備 RX 9060 的 AMD worker 上執行；DGX 沒有這張卡，不能代替驗收。

```json
{"compiler_command": ["python", "-m", "tools.training_studio.compile", "--run", "{run}"]}
```

編譯器保存實際 tinygrad runtime、gfx1200 產物及來源 ONNX 雜湊。未設定編譯器時仍保存完整學生 ONNX，版本標示待裝置驗收，發布按鈕不可用。

驗收檔必須由真正的閉迴路／裝置測試產生。`accept` 只做證據一致性與門檻檢查，並不自己完成那些測試：

```bash
python -m tools.training_studio.release accept --root build/training-studio \
  --version n16-ACTUAL-VERSION --closed-loop actual-closed-loop.json --device actual-rx9060.json
```

閉迴路報告包含 `candidate_sha256`、`passed`、非空 `cases`（各自 `passed`／`evidence_sha256`）。裝置報告必須包含相同 candidate 與 compiled `artifact_sha256`、`gpu_model: AMD Radeon RX 9060`、`gpu_arch: gfx1200`、`precision: FP16`、實測 `inference_p99_ms < 25`、`peak_vram_bytes <= 3000000000`、`model_hz >= 20`，以及通過的 `fallback_passed`／`thermal_soak_passed`。

通過後由儀表板手動推送。GitHub 認證使用現有 Git credential manager 或工作程序環境中的 `GH_TOKEN`，不會透過表單收取或寫進程式碼。先建立 draft、串流上傳並核對 GitHub asset SHA-256，最後才公開 prerelease；不自動改車載預設模型。

車機在停車時可下載指定版本及其固定 runtime，下一次開機才選用：

```bash
python -m openpilot.sunnypilot.formosalink.training_models select \
  --manifest-url https://github.com/TonyBinheWu/sunnypilot/releases/download/n16-ACTUAL-VERSION/manifest.json
```

恢復原本模型目錄：

```bash
python -m openpilot.sunnypilot.formosalink.training_models restore-catalog
```

## 驗證

```powershell
python -m pytest formosalink/tests/test_training_api.py formosalink/tests/test_training_contributions.py tools/training_studio/tests -q
node --check tools/training_studio/web/studio.js
node --check formosalink/web/training-data.js
```

另外已用真正的固定 N16 完成 action／trajectory PyTorch↔ONNX FP16 比對、兩個 synthetic epochs、非零權重更新及完整 ONNX 匯出。這是實作測試，不是 Alpamayo 真實行車蒸餾結果；測試產物放在 `build/training-studio-tests/`，不會混入正式版本登錄。
