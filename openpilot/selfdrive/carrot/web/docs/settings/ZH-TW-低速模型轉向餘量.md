<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 低速模型轉向餘量

**選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## 低速模型轉向餘量

`LowSpeedSteerReserve`

僅 Hyundai／Kia CAN-FD 扭力控制。30 km/h 以下持續達到原上限才提供額外輸出，最高 409；30–40 km/h 逐步回歸原上限。保留 CustomSteerMax 與控制比例，需實車驗證。

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="326f938fe5354466c9e449dbdb9e1feef5c4e3de56b938a06d221dabc4049406" semantic="6a5d981658c4dd294c2fd535015e46b0fe4d8c3e9583fbe6b51bcf29586bdb4d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 高階扭矩 \> 轉向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

僅支援 Hyundai／Kia CAN-FD 扭力轉向。需求連續約 0.30 秒接近原本上限時，30 km/h 以下可依需求使用額外輸出，最高 409；30–40 km/h 的目標上限逐步回到原本值。一般需求的控制比例、增益與學習參數維持原樣。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

開關位於 CustomSteerMax 正下方，初始為關閉。設定約 0.5 秒內重新讀取，不需重新啟動；原本 CustomSteerMax 不會被改寫，原上限已達 409 或更高時不再增加。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

駕駛介入、倒車／靜止、CAN 異常、轉向故障、缺少或過期的模型資料，以及退出橫向控制時，取消額外輸出資格。實際輸出依原本變化速率收回，並非瞬間歸零；EPS 大角度保護與 Panda 安全限制維持原樣。目前只有桌面測試，409 與速度門檻尚未經實車驗證，不保證能完成急彎或路口轉彎。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
