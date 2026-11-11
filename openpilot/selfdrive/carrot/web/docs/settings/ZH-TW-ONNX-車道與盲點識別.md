<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_ONNX" param="ShareData" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ONNX 車道與盲點識別

**選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點

---

<!-- CARROT:SETTING:BEGIN ShareData -->
<a id="ShareData"></a>

## ONNX 車道與盲點識別

`ShareData`

開啟後在 comma 裝置上識別車道型別。僅在單獨開啟 OnnxBsdEnabled 後執行攝影機 BSD；該開關預設關閉，並在已配置且模型估算寬度至少 2m 的左右區域間輪流檢查。關閉本設定會停止視覺服務並保留車輛原有 BSD。即使已開啟，也會等待 onroad 初始化及模型、CAN、Panda 就緒並穩定 0.5 秒後啟動，無需啟用巡航。Offroad 時停止，下次 onroad 重新等待。

<!-- CARROT:AUTO:BEGIN ShareData -->
<!-- CARROT:AUTO:SOURCE facts="ad54b7061473eca45946f804feb0b666fbeb9c65a426fb0ecc1f2614dc4297ab" semantic="0ea20987779bff6e6de29f186065d105a554022ef87fd4b93b59b42d499ee336" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShareData -->

<!-- CARROT:MANUAL:BEGIN ShareData -->
<!-- CARROT:REVIEW reviewed-for="0ea20987779bff6e6de29f186065d105a554022ef87fd4b93b59b42d499ee336" reviewed-at="2026-10-20T08:49:07+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

開啟後 comma 裝置使用攝像頭影象識別實線、虛線；同時開啟 `OnnxBsdEnabled` 後才檢測盲點。關閉後停止視覺服務，車輛原有 BSD 保持有效。

- 有攝像頭影象時持續識別車道線型別。
- 開啟 `OnnxBsdEnabled` 後，攝像頭盲區檢測交替檢查已配置區域且模型估計車道寬度至少為 2 米的左右側，不受車速和變道方向限制。

開啟後仍須等待 onroad 初始化及模型、CAN、Panda 就緒狀態持續 0.5 秒，無需開啟巡航。Offroad 時停止，下次 onroad 時再次等待。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

透過 Carrot Web 中的此開關啟用或關閉。保留已有設定值。滿足啟動條件後，設定和 mici 顯示會在幾秒後更新。

mici 的 VISION 卡片顯示左右車道線型別、最近一次處理耗時和 BSD 狀態。隱藏攝像頭畫面後，卡片和 BSD 警告仍可見。
僅原車檢測時盲區牆為黃色，僅視覺檢測時為藍色，兩者同時檢測時為淺紅色。左右側分別顯示訊號來源。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

更新中包含 OpenCV，裝置正常啟動時自動安裝到本地可寫目錄，無需單獨執行 pip。

BSD 待機表示當前沒有檢查該側。未檢出不代表整個盲區安全；關閉服務後，最後的結果會在有效期結束時消失。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END ShareData -->

<!-- CARROT:SETTING:END ShareData -->
