<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 低速模型转向余量

**菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## 低速模型转向余量

`LowSpeedSteerReserve`

仅 Hyundai/Kia CAN-FD 力矩控制。30 km/h 以下持续达到原上限才提供额外输出，最高 409；30–40 km/h 逐步回归原上限。保留原参数与控制比例，需实车验证。

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="c84f1d8532b2f5093443d04c0211379af50b173d51607c8cfe5998c0b9e9d37c" semantic="6a5d981658c4dd294c2fd535015e46b0fe4d8c3e9583fbe6b51bcf29586bdb4d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 运作方式

仅支持 Hyundai／Kia CAN-FD 力矩转向。需求连续约 0.30 秒接近原上限时，30 km/h 以下可按需使用额外输出，最高 409；30–40 km/h 的目标上限逐步回到原值。普通需求的控制比例、增益与学习参数不变。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

开关位于 CustomSteerMax 正下方，初始关闭。约 0.5 秒内重新读取，无需重启；不会改写原设置，原上限已达 409 或更高时不再增加。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 补充说明

驾驶员介入、倒车／静止、CAN 异常、转向故障、缺少或过期的模型数据及横向退出时取消额外资格。输出按原变化速率收回，并非瞬间归零；保留 EPS 大角度保护与 Panda 限制。仅完成桌面测试，409 与速度门槛未经实车验证，不保证急弯或路口转弯。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
