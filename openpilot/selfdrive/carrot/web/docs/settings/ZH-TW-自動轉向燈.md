<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="AutoBlinkerControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自動轉向燈

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN AutoBlinkerControl -->
<a id="AutoBlinkerControl"></a>

## 自動轉向燈

`AutoBlinkerControl`

0 藍牙單次閃燈。模式 1 可在 5 km/h 以下維持駕駛用藍牙按鈕開啟的方向燈直到轉彎完成。模式 2 另支援駕駛明確發出的操作請求。同一按鈕取消，另一側按鈕切換，原車撥桿優先。導航透過畫面與聲音提示。

<!-- CARROT:AUTO:BEGIN AutoBlinkerControl -->
<!-- CARROT:AUTO:SOURCE facts="493cf3ce8bd46965844eed2b852c80d8ece3199e2d6d8e8ba7b19db6b7499e34" semantic="6a1867189f6b090ec92c031c906f21c613b4aa48685d0feccb1587057093bf19" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoBlinkerControl -->

<!-- CARROT:MANUAL:BEGIN AutoBlinkerControl -->
<!-- CARROT:REVIEW reviewed-for="6a1867189f6b090ec92c031c906f21c613b4aa48685d0feccb1587057093bf19" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

0 藍牙單次閃燈。模式 1 可在 5 km/h 以下維持駕駛用藍牙按鈕開啟的方向燈直到轉彎完成。模式 2 另支援駕駛明確發出的操作請求。同一按鈕取消，另一側按鈕切換，原車撥桿優先。導航透過畫面與聲音提示。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoBlinkerControl -->

<!-- CARROT:SETTING:END AutoBlinkerControl -->
