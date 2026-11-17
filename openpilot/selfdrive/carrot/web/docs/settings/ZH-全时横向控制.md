<!-- CARROT:GENERATED schema="1" locale="zh" group="BASIC_START" param="AlwaysLateral" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 全时横向控制

**菜单:** 驾驶控制 \> 启动·自动 \> 起步动作

---

<!-- CARROT:SETTING:BEGIN AlwaysLateral -->
<a id="AlwaysLateral"></a>

## 全时横向控制

`AlwaysLateral`

即使巡航未激活，也允许横向控制。 系统启动后，首次确认所需输入就绪前不执行转向。一旦通过，此启动检查不再阻断；现有行驶中安全处理保持不变。 Tesla 在实际静止时可以转向；低速移动时仍遵守最低转向速度限制。 有车辆 CAN 扩展的 Tesla，每次独立三指触屏立即切换此设置，不再切换实验模式。关闭不等于解除已激活巡航中的转向控制。 确认持续的 CAN 控制器错误或反复出现的 Casper 前方安全系统故障时，会发出警报并停止全时转向；故障解除前不能重新启用。 0: 关闭, 1: 开启 Hyundai／Kia CAN-FD 会在启动时另行载入 Panda 全时横向控制授权。若启动时为关闭，改为开启后须停车重新启动；关闭时主机仍立即停止全时转向。巡航未启用时，Panda 也会确认轮速／驾驶扭力接收资料未超过 100 毫秒。Tesla 的即时切换维持原样。

<!-- CARROT:AUTO:BEGIN AlwaysLateral -->
<!-- CARROT:AUTO:SOURCE facts="b21c36de8ec26a46af3b24105c8b2fb3376876d951da5cc1bcc72c0a3ceefd3d" semantic="0dd1642d4ae06bd0308b3ae7e3b892138a13022b1d17d05aff0df4a2a40d5c08" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 启动·自动 \> 起步动作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AlwaysLateral -->

<!-- CARROT:MANUAL:BEGIN AlwaysLateral -->
<!-- CARROT:REVIEW reviewed-for="0dd1642d4ae06bd0308b3ae7e3b892138a13022b1d17d05aff0df4a2a40d5c08" reviewed-at="2026-11-17T15:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 工作方式

- **开启：** 前进挡且横向控制已启用时，巡航关闭或行驶中踩刹车取消巡航后仍可转向。
- **关闭：** 仅在驾驶控制激活时转向。

此设置不改变加速或制动，也不会自行开启横向控制。
支持的 Tesla 车型在前进挡且横向控制已启用时，完全静止也可保持转向控制。车辆移动时仍受最低转向速度限制；转向故障或横向控制关闭时不会转向。

系统启动后，首次确认模型、车辆参数、姿态等必需输入有效且就绪前，不允许转向。一旦通过，此启动检查即结束；之后的输入暂时异常或横向控制关闭再开启，不会重新触发该检查。现有行驶中安全处理保持不变。启动等待时间结束本身不能通过此检查。
确认持续的 CAN 控制器错误或反复出现的 Casper 前方安全系统故障时，会发出警报并停止全时转向；故障解除前不能重新启用。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AlwaysLateral -->

<!-- CARROT:SETTING:END AlwaysLateral -->
