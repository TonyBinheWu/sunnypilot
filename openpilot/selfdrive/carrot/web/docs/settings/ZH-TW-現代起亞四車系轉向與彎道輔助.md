<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_FEEL" param="HkgPhase1Assist" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 現代起亞四車系轉向與彎道輔助

**選單:** 駕駛控制 \> 轉向 \> 轉向手感

---

<!-- CARROT:SETTING:BEGIN HkgPhase1Assist -->
<a id="HkgPhase1Assist"></a>

## 現代起亞四車系轉向與彎道輔助

`HkgPhase1Assist`

僅限已登錄的 EV6、Ioniq 5、Carnival、Sorento 平台。CAN-FD 扭力車型沿用低速需求跟隨（最高 409、4／4），保留已存手動值；角度控制及舊款 Sorento 保持原執行器限制。40–80 km/h 逐漸平順小幅曲率修正，大幅需求減少濾波。直接縱向 ACC 模式下，以連續三個新鮮模型幀確認前方彎道，再降低 MPC 速度上限。預設關閉，保留 EPS／Panda 保護；不包含緊急避讓，不保證迴轉或實車效果。 低速同方向入彎需求將既有目標濾波時間常數最多縮短 40%；回正與反向維持原濾波，30–40 km/h 漸退。 低速模型目標反應調整僅用於無車道線模型路徑；自訂車道線規劃濾波及其延遲補償維持原樣。

<!-- CARROT:AUTO:BEGIN HkgPhase1Assist -->
<!-- CARROT:AUTO:SOURCE facts="527533dbc49133dd2ba8619e49a61cc786027a1915fb52a70dc4bb8cce4307f7" semantic="1c9c7c054bb743a7a9af0906faec089755f21f0f914e02d4a5b7addd3c56d7c2" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 轉向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HkgPhase1Assist -->

<!-- CARROT:MANUAL:BEGIN HkgPhase1Assist -->
<!-- CARROT:REVIEW reviewed-for="1c9c7c054bb743a7a9af0906faec089755f21f0f914e02d4a5b7addd3c56d7c2" reviewed-at="2026-11-18T00:00:00+08:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

僅套用已登錄的 EV6、Ioniq 5、Carnival、Sorento 平台，維持既有車型、HDA 與扭力／角度辨識。低速同方向增大的入彎需求，將既有目標濾波時間常數最多縮短 40%，30–40 km/h 漸退；回正與反向使用原濾波。CAN-FD 扭力車型另沿用 LowSpeedSteerReserve 的資格確認、扭力上限與速率保護。角度車型與舊款 Sorento 不增加執行器權限。高速小幅曲率修正增加最多 0.08 秒時間常數的濾波，大幅需求減少濾波，最終曲率與執行器限制仍生效。
低速模型目標反應調整僅用於無車道線模型路徑；自訂車道線規劃濾波及其延遲補償維持原樣。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

停妥後在駕駛控制 > 轉向 > 轉向手感啟用，逐一驗證各車配置。轉向約 0.5 秒、彎道輔助約 1 秒讀取設定；本開關與 LowSpeedSteerReserve 都關閉後才恢復手動限制，儲存值不被覆寫。既有低速扭力路徑仍須相容 Panda 韌體。僅在 ACC 模式、直接縱向與橫向控制皆啟用、車輛／控制／模型資料有效並連續三個新模型幀確認後，套用彎前速度上限；原廠 ACC 與 blended 模式不變。使用模型前方最多 4 秒幾何、2.0 m/s² 橫向舒適目標與 1.2 m/s² 接近減速預算；上限每秒最多下降 1.2 m/s、每秒回升 0.5 m/s。在 Carrot 選速之後交給 MPC，不提高較低速度或停車目標，也不讓滑行與前車加速預覽抵銷彎道減速。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

駕駛踏板／轉向介入、CAN 無效、轉向故障、控制退出、模型過期／重複／重啟或幾何異常會重置彎道上限。新增彎道功能不要求停車，不以觀察紀錄推定 EPS 能力。維持 EPS／Panda 保護、駕駛優先、請求位元防故障、模型檔與緊急行為。桌面測試不能證明實車操控效果、滿舵／迴轉能力或與 FSD 等效。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END HkgPhase1Assist -->

<!-- CARROT:SETTING:END HkgPhase1Assist -->
