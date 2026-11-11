<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_SCREEN" param="ClusterHudCameraViewMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Camera View Mode(0)

**選單:** 顯示 \> 外部HUD \> 畫面·攝影機

---

<!-- CARROT:SETTING:BEGIN ClusterHudCameraViewMode -->
<a id="ClusterHudCameraViewMode"></a>

## External HUD Camera View Mode(0)

`ClusterHudCameraViewMode`

0: Default 1: Mode 1 (bottom view) 2: Narrow road camera 3: Wide road camera 4: Automatic narrow/wide camera by speed

<!-- CARROT:AUTO:BEGIN ClusterHudCameraViewMode -->
<!-- CARROT:AUTO:SOURCE facts="3512c83f1d51c55bd0aa498d0295e55cff7ba7a52a8d06d1024abd5c9101f2b8" semantic="af3b40d3730a153e0c5d95a63e09da0dd2f8fe994a2a77fcbd201478e1a2773f" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** Default (`0`)
- **範圍:** Default (`0`) ~ Speed automatic (`4`)
- **步長:** `1`
- **選項:** `0` Default, `1` Bottom view, `2` Narrow camera, `3` Wide camera, `4` Speed automatic
- **選單:** 顯示 \> 外部HUD \> 畫面·攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudCameraViewMode -->

<!-- CARROT:MANUAL:BEGIN ClusterHudCameraViewMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 預設
- `1` — 模式 1（底部畫面）
- `2` — 道路攝影機背景
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

選擇模式時，檢查外接 HUD 的顯示延遲、清晰度及 CPU 使用量。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudCameraViewMode -->

<!-- CARROT:SETTING:END ClusterHudCameraViewMode -->
