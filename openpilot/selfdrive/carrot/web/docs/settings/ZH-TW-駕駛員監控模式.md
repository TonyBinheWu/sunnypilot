<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_DM" param="DriverMonitoringMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 駕駛員監控模式

**選單:** 車輛與硬體 \> 駕駛員監控

---

<!-- CARROT:SETTING:BEGIN DriverMonitoringMode -->
<a id="DriverMonitoringMode"></a>

## 駕駛員監控模式

`DriverMonitoringMode`

0：標準；1：實驗。實驗模式可能違反法規，僅限受控測試。無攝影機時基礎警告為15/30/45秒；實驗模式在確認的空曠直道上為30/60/90秒。周圍從無移動車輛變為首次確認有移動車輛時，才啟用20秒標準監測。持續觀測或新增車輛不會延長，之後恢復實驗監測。此期間停止攝影機操作寬限、特殊前方注視重置和檢測放寬，並結束此前寬限。有攝影機的0模式保留comma行為；1模式為10/16/26秒，空曠道路為20/32/52秒，頭部姿態容差增加20%。駕駛員或藍芽按鍵操作重置計時，推遲攝影機警告45或90秒後開始攝影機監控；這也會延遲睏倦、閉眼和手機警告。連續2秒明確注視前方可重置攝影機計時。操作不能解除最高警告或鎖定。攝影機故障自動切換為操作監控。標準模式不保證合法認證。模式更改無需重新啟動，約每0.5秒實時應用。切換保留累計監控時間、警告次數和鎖定，並結束此前的操作寬限及連續前方注視判定。 現代/起亞/捷尼賽思CAN-FD中不按車型名稱限制、透過格式、校驗和、計數器及新鮮度驗證的原始STEER\_TOUCH\_2AF觸控在攝影機不可用時持續重置操作計時；攝影機正常的1模式僅將新接觸視為操作，0模式保持原樣。 共同例外：無論攝影機是否可用，兩種模式均在有效訊號持續確認P擋、完全靜止及輔助駕駛解除1秒後重置累計警告和鎖定。僅零速或關閉再開啟不能解除，必須手動重新啟用。

<!-- CARROT:AUTO:BEGIN DriverMonitoringMode -->
<!-- CARROT:AUTO:SOURCE facts="58159b01629cb9108dc34805dfc16fd53013a2fad79eb1acb63c6360e6c2fc39" semantic="41de43ecd7b558bf3408066b776219f5a1367f4ed91a5aae8a31995a4f0b821a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 標準 (`0`)
- **範圍:** 標準 (`0`) ~ 實驗（僅供測試） (`1`)
- **步長:** `1`
- **選項:** `0` 標準, `1` 實驗（僅供測試）
- **選單:** 車輛與硬體 \> 駕駛員監控
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DriverMonitoringMode -->

<!-- CARROT:MANUAL:BEGIN DriverMonitoringMode -->
<!-- CARROT:REVIEW reviewed-for="71597058dbc3a5673ec5c3fa80f182b7386309654371ebfdfcbf577dd83a765d" reviewed-at="2026-09-28T23:46:27.865578+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

標準模式在攝像頭正常時保留comma行為，不可用時採用獨立的操作監控時間。實驗模式在觀測到的空曠道路上延長時間，在駕駛員或藍芽操作後推遲攝像頭警告，並在明確注視前方時重置計時。

現代/起亞/捷尼賽思CAN-FD中不按車型名稱限制、透過格式、校驗和、計數器及新鮮度驗證的原始STEER_TOUCH_2AF觸控在攝像頭不可用時持續重置操作計時。攝像頭正常時，實驗模式僅將有效鬆手後的新接觸視為操作；持續握持或訊號恢復不會重複延長寬限。攝像頭正常的標準模式保持原樣，觸控不能解除最高警告。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

實驗模式僅限受控測試。模式更改無需重啟，約每0.5秒實時應用，保留累計監控時間、警告次數和鎖定。此前的操作寬限及連續前方注視判定結束。周圍從無移動車輛變為首次確認有移動車輛時，才啟用20秒標準監測。持續觀測或新增車輛不會延長，之後恢復實驗監測，但仍有車輛時不增加空路倍率。攝像頭正常時，此期間使用原廠檢測和輸入處理，暫停實驗操作寬限和特殊前方注視重置。此前寬限結束；所有觀測消失且超過最後觀測的2秒保留期後，再次出現才可觸發新的監測視窗。

無論攝像頭是否可用，兩種模式均在有效訊號持續確認P擋、完全靜止及輔助駕駛解除1秒後重置累計警告和鎖定。該例外也適用於標準模式；僅零速或關閉再開啟不能解除，必須手動重新啟用。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

操作寬限也會延遲睏倦、閉眼及手機警告，不能保證清醒或合法合規。請閱讀[四種模式的時間、寬限、重置和最高警告限制](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/driver-monitoring.md)。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END DriverMonitoringMode -->

<!-- CARROT:SETTING:END DriverMonitoringMode -->
