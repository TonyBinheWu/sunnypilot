<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_LONGTUNE" param="LongTuningKpV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 纵向 KpV(100)x0.01

**菜单:** 驾驶控制 \> 巡航与车距 \> 加减速调校

---

<!-- CARROT:SETTING:BEGIN LongTuningKpV -->
<a id="LongTuningKpV"></a>

## 纵向 KpV(100)x0.01

`LongTuningKpV`

纵向控制比例增益。现代、起亚和捷尼赛思的一般纵向控制固定为 Kp 1.0，因此不会显示或应用此设置。 丰田/雷克萨斯的通用 Kp=0 固定，以避免与专用控制器重复补偿；此设置隐藏且不应用保存值。 已识别为 Ray EV Comma Pedal 控制时显示此设置，并在约一秒内将保存值应用于速度 PID。

<!-- CARROT:AUTO:BEGIN LongTuningKpV -->
<!-- CARROT:AUTO:SOURCE facts="f069b8b5780d90d17026d832211c4423c95a51b5cd09698e65690ea9fe57403c" semantic="da83b19cd7c1eaed65e221d1571b66a8f33f00b0c83097c2f56007bccd5323c1" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `100`
- **范围:** `0` ~ `200`
- **步长:** `5`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 加减速调校
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongTuningKpV -->

<!-- CARROT:MANUAL:BEGIN LongTuningKpV -->
<!-- CARROT:REVIEW reviewed-for="da83b19cd7c1eaed65e221d1571b66a8f33f00b0c83097c2f56007bccd5323c1" reviewed-at="2026-11-11T05:33:10.288234+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 动作

Ray EV 检测到 Comma Pedal 且启用 openpilot 纵向控制后，会显示 Long Kp/Ki/Kf，并将保存值用于速度 PID。启动时读取保存值，运行期间约每秒更新一次。

其他现代/起亚/捷尼赛思配置的通用 Kp/Ki/Kf 固定为 1/0/1。丰田/雷克萨斯由专用车辆控制器补偿加速度，通用增益固定为 0/0/1。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END LongTuningKpV -->

<!-- CARROT:SETTING:END LongTuningKpV -->
