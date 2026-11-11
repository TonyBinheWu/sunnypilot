<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_DRIVE_MODE" param="MyDrivingMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 驾驶模式: 初始 (3)

**菜单:** 驾驶控制 \> 巡航与车距 \> 加速特性 \> 驾驶模式

---

<!-- CARROT:SETTING:BEGIN MyDrivingMode -->
<a id="MyDrivingMode"></a>

## 驾驶模式: 初始 (3)

`MyDrivingMode`

1: 节能 - 最大加速度×0.9，时间车距×1.1，前车响应最高2。 2: 安全 - 最大加速度×0.8，时间车距×1.2，前车响应最高3，并保留提前平缓减速的余量。 3: 普通 - 基本加速和车距，使用所选响应。 4: 高速 - 最大加速度×1.2，保留所选响应，禁用红绿灯停车。 不再叠加模式专用的加加速度调整，模式车距余量逐渐释放。较低响应值和0不会提高。

<!-- CARROT:AUTO:BEGIN MyDrivingMode -->
<!-- CARROT:AUTO:SOURCE facts="5335778b6201df72ae3a866c83a16bd6c106449cf9fce68781431cc7179ddbaf" semantic="6405b6142b9c6696548a67a172fbe0c6fcae9520e0055bb628b5ca3647987b6e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `3`
- **范围:** `1` ~ `4`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 加速特性 \> 驾驶模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MyDrivingMode -->

<!-- CARROT:MANUAL:BEGIN MyDrivingMode -->
<!-- CARROT:REVIEW reviewed-for="6405b6142b9c6696548a67a172fbe0c6fcae9520e0055bb628b5ca3647987b6e" reviewed-at="2026-09-13T10:16:28.802623+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

节能使用最大加速度×0.9、时间车距×1.1。安全使用最大加速度×0.8、时间车距×1.2及平缓停车余量。普通使用基本值，高速使用最大加速度×1.2并关闭红绿灯停止和起步检测。

确定通用值或车距专用响应后，节能最高2，安全最高3。普通和高速保留所选值，不提高较低值和0，也不改写保存值。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END MyDrivingMode -->

<!-- CARROT:SETTING:END MyDrivingMode -->
