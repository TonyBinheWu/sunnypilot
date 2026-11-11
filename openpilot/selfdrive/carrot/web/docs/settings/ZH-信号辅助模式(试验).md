<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_TRAFFIC" param="SignalAssistMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 信号辅助模式（试验）

**菜单:** 驾驶控制 \> 速度与减速 \> 信号灯

---

<!-- CARROT:SETTING:BEGIN SignalAssistMode -->
<a id="SignalAssistMode"></a>

## 信号辅助模式（试验）

`SignalAssistMode`

0:关闭识别、显示及控制。1:行驶中持续显示识别结果，提供提醒及停车时红灯起步限制。2:在1的基础上增加行驶中减速准备；确认有效红灯且50米以内没有前车时逐渐请求约-0.5m/s²。任一跟踪前车进入50米以内则取消辅助减速，保留原有跟车。停车后与模式1相同，辅助减速不直接要求停车。停车红灯起步限制仅在5km/h及以下保留，超过该速度后清除此前的停车记忆。夜间需要两个红灯及道路方向支持；红灯证据消失或绿灯冲突时取消准备。显示与控制介入独立，旧结果最多暗显2秒后转为未知。与主模型独立，试验功能仍可能误检或漏检。

<!-- CARROT:AUTO:BEGIN SignalAssistMode -->
<!-- CARROT:AUTO:SOURCE facts="6cb3695ccc37add6ce4a5eac832f3193d32637a0def9f2fdbf20841d1b2e7803" semantic="ba8119151eab7971db5323d2e70e29e83140178360a67bae13fb690b0084d730" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `0`
- **范围:** `0` ~ `2`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 信号灯
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SignalAssistMode -->

<!-- CARROT:MANUAL:BEGIN SignalAssistMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END SignalAssistMode -->

<!-- CARROT:SETTING:END SignalAssistMode -->
