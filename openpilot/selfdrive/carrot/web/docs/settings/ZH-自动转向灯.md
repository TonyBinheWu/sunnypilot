<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="AutoBlinkerControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自动转向灯

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN AutoBlinkerControl -->
<a id="AutoBlinkerControl"></a>

## 自动转向灯

`AutoBlinkerControl`

0 蓝牙单次闪灯。模式 1 可在 5 km/h 以下保持驾驶人用蓝牙按钮开启的方向灯直到转弯完成。模式 2 另支持驾驶人明确发出的操作请求。同一按钮取消，另一侧按钮切换，原车拨杆优先。导航通过画面与声音提示。

<!-- CARROT:AUTO:BEGIN AutoBlinkerControl -->
<!-- CARROT:AUTO:SOURCE facts="1efb0e75f5f8a1f48c99802b372c588607866348f5cba3a80314c85bba8f1f63" semantic="6a1867189f6b090ec92c031c906f21c613b4aa48685d0feccb1587057093bf19" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `0`
- **范围:** `0` ~ `2`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoBlinkerControl -->

<!-- CARROT:MANUAL:BEGIN AutoBlinkerControl -->
<!-- CARROT:REVIEW reviewed-for="6a1867189f6b090ec92c031c906f21c613b4aa48685d0feccb1587057093bf19" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

0 蓝牙单次闪灯。模式 1 可在 5 km/h 以下保持驾驶人用蓝牙按钮开启的方向灯直到转弯完成。模式 2 另支持驾驶人明确发出的操作请求。同一按钮取消，另一侧按钮切换，原车拨杆优先。导航通过画面与声音提示。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoBlinkerControl -->

<!-- CARROT:SETTING:END AutoBlinkerControl -->
