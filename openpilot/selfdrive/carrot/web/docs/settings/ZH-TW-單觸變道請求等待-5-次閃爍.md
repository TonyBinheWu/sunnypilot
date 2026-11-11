<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="LaneChangeLeverWait" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 單觸變道請求等待 5 次閃爍

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN LaneChangeLeverWait -->
<a id="LaneChangeLeverWait"></a>

## 單觸變道請求等待 5 次閃爍

`LaneChangeLeverWait`

僅限現代 CAN-FD（0x3C1 撥杆訊號）。單觸撥杆後若變道未立即獲批（BSD、側方車輛、車道線等原有判斷），從撥杆起保持轉向燈並等待 5 次閃爍（約 4 秒）。期間解除則變道，否則放棄請求，剩餘閃爍不會再觸發。鎖定撥杆時照舊持續等待。

<!-- CARROT:AUTO:BEGIN LaneChangeLeverWait -->
<!-- CARROT:AUTO:SOURCE facts="7e456240884ed87579c04a02ed8a5121622bef35a8597848b0b500e51aae277f" semantic="ea223332818ad995bfa4b772614a0e20f4c64f676f70ec1be8afd5eb871ae2db" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeLeverWait -->

<!-- CARROT:MANUAL:BEGIN LaneChangeLeverWait -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END LaneChangeLeverWait -->

<!-- CARROT:SETTING:END LaneChangeLeverWait -->
