<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="ModelPathIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 模型路径转向灯（试验）

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN ModelPathIndicator -->
<a id="ModelPathIndicator"></a>

## 模型路径转向灯（试验）

`ModelPathIndicator`

车速至少30km/h，模型未来1至3秒路径持续越过弯曲车道边界，且控制曲率方向一致时显示转向灯。要求目标线置信度至少10%、连续边界及重复观测。排除左侧中央线及右侧道路边缘，不新增自动转向请求。 默认关闭，仅支持Ioniq 5 PE、Jetson USB2CAN及自动转向灯模式1或2；实车验证另行进行。

<!-- CARROT:AUTO:BEGIN ModelPathIndicator -->
<!-- CARROT:AUTO:SOURCE facts="d221cc76331799935492a0304a2a0d9705635f3f1bd8620105befe111d27e8cc" semantic="09c4851f68312e9070186bb23698703b51d5b7dce50dbeca5e9cb4cf5626b6c8" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ModelPathIndicator -->

<!-- CARROT:MANUAL:BEGIN ModelPathIndicator -->
<!-- CARROT:REVIEW reviewed-for="09c4851f68312e9070186bb23698703b51d5b7dce50dbeca5e9cb4cf5626b6c8" reviewed-at="2026-11-01T04:38:46.048274+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

在相同前方位置比较模型路径与弯曲边界，检测持续越线。要求目标线置信度至少10%、连续几何、重复观测，以及相对道路曲率一致的控制方向。

仅重新识别车道线不会产生新请求，生成的信号不会请求转向。宽路肩及路口仍存在边界估计局限。
手动及模型显示仅在请求时间、方向和拨杆计数一致时有限识别自身轻触反馈。反向输入、拨杆锁定或接收端检测到驾驶员介入时取消。先于发送完成应答的点灯反馈会短暂记忆，但保持仍须匹配应答；短暂发送期间同方向人工操作无法仅凭这些信息完全区分。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ModelPathIndicator -->

<!-- CARROT:SETTING:END ModelPathIndicator -->
