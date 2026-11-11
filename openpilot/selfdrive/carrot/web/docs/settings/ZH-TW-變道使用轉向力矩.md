<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="LaneChangeNeedTorque" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 變道使用轉向力矩

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN LaneChangeNeedTorque -->
<a id="LaneChangeNeedTorque"></a>

## 變道使用轉向力矩

`LaneChangeNeedTorque`

0: 立即變道, 1: 需要力矩 (輕撥), -1: 自動變道關閉

<!-- CARROT:AUTO:BEGIN LaneChangeNeedTorque -->
<!-- CARROT:AUTO:SOURCE facts="41ec8b829d4359485c5f43e02d64ae109f47da4fff08ccb3b6a861489ddc5378" semantic="70cb75233be32678e1cf5e9957be1e809887dca4e08053751f65ac6a2f29c189" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `-1` ~ `1`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeNeedTorque -->

<!-- CARROT:MANUAL:BEGIN LaneChangeNeedTorque -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 立即
- `1` — 需要施加轉向扭矩（輕推方向盤）
- `-1` — 關閉自動變換車道
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在車道線清楚且附近無車流處測試，確認打方向燈後的等待、車道檢查及完成時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

關於路徑由誰決定及駕駛的安全責任，請參閱[變換車道說明（英文）](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/lane-change.md)。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneChangeNeedTorque -->

<!-- CARROT:SETTING:END LaneChangeNeedTorque -->
