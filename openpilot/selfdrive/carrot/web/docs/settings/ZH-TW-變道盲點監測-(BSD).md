<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="LaneChangeBsd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 變道盲點監測 (BSD)

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN LaneChangeBsd -->
<a id="LaneChangeBsd"></a>

## 變道盲點監測 (BSD)

`LaneChangeBsd`

0: BSD 檢測 (允許轉向力矩), 1: 阻止轉向力矩, -1: 忽略 BSD

<!-- CARROT:AUTO:BEGIN LaneChangeBsd -->
<!-- CARROT:AUTO:SOURCE facts="17865f55ad3dd349d045c06eea175c86ba893b01e8f491df284a987296bba0cf" semantic="04954a5af52833d5de668494cc66d168955efdddb321270af7866ff7bd295569" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `-1` ~ `1`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeBsd -->

<!-- CARROT:MANUAL:BEGIN LaneChangeBsd -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 偵測 BSD（允許駕駛施加轉向扭矩）
- `1` — 阻擋駕駛施加轉向扭矩
- `-1` — 忽略 BSD
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在車道線清楚且附近無車流處測試，確認打方向燈後的等待、車道檢查及完成時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

BSD 無法取代駕駛對盲點及後方車流的檢查。請參閱[變換車道說明（英文）](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/lane-change.md)。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneChangeBsd -->

<!-- CARROT:SETTING:END LaneChangeBsd -->
