<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="BlinkerLatchedTurn" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 轉向燈撥杆區分轉彎/變道 (km/h, 0=關)

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN BlinkerLatchedTurn -->
<a id="BlinkerLatchedTurn"></a>

## 轉向燈撥杆區分轉彎/變道 (km/h, 0=關)

`BlinkerLatchedTurn`

僅限現代 CAN-FD（0x3C1 撥杆訊號）。0 為關閉。設定速度及以下時，先半撥（單觸），轉向燈亮-滅-亮之後再撥到底（鎖定）為左/右轉彎；直接鎖定或僅單觸為變道；撥杆仍在單觸位置時不開始變道（鎖定前也會經過該位置約 0.1 秒）。超過設定速度時，即使鎖定撥杆也只變道。

<!-- CARROT:AUTO:BEGIN BlinkerLatchedTurn -->
<!-- CARROT:AUTO:SOURCE facts="69d64b6776b0ba6bee9e682b0950295e3b126b8c6bf0f4cc0ba047c43d419bea" semantic="76514ada656e4e01d74e337bcc01f3dc8948509aca88bc57278eade000b25502" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0km/h`
- **範圍:** `0km/h` ~ `80km/h`
- **步長:** `5`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END BlinkerLatchedTurn -->

<!-- CARROT:MANUAL:BEGIN BlinkerLatchedTurn -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END BlinkerLatchedTurn -->

<!-- CARROT:SETTING:END BlinkerLatchedTurn -->
