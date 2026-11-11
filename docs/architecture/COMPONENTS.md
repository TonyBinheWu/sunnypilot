# 模組部件目錄

由 `module_map.json` 產生的 15 個維護部件。路徑可重疊，表示監看範圍，不代表獨立套件或可單獨部署的服務。

| ID | 部件 | 適用分支 |
| --- | --- | --- |
| `platform` | 硬體、開機與建置 | hkg-enhanced、ccnc-port |
| `bus` | 訊息、影像傳輸與設定 | hkg-enhanced、ccnc-port |
| `model_registry` | 模型目錄、下載與選擇 | hkg-enhanced、ccnc-port |
| `inference` | 感知模型與推論執行 | hkg-enhanced、ccnc-port |
| `localization` | 定位、校正與車輛估測 | hkg-enhanced、ccnc-port |
| `vehicle_safety` | 車型、CAN、控制器與 Panda safety | hkg-enhanced、ccnc-port |
| `engagement` | 啟用狀態、MADS 與駕駛監控 | hkg-enhanced、ccnc-port |
| `map_assistance` | 地圖資料、限速與智慧巡航 | hkg-enhanced、ccnc-port |
| `planning_control` | 規劃、橫縱向控制與擴充 | hkg-enhanced、ccnc-port |
| `navigation` | 路線導航與地圖影像 | hkg-enhanced、ccnc-port |
| `release` | 版本、裝置更新與打包 | hkg-enhanced、ccnc-port |
| `ui` | C3X／C4 介面、翻譯與字型 | hkg-enhanced、ccnc-port |
| `cloud` | 雲端、遠端設定、備份與串流 | hkg-enhanced、ccnc-port |
| `observability` | 記錄、健康狀態與故障診斷 | hkg-enhanced、ccnc-port |
| `validation` | CI、測試基準與維護地圖 | hkg-enhanced、ccnc-port |

## platform：硬體、開機與建置

**程式與監看路徑**

* `launch_chffrplus.sh`
* `launch_env.sh`
* `launch_openpilot.sh`
* `SConstruct`
* `pyproject.toml`
* `uv.lock`
* `openpilot/common/hardware/`
* `openpilot/system/hardware/`
* `system/`
* `openpilot/system/manager/`
* `tools/op.sh`
* `.gitmodules`
* `.python-version`

**對外契約**

* AGNOS 版本與 manifest／相容路徑
* 裝置身分、USB 狀態、manager 啟動條件
* 原生建置與 Python／套件版本

**升級依賴**：無上層模組依賴。

**成組升級單位**：AGNOS／manifest／啟動器／硬體層／原生依賴與 C3X、C4 開機一起驗證。

**驗證入口**

* `.github/workflows/tests.yaml`

## bus：訊息、影像傳輸與設定

**程式與監看路徑**

* `openpilot/cereal/`
* `msgq_repo`
* `openpilot/common/params*`
* `openpilot/common/params_keys.h`
* `openpilot/common/realtime.py`
* `openpilot/sunnypilot/system/params_migration.py`
* `openpilot/common/tests/test_ratekeeper_stall.py`

**對外契約**

* Cap’n Proto schema 與 SP 擴充
* PubMaster／SubMaster／VisionIPC 的頻率與有效性
* Params 型別、預設、清除時機與遷移

**升級依賴**：`platform`。

**成組升級單位**：schema／services／訊息兩端／msgq／原生產物與紀錄遷移成組。

**驗證入口**

* `.github/workflows/cereal_validation.yaml`
* `.github/workflows/tests.yaml`

## model_registry：模型目錄、下載與選擇

**程式與監看路徑**

* `openpilot/sunnypilot/models/`
* `.github/workflows/build-default-models.yaml`
* `.github/workflows/build-all-tinygrad-models.yaml`
* `.github/workflows/build-single-tinygrad-model.yaml`
* `.github/workflows/download-hf-model-chunks/`

**對外契約**

* QCOM／Chestnut 各自的 active bundle
* manifest、selector 版本、SHA-256 與快取
* runner 類型與下載完成狀態

**升級依賴**：`platform`、`bus`。

**成組升級單位**：模型目錄／格式版本／產物 SHA／選擇器／下載與重設策略一起審閱。

**驗證入口**

* `.github/workflows/test_models.yml`
* `.github/workflows/model-runtime-contract.yml`
* `.github/workflows/tests.yaml`

## inference：感知模型與推論執行

**程式與監看路徑**

* `openpilot/selfdrive/modeld/`
* `openpilot/system/camerad/`
* `openpilot/sunnypilot/modeld_v2/`
* `tinygrad_repo`
* `.gitattributes`
* `openpilot/common/transformations/camera.py`
* `openpilot/common/transformations/model.py`

**對外契約**

* VisionIPC 相機影像與 warp
* modelV2、cameraOdometry、drivingModelData、driverStateV2
* plain artifact、shape／dtype、QCOM／Chestnut 與失敗處理

**升級依賴**：`platform`、`bus`、`model_registry`。

**成組升級單位**：tinygrad pin／模型載入與編譯器／adapter／warp／快取／warmup／後端一起驗證。

**驗證入口**

* `.github/workflows/model-runtime-contract.yml`
* `.github/workflows/test_models.yml`
* `.github/workflows/tests.yaml`
* CPU loader／contract 成功後，仍須驗證兩種裝置的 QCOM 與實際使用的 Chestnut 後端。

## localization：定位、校正與車輛估測

**程式與監看路徑**

* `openpilot/selfdrive/locationd/`
* `openpilot/sunnypilot/selfdrive/locationd/`
* `openpilot/system/sensord/`
* `openpilot/system/qcomgpsd/`
* `openpilot/system/ubloxd/`
* `openpilot/sunnypilot/livedelay/`
* `rednose_repo`
* `openpilot/common/transformations/`
* `openpilot/common/kalman/`
* `openpilot/common/filter_simple.py`

**對外契約**

* cameraOdometry／感測器／GPS 輸入
* deviceMotion、extrinsicsCalibration、vehicleParameters、lateralDelay

**升級依賴**：`platform`、`bus`。

**成組升級單位**：定位狀態與 schema／座標系／校正／rednose／下游控制器一起審閱。

**驗證入口**

* `.github/workflows/tests.yaml`

## vehicle_safety：車型、CAN、控制器與 Panda safety

**程式與監看路徑**

* `opendbc_repo`
* `panda`
* `.gitmodules`
* `openpilot/selfdrive/car/`
* `openpilot/selfdrive/pandad/`
* `openpilot/sunnypilot/selfdrive/car/`
* `docs/HKG_LOW_SPEED_TORQUE.md`

**對外契約**

* CarParams／CarParamsSP、carState、carOutput
* carControl／CarControlSP → CAN → Panda safety
* fingerprint、DBC、旗標與韌體簽章

**升級依賴**：`platform`、`bus`。

**成組升級單位**：opendbc 的車型辨識／controller／interface／DBC／safety 與 Panda 建置成組；另跑子模組 car、safety 與 mutation 測試。

**驗證入口**

* `.github/workflows/tests.yaml`
* 子模組內另行驗證 car／controller、Panda safety 與 mutation；主儲存庫 CI 不能替代這些測試。

## engagement：啟用狀態、MADS 與駕駛監控

**程式與監看路徑**

* `openpilot/selfdrive/selfdrived/`
* `openpilot/selfdrive/monitoring/`
* `openpilot/sunnypilot/mads/`
* `openpilot/sunnypilot/selfdrive/selfdrived/`

**對外契約**

* selfdriveState／selfdriveStateSP、onroadEvents
* driverMonitoringState 與駕駛介入條件
* 橫縱向啟用、CP alternativeExperience 與 safety flags

**升級依賴**：`bus`、`vehicle_safety`。

**成組升級單位**：MADS 狀態機／selfdrived／駕駛監控／警示與制動油門介入一起驗證。

**驗證入口**

* `.github/workflows/tests.yaml`

## map_assistance：地圖資料、限速與智慧巡航

**程式與監看路徑**

* `openpilot/sunnypilot/mapd/`
* `openpilot/third_party/mapd_pfeiferj/`
* `openpilot/sunnypilot/selfdrive/controls/lib/smart_cruise_control/`
* `openpilot/sunnypilot/selfdrive/controls/lib/speed_limit/`

**對外契約**

* liveMapDataSP、GPS 與道路／限速資料
* 送入規劃器的速度與加速度約束

**升級依賴**：`platform`、`bus`。

**成組升級單位**：mapd 安裝／資料時效／GPS 來源／限速解析與規劃器成組；與 mapsd 導航影像分開管理。

**驗證入口**

* `.github/workflows/tests.yaml`

## planning_control：規劃、橫縱向控制與擴充

**程式與監看路徑**

* `openpilot/selfdrive/controls/`
* `openpilot/sunnypilot/selfdrive/controls/`
* `openpilot/sunnypilot/neural_network_data`
* `openpilot/common/constants.py`

**對外契約**

* modelV2／radarState／定位與 engagement 輸入
* longitudinalPlan／longitudinalPlanSP
* carControl／carControlSP、NNLC／LJTC／DEC 等擴充

**升級依賴**：`bus`、`inference`、`localization`、`vehicle_safety`、`engagement`、`map_assistance`。

**成組升級單位**：planner／controller／SP 擴充／車型能力／參數與重播一起審閱；DEC 僅 HKG 保留。

**驗證入口**

* `.github/workflows/tests.yaml`

## navigation：路線導航與地圖影像

**程式與監看路徑**

* `openpilot/selfdrive/navigation/`
* `openpilot/selfdrive/ui/mici/onroad/navigation.py`

**對外契約**

* NavDestination、navRoute、navInstruction
* mapsd 的 VISION_STREAM_MAP；目前未接入駕駛模型

**升級依賴**：`platform`、`bus`。

**成組升級單位**：navd／mapsd／地圖資料 API／訊息／UI 成組；導入導航模型另含 runner 與模型輸入。

**驗證入口**

* `.github/workflows/tests.yaml`

## release：版本、裝置更新與打包

**程式與監看路徑**

* `CHANGELOG.md`
* `README.md`
* `RELEASES.md`
* `openpilot/common/version.py`
* `openpilot/common/version.h`
* `openpilot/common/release_notes.py`
* `openpilot/sunnypilot/common/version.h`
* `openpilot/system/updated/`
* `tools/release/`
* `release/`
* `docs/DEVICE_RELEASE_NOTES.md`
* `.github/release-drafter.yml`

**對外契約**

* SUNNYPILOT_VERSION 與 CHANGELOG 最新一筆
* UpdaterCurrent／UpdaterNew Description 與 ReleaseNotes
* finalized overlay、build metadata 與安裝後版本

**升級依賴**：`platform`、`bus`。

**成組升級單位**：版本／中文說明／metadata／updated／兩介面與 stripped、prebuilt 套件一起核對。

**驗證入口**

* `.github/workflows/release-notes.yml`
* `.github/workflows/device-update-compat.yml`
* `.github/workflows/tests.yaml`

## ui：C3X／C4 介面、翻譯與字型

**程式與監看路徑**

* `openpilot/selfdrive/ui/`
* `openpilot/system/ui/`
* `openpilot/selfdrive/assets/`
* `.gitattributes`

**對外契約**

* tizi 大型介面／mici 小型介面與 sunnypilot 覆寫
* ui_state 訂閱、能力判斷與 Params 設定
* PO／POT、字型、測量／換行／繪製、更新資訊

**升級依賴**：`bus`、`inference`、`engagement`、`vehicle_safety`、`release`。

**功能啟用時的依賴**：`navigation`。

**成組升級單位**：兩套介面／翻譯擷取與資源／能力規則／字型度量／兩機種截圖一起驗證。

**驗證入口**

* `.github/workflows/device-update-compat.yml`
* `.github/workflows/tests.yaml`

## cloud：雲端、遠端設定、備份與串流

**程式與監看路徑**

* `openpilot/system/athena/`
* `openpilot/system/webrtc/`
* `openpilot/system/loggerd/uploader.py`
* `openpilot/sunnypilot/sunnylink/`
* `teleoprtc_repo`

**對外契約**

* athena／sunnylink 註冊與能力
* SDUI YAML → settings_ui.json
* 設定備份、上傳與 HKG 遠端更新請求

**升級依賴**：`bus`、`vehicle_safety`、`model_registry`、`release`。

**成組升級單位**：認證／能力／設定 schema／產生的 JSON／備份與更新請求限制一起審閱；不假設兩分支雲端功能相同。

**驗證入口**

* `.github/workflows/tests.yaml`

## observability：記錄、健康狀態與故障診斷

**程式與監看路徑**

* `openpilot/system/loggerd/`
* `openpilot/system/logmessaged.py`
* `openpilot/system/tombstoned.py`
* `openpilot/system/manager/boot_diagnostics.py`
* `openpilot/system/ui/crash_screen.py`
* `tools/diagnostics/`

**對外契約**

* managerState、程序健康狀態與崩潰紀錄
* loggerd 紀錄／回放
* HKG 獨立開機與 UI 診斷

**升級依賴**：`platform`、`bus`。

**成組升級單位**：程序生命週期／記錄 schema／獨立診斷依賴與敏感資料處理一起審閱。

**驗證入口**

* `.github/workflows/tests.yaml`

## validation：CI、測試基準與維護地圖

**程式與監看路徑**

* `.github/workflows/`
* `scripts/lint/`
* `tools/maintenance/`
* `docs/architecture/`
* `openpilot/selfdrive/test/`
* `*/tests/*`

**對外契約**

* head SHA、事件類型與分支相符的 CI 結果
* 固定重播基準與真實差異
* 主機／CPU／裝置／實車驗證範圍分開記錄

**升級依賴**：`platform`、`bus`、`model_registry`、`inference`、`localization`、`vehicle_safety`、`engagement`、`map_assistance`、`planning_control`、`release`、`ui`、`cloud`、`observability`。

**功能啟用時的依賴**：`navigation`。

**成組升級單位**：CI 觸發／固定依賴／fixtures／重播 refs 與主機測試配置成組；不能以忽略輸出或覆寫 refs 消除失敗。

**驗證入口**

* `.github/workflows/tests.yaml`
* `.github/workflows/device-update-compat.yml`
* `.github/workflows/release-notes.yml`
