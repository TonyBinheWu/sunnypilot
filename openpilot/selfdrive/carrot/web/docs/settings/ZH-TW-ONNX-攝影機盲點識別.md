<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_ONNX" param="OnnxBsdEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ONNX 攝影機盲點識別

**選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點

---

<!-- CARROT:SETTING:BEGIN OnnxBsdEnabled -->
<a id="OnnxBsdEnabled"></a>

## ONNX 攝影機盲點識別

`OnnxBsdEnabled`

開啟廣角攝影機的 ONNX 車輛側方盲點識別。它與車道識別獨立，預設關閉，不影響車輛自身提供的盲點資訊。

<!-- CARROT:AUTO:BEGIN OnnxBsdEnabled -->
<!-- CARROT:AUTO:SOURCE facts="d6b97d01d955c08c4850d1bdf0ba72c2c88beb81e7fbcb35f52ceb15433b6842" semantic="96272d6cd431cbf5a7da6b15e4a4e61a939dbe4357ffcbbc432c06e64be4efbd" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdEnabled -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdEnabled -->
<!-- CARROT:REVIEW reviewed-for="96272d6cd431cbf5a7da6b15e4a4e61a939dbe4357ffcbbc432c06e64be4efbd" reviewed-at="2026-10-20T08:49:07+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

開啟後載入廣角攝像頭 BSD 模型，交替檢查已配置且模型估算車道寬度至少為 2 米的左右區域。關閉後解除安裝 BSD 模型並清除舊檢測結果，車道識別繼續執行。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

先開啟 `ShareData` 以執行視覺服務，再在 Carrot Web 的 ONNX 詳情頁面使用此開關。服務約每秒檢查一次設定。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

不影響車輛自身的 BSD。原來使用車道與盲點識別的使用者如需繼續攝像頭 BSD，必須單獨開啟此開關。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END OnnxBsdEnabled -->

<!-- CARROT:SETTING:END OnnxBsdEnabled -->
