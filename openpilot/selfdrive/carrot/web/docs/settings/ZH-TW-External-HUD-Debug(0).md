<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_PERF" param="ClusterHudDebug" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Debug(0)

**選單:** 顯示 \> 外部HUD \> 效能·除錯

---

<!-- CARROT:SETTING:BEGIN ClusterHudDebug -->
<a id="ClusterHudDebug"></a>

## External HUD Debug(0)

`ClusterHudDebug`

0: Onroad only 1: Always 2: Always + UI 3: Always + Navi

<!-- CARROT:AUTO:BEGIN ClusterHudDebug -->
<!-- CARROT:AUTO:SOURCE facts="525d430de0b97a3900748cf84ad525ba15ea68eaf6325bcf1739ce10cf0d45e2" semantic="f3690826c5fa0e74264bedafa8192c8a74e880f3190c33ebf87d9b5748bcdf27" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 顯示 \> 外部HUD \> 效能·除錯
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudDebug -->

<!-- CARROT:MANUAL:BEGIN ClusterHudDebug -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 僅行車時
- `1` — 持續啟用
- `2` — 持續啟用＋介面
- `3` — 持續啟用＋導航
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

僅供診斷，每次調整一項，確認外接 HUD 的影格穩定性及系統負載。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudDebug -->

<!-- CARROT:SETTING:END ClusterHudDebug -->
