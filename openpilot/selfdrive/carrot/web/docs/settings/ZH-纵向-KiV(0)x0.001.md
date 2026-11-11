<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_LONGTUNE" param="LongTuningKiV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 纵向 KiV(0)x0.001

**菜单:** 驾驶控制 \> 巡航与车距 \> 加减速调校

---

<!-- CARROT:SETTING:BEGIN LongTuningKiV -->
<a id="LongTuningKiV"></a>

## 纵向 KiV(0)x0.001

`LongTuningKiV`

纵向控制积分增益。现代、起亚和捷尼赛思的一般纵向控制固定为 Ki 0，因此不会显示或应用此设置。 丰田/雷克萨斯的通用 Ki=0 固定，以避免与专用控制器重复补偿；此设置隐藏且不应用保存值。 已识别为 Ray EV Comma Pedal 控制时显示此设置，并在约一秒内将保存值应用于速度 PID。 实际 Ki 为保存值乘以 0.001。

<!-- CARROT:AUTO:BEGIN LongTuningKiV -->
<!-- CARROT:AUTO:SOURCE facts="b038d0f6a4e9537c25b607c4a8f53b7ab6a092ae2fb4fc24404426f913409b9e" semantic="408a16f2cac3b273bfca7a6a8fe50a70b9f2aed1b3ad6042d70f49451eb04700" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0`
- **范围:** `0` ~ `2000`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 加减速调校
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongTuningKiV -->

<!-- CARROT:MANUAL:BEGIN LongTuningKiV -->
<!-- CARROT:REVIEW reviewed-for="408a16f2cac3b273bfca7a6a8fe50a70b9f2aed1b3ad6042d70f49451eb04700" reviewed-at="2026-11-11T05:33:10.295260+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 动作

Ray EV 检测到 Comma Pedal 且启用 openpilot 纵向控制后，会显示 Long Kp/Ki/Kf，并将保存值用于速度 PID。启动时读取保存值，运行期间约每秒更新一次。

其他现代/起亚/捷尼赛思配置的通用 Kp/Ki/Kf 固定为 1/0/1。丰田/雷克萨斯由专用车辆控制器补偿加速度，通用增益固定为 0/0/1。
实际 Ki 系数为保存值 × 0.001。保存值 50 对应 0.050，100 对应 0.100。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END LongTuningKiV -->

<!-- CARROT:SETTING:END LongTuningKiV -->
