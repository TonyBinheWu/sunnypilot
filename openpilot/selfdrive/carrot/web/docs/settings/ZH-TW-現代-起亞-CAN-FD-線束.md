<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_CANFD" param="CanfdHDA2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 現代／起亞 CAN-FD 線束

**選單:** 車輛與硬體 \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdHDA2 -->
<a id="CanfdHDA2"></a>

## 現代／起亞 CAN-FD 線束

`CanfdHDA2`

下次啟動生效。可自動偵測，或依實際接線選攝影機或 ADAS ECU。

<!-- CARROT:AUTO:BEGIN CanfdHDA2 -->
<!-- CARROT:AUTO:SOURCE facts="7449d8c151a34093f9d66e796a6f080ddfa2131c5329e1e558d2c378a95c75ff" semantic="a4d30a9a469e9c7a3be9b5bb5943a92f33fce83e193ba0e774e932a8a536e295" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 自動偵測 (`2`)
- **範圍:** 攝影機（HDA1） (`0`) ~ 自動偵測 (`2`)
- **步長:** `1`
- **選項:** `0` 攝影機（HDA1）, `1` ADAS ECU（HDA2）, `2` 自動偵測
- **選單:** 車輛與硬體 \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdHDA2 -->

<!-- CARROT:MANUAL:BEGIN CanfdHDA2 -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- `0` — 將 Hyundai／Kia CAN FD 車輛視為 HDA1 配置。
- `1` — 使用 HDA2 CAN 匯流排配置。
- `2` — 根據實際收到的 LKAS 訊息與長度，自動辨識 CAN-FD 轉向線束。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

確認車輛的 HDA 及 CAN FD 配置，停妥後設定，並於下次行車檢查相關功能及故障訊息。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 未經驗證的 CAN FD 配置，可能造成車輛警告或 CAN 故障。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CanfdHDA2 -->

<!-- CARROT:SETTING:END CanfdHDA2 -->
