<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_RADAR" param="EnableRadarTracks" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 開啟雷達軌跡 (0)

**選單:** 車輛與硬體 \> 雷達

---

<!-- CARROT:SETTING:BEGIN EnableRadarTracks -->
<a id="EnableRadarTracks"></a>

## 開啟雷達軌跡 (0)

`EnableRadarTracks`

-2: VOACC 純視覺測試 -1: 無視覺匹配始終使用 SCC；無 SCC 時使用視覺 0: 始終使用 SCC 縱向距離和相對速度；無 SCC 時使用視覺 1: 僅前雷達與視覺匹配；失敗時使用視覺 2: 前雷達 + 低速 SCC 與視覺匹配；失敗時使用視覺 3: 前雷達視覺匹配失敗後始終使用 SCC；無 SCC 時使用視覺 新視覺目標要求 prob \>= 0.40；所有 SCC 匹配均忽略橫向位置 自動支援傳統 Mando 32/64 槽位版本

<!-- CARROT:AUTO:BEGIN EnableRadarTracks -->
<!-- CARROT:AUTO:SOURCE facts="b4658fdb18f329a648a130938d7a5c6ce2354ff051c3d2abef1b1d8170382514" semantic="0aab8f5fa0c29c37fd4b650cd2a25ffe0451f1c62b9f8fcbcb386721f8c81218" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** `0`
- **範圍:** `-2` ~ `3`
- **步長:** `1`
- **選單:** 車輛與硬體 \> 雷達
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END EnableRadarTracks -->

<!-- CARROT:MANUAL:BEGIN EnableRadarTracks -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END EnableRadarTracks -->

<!-- CARROT:SETTING:END EnableRadarTracks -->
