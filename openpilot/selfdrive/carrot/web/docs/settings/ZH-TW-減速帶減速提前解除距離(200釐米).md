<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_BUMP" param="AutoNaviSpeedBumpEndDistance" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 減速帶減速提前解除距離（200釐米）

**選單:** 駕駛控制 \> 速度與減速 \> 減速帶

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedBumpEndDistance -->
<a id="AutoNaviSpeedBumpEndDistance"></a>

## 減速帶減速提前解除距離（200釐米）

`AutoNaviSpeedBumpEndDistance`

外部導航連線期間僅按其剩餘距離解除減速，否則使用原車導航距離。 當原車導航或 Carrot Navi 提供的減速帶剩餘距離小於或等於此值時，提前解除減速限制。儲存值和顯示單位為釐米；0 表示保持控制直到接收的位置。此設定可補償地圖中的減速帶位置晚於實際位置而導致透過後恢復速度過慢的問題。設定過大可能會在實際減速帶前開始加速。

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedBumpEndDistance -->
<!-- CARROT:AUTO:SOURCE facts="1143276ede20c8efea97a1c6797dad818689b664c216a3959f73130c4b179332" semantic="1d2c29dce19e2a3851161d46ce76db89eb7be23e3f9b3b3c1be663a3e2b402c9" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `200cm`
- **範圍:** `0cm` ~ `5000cm`
- **步長:** `10`
- **顯示單位:** `cm`
- **選單:** 駕駛控制 \> 速度與減速 \> 減速帶
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedBumpEndDistance -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedBumpEndDistance -->
<!-- CARROT:REVIEW reviewed-for="1d2c29dce19e2a3851161d46ce76db89eb7be23e3f9b3b3c1be663a3e2b402c9" reviewed-at="2026-09-13T07:52:41.244419+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

外部導航連線期間僅使用外部導航，即使沒有當前引導專案也不使用原車導航。確認斷開連線或接收超時後，按各項設定恢復使用原車導航。

增大正值會在剩餘距離更大時解除減速帶限速，減小則更接近減速帶時解除。0保持到無剩餘距離。外部導航連線期間僅按其距離解除。解除並不代表立即恢復到原巡航速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同時檢查外部導航連線狀態以及顯示的事件型別和剩餘距離。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedBumpEndDistance -->

<!-- CARROT:SETTING:END AutoNaviSpeedBumpEndDistance -->
