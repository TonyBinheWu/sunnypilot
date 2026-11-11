<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleNaviSectionAvgControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 原車導航區間測速平均速度控制

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleNaviSectionAvgControl -->
<a id="VehicleNaviSectionAvgControl"></a>

## 原車導航區間測速平均速度控制

`VehicleNaviSectionAvgControl`

僅在外部導航未連線時應用。原車導航 CAN 區間測速期間照常固定在區間限速（× 安全係數）。openpilot 啟用且巡航設定速度高於該上限時，按一次巡航 + 鍵或輕踩油門即解除該區間的固定，僅在進入區間後的平均速度保持在區間限速以下的範圍內允許達到設定速度。只能使用因擁堵等積累的餘量；沒有餘量時與原限制相同。此輸入不會提高設定速度。長按巡航 - 鍵重新固定且不改變設定速度（短按仍照常降低設定速度），離開區間時復位。終點攝影機約提前 2km 預告後按點位減速。區間起點取平均速度訊號出現的時刻，為實驗功能。

<!-- CARROT:AUTO:BEGIN VehicleNaviSectionAvgControl -->
<!-- CARROT:AUTO:SOURCE facts="4135e7795ead920cd1b2b420ae31731649989fe2dd89ece377375ade24fd948b" semantic="279eeacf277d306a733765fc4b26354220278af698c6266e606d727260d2e3ec" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviSectionAvgControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviSectionAvgControl -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END VehicleNaviSectionAvgControl -->

<!-- CARROT:SETTING:END VehicleNaviSectionAvgControl -->
