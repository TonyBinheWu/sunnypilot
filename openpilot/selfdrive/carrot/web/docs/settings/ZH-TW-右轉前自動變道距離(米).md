<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="AutoTurnControlRightLaneChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 右轉前自動變道距離(米)

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlRightLaneChange -->
<a id="AutoTurnControlRightLaneChange"></a>

## 右轉前自動變道距離(米)

`AutoTurnControlRightLaneChange`

0米關閉，在設定距離內檢查條件。250米對應原有範圍，也可選擇300–400米。原開啟設定在啟動時轉換為250米。附加於ATC模式1或2。車速至少10km/h時，距TBT右轉或右側分岔設定距離以內且尚未開始轉彎時請求右轉向燈。需要Ioniq 5 PE USB2CAN、AutoBlinkerControl=2及LaneChangeNeedTorque=0。後方僅檢查有效原車BSD警告，不使用角雷達距離。右側目標車道的前方車輛當前距離及按相對速度預測3秒後的距離均須至少5米。前雷達故障或資料過期時不啟動。請求前轉向會重新確認條件，請求後駕駛員干預會取消。 低於30km/h開始的訊號始終僅作顯示；至少30km/h開始時才進入既有變道流程。右側車道線到道路邊緣須至少2.5米。

<!-- CARROT:AUTO:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:AUTO:SOURCE facts="39ecc892d2c12e21d9ea37b0679121c936c901f371547d3c3bf2e183a2ed7f16" semantic="3008498ad9b26c4e6721da72acaa56057939a66d7d15c51954adbc9bb64b1584" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `500`
- **步長:** `50`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlRightLaneChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:REVIEW reviewed-for="3008498ad9b26c4e6721da72acaa56057939a66d7d15c51954adbc9bb64b1584" reviewed-at="2026-11-02T22:15:29.552199+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

0米關閉附加功能，增大數值會在右轉或右側分岔前更遠處檢查條件。250米對應原有範圍，原開啟設定在重啟時轉換為250米。

車速至少10km/h時檢查右側車道、道路邊緣、有效BSD及當前和3秒預測前車距離。低於30km/h開始的訊號僅作顯示，達到30km/h時開始的訊號進入既有變道判斷。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoTurnControlRightLaneChange -->

<!-- CARROT:SETTING:END AutoTurnControlRightLaneChange -->
