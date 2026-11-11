<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="ManualLaneChangeIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 手动变道转向灯（试验）

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN ManualLaneChangeIndicator -->
<a id="ManualLaneChangeIndicator"></a>

## 手动变道转向灯（试验）

`ManualLaneChangeIndicator`

车速至少5km/h，确认同方向转向0.15秒后，松手或短暂反向施力但仍接近边界时最多保留意图1.5秒；停止接近超过0.3秒、回退超过0.15米或单次跟踪超过4秒则取消。左侧通过新鲜的原车白线分类排除中央线，黄色、未知或过期分类阻止触发。右侧仅要求当前及前方的目标车道线至道路边缘距离至少2.5米；不使用外侧车道线概率、相邻车道宽度或道路边缘标准差。宽路肩也可能满足距离条件。 独立于ATC及右转距离选项，不请求自动转向。默认关闭，仅支持Ioniq 5 PE、Jetson USB2CAN及自动转向灯模式1或2。再次请求须间隔3秒且连续熄灯1秒，自动转向反馈隔离至少12秒。不能保证真实车道或安全间距，修改后仍需实车验证。 开始接近时确认目标线置信度至少10%，连续接近最多跟踪4秒。请求后跟踪完成、返回或输入失效，最长12秒；不能保证原车轻触闪灯立即熄灭。 根据测得的车道边界接近速度预测0.3秒后的位置，提前请求转向灯。车体中心至边界的距离阈值从0.9米最多提前至1.2米，仍要求至少0.15米实际接近、驾驶员意图及两侧边界一致移动。

<!-- CARROT:AUTO:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:AUTO:SOURCE facts="fd6db5c0b6ff7bcfdad2dca25d2d2e07209ca9fd9ed7ef548a17a09f993cea61" semantic="e2259bfc81f439587e99cd8f87f9640f16cb2ddb370571afbfd23611dc2f1d7f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ManualLaneChangeIndicator -->

<!-- CARROT:MANUAL:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:REVIEW reviewed-for="e2259bfc81f439587e99cd8f87f9640f16cb2ddb370571afbfd23611dc2f1d7f" reviewed-at="2026-11-08T22:13:25+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

结合近期驾驶员转向意图与连续边界接近进行显示。开始时确认目标线置信度至少10%，并应用左侧中央线和右侧道路边缘排除条件。

请求后跟踪完成、返回及输入失效，不请求自动转向。保持请求结束后原车轻触闪灯仍可能继续。
根据测得的车道边界接近速度预测0.3秒后的位置，提前请求转向灯。车体中心至边界的距离阈值从0.9米最多提前至1.2米，仍要求至少0.15米实际接近、驾驶员意图及两侧边界一致移动。

手动及模型显示仅在请求时间、方向和拨杆计数一致时有限识别自身轻触反馈。反向输入、拨杆锁定或接收端检测到驾驶员介入时取消。先于发送完成应答的点灯反馈会短暂记忆，但保持仍须匹配应答；短暂发送期间同方向人工操作无法仅凭这些信息完全区分。
车速达到5公里/小时且检测到驾驶员转向并实际靠近相邻车道线时，可请求对应方向的转向灯。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ManualLaneChangeIndicator -->

<!-- CARROT:SETTING:END ManualLaneChangeIndicator -->
