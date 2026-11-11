<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_STOPGO" param="VEgoStopping" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 停止/啟動靈敏度(50)x0.01

**選單:** 駕駛控制 \> 巡航與車距 \> 停車與再起步

---

<!-- CARROT:SETTING:BEGIN VEgoStopping -->
<a id="VEgoStopping"></a>

## 停止/啟動靈敏度(50)x0.01

`VEgoStopping`

根據規劃速度判斷停車與起步。降低數值會推遲停車判斷，並可能更早解除停車狀態。最低值為10（0.10m/s），此前儲存的小於10的值也會自動提高到10。

<!-- CARROT:AUTO:BEGIN VEgoStopping -->
<!-- CARROT:AUTO:SOURCE facts="cff9861a5478c47af3496976facef699424de035a482891738b50b31fed033cf" semantic="887184b01d8bb7422533a0039715941602b954e65f56f045b2a9a34d9b135001" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `50`
- **範圍:** `10` ~ `100`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 停車與再起步
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VEgoStopping -->

<!-- CARROT:MANUAL:BEGIN VEgoStopping -->
<!-- CARROT:REVIEW reviewed-for="887184b01d8bb7422533a0039715941602b954e65f56f045b2a9a34d9b135001" reviewed-at="2026-09-27T06:35:25+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

規劃器在控制延遲對應時刻及其一秒後的目標速度均低於閾值時判斷停車。不再附加CANFD提前停車判斷。

**調高：** 可能提前判斷停車並延後再起步。

**調低：** 可能延後判斷停車並提前再起步。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

在相近的前車停車與起步條件下，每次調整一項，並檢查最終停車位置和再起步反應。此前儲存的值低於當前下限時，啟動程式會自動提高該值。行駛中再次寫入較低值時，控制立即採用下限並修正儲存值。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

此項是速度閾值；停車減速請求遵循StoppingAccel。CANFD重試在停車控制開始後檢查持續的速度回升或減速丟失。shouldStop仍為false時不會啟動重試。參見[停車與再起步指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md#stop-resume)。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END VEgoStopping -->

<!-- CARROT:SETTING:END VEgoStopping -->
