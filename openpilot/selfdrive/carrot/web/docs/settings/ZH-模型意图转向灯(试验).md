<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="ModelDesireIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 模型意图转向灯（试验）

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN ModelDesireIndicator -->
<a id="ModelDesireIndicator"></a>

## 模型意图转向灯（试验）

`ModelDesireIndicator`

重复确认模型转弯或变道概率至少50%，且优于直行和反方向时显示转向灯。转弯至少10km/h，变道至少30km/h，并要求横向控制激活；不新增自动转向请求。 默认关闭，仅支持Ioniq 5 PE、Jetson USB2CAN及自动转向灯模式1或2；实车验证另行进行。 在30 km/h及以上，若模型最近两个预测时点对同一方向变道的概率均不低于65%，且测得的两侧车道线位置都显示车辆正在向该侧靠近，也可请求转向灯。仅有预测不会触发，也不请求转向。 预测触发后，若分叉处车道变宽，但模型意图与实际移动仍一致，则保持同一请求。意图减弱或反向时结束分叉保持；巡航 CANCEL 会立即解除保持请求。

<!-- CARROT:AUTO:BEGIN ModelDesireIndicator -->
<!-- CARROT:AUTO:SOURCE facts="18a389ecaeeef9d8d4e2e220a8bc2c455328e2ca995ccd532361a3c316e4badc" semantic="85643599439e3e55d38ab927bf13b2d2b17ffa165c1e3dd5f7b7d003daaf5a6d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ModelDesireIndicator -->

<!-- CARROT:MANUAL:BEGIN ModelDesireIndicator -->
<!-- CARROT:REVIEW reviewed-for="85643599439e3e55d38ab927bf13b2d2b17ffa165c1e3dd5f7b7d003daaf5a6d" reviewed-at="2026-11-10T10:51:22.872838+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

横向控制激活时，重复确认模型明显占优的转弯或变道预测后显示信号。不改变既有ATC条件，也不新增转向请求。

同方向其他原因接续现有信号，不重复轻触。实际点灯及检出率需要另行验证。
手动及模型显示仅在请求时间、方向和拨杆计数一致时有限识别自身轻触反馈。反向输入、拨杆锁定或接收端检测到驾驶员介入时取消。先于发送完成应答的点灯反馈会短暂记忆，但保持仍须匹配应答；短暂发送期间同方向人工操作无法仅凭这些信息完全区分。

在30 km/h及以上，若模型最近两个预测时点对同一方向变道的概率均不低于65%，且测得的两侧车道线位置都显示车辆正在向该侧靠近，也可请求转向灯。仅有预测不会触发，也不请求转向。

预测触发后，若分叉处车道变宽，但模型意图与实际移动仍一致，则保持同一请求。意图减弱或反向时结束分叉保持；巡航 CANCEL 会立即解除保持请求。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ModelDesireIndicator -->

<!-- CARROT:SETTING:END ModelDesireIndicator -->
