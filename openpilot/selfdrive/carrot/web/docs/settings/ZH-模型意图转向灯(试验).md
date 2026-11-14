<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="ModelDesireIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 模型意图转向灯（试验）

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN ModelDesireIndicator -->
<a id="ModelDesireIndicator"></a>

## 模型意图转向灯（试验）

`ModelDesireIndicator`

重复确认模型转弯或变道概率至少50%，且优于直行和反方向时显示转向灯。转弯至少10km/h，变道至少30km/h，并要求横向控制激活；不新增自动转向请求。 默认关闭，仅支持Ioniq 5 PE、Jetson USB2CAN及自动转向灯模式1或2；实车验证另行进行。 在30 km/h及以上，若模型最近两个预测时点对同一方向变道的概率均不低于65%，且测得的两侧车道线位置都显示车辆正在向该侧靠近，也可请求转向灯。仅有预测不会触发，也不请求转向。 预测触发后，若分叉处车道变宽，但模型意图与实际移动仍一致，则保持同一请求。意图减弱或反向时结束分叉保持；巡航 CANCEL 会立即解除保持请求。 模型转弯指示还要求同向转角至少15度及实际车身旋转至少3度/秒。行驶中转弯概率低于30%且方向盘在±10度内稳定0.4秒后结束保持。

<!-- CARROT:AUTO:BEGIN ModelDesireIndicator -->
<!-- CARROT:AUTO:SOURCE facts="7cef9fbf6d0c1a9e920d6acc051469d924e9cf25cf203e11506b9dcda6f746be" semantic="d73f84bcf6ba7064705bfb722d8a81eb4a2d19fa2936d3d3e21fe478a59c63b5" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ModelDesireIndicator -->

<!-- CARROT:MANUAL:BEGIN ModelDesireIndicator -->
<!-- CARROT:REVIEW reviewed-for="d73f84bcf6ba7064705bfb722d8a81eb4a2d19fa2936d3d3e21fe478a59c63b5" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

横向控制激活时，重复确认模型明显占优的转弯或变道预测后显示信号。不改变既有ATC条件，也不新增转向请求。

同方向其他原因接续现有信号，不重复轻触。实际点灯及检出率需要另行验证。
手动及模型显示仅在请求时间、方向和拨杆计数一致时有限识别自身轻触反馈。反向输入、拨杆锁定或接收端检测到驾驶员介入时取消。先于发送完成应答的点灯反馈会短暂记忆，但保持仍须匹配应答；短暂发送期间同方向人工操作无法仅凭这些信息完全区分。

在30 km/h及以上，若模型最近两个预测时点对同一方向变道的概率均不低于65%，且测得的两侧车道线位置都显示车辆正在向该侧靠近，也可请求转向灯。仅有预测不会触发，也不请求转向。

预测触发后，若分叉处车道变宽，但模型意图与实际移动仍一致，则保持同一请求。意图减弱或反向时结束分叉保持；巡航 CANCEL 会立即解除保持请求。
模型转弯点灯另须同方向转角至少15度，及新鲜实测车身旋转至少每秒3度。行进中，转弯概率低于30%且方向盘回到正负10度内稳定0.4秒时，即使尚未达到原30度峰值，也可结束保持。

B1 第5版允许已确认的自身轻触回讯持续穿过闪灯的熄灭间隔。轻触结束后收到中立回讯即关闭此允许，后续拨杆回讯会取消所有权；反侧灯、原始驾驶员输入、CAN异常及租约到期仍会取消。软件回放不代表实际保持或取消性能验收。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ModelDesireIndicator -->

<!-- CARROT:SETTING:END ModelDesireIndicator -->
