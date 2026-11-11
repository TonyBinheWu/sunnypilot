<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_RADAR" param="RadarTrackFlip" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 雷达左右反转

**菜单:** 车辆与硬件 \> 雷达

---

<!-- CARROT:SETTING:BEGIN RadarTrackFlip -->
<a id="RadarTrackFlip"></a>

## 雷达左右反转

`RadarTrackFlip`

校正前雷达轨迹的左右方向。 0：正常（默认） 1：反转横向位置和横向速度 不适用于 SCC、角雷达或视觉。同时影响前车选择和雷达显示。不按车型自动反转；仅在确认左右不一致后选择。更改后请重新启动车辆或设备。

<!-- CARROT:AUTO:BEGIN RadarTrackFlip -->
<!-- CARROT:AUTO:SOURCE facts="1b50b27064ce3a21b62a6ae20640dc4cc261bcfce35f74711ffe39d82e938c60" semantic="943dbe7612241b525566748d4a0c0383a19f20e4a140a100fad0a061f818df64" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 正常 (`0`)
- **范围:** 正常 (`0`) ~ 左右反转 (`1`)
- **步长:** `1`
- **选项:** `0` 正常, `1` 左右反转
- **菜单:** 车辆与硬件 \> 雷达
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RadarTrackFlip -->

<!-- CARROT:MANUAL:BEGIN RadarTrackFlip -->
<!-- CARROT:REVIEW reviewed-for="bd236f17fd9177f84d830907b23c61d75e1e8216aac4ca4dfb3cc9e3d4460cb8" reviewed-at="2026-09-23T00:19:35.952962+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

正常模式保留前雷达轨迹坐标；反转模式同时反转横向位置和横向速度。它影响前车选择和雷达显示，不改变 SCC、角雷达、视觉及纵向距离和速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

仅在确认视频与雷达左右不一致后选择反转。不会按车型自动反转；更改后请重新启动车辆或设备，在下一次 OnRoad 启动时生效。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END RadarTrackFlip -->

<!-- CARROT:SETTING:END RadarTrackFlip -->
