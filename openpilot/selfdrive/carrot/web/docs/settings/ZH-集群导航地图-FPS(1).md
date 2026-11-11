<!-- CARROT:GENERATED schema="1" locale="zh" group="HUD_BASIC" param="ClusterNaviMapFps" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 集群导航地图 FPS(1)

**菜单:** 显示 \> 外部HUD \> 基本

---

<!-- CARROT:SETTING:BEGIN ClusterNaviMapFps -->
<a id="ClusterNaviMapFps"></a>

## 集群导航地图 FPS(1)

`ClusterNaviMapFps`

0: 5 FPS 1: 10 FPS（默认） 2: 20 FPS 3: 30 FPS 此设置独立于 HUD FPS，地图比特率自动设置。 更改后外部导航应用会自动重新连接。

<!-- CARROT:AUTO:BEGIN ClusterNaviMapFps -->
<!-- CARROT:AUTO:SOURCE facts="31a1febc21b84ccb152c5b280ec0e69d936e233dc825e090cb595d0cc5a581e2" semantic="e37c29337d96679ca12cd545db724e093fed073e51e81b87e087206f74a837b1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** 10 FPS (`1`)
- **范围:** 5 FPS (`0`) ~ 30 FPS (`3`)
- **步长:** `1`
- **选项:** `0` 5 FPS, `1` 10 FPS, `2` 20 FPS, `3` 30 FPS
- **菜单:** 显示 \> 外部HUD \> 基本
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterNaviMapFps -->

<!-- CARROT:MANUAL:BEGIN ClusterNaviMapFps -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END ClusterNaviMapFps -->

<!-- CARROT:SETTING:END ClusterNaviMapFps -->
