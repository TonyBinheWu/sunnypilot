<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_FEEL" param="LowSpeedRadarGuard" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 低速近距雷達輔助

**選單:** 駕駛控制 \> 轉向 \> 轉向手感

---

<!-- CARROT:SETTING:BEGIN LowSpeedRadarGuard -->
<a id="LowSpeedRadarGuard"></a>

## 低速近距雷達輔助

`LowSpeedRadarGuard`

時速 15 公里以下，前方雷達連續確認接近目標時，限制 openpilot 縱向控制的正加速度。側方有目標或雷達失效時，暫緩新的自動轉彎請求。這些訊號無法量測牆面淨距。

<!-- CARROT:AUTO:BEGIN LowSpeedRadarGuard -->
<!-- CARROT:AUTO:SOURCE facts="ba33e5f02f52899378fa55742cc19a01d200cf20b6b9ad994bb3f4f76577a055" semantic="2daf7c8d9946d5aba8152c1a68abb9c8ea0a70692d3a23d8a390eb3222389f13" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 轉向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedRadarGuard -->

<!-- CARROT:MANUAL:BEGIN LowSpeedRadarGuard -->
<!-- CARROT:REVIEW reviewed-for="2daf7c8d9946d5aba8152c1a68abb9c8ea0a70692d3a23d8a390eb3222389f13" reviewed-at="2026-11-27T22:32:00+08:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

同一前方目標須在 7 公尺內，以超過 0.5 公尺／秒的相對速度接近，預估接觸時間不超過 2 秒，且連續出現在三筆不同的雷達資料中。觸發後限制正加速度，保留更強的減速要求。側方沒有目標時，需要現代或起亞 0x180 或 0x235 角雷達一組完整且新鮮的掃描才能解除側方限制。牆面和路緣可能位於探測範圍以外。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END LowSpeedRadarGuard -->

<!-- CARROT:SETTING:END LowSpeedRadarGuard -->
