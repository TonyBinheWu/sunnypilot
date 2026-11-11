<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="ManualLaneChangeIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 手動變道轉向燈（試驗）

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN ManualLaneChangeIndicator -->
<a id="ManualLaneChangeIndicator"></a>

## 手動變道轉向燈（試驗）

`ManualLaneChangeIndicator`

車速至少5km/h，確認同方向轉向0.15秒後，鬆手或短暫反向施力但仍接近邊界時最多保留意圖1.5秒；停止接近超過0.3秒、回退超過0.15米或單次跟蹤超過4秒則取消。左側透過新鮮的原車白線分類排除中央線，黃色、未知或過期分類阻止觸發。右側僅要求當前及前方的目標車道線至道路邊緣距離至少2.5米；不使用外側車道線機率、相鄰車道寬度或道路邊緣標準差。寬路肩也可能滿足距離條件。 獨立於ATC及右轉距離選項，不請求自動轉向。預設關閉，僅支援Ioniq 5 PE、Jetson USB2CAN及自動轉向燈模式1或2。再次請求須間隔3秒且連續熄燈1秒，自動轉向反饋隔離至少12秒。不能保證真實車道或安全間距，修改後仍需實車驗證。 開始接近時確認目標線置信度至少10%，連續接近最多跟蹤4秒。請求後跟蹤完成、返回或輸入失效，最長12秒；不能保證原車輕觸閃燈立即熄滅。 根據測得的車道邊界接近速度預測0.3秒後的位置，提前請求轉向燈。車體中心至邊界的距離閾值從0.9米最多提前至1.2米，仍要求至少0.15米實際接近、駕駛員意圖及兩側邊界一致移動。

<!-- CARROT:AUTO:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:AUTO:SOURCE facts="de3b338ecea4846c9ebe37685b4f2e22b232ec7b93fc44b006700a903800119f" semantic="e2259bfc81f439587e99cd8f87f9640f16cb2ddb370571afbfd23611dc2f1d7f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ManualLaneChangeIndicator -->

<!-- CARROT:MANUAL:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:REVIEW reviewed-for="e2259bfc81f439587e99cd8f87f9640f16cb2ddb370571afbfd23611dc2f1d7f" reviewed-at="2026-11-08T22:13:25+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

結合近期駕駛員轉向意圖與連續邊界接近進行顯示。開始時確認目標線置信度至少10%，並應用左側中央線和右側道路邊緣排除條件。

請求後跟蹤完成、返回及輸入失效，不請求自動轉向。保持請求結束後原車輕觸閃燈仍可能繼續。
根據測得的車道邊界接近速度預測0.3秒後的位置，提前請求轉向燈。車體中心至邊界的距離閾值從0.9米最多提前至1.2米，仍要求至少0.15米實際接近、駕駛員意圖及兩側邊界一致移動。

手動及模型顯示僅在請求時間、方向和撥杆計數一致時有限識別自身輕觸反饋。反向輸入、撥杆鎖定或接收端檢測到駕駛員介入時取消。先於傳送完成應答的點燈反饋會短暫記憶，但保持仍須匹配應答；短暫傳送期間同方向人工操作無法僅憑這些資訊完全區分。
車速達到5公里/小時且檢測到駕駛員轉向並實際靠近相鄰車道線時，可請求對應方向的轉向燈。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ManualLaneChangeIndicator -->

<!-- CARROT:SETTING:END ManualLaneChangeIndicator -->
