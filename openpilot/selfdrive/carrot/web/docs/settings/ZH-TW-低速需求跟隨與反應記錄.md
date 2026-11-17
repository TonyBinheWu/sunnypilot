<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 低速需求跟隨與反應記錄

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## 低速需求跟隨與反應記錄

`LowSpeedSteerReserve`

僅 Hyundai／Kia CAN-FD 扭力控制。持續需求 0.30 秒後，≤30 km/h 按需提供最高 409 的餘量，30–40 漸退。開啟時全速域使用車型預設比例及增減速率，手動值保留；≥40 不再提供餘量。只記錄反應，不探測或提高硬體上限，需實車驗證。

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="27cb22d78afd1e9660b1ea9f7a3feba5ab010c00dc147d0e4d5926a346524758" semantic="f3e6e9a5914e7a8cb28bed45e8f14db13132a0c4aeea40956275b3c4dffe4bba" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:REVIEW reviewed-for="f3e6e9a5914e7a8cb28bed45e8f14db13132a0c4aeea40956275b3c4dffe4bba" reviewed-at="2026-11-17T12:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

僅支援 Hyundai／Kia CAN-FD 扭力轉向。需求接近預設上限並持續 0.30 秒後，≤30 km/h 只依實際需求提供最高 409 的餘量；30–40 km/h 上限漸退，≥40 km/h 使用車型預設上限。開啟期間全速域採用車型預設換算比例與指令增加／減少速率；儲存的 CustomSteerMax 與 CustomSteerDelta 數值暫不參與執行，但不會被覆寫。增益與即時扭力學習不變，角度控制車型不增加控制權限。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

此選用開關仍位於 CustomSteerMax 正下方，約 0.5 秒內讀取、不需重新啟動；關閉後恢復儲存的手動限制。機器「設備 > 轉向學習進度」與網頁／APK「工具 > 轉向學習進度」可查看需求／送出指令、目標／實際方向盤角度、實際角度速率、目前限制，以及左右指令期間的觀察峰值。即時狀態超過 2 秒標示過期；歷史彙總另行標示，僅載入相同車型與控制類型的紀錄。只在功能開啟時於本機收集彙總，每 60 秒及退出控制／關閉功能時儲存；不含位置、行程或雲端上傳。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

駕駛接管、CAN 無效、轉向故障、倒車／靜止、模型過期或退出橫向控制會取消餘量資格。收回輸出仍遵守車型預設變化速率，保留 EPS 轉向請求保護與 Panda 安全限制。指令單位是 CAN 數值，不是牛頓米；增加／減少數值表示每 10 毫秒的 CAN 指令變化量，不是方向盤角速度。觀察峰值與角度誤差無法證明 EPS 硬體極限，不會用來提高控制上限或試探極限。目前只有桌面測試，仍需實車驗證。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
