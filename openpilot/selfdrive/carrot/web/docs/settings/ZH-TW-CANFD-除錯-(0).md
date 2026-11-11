<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_CANFD" param="CanfdDebug" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CANFD 除錯 (0)

**選單:** 車輛與硬體 \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdDebug -->
<a id="CanfdDebug"></a>

## CANFD 除錯 (0)

`CanfdDebug`

CANFD 除錯 (0)

<!-- CARROT:AUTO:BEGIN CanfdDebug -->
<!-- CARROT:AUTO:SOURCE facts="b378d327be9c68edeb76c461647ab366d203238084ced5e11b0448896e4b1e0f" semantic="12eb933ab9caf967e2a49d1d4a6b0a39f236a64333398e155efc78871fd68181" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `-1` ~ `128`
- **步長:** `1`
- **選單:** 車輛與硬體 \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdDebug -->

<!-- CARROT:MANUAL:BEGIN CanfdDebug -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

將此值作為診斷模式傳給 Hyundai／Kia CCNC CAN FD 訊息產生器。這不是一般使用者功能，各數值對應行為不屬於穩定的使用者介面規格。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

確認車輛的 HDA 及 CAN FD 配置，停妥後設定，並於下次行車檢查相關功能及故障訊息。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 這是直接傳入車輛 CAN 訊息產生程序的開發除錯值。除非正在診斷該路徑，否則請保留預設值。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CanfdDebug -->

<!-- CARROT:SETTING:END CanfdDebug -->
