<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 低速需求跟随与反应记录

**菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## 低速需求跟随与反应记录

`LowSpeedSteerReserve`

仅 Hyundai/Kia CAN-FD 力矩控制。持续需求 0.30 秒后，≤30 km/h 按需提供最高 409，指令增加/减少速率依需求最高 4/4（每 10 毫秒）。30–40 渐退；≥40 使用车型默认比例与 2/3。保留手动值与学习参数；记录不会提高上限。需更新 Panda 韧体并重启，尚待实车验证。

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="56fb1c4c72d5f4f2e308e58aca3d3c4e083d905a7f1fce6234dd7619fad8b8ed" semantic="861e9b50486d57aed386bb0c56462a4991e79e31206164c4e0af7c8737bc3700" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:REVIEW reviewed-for="861e9b50486d57aed386bb0c56462a4991e79e31206164c4e0af7c8737bc3700" reviewed-at="2026-11-17T15:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 运作方式

仅支援 Hyundai／Kia CAN-FD 扭力转向。需求接近预设上限并持续 0.30 秒后，≤30 km/h 可依需求提供最高 409。控制器也依「允许的需求指令与目前输出之差」选择指令增加／减少速率，从预设 2／3 到最高 4／4 个 CAN 单位／每 10 毫秒；接近目标时回到预设速率。扭力余量与额外速率都在 30–40 km/h 渐退；整数指令采离散级距，≥40 km/h 使用车型预设比例与速率。

储存的 CustomSteerMax 与 CustomSteerDelta 不会被覆写，开启时以车型预设换算比例为基准。关闭后恢复手动值，但超出 Panda 已恢复执行的限制之指令会遭拒绝。本功能不增加控制增益、即时扭力学习值或角度控制权限。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

请停车更新并完成重新启动，让新版 Panda 韧体与安全参数载入。选用开关仍位于 CustomSteerMax 下方、预设关闭；完成此次更新后，开关约 0.5 秒内读取，不需再次重新启动。机器「设备 > 转向学习进度」与网页／APK「工具 > 转向学习进度」可查看目前指令、所选速率、目标／实际方向盘角度及转动速率、受限原因与左右指令期间的观察峰值。

即时状态超过 2 秒标示过期。本机历史汇总只载入相同车型／控制类型，每 60 秒或退出时储存；此记录器不收集位置、行程或上传云端。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 补充说明

驾驶接管、CAN 无效、转向故障、倒车／静止、模型过期或退出横向控制都会取消余量资格。Panda 以独立接收且通过 CRC／计数器检查的新鲜轮速与驾驶资料限制增加速率；缺少／过期资料不能授权额外速率。既有 112 单位／250 毫秒即时变化限制、请求位元及驾驶让步检查均恢复执行，包含接收节奏转送的替代指令；保留接管时迅速释放转向力的路径。

CAN 指令变化率不是牛顿米，也不是实际方向盘角速度。观察峰值不会被当成硬体极限或用来提高上限，也不会试探物理极限。桌面／原生测试不能证明实车能力，请参阅[验证范围与既有测试失败](https://github.com/TonyBinheWu/sunnypilot/blob/carrot-wip/docs/LOW_SPEED_STEERING_SAFETY.zh-TW.md)。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
