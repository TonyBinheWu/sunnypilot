<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_DM" param="DriverMonitoringEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 啟用駕駛員監控（例外設定）

**選單:** 車輛與硬體 \> 駕駛員監控

---

<!-- CARROT:SETTING:BEGIN DriverMonitoringEnabled -->
<a id="DriverMonitoringEnabled"></a>

## 啟用駕駛員監控（例外設定）

`DriverMonitoringEnabled`

預設開啟，建議保持開啟。此例外選項僅供未安裝 DM 攝影機，或 DM 攝影機故障而無法正常進行駕駛員監控的裝置使用。關閉後，正常行駛時的 DM 模型與警告、監控觸發的強制減速及鎖定都會停用。未啟用駕駛員監控時駕駛，可能違反所在地法律、車輛要求或使用條件；請僅在確認適用要求並承擔安全責任後關閉。

<!-- CARROT:AUTO:BEGIN DriverMonitoringEnabled -->
<!-- CARROT:AUTO:SOURCE facts="a6626a3cd8f8c2366e9c34b0d55a05247f07135096b279e31f8e965ef6f3379b" semantic="75de16e159e826f4dfe20f040bbaada4fc65960b24b5d45781569bb9bb118027" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `1`
- **範圍:** `0` ~ `1`
- **選單:** 車輛與硬體 \> 駕駛員監控
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DriverMonitoringEnabled -->

<!-- CARROT:MANUAL:BEGIN DriverMonitoringEnabled -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END DriverMonitoringEnabled -->

<!-- CARROT:SETTING:END DriverMonitoringEnabled -->
