<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 低速需求跟隨與反應記錄

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## 低速需求跟隨與反應記錄

`LowSpeedSteerReserve`

僅 Hyundai／Kia CAN-FD 扭力控制。持續需求 0.30 秒後，≤30 km/h 按需提供最高 409，指令增加／減少速率依需求最高 4／4（每 10 毫秒）。30–40 漸退；≥40 使用車型預設比例與 2／3。保留手動值與學習參數；紀錄不會提高上限。需更新 Panda 韌體並重啟，尚待實車驗證。

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="dde8f5f52f60aca68026b8d701d363ec3eb5acb86937605c88fc7b6b4ab6ea5b" semantic="861e9b50486d57aed386bb0c56462a4991e79e31206164c4e0af7c8737bc3700" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:REVIEW reviewed-for="861e9b50486d57aed386bb0c56462a4991e79e31206164c4e0af7c8737bc3700" reviewed-at="2026-11-17T15:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

僅支援 Hyundai／Kia CAN-FD 扭力轉向。需求接近預設上限並持續 0.30 秒後，≤30 km/h 可依需求提供最高 409。控制器也依「允許的需求指令與目前輸出之差」選擇指令增加／減少速率，從預設 2／3 到最高 4／4 個 CAN 單位／每 10 毫秒；接近目標時回到預設速率。扭力餘量與額外速率都在 30–40 km/h 漸退；整數指令採離散級距，≥40 km/h 使用車型預設比例與速率。

儲存的 CustomSteerMax 與 CustomSteerDelta 不會被覆寫，開啟時以車型預設換算比例為基準。關閉後恢復手動值，但超出 Panda 已恢復執行的限制之指令會遭拒絕。本功能不增加控制增益、即時扭力學習值或角度控制權限。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

請停車更新並完成重新啟動，讓新版 Panda 韌體與安全參數載入。選用開關仍位於 CustomSteerMax 下方、預設關閉；完成此次更新後，開關約 0.5 秒內讀取，不需再次重新啟動。機器「設備 > 轉向學習進度」與網頁／APK「工具 > 轉向學習進度」可查看目前指令、所選速率、目標／實際方向盤角度及轉動速率、受限原因與左右指令期間的觀察峰值。

即時狀態超過 2 秒標示過期。本機歷史彙總只載入相同車型／控制類型，每 60 秒或退出時儲存；此記錄器不收集位置、行程或上傳雲端。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

駕駛接管、CAN 無效、轉向故障、倒車／靜止、模型過期或退出橫向控制都會取消餘量資格。Panda 以獨立接收且通過 CRC／計數器檢查的新鮮輪速與駕駛資料限制增加速率；缺少／過期資料不能授權額外速率。既有 112 單位／250 毫秒即時變化限制、請求位元及駕駛讓步檢查均恢復執行，包含接收節奏轉送的替代指令；保留接管時迅速釋放轉向力的路徑。

CAN 指令變化率不是牛頓米，也不是實際方向盤角速度。觀察峰值不會被當成硬體極限或用來提高上限，也不會試探物理極限。桌面／原生測試不能證明實車能力，請參閱[驗證範圍與既有測試失敗](https://github.com/TonyBinheWu/sunnypilot/blob/carrot-wip/docs/LOW_SPEED_STEERING_SAFETY.zh-TW.md)。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
