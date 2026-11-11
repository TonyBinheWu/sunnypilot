<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="AutoTurnMapChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC 輔助地圖顯示(0)

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnMapChange -->
<a id="AutoTurnMapChange"></a>

## ATC 輔助地圖顯示(0)

`AutoTurnMapChange`

(APN) ATC 啟用時開啟地圖

<!-- CARROT:AUTO:BEGIN AutoTurnMapChange -->
<!-- CARROT:AUTO:SOURCE facts="df64fde4966ae15daf2a92a3f4e7325ba103f21250e881049efa91bc1fb75715" semantic="e5a6acf262e3326cb0dab44709ee7c0a63122f628c93714fdb9143510beeead6" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnMapChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnMapChange -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- **開啟：** ATC 轉彎控制啟動時，將連接的顯示器切換至地圖模式；該路段結束後恢復道路畫面。
- **關閉：** ATC 不會傳送畫面切換指令。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在車道線清楚且附近無車流處測試，確認打方向燈後的等待、車道檢查及完成時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> 此輔助功能會在 ATC 啟用期間，切換至已連接的外部導航地圖。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoTurnMapChange -->

<!-- CARROT:SETTING:END AutoTurnMapChange -->
