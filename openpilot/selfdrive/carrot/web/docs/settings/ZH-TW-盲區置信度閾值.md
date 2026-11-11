<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_ONNX" param="OnnxBsdThreshold" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 盲區置信度閾值

**選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點

---

<!-- CARROT:SETTING:BEGIN OnnxBsdThreshold -->
<a id="OnnxBsdThreshold"></a>

## 盲區置信度閾值

`OnnxBsdThreshold`

將在檢測區域內的車輛判定為攝影機盲區警告所需的最低置信度。

<!-- CARROT:AUTO:BEGIN OnnxBsdThreshold -->
<!-- CARROT:AUTO:SOURCE facts="b082fc012b37afa446b7d49397aec70d9320278326a7b2c1a81864fbf86dd08a" semantic="93b3cd562cb2ac377453782fc4a8fb383aa6da0af1741171fc90eac4b5696e07" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `94%`
- **範圍:** `0%` ~ `100%`
- **步長:** `1`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdThreshold -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdThreshold -->
<!-- CARROT:REVIEW reviewed-for="93b3cd562cb2ac377453782fc4a8fb383aa6da0af1741171fc90eac4b5696e07" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

提高此值會要求盲區威脅類別具有更高置信度，降低則允許較低置信度觸發警告。遠處或後方車輛類別不會觸發警告。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxBsdThreshold -->

<!-- CARROT:SETTING:END OnnxBsdThreshold -->
