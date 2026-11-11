<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="AutoNaviSpeedDecelRate" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 导航减速效率 0.01m/s^2x(120)

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedDecelRate -->
<a id="AutoNaviSpeedDecelRate"></a>

## 导航减速效率 0.01m/s^2x(120)

`AutoNaviSpeedDecelRate`

用于计算接近摄像头和减速带时的减速曲线。存储值乘以 0.01 m/s²，120 表示 1.2 m/s²。数值越低，开始减速的距离越远；数值越高，开始减速的距离越近。软件更新不会更改已保存的设置。

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedDecelRate -->
<!-- CARROT:AUTO:SOURCE facts="a36c1b1c8832f3bd31f1946f958595c0c61acf3ec1baa869a5d4021e7588a23d" semantic="dd424d47dfc026837af962b9c56209e7643717b0eba2e3136437850b8bdd30c3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `120`
- **范围:** `50` ~ `300`
- **步长:** `10`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedDecelRate -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedDecelRate -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END AutoNaviSpeedDecelRate -->

<!-- CARROT:SETTING:END AutoNaviSpeedDecelRate -->
