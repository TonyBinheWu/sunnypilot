<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 低速需求跟随与反应记录

**菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## 低速需求跟随与反应记录

`LowSpeedSteerReserve`

仅 Hyundai/Kia CAN-FD 力矩控制。持续需求 0.30 秒后，≤30 km/h 按需提供最高 409 的余量，30–40 渐退。开启时全速域使用车型默认比例及增减速率，手动值保留；≥40 不再提供余量。只记录反应，不探测或提高硬件上限，需实车验证。

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="8f3a089cf0a813230855d3d9e272d4ea3382735c3d6044d41039622dc164553d" semantic="f3e6e9a5914e7a8cb28bed45e8f14db13132a0c4aeea40956275b3c4dffe4bba" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:REVIEW reviewed-for="f3e6e9a5914e7a8cb28bed45e8f14db13132a0c4aeea40956275b3c4dffe4bba" reviewed-at="2026-11-17T12:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 运作方式

仅支援 Hyundai／Kia CAN-FD 扭力转向。需求接近预设上限并持续 0.30 秒后，≤30 km/h 只依实际需求提供最高 409 的余量；30–40 km/h 上限渐退，≥40 km/h 使用车型预设上限。开启期间全速域采用车型预设换算比例与指令增加／减少速率；储存的 CustomSteerMax 与 CustomSteerDelta 数值暂不参与执行，但不会被覆写。增益与即时扭力学习不变，角度控制车型不增加控制权限。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

此选用开关仍位于 CustomSteerMax 正下方，约 0.5 秒内读取、不需重新启动；关闭后恢复储存的手动限制。机器「设备 > 转向学习进度」与网页／APK「工具 > 转向学习进度」可查看需求／送出指令、目标／实际方向盘角度、实际角度速率、目前限制，以及左右指令期间的观察峰值。即时状态超过 2 秒标示过期；历史汇总另行标示，仅载入相同车型与控制类型的纪录。只在功能开启时于本机收集汇总，每 60 秒及退出控制／关闭功能时储存；不含位置、行程或云端上传。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 补充说明

驾驶接管、CAN 无效、转向故障、倒车／静止、模型过期或退出横向控制会取消余量资格。收回输出仍遵守车型预设变化速率，保留 EPS 转向请求保护与 Panda 安全限制。指令单位是 CAN 数值，不是牛顿米；增加／减少数值表示每 10 毫秒的 CAN 指令变化量，不是方向盘角速度。观察峰值与角度误差无法证明 EPS 硬体极限，不会用来提高控制上限或试探极限。目前只有桌面测试，仍需实车验证。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
