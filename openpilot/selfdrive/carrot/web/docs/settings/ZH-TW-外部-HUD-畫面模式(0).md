<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_SCREEN" param="ClusterHudScreenMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 外部 HUD 畫面模式(0)

**選單:** 顯示 \> 外部HUD \> 畫面·攝影機

---

<!-- CARROT:SETTING:BEGIN ClusterHudScreenMode -->
<a id="ClusterHudScreenMode"></a>

## 外部 HUD 畫面模式(0)

`ClusterHudScreenMode`

-1: 3D全屏 0: 預設(導航/駕駛報告) 1: 除錯 2: 除錯(系統) 3: 除錯(圖表1) 4: 除錯(圖表2) 5: 駕駛報告 6: 外部導航全屏 7: 駕駛畫面 + 右側Nav地圖 Onroad 狀態下，P 擋優先顯示駐車畫面，R 擋顯示基於 EV6 尺寸的倒車參考圖。其他擋位或 offroad 恢復原畫面模式。

<!-- CARROT:AUTO:BEGIN ClusterHudScreenMode -->
<!-- CARROT:AUTO:SOURCE facts="1649c487fa60e94a2b50ff703284d773053635b5ddf019b3740c59ca3fbacee6" semantic="4454f6bc7bf3c1b0d27dc7adfae91475bc67670dc85dee7fee357a165b54433d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** `0`
- **範圍:** `-1` ~ `7`
- **步長:** `1`
- **選單:** 顯示 \> 外部HUD \> 畫面·攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudScreenMode -->

<!-- CARROT:MANUAL:BEGIN ClusterHudScreenMode -->
<!-- CARROT:REVIEW reviewed-for="627a973ecafa1b31a96e570c3d02499497c8b6d45ab1e2366aa65ab21435fe93" reviewed-at="2026-07-31T23:37:31+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

- `-1` — 在 3D 攝像頭檢視 `0`、`1` 中取消資訊面板並使用全屏寬度。左側專案保持原邊距，右側儀表和 TPMS 對齊物理螢幕右邊緣，時鐘、3D 場景和轉向燈以全屏中心為軸。在道路攝像頭檢視 `2` 中，導航/駕駛報告自動切換和左右面板佈局與模式 `0` 完全相同。
- `0` — 預設畫面；收到導航時顯示導航面板，否則自動顯示駕駛報告。
- `1` — 顯示延遲、扭矩、轉向和橫向規劃狀態的實時除錯畫面。
- `2` — 基準系統畫面；不使用模式 `0` 的自動駕駛報告回退，有導航狀態時保持導航或 `NAVI DISCONNECTED`，僅在沒有導航來源時顯示路線疊加層。
- `3` — 關閉駕駛場景並放大顯示 `ShowPlotMode` 圖表。
- `4` — 保留駕駛場景並在資訊面板中顯示圖表。加速度、轉向、燃油和 DEF 儀表緊靠圖表左側並隨面板左右切換，TPMS 保留在駕駛畫面一側。
- `5` — 始終顯示駕駛報告。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

日常自動導航/報告使用 `0`，需要更寬的 3D 場景時使用 `-1`，需要同時比較駕駛場景和圖表時使用 `4`。要恢復普通自動畫面，請重新選擇 `0`。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudScreenMode -->

<!-- CARROT:SETTING:END ClusterHudScreenMode -->
