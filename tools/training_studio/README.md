# FormosaPilot Training Studio

這是實際讀取資料與工作狀態的本機工具。資料與模型不會發布到公開網站；服務只監聽 `127.0.0.1:8890`。

儀表板會區分「同步行車資料」「驗證匯入資料」「教師標註」與「正在訓練」。工作程序心跳獨立於慢速下載與雜湊處理，每 2 秒更新；同步時顯示檔案及已接收 MiB。若尚無訓練版本，狀態列列出缺少的完整行程資料組與教師資格條件。同一趟行程即使有很多片段，也不會拆到 train／validation／test 三組；收集成功不代表已開始訓練。

## 已實作的流程

1. 車主在 Carrot 原生網頁「工具 → 訓練資料授權」、車機 FormosaLink 配對畫面，或已登入的 FormosaLink 裝置網頁，明確同意訓練資料用途。
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

Carrot 原生網頁的入口位於「工具 → 訓練資料授權」，顯示目前授權、待同步狀態及本機保留的已上傳片段數。啟用前需完成 FormosaLink 配對並停車，再按「同意並自動上傳」。開啟或取消視窗不會授權；「停止未來上傳」立即阻止本機繼續上傳，連線後同步雲端。

授權不會補傳先前錄影。授權後的新片段必須同時保留 rlog、fcamera、ecamera，且結束滿 2 分鐘並處於停車狀態才上傳。「紀錄 → 手動傳送」仍是原有分享服務，不會進入訓練資料庫。重新開啟授權視窗可查看上傳器心跳、等待原因、檔案傳輸進度及安全的錯誤類型；單一無法解析的記錄會略過，不阻擋後續片段。

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

### 持續教師適配

操作者明確啟用 runtime `teacher_adaptation.enabled` 後，Studio 會在合格前反覆建立模擬監督資料、訓練實際 Action Expert LoRA、載入自己標記的 `studio-teacher` 容器，再重跑原有完整資格。原始 NVIDIA 基底、VLM／語言解碼器與原有教師容器保持不變；只更新動作專家的注意力、MLP 與輸出投影適配器。這些容器帶有 `formosapilot.owner=training-studio`，停止／替換前核對標記，沒有車機控制或自動發布。

訓練通過與官方推論完全相同的 10 步 Euler 採樣路徑反向傳播，先核對輸出，再用真實未來位置、速度、車身方向及停等誤差最佳化。模擬真值僅供離線監督；送入模型的欄位有明確白名單，排除未來軌跡、號誌狀態與評分器真值。較遠縱向誤差使用 Smooth L1，避免長距離平方誤差壓過近 2 秒停等及車道置中；每次更新實測損失，不採用反而使該樣本損失上升的步幅。

注意力與 MLP 使用低秩殘差；小型動作輸出投影使用完整矩陣殘差，增加煞停與起步的適配能力。從舊低秩投影升級時保留其實際映射，原始投影仍凍結。資料另外涵蓋煞車歷史、紅轉綠、加速與向外偏移歷史。教師服務及最佳化容器使用依內容雜湊命名的程式快照，避免其他版本的程式上傳改變正在執行的模型。

對已在有效停止區內停妥的受阻樣本，離線參考軌跡維持原地停止，不能讓通用接近停止線的參考控制再次要求前移；停得太遠與綠燈起步仍使用原有接近／行進參考。這項修正只產生離線訓練標籤，教師推論仍只有影像、自車歷史及導航文字，閉迴路評分器不變。

停等階段另外對齊官方逆動力學所編碼的參考加速度，並懲罰最壞時刻的速度誤差，避免 6.4 秒平均 loss 稀釋最初 0.1–0.2 秒的正加速度脈衝。續訓父模型排序優先保留已修好的車道關卡，不能只因仍不合格的連續停等秒數稍長就退回有車道失敗的版本；舊排序會依已記錄且權重身分一致的閉迴路證據重新計算。這些排序與離線 loss 都不是資格判定。

離線停等計數使用 `valid_stop_zone_v2`：除未越線與末段低速外，預測末端必須落在既有的停止線前 0–5 公尺內。停在約 5.1 公尺處不能因速度為零而被選為達標樣本。參考已進入有效區時，損失另懲罰預測過早停止；搭配停止區邊界內外的實際渲染樣本，區內維持停等、區外先進入有效區再停車。此版本只修正離線訓練及選模，原閉迴路驗收程式與門檻不變。

教師訓練及服務使用相同的 `teacher_motion` 狀態修正：歷史擬合速度為負、但最近實測自車位移仍向前或為零時，改用最近位移的縱向速度作為解碼初速。真正向後的最近位移與正常正速度擬合保持原值。這可消除煞停後負速度擬合超調所要求的正加速度；不修改量測歷史、模型權重基底、官方來源檔案或場景追蹤器。服務 provenance 包含修正 profile 與程式雜湊，變更後必須重新通過完整資格。新增的煞停至停等樣本使用實際物理步進與速度回饋產生歷史，涵蓋不同車輛動態。

已停妥樣本另有前 2 秒的前進執行速度損失：從最近觀測速度出發，使用既有加速度上限逐步積分，每一步限制速度不小於零。這個近似損失避免用倒退速度抵銷正加速度脈衝；不替代物理閉迴路，也不變更任何驗收界線。

紅燈與行人模擬自行行駛片段可用 `teacher_policy_data` 產生修正監督。它只接受獨立訓練／驗證 seed，核對實際 NVIDIA 輸入與教師身分，重播控制至選定時刻，再驗證當下狀態及最近 20 筆位姿一致。紅燈觀測的參考未來維持紅燈；尚未清空的行人固定在實際觀測位置，避免預知將來放行或因修改時間而使行人跳回原處。已清空的觀測保留正常起步參考。原狀態或參考未來已違規時拒收。相機封包與歷史位姿不變，僅產生離線未來軌跡標籤；這些片段不會變成資格通過證據。其他動態場景尚未支援物理重播監督，必須明確實作後才能收進這條管線。

```bash
python -m tools.training_studio.teacher_policy_data --episode TRAINING_SEED_SIMULATION \
  --index 4 --split train --output build/training-studio/policy-reference
```

runtime `teacher_adaptation.supervision_replay_manifest` 可指定已驗證的模擬修正資料。每輪在傳送 GPU 前依來源雜湊重播一次，核對封包／影像雜湊、有限參考軌跡與獨立資料組，拒絕跨組重複影像。來源不變時不重複加入；更新來源只影響之後的新快照。

凍結 VLM 的逐筆上下文使用工作目錄內的暫存檔，透過記憶體映射載入，最多保留一筆快取；不隨資料筆數累積完整 CPU 副本。訓練完成會清理可重建的暫存上下文，保留資料快照、權重與結果。第一筆同時檢查記憶體與磁碟載入後的動作輸出是否符合官方採樣，避免增加重播資料後超過容器記憶體上限。

行人監督涵蓋穿越中段、接近對側及完全離開後起步，避免預判即將清空就提前越線。標註未來保持當下仍未清空的行人位置與等待條件；一旦在有效區內停妥，參考控制持續停車。資料產生程序與每個 renderer 子程序使用同一份封存程式，`--only-scenario` 可單獨建立新情境資料。

資格採失敗即停止，因此不同候選可能測到不同情境。續訓排序先保留實際已通過的前綴，再比較同等進度的失敗，避免把尚未測到的風險當成比較安全。這只決定續訓父權重；仍須同一候選完整通過 11 關才取得資格。

每輪保留不可變資料、父權重雜湊、候選、實際 loss 及資格失敗。分別保留停等安全優先與綜合驗證 loss 最低的候選，去除相同雜湊後，各自接受同一套完整資格；不能只因最後一個 epoch 的總 loss 最低就放行。後續訓練的父模型依實際閉迴路失敗與已通過關卡選擇，仍不是上車或發布資格。資料含接近停止區、提早停車、低速蠕行、起步與偏移置中；新失敗情境加入後仍重播舊情境，避免遺忘。訓練 seed 1000–6999、驗證 seed 8000–9499 與資格 seed 300–303 隔離；每筆在獨立 renderer 程序生成，以免累積 D3D12 context 損壞。真實片段的學生資料分組規則不變。

`teacher-adaptation/state.json` 鎖定場景評分器、紅燈停等稽核、追蹤器及資格實驗程式的雜湊；變動時拒絕默默沿用。每輪仍須通過 3 個紅燈及其他 8 個情境，不放寬停等、車道、碰撞、進度或起步門檻。儀表板的「教師訓練 loss」與 N16 學生 loss 分開顯示。按「暫停持續訓練」會停止自己的訓練工作；失聯 lease 超過 90 秒也會結束 GPU 最佳化。再次啟動保留已執行版本，建立下一輪，直到完整資格通過或操作者停止。

Studio 可維護自己的 SSH tunnel，並由背景監看程序每 3 秒核對線上教師。runtime `config.json` 的 `teacher_connection.tunnel_command` 使用可信任的本機參數陣列（既有 SSH wrapper、`-N`、`-o ExitOnForwardFailure=yes`、`-L 127.0.0.1:18766:127.0.0.1:8766`、既有 DGX host）；只停止自己啟動的 tunnel，不停止既有教師容器。`teacher_url` 指向 `http://127.0.0.1:18766`。

Windows 請使用 `scripts/run_training_studio.ps1`：啟動器會隱藏視窗並維持 `wsl.exe` 存活，讓既有 Windows TCP proxy 的 WSL interop 環境不會隨啟動命令結束而失效。SSH 建議設定 `ConnectTimeout=10`、`ConnectionAttempts=1`、`ServerAliveInterval=15` 與 `ServerAliveCountMax=3`，讓失聯通道可以結束並由監看程序重建。

`qualification_checkout` 必須指向已備妥 MetaDrive 完整場景資產、可執行 `openpilot.tools.sim.training.edge_experiment` 的 checkout；`qualification_display` 預設 `:0`。`teacher_qualification` 指定合格報告的本機檔案路徑。每個新教師指紋會自動執行一次真實資格驗證：3 個紅燈停等案例及其餘 8 個情境。任一失敗即停止並保留證據；相同失敗權重不會不斷重跑。修正教師後可按「重新驗證教師」，權重指紋改變也會自動重新驗證。

儀表板顯示接口心跳、GPU、驗證情境、完成關卡、實際模型推論次數、模擬時間、推論耗時與失敗原因。資格驗證不是學生最佳化，不會產生假的 loss。通過全部關卡、報告與線上完整 provenance 一致、且三個完整行程資料組都有資料後，工作程序才自動排入蒸餾；DGX 每 3 秒同步真實 epoch／train loss／validation loss。教師斷線、權重或 LoRA 改變、報告不符時，會暫停建立新訓練工作。

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
