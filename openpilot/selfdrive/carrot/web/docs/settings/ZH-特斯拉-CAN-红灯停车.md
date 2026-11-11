<!-- CARROT:GENERATED schema="1" locale="zh" group="BASIC_START" param="TeslaCanTrafficStop" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉 CAN 红灯停车

**菜单:** 驾驶控制 \> 启动·自动 \> 起步动作

---

<!-- CARROT:SETTING:BEGIN TeslaCanTrafficStop -->
<a id="TeslaCanTrafficStop"></a>

## 特斯拉 CAN 红灯停车

`TeslaCanTrafficStop`

默认关闭，修改后重启。仅 Tesla Model 3/Y 且 openpilot 纵向已激活时，使用新鲜 APP\_trafficControl 红灯及小于126米的停止线补充停车约束。仅支持8字节、米制、视觉来源协议，拒绝6字节 DAS\_road。绿灯只解除本约束，不覆盖其他障碍和人工停车。近距离变红可能超出制动能力；信号丢失或距离不一致会提示接管并请求既有软退出。需核对实车协议和距离参考点，并在封闭场地验证，不代表已通过道路验收。

<!-- CARROT:AUTO:BEGIN TeslaCanTrafficStop -->
<!-- CARROT:AUTO:SOURCE facts="51ef6fd35dac41fd4bca7eea57db084c388d3291a52ea924f03841f1deda44da" semantic="046215718bed37d52f0c6633e5d551de2ff163be2a341b1cb647fab8b5f803dc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 启动·自动 \> 起步动作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaCanTrafficStop -->

<!-- CARROT:MANUAL:BEGIN TeslaCanTrafficStop -->
<!-- CARROT:REVIEW reviewed-for="046215718bed37d52f0c6633e5d551de2ff163be2a341b1cb647fab8b5f803dc" reviewed-at="2026-11-08T01:13:19.667172+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

开启后仅在 Model 3/Y 实际 openpilot 纵向激活时补充停车，关闭保留原行为。3次不同红灯跨越0.2秒且正停止线小于126米，在 ACC/blended 添加约束；同一目标3次连续绿灯跨越0.5秒，仅解除此约束。CAN 停车期间 blended 临时使用 ACC 求解，保留更强模型制动，解除后恢复原模式。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

修改后重启，独立于打灯、数据共享及信号辅助。仅接受严格8字节、米制、视觉来源 APP_trafficControl，拒绝6字节 DAS_road。踩踏板后需退出并重新接入、等待新观测；其他车型忽略此开关。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

先在封闭场地核对原始 CAN、行驶方向适用性及暂定2米停车余量。近距离变红可能超出制动能力；信号超过0.5秒未更新或目标跳变会请求接管和最终解除控制的软退出，驾驶员必须制动。不增加 Panda 权限，不代表道路验收。详见源码仓库 docs/user/zh/tesla.md。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaCanTrafficStop -->

<!-- CARROT:SETTING:END TeslaCanTrafficStop -->
