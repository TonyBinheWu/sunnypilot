<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="ModelDesireIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 模型意圖轉向燈（試驗）

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN ModelDesireIndicator -->
<a id="ModelDesireIndicator"></a>

## 模型意圖轉向燈（試驗）

`ModelDesireIndicator`

重複確認模型轉彎或變道機率至少50%，且優於直行和反方向時顯示轉向燈。轉彎至少10km/h，變道至少30km/h，並要求橫向控制啟用；不新增自動轉向請求。 預設關閉，僅支援Ioniq 5 PE、Jetson USB2CAN及自動轉向燈模式1或2；實車驗證另行進行。 在30 km/h及以上，若模型最近兩個預測時點對同一方向變道的機率均不低於65%，且測得的兩側車道線位置都顯示車輛正在向該側靠近，也可請求轉向燈。僅有預測不會觸發，也不請求轉向。 預測觸發後，若分叉處車道變寬，但模型意圖與實際移動仍一致，則保持同一請求。意圖減弱或反向時結束分叉保持；巡航 CANCEL 會立即解除保持請求。

<!-- CARROT:AUTO:BEGIN ModelDesireIndicator -->
<!-- CARROT:AUTO:SOURCE facts="2e6d9b83ebce62d52dcd3c0926755d78ec1bd81532d6247e7351136486089f47" semantic="85643599439e3e55d38ab927bf13b2d2b17ffa165c1e3dd5f7b7d003daaf5a6d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ModelDesireIndicator -->

<!-- CARROT:MANUAL:BEGIN ModelDesireIndicator -->
<!-- CARROT:REVIEW reviewed-for="85643599439e3e55d38ab927bf13b2d2b17ffa165c1e3dd5f7b7d003daaf5a6d" reviewed-at="2026-11-10T10:51:22.872838+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

橫向控制啟用時，重複確認模型明顯佔優的轉彎或變道預測後顯示訊號。不改變既有ATC條件，也不新增轉向請求。

同方向其他原因接續現有訊號，不重複輕觸。實際點燈及檢出率需要另行驗證。
手動及模型顯示僅在請求時間、方向和撥杆計數一致時有限識別自身輕觸反饋。反向輸入、撥杆鎖定或接收端檢測到駕駛員介入時取消。先於傳送完成應答的點燈反饋會短暫記憶，但保持仍須匹配應答；短暫傳送期間同方向人工操作無法僅憑這些資訊完全區分。

在30 km/h及以上，若模型最近兩個預測時點對同一方向變道的機率均不低於65%，且測得的兩側車道線位置都顯示車輛正在向該側靠近，也可請求轉向燈。僅有預測不會觸發，也不請求轉向。

預測觸發後，若分叉處車道變寬，但模型意圖與實際移動仍一致，則保持同一請求。意圖減弱或反向時結束分叉保持；巡航 CANCEL 會立即解除保持請求。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ModelDesireIndicator -->

<!-- CARROT:SETTING:END ModelDesireIndicator -->
