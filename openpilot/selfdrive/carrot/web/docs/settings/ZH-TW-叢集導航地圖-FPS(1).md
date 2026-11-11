<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_BASIC" param="ClusterNaviMapFps" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 叢集導航地圖 FPS(1)

**選單:** 顯示 \> 外部HUD \> 基本

---

<!-- CARROT:SETTING:BEGIN ClusterNaviMapFps -->
<a id="ClusterNaviMapFps"></a>

## 叢集導航地圖 FPS(1)

`ClusterNaviMapFps`

0: 5 FPS 1: 10 FPS（預設） 2: 20 FPS 3: 30 FPS 此設定獨立於 HUD FPS，地圖位元率自動設定。 更改後外部導航應用會自動重新連線。

<!-- CARROT:AUTO:BEGIN ClusterNaviMapFps -->
<!-- CARROT:AUTO:SOURCE facts="046c82d14947092303155cd9357b93e5c750533c55a2057db0942d0a2d7ef26a" semantic="e37c29337d96679ca12cd545db724e093fed073e51e81b87e087206f74a837b1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** 10 FPS (`1`)
- **範圍:** 5 FPS (`0`) ~ 30 FPS (`3`)
- **步長:** `1`
- **選項:** `0` 5 FPS, `1` 10 FPS, `2` 20 FPS, `3` 30 FPS
- **選單:** 顯示 \> 外部HUD \> 基本
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterNaviMapFps -->

<!-- CARROT:MANUAL:BEGIN ClusterNaviMapFps -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 5 FPS
- `1` — 10 FPS（預設）
- `2` — 20 FPS
- `3` — 30 FPS／此設定獨立於 HUD FPS，並會自動選擇地圖位元率。／變更時會自動重新連接外部導航 App
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

連接外接 HUD 後變更，確認方向、亮度及地圖連線。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> 地圖 FPS 獨立於主 HUD FPS，地圖位元率會依選定幀率自動調整。變更此設定會重新連接外部導航。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ClusterNaviMapFps -->

<!-- CARROT:SETTING:END ClusterNaviMapFps -->
