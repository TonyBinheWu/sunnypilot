<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="AutoNaviCountDownMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 导航倒计时模式

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN AutoNaviCountDownMode -->
<a id="AutoNaviCountDownMode"></a>

## 导航倒计时模式

`AutoNaviCountDownMode`

外部导航连接期间仅使用外部导航距离，否则使用原车导航距离。连接状态变化时重置之前的倒计时。 0: 不使用, 1: 转向点 + 速度, 2: 转向点 + 速度 + 减速带

<!-- CARROT:AUTO:BEGIN AutoNaviCountDownMode -->
<!-- CARROT:AUTO:SOURCE facts="f247027461b6ac07dc493f1eb4076a6b10da9611f5b9193ea7430e0ed3e2e099" semantic="164adc98b3573e2f4d0ea6aa380a9920ed4d56a1dc37b6bdf056a7ae5f0de063" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `2`
- **范围:** `0` ~ `2`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviCountDownMode -->

<!-- CARROT:MANUAL:BEGIN AutoNaviCountDownMode -->
<!-- CARROT:REVIEW reviewed-for="164adc98b3573e2f4d0ea6aa380a9920ed4d56a1dc37b6bdf056a7ae5f0de063" reviewed-at="2026-09-13T07:52:41.385068+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

外部导航连接期间仅使用外部导航，即使没有当前引导项目也不使用原车导航。确认断开连接或接收超时后，按各项设置恢复使用原车导航。

0关闭提醒；1包含转向点和速度事件；2还包含减速带。连接期间仅使用外部距离，否则使用原车距离，连接切换时重置之前的倒计时。不改变减速时机或强度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同时检查外部导航连接状态以及显示的事件类型和剩余距离。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoNaviCountDownMode -->

<!-- CARROT:SETTING:END AutoNaviCountDownMode -->
