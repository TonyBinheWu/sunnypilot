# HKG 低速動態轉向扭力實驗分支

分支：`TonyBinheWu/sunnypilot:hkg-enhanced`

此功能由 `ev6-low-speed-torque` 分支恢復至 `hkg-enhanced`，供 Hyundai／Kia／Genesis（HKG）CAN-FD 車型使用。

目前 opendbc 固定至 `TonyBinheWu/opendbc@1c51731784729da5ebaf24b3c34106bd27aaf94b`，讓 Python 控制器與 Panda safety 使用同一組動態扭力與轉向速率曲線及啟用旗標。

## 安裝

在 comma 裝置的「Custom Software／自訂軟體」安裝畫面輸入：

```text
install.sunnypilot.ai/fork/TonyBinheWu/hkg-enhanced
```

完整網址：<https://install.sunnypilot.ai/fork/TonyBinheWu/hkg-enhanced>

`/fork/TonyBinheWu/` 指定此帳號的 `sunnypilot` 儲存庫。

這是原始碼分支。安裝器會下載程式與子模組，首次啟動沿用 `launch_chffrplus.sh` → `openpilot/system/manager/build.py` 的 SCons 編譯流程；分支沒有 `prebuilt` 標記。首次安裝須保留穩定供電、Wi-Fi 與下載模型及編譯的時間。AGNOS 依 `launch_env.sh` 選擇 C3X 19.9／C4 20.1；實機驗證範圍見[平台更新紀錄](architecture/PLATFORM_UPGRADE_2026_11.md)。

目前裝有其他版本時，先在停車狀態透過原本的解除安裝流程回到自訂軟體畫面。不要在行駛時安裝或切換分支。

## 適用車型與設定

在裝置的 **Settings → Steering → HKG 低速轉向扭力（實驗功能）** 開啟。英文名稱為 **HKG Low-Speed Steering Torque (Experimental)**。

- 預設關閉，包括從舊 EV6 版本更新的裝置；更新後需手動開啟。
- 僅在非行車狀態且已辨識到相容車型時才能調整。首次使用若尚未辨識車型，先啟動車輛完成辨識，再回到非行車狀態設定。
- 設定在下次啟動行車系統時生效。停車但仍在行車模式時不會即時切換；關閉開關後，下次行車恢復原上限。
- sunnylink 的 Steering 設定定義也加入同一開關、非行車限制與相容性判斷。

條件為：已收錄的 HKG CAN-FD 平台、扭力控制、`hyundaiCanfd` Panda 模式，且沒有 `ALT_LIMITS`、`ALT_LIMITS_2` 或 `dashcamOnly` 限制。UI 與車輛初始化共用同一相容性函式。手動寫入設定也不能在不相容車型上啟用。

**傳統 CAN 與角度控制車型不支援此功能。** 傳統 CAN 車型有 170、255、270、384 等不同上限，不能直接套用此曲線。這不會新增未收錄的年式或 EPS 韌體支援，也不保證停車或髮夾彎可以自動完成。

目前符合架構條件的 19 個平台如下；這是程式相容性範圍，不代表每一款車都已完成實車驗證。

| 品牌 | 平台識別碼 |
| --- | --- |
| Hyundai | `HYUNDAI_IONIQ_5`、`HYUNDAI_IONIQ_6`、`HYUNDAI_KONA_EV_2ND_GEN`、`HYUNDAI_SANTA_CRUZ_1ST_GEN`、`HYUNDAI_STARIA_4TH_GEN`、`HYUNDAI_TUCSON_4TH_GEN` |
| Kia | `KIA_CARNIVAL_4TH_GEN`、`KIA_EV6`、`KIA_K8_HEV_1ST_GEN`、`KIA_NIRO_EV_2ND_GEN`、`KIA_NIRO_HEV_2ND_GEN`、`KIA_SORENTO_4TH_GEN`、`KIA_SORENTO_HEV_4TH_GEN`、`KIA_SPORTAGE_5TH_GEN` |
| Genesis | `GENESIS_G80_2ND_GEN_FL`、`GENESIS_GV60_EV_1ST_GEN`、`GENESIS_GV70_1ST_GEN`、`GENESIS_GV70_ELECTRIFIED_1ST_GEN`、`GENESIS_GV80` |

開關啟用時的曲線：

| 車速 | 轉向 CAN 指令絕對值上限 |
| --- | ---: |
| ≤ 46.8 km/h（13 m/s） | 409 |
| 46.8～61.2 km/h（13～17 m/s） | 409 線性降至 270 |
| ≥ 61.2 km/h（17 m/s） | 270 |

409 相較原 270 增加約 51.5%。這是 CAN 指令數值，不是 Nm，也不能推論實際轉向扭矩或可完成彎道增加相同比例。

開關啟用時的轉向扭力上升／下降速率：

| 車速 | 上升速率 | 下降速率 |
| --- | ---: | ---: |
| ≤ 46.8 km/h（13 m/s） | 4 | 6 |
| 46.8～61.2 km/h（13～17 m/s） | 4 線性降至 2 | 6 線性降至 3 |
| ≥ 61.2 km/h（17 m/s） | 2 | 3 |

Controller 依 `vEgoRaw` 計算速率，Panda safety 依 CAN 輪速獨立計算並採相同曲線。因 CAN 指令速率為整數，13～17 m/s 的線性插值會以整數階梯呈現；Controller 在速率取整邊界採保守的較高速 bin，避免因 Float32 與 CAN 輪速量化差異而送出 Panda 不接受的指令。為容納低速 4／6 rate，Panda 在必要的低速／過渡 realtime 視窗使用 162 的 `max_rt_delta`，回到一般速率後恢復 112。駕駛扭力 allowance／multiplier 仍為 250／2，並保留既有約 85° 的 EPS 故障避免邏輯。開關關閉時仍維持 CAN-FD 原本 270 上限與 2／3 速率。

## 整合方式

將 [opendbc PR #3720](https://github.com/commaai/opendbc/pull/3720) 的候選實作移植到主分支原本釘選的 sunnypilot/opendbc 提交 `f95f996f5917dcbbf2e32fe51b606a24cf836af6`，保留 sunnypilot 的 `CarParamsSP`、`CarControlSP`、MADS 與其他既有擴充。

本次 4／6 速率實作來源分支為 `TonyBinheWu/opendbc:hkg-steering-rates-4-6`。主儲存庫的 `.gitmodules` 指向此 fork，`opendbc_repo` 以固定提交釘選。更新 opendbc 分支本身不會自動改變本分支；必須另行更新子模組提交。

`HkgLowSpeedTorque` 是預設 `false` 的持久化布林設定。`card.py` 透過既有 `initialize_params` → `get_car` → opendbc `setup_interfaces` 流程讀取；在建立 CarController 前，同步設定 `CarParams.flags` 與 Panda 的 `safetyParam`。不在控制迴圈中讀取開關，也不會出現僅更新 Python 上限卻漏掉 Panda 參數的切換方式。

MADS、Chestnut 模型載入與既有裝置編譯流程沿用本分支基底。此功能不需要合併回 `master`；日後合入上游更新時，必須保留開關與 opendbc 的固定提交，並重新驗證 HKG 控制器及 safety 測試。

CarController 計算速度上限，Panda 另由 CAN 輪速取樣獨立計算與檢查。Panda 使用既有輪速取樣最小值，因此加速跨過邊界時，可能短暫保留先前較低的輪速樣本；當取樣最小值達 17 m/s 時，上限為 270。

本基底的 Panda `SConscript` 直接包含已釘選 opendbc 的 safety 原始碼。裝置編譯後，`pandad` 會依韌體簽章比對更新 Panda；不需要手動繞過 Panda 或改刷不相符的韌體。

## 2026.003.008：低速左右晃動的換算修正

舊版將控制器正規化需求直接乘以當下的動態上限。同樣的 `0.1` 需求，關閉高扭時為 27 CAN 單位，低速開啟時變成約 41；409 上限相對 270 的額外餘裕，因此也放大了小幅轉向修正。大、小模型共用此控制路徑，模型輸出的小幅正負變化可能被這個額外增益加劇。

本版用獨立的 `HkgTorqueScale` 部件處理換算：

* v0／v1、NNLC／Jerk 延伸控制器內部維持原本 270 單位的調校基準；可用 PID 上限依車速擴展到 `動態上限 / 270`。
* 送入 CarController 前，將需求轉回當下動態上限的正規化尺度。因此相同的小幅需求維持約 27 CAN 單位；當持續轉向需求足夠時，仍可用完整 409 單位。
* 使用 `vEgoRaw` 與相同的速度量化、取整方式配對 CarController，避免 13～17 m/s 過渡區使用不同換算。
* 扭力學習改讀 `torqueOutputCan / 270`，不再直接使用會隨動態上限改變的正規化輸出。高扭啟用時學習版本為 101，拒絕還原舊尺度的快取；開關狀態不同的快取亦分開。
* 上限曲線、4／6→2／3 速率、Panda safety、駕駛介入與 EPS 故障避免邏輯維持原設定，未修改 opendbc pin 或韌體；沒有新增模型輸出濾波延遲。

驗證以實際 v0／v1 與 Hyundai CarController 串接，覆蓋 EV6、IONIQ 5、GV60 的 20 Hz 左右交替需求、409／340／270 上限、421 個速度量化點與學習快取隔離。這是控制器層的相容性修正；尚未執行指定大模型或故障車 EPS 的實機測試，不能保證已排除所有方向盤震盪原因。

2026-11-09 原生 Linux 驗證：舊版重現 24 組轉向需求放大與 1 組學習尺度錯誤；修正後含既有 HKG 車型初始化、速率、駕駛介入、EPS 故障避免、控制器延伸、Honda／Toyota 與更新說明共 68 項測試通過。修改的 Python 檔案 Ruff 通過；C3X／C4 相容性工作流程已加入這組新回歸測試，遠端 Actions 以對應提交的實際結果為準。

## 確認與還原

安裝完成後，在軟體資訊頁確認分支為 `hkg-enhanced`。有 SSH 時可在裝置檢查：

```bash
cd /data/openpilot
git branch --show-current
git remote get-url origin
git submodule status opendbc_repo
```

預期 origin 為 `https://github.com/TonyBinheWu/sunnypilot.git`，opendbc 提交與 GitHub 本分支的子模組一致。

若只要還原轉向上限，在 Steering 頁關閉開關，於下次行車生效。若要移除此實驗分支，可透過自訂軟體安裝：

```text
install.sunnypilot.ai/fork/TonyBinheWu/master
```

## 驗證範圍

本次 HKG 開關整合驗證結果（更新至 2026-09-25）：

- 409 上限＋4／6 動態速率版本的 opendbc GitHub Actions 已通過 safety、safety mutation、Linux／macOS `./test.sh` 與 car-model 測試矩陣。
- 新增 Controller 與 Panda safety 的 4／6→2／3 邊界、速率過渡、開關關閉回復、driver torque、realtime limit 與 CAN 輪速量化測試。
- sunnylink 設定編譯、結構、能力判斷沿用既有 `HkgLowSpeedTorque` 開關；`settings_ui.json` 與 YAML 定義不需新增第二個開關。
- `HkgLowSpeedTorque` 仍為預設關閉的持久化布林參數；Steering 頁與繁體中文翻譯維持既有設定。

驗證涵蓋全部 HKG 平台的相容性與重設、符合條件的 CAN-FD 平台經 `get_car` 初始化後產生的 CAN 指令，以及多 Panda 參數、未知平台、角度控制與其他品牌的隔離。速度插值、正規化回饋、駕駛介入、速率與高角度故障避免測試涵蓋 EV6、IONIQ 5 與 GV60。Panda 測試包含多種 CAN-FD 配置、輪速量化、旗標重設，以及 MADS 在 ACC 未啟用時仍遵守同一扭力上限。

409 是待驗證的實驗候選值。軟體測試與韌體編譯不代表已驗證各 HKG 車型 EPS 的物理極限、橫向加速度、jerk 或轉彎效果。此環境沒有連接實車、comma 或 Chestnut 裝置，無法完成裝置上的整套 sunnypilot 編譯、開機、刷寫與行車驗證。安裝成功後仍需在受控場地、可隨時接管的條件下比對修改前後的紀錄，不能把它視為已驗證的道路版本。
