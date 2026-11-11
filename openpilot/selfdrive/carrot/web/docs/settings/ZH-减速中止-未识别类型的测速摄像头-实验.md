<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="VehicleNaviDecelCancelUnknown" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 减速中止：未识别类型的测速摄像头 \[实验\]

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelUnknown -->
<a id="VehicleNaviDecelCancelUnknown"></a>

## 减速中止：未识别类型的测速摄像头 \[实验\]

`VehicleNaviDecelCancelUnknown`

减速中止请求开启时，允许用巡航 + 键或轻踩油门中止原车导航测速警告中未收到或无法解析摄像头类型预告（CAN 未接收/未处理）的警告的减速（实验功能）。由于类型未知，可能包含无预告的闯红灯或测速摄像头，因此默认关闭，即使开启上级也需单独开启。30km/h 及以下的警告（儿童·老人保护区等）和区间测速中不适用。中止后若匹配到闯红灯、后向或固定预告，则遵循该类型的规则。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelUnknown -->
<!-- CARROT:AUTO:SOURCE facts="4bfda5573816aacceb0682298ff47912c6af2254890b31edddfb2c8b0f85f26b" semantic="bc790dfd91a22232bbc47f0077d136baa937beae69d660870e3b370ffa0052a7" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelUnknown -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelUnknown -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelUnknown -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelUnknown -->
