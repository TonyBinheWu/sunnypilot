<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="LaneChangeDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 變道延遲 x0.1s(0)

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN LaneChangeDelay -->
<a id="LaneChangeDelay"></a>

## 變道延遲 x0.1s(0)

`LaneChangeDelay`

開啟轉向燈後在設定時間後變道

<!-- CARROT:AUTO:BEGIN LaneChangeDelay -->
<!-- CARROT:AUTO:SOURCE facts="4af74683534990b10e04ee81637e5d0b59adff9195d60c9a45532782e989dcef" semantic="6740c9942977f73420ed5c963b1d5773b4d958e0c8fb4bb8e03d397a45348792" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `100`
- **步長:** `10`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeDelay -->

<!-- CARROT:MANUAL:BEGIN LaneChangeDelay -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

啟用方向燈後，等待設定時間再變換車道。

- **調高：** 增加適用的時間或延遲。
- **調低：** 減少時間或延遲。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在車道線清楚且附近無車流處測試，確認打方向燈後的等待、車道檢查及完成時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

此設定改變進入車道前的等待時間，不會改變已開始變換車道時的速度。請參閱[變換車道說明（英文）](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/lane-change.md)。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneChangeDelay -->

<!-- CARROT:SETTING:END LaneChangeDelay -->
