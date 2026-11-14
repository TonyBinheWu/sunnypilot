<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="ManualLaneChangeIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 手動變道轉向燈（試驗）

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN ManualLaneChangeIndicator -->
<a id="ManualLaneChangeIndicator"></a>

## 手動變道轉向燈（試驗）

`ManualLaneChangeIndicator`

車速至少5km/h，確認同方向轉向0.15秒後，鬆手或短暫反向施力但仍接近邊界時最多保留意圖1.5秒；停止接近超過0.3秒、回退超過0.15米且持續0.15秒，或單次跟蹤超過4秒則取消。左側透過新鮮的原車白線分類排除中央線，黃色、未知或過期分類阻止觸發。右側僅要求當前及前方的目標車道線至道路邊緣距離至少2.5米；不使用外側車道線機率、相鄰車道寬度或道路邊緣標準差。寬路肩也可能滿足距離條件。 獨立於ATC及右轉距離選項，不請求自動轉向。預設關閉，僅支援Ioniq 5 PE、Jetson USB2CAN及自動轉向燈模式1或2。再次請求須間隔3秒且連續熄燈1秒，自動轉向反饋隔離至少12秒。不能保證真實車道或安全間距，修改後仍需實車驗證。 開始接近時確認目標線置信度至少10%，連續接近最多跟蹤4秒。請求後跟蹤完成、返回或輸入失效，最長12秒；不能保證原車輕觸閃燈立即熄滅。 根據測得的車道邊界接近速度預測0.3秒後的位置，提前請求轉向燈。車體中心至邊界的距離閾值從0.9米最多提前至1.2米，仍要求至少0.15米實際接近、駕駛員意圖及兩側邊界一致移動。 邊界回退持續0.15秒才取消追蹤，回退期間暫停新請求。近期有轉向意圖且兩側邊界同向移動、車道寬度一致時，可接受有限的位置變化並繼續追蹤。

<!-- CARROT:AUTO:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:AUTO:SOURCE facts="c4ae2e45cd1cedda7fe861233987292192e45e283e6d208bf8e2e80b51da0eda" semantic="d96432b8f8ff840459f65cab076ba12f6d57b1d333e585a4be25652182e1e7ba" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ManualLaneChangeIndicator -->

<!-- CARROT:MANUAL:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:REVIEW reviewed-for="d96432b8f8ff840459f65cab076ba12f6d57b1d333e585a4be25652182e1e7ba" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

結合近期駕駛員轉向意圖與連續邊界接近進行顯示。開始時確認目標線置信度至少10%，並應用左側中央線和右側道路邊緣排除條件。

請求後跟蹤完成、返回及輸入失效，不請求自動轉向。保持請求結束後原車輕觸閃燈仍可能繼續。
根據測得的車道邊界接近速度預測0.3秒後的位置，提前請求轉向燈。車體中心至邊界的距離閾值從0.9米最多提前至1.2米，仍要求至少0.15米實際接近、駕駛員意圖及兩側邊界一致移動。

手動及模型顯示僅在請求時間、方向和撥杆計數一致時有限識別自身輕觸反饋。反向輸入、撥杆鎖定或接收端檢測到駕駛員介入時取消。先於傳送完成應答的點燈反饋會短暫記憶，但保持仍須匹配應答；短暫傳送期間同方向人工操作無法僅憑這些資訊完全區分。
車速達到5公里/小時且檢測到駕駛員轉向並實際靠近相鄰車道線時，可請求對應方向的轉向燈。
邊界回退持續0.15秒才取消接近追蹤，回退期間暫停新點燈。近期有駕駛員意圖，且兩側邊界同向移動、車道寬度一致時，允許有限的位置變化並繼續追蹤。

B1 第5版允許已確認的自身輕觸回訊持續穿過閃燈的熄滅間隔。輕觸結束後收到中立回訊即關閉此允許，後續撥桿回訊會取消所有權；反側燈、原始駕駛員輸入、CAN異常及租約到期仍會取消。軟體回放不代表實際保持或取消效能驗收。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ManualLaneChangeIndicator -->

<!-- CARROT:SETTING:END ManualLaneChangeIndicator -->
