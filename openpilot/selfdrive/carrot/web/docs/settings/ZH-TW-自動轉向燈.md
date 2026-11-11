<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="AutoBlinkerControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自動轉向燈

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN AutoBlinkerControl -->
<a id="AutoBlinkerControl"></a>

## 自動轉向燈

`AutoBlinkerControl`

0：關閉（保留藍芽輕觸）。1：低於5km/h藍芽保持至轉彎結束，從ATC audioTurn提示開始保持，路口停車時不熄滅，實際轉彎後方向盤回正時解除。2：另含實際開始的ATC變道，等待時不亮。同方向取消保持，反方向切換。原車撥杆優先。需要支援的Jetson USB-CAN/B1車輛。 ATC在確認傳送完成但未亮燈時最多重試一次。有效TBT座標與車輛GPS確認直行透過後自動取消；位置不可靠時不使用該位置取消判斷。 TBT按audioTurn距離及行駛距離跟蹤至轉彎點後30米。確認對應方向轉角超過30度且車身方向變化至少20度後，車速至少1km/h時方向盤回到±15度以內立即結束保持。進入轉彎前的訊號燈停車仍保持。新的下一轉彎提示在當前轉彎結束後接續；對應方向轉角達到30度後，駕駛員反向施力使轉角越過零點進入反方向時取消。已確認傳送及亮燈的TBT保持不因接收端driver\_override狀態單獨解除。不能保證原車燈立即熄滅。 按巡航 CANCEL 會停止自動轉向燈請求並解除自動保持。泊車轉動方向盤不會重新觸發；用 SET/RES 或 +/− 解除巡航取消狀態後，新動作才可觸發。原車撥杆和藍芽轉向燈按鈕仍可手動使用。

<!-- CARROT:AUTO:BEGIN AutoBlinkerControl -->
<!-- CARROT:AUTO:SOURCE facts="f3085c76dc1576320b39e25749089d6d81e1b2f42cefcff1091230f7781c2d18" semantic="edd05659292aebc71be712906d3faaadf71c30551e5a372287abb2bf65bd60ca" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoBlinkerControl -->

<!-- CARROT:MANUAL:BEGIN AutoBlinkerControl -->
<!-- CARROT:REVIEW reviewed-for="edd05659292aebc71be712906d3faaadf71c30551e5a372287abb2bf65bd60ca" reviewed-at="2026-11-10T10:39:14.890627+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

在支援的車輛上管理BT和ATC實際轉向燈請求及保持。

確認進入轉彎後，行駛中方向盤回到±15度以內即正常結束，也使用轉彎點後的行駛距離判斷結束。對應方向轉角達到30度後，駕駛員反向施力使轉角越過零點進入反方向時取消。

已確認傳送及亮燈的TBT保持可在接收端driver_override狀態下繼續至轉彎結束。缺少首次傳送確認時無法啟用保持。新的下一轉彎提示在當前轉彎結束後接續。

按巡航 CANCEL 會停止自動轉向燈請求並解除自動保持。泊車轉動方向盤不會重新觸發；用 SET/RES 或 +/− 解除巡航取消狀態後，新動作才可觸發。原車撥杆和藍芽轉向燈按鈕仍可手動使用。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoBlinkerControl -->

<!-- CARROT:SETTING:END AutoBlinkerControl -->
