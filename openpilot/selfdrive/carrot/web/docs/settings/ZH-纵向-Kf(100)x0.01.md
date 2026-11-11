<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_LONGTUNE" param="LongTuningKf" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 纵向 Kf(100)x0.01

**菜单:** 驾驶控制 \> 巡航与车距 \> 加减速调校

---

<!-- CARROT:SETTING:BEGIN LongTuningKf -->
<a id="LongTuningKf"></a>

## 纵向 Kf(100)x0.01

`LongTuningKf`

在加速和制动方向预先应用目标加速度。现代、起亚和捷尼赛思的一般纵向控制固定为 Kf 1.0，因此不会显示或应用此设置。 丰田/雷克萨斯的通用 Kf=1 固定，以避免与专用控制器重复补偿；此设置隐藏且不应用保存值。 已识别为 Ray EV Comma Pedal 控制时显示此设置，并在约一秒内将保存值应用于速度 PID。

<!-- CARROT:AUTO:BEGIN LongTuningKf -->
<!-- CARROT:AUTO:SOURCE facts="535d30707981a06baa12dd365790808d7d74152b80a4793aa23e05d775536257" semantic="b3ec7b2deffaf3c3c23388c2c4847d52984e1061625b5bb1cf8f304f7afcd1e5" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `100`
- **范围:** `0` ~ `200`
- **步长:** `5`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 加减速调校
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongTuningKf -->

<!-- CARROT:MANUAL:BEGIN LongTuningKf -->
<!-- CARROT:REVIEW reviewed-for="b3ec7b2deffaf3c3c23388c2c4847d52984e1061625b5bb1cf8f304f7afcd1e5" reviewed-at="2026-11-11T05:33:10.303272+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 动作

Ray EV 检测到 Comma Pedal 且启用 openpilot 纵向控制后，会显示 Long Kp/Ki/Kf，并将保存值用于速度 PID。启动时读取保存值，运行期间约每秒更新一次。

其他现代/起亚/捷尼赛思配置的通用 Kp/Ki/Kf 固定为 1/0/1。丰田/雷克萨斯由专用车辆控制器补偿加速度，通用增益固定为 0/0/1。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END LongTuningKf -->

<!-- CARROT:SETTING:END LongTuningKf -->
