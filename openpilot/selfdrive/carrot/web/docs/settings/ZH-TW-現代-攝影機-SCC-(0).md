<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_HYUNDAI" param="HyundaiCameraSCC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 現代: 攝影機 SCC (0)

**選單:** 車輛與硬體 \> 現代·起亞

---

<!-- CARROT:SETTING:BEGIN HyundaiCameraSCC -->
<a id="HyundaiCameraSCC"></a>

## 現代: 攝影機 SCC (0)

`HyundaiCameraSCC`

1: 縱向控制車輛, 2: 巡航狀態同步 (CAN-FD 車輛), 3: 原廠巡航 (CANFD 縱向線束) 關閉時，若在攝影機匯流排上檢測到 SCC，發生 CAN 錯誤時會提示啟用此設定。已配置攝影機 SCC 的車型除外。 CAN-FD CameraSCC 使用 openpilot 縱向控制並啟用角雷達時，在 CAN 有效、D 擋、鬆開制動且車速超過 10.8 km/h 的條件下，會週期性請求開啟原廠 SCC MAIN。此功能獨立於 AutoEngage 和 Carrot 巡航啟用狀態，MAIN 開啟後停止該請求。SET 和停車後恢復請求仍要求 Carrot 巡航處於啟用狀態。 CAN-FD CameraSCC 使用 openpilot 縱向控制時，用於儀表顯示的原廠 SCC MAIN 狀態與 Carrot 啟用意圖分別處理。轉向啟用遵循 AutoEngage 初始設定及現有駕駛員按鍵設定。

<!-- CARROT:AUTO:BEGIN HyundaiCameraSCC -->
<!-- CARROT:AUTO:SOURCE facts="20e353fdcd7b15bc345d4353d408e653b73350dadee1fe5f239d6fbc10c59262" semantic="287a1e4a7254a0c59acf4e381efa7c629c34796276cbd8584241a52c4a779f28" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 車輛與硬體 \> 現代·起亞
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HyundaiCameraSCC -->

<!-- CARROT:MANUAL:BEGIN HyundaiCameraSCC -->
<!-- CARROT:REVIEW reviewed-for="287a1e4a7254a0c59acf4e381efa7c629c34796276cbd8584241a52c4a779f28" reviewed-at="2026-11-04T12:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- `0` — 不透過此設定強制啟用攝影機 SCC；車型預設與其他縱向控制設定仍會生效。
- `1` — 使用攝影機 SCC 配置，並啟用 openpilot 縱向控制。
- `2` — 標示為巡航狀態同步；目前車輛介面的實作與 `1` 相同，會啟用攝影機 SCC 與縱向控制。
- `3` — 使用攝影機 SCC 線組，縱向控制仍交由原廠巡航。

若此設定關閉且尚未套用攝影機 SCC，在本次行車期間從攝影機匯流排（bus2 或多 Panda 的對應匯流排）收到 `SCC_CONTROL`（CAN-FD）或 `SCC12`（傳統 CAN），會在 CAN 錯誤警示加入 **Enable CameraSCC**。系統絕不會自動變更此設定，原有解除控制及禁止啟用機制仍有效。
啟用 CAN-FD CameraSCC、openpilot 縱向控制及角雷達時，若 CAN 有效、排入 D 檔、煞車已放開且車速高於 10.8 km/h，系統可定期請求開啟原廠 SCC MAIN。此行為獨立於 AutoEngage 及 Carrot 巡航啟用狀態，MAIN 開啟後即停止請求。SET 及靜止恢復請求仍須符合既有 Carrot 巡航啟用條件。

使用 CAN-FD CameraSCC 及 openpilot 縱向控制時，儀表顯示使用的原廠 SCC MAIN 狀態，會與 Carrot 啟用意圖分開追蹤。轉向啟用遵循 AutoEngage 初始化及既有駕駛按鈕設定。

<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

確認車輛規格及線組配置，停妥後設定，並於下次行車確認 SCC 及車道警示行為。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 車型、年式、HDA 世代或線組位置不符，可能導致 SCC 或縱向控制行為錯誤。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HyundaiCameraSCC -->

<!-- CARROT:SETTING:END HyundaiCameraSCC -->
