<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SYS_NET" param="HotspotOnBoot" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 開啟熱點 (0)

**選單:** 系統 \> 網路與地圖

---

<!-- CARROT:SETTING:BEGIN HotspotOnBoot -->
<a id="HotspotOnBoot"></a>

## 開啟熱點 (0)

`HotspotOnBoot`

SIM 就緒且行動數據已連線時，自動開啟已儲存的 Wi-Fi 熱點並分享上網；手動關閉熱點會暫停本次開機的自動開啟。

<!-- CARROT:AUTO:BEGIN HotspotOnBoot -->
<!-- CARROT:AUTO:SOURCE facts="fa18e51d54b1caf70996d244b74fe595f55b78787f3b04af1665d9dc6cc3a5e9" semantic="483a8e450bc5248e62520b76fc55c79fad20bff0753ad2f7a1540169a0b7c434" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 系統 \> 網路與地圖
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HotspotOnBoot -->

<!-- CARROT:MANUAL:BEGIN HotspotOnBoot -->
<!-- CARROT:REVIEW reviewed-for="483a8e450bc5248e62520b76fc55c79fad20bff0753ad2f7a1540169a0b7c434" reviewed-at="2026-11-18T09:30:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

開啟後等待 SIM 就緒且有新鮮有效的行動數據連線，再啟動已儲存的熱點與網際網路共享。關閉後停止由本選項自動管理的熱點。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

更新後重新啟動一次，此後變更約五秒內生效。沿用熱點名稱和密碼；連接其他裝置，確認 Carrot 頁面及外部網站均可開啟。啟動失敗會間隔重試。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

手動關閉熱點會暫停自動啟動，關閉再開啟本選項或重新啟動裝置可恢復。行動網路短暫中斷時保留區域網路。單一 Wi-Fi 無線介面可能從用戶端切換為熱點；SIM 方案、APN 和電信業者必須允許共享。本功能不修改 APN 或漫遊設定。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END HotspotOnBoot -->

<!-- CARROT:SETTING:END HotspotOnBoot -->
