<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_ONNX" param="OnnxBsdSmoothingMs" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 盲區保持時間

**選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點

---

<!-- CARROT:SETTING:BEGIN OnnxBsdSmoothingMs -->
<a id="OnnxBsdSmoothingMs"></a>

## 盲區保持時間

`OnnxBsdSmoothingMs`

平滑盲區置信度；警告啟用後會在低於啟動閾值15個百分點時解除。

<!-- CARROT:AUTO:BEGIN OnnxBsdSmoothingMs -->
<!-- CARROT:AUTO:SOURCE facts="b2b8b5fd08d1d267b28599154d0f098d09921eaa6ff94390204944f4eca649f5" semantic="fbbb637458a2aa850365acb0eff1f4fa744b9934ed8dfd981401753968ba6375" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `200ms`
- **範圍:** `100ms` ~ `500ms`
- **步長:** `100`
- **顯示單位:** `ms`
- **選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdSmoothingMs -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdSmoothingMs -->
<!-- CARROT:REVIEW reviewed-for="fbbb637458a2aa850365acb0eff1f4fa744b9934ed8dfd981401753968ba6375" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

提高此值會減慢盲區置信度平滑，降低則更快響應新結果。解除閾值比啟動閾值低 15 個百分點，下限為零。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxBsdSmoothingMs -->

<!-- CARROT:SETTING:END OnnxBsdSmoothingMs -->
