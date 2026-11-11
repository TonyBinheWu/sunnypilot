<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_AUX" param="SpeedFromPCM" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 来自 PCM 的速度 (原厂 SCC)

**菜单:** 车辆与硬件 \> 车辆辅助

---

<!-- CARROT:SETTING:BEGIN SpeedFromPCM -->
<a id="SpeedFromPCM"></a>

## 来自 PCM 的速度 (原厂 SCC)

`SpeedFromPCM`

PCM 车辆速度控制。0: 弯道/摄像头减速 + 纵向控制，1: 使用原厂设定速度且不连续发送按钮，2: 弯道/摄像头减速，3: 本田/丰田（丰田/雷克萨斯使用原厂设定速度，不切换纵向控制模式）

<!-- CARROT:AUTO:BEGIN SpeedFromPCM -->
<!-- CARROT:AUTO:SOURCE facts="6ff393b538dcd40de57b609d12f24cb962c10671e9e6a8b33f48024101af66c7" semantic="826f2d40ddf5f91d56d0f427bee488abab5c3cb4e0d0c3487843d985b45560cc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `2`
- **范围:** `0` ~ `3`
- **步长:** `1`
- **菜单:** 车辆与硬件 \> 车辆辅助
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SpeedFromPCM -->

<!-- CARROT:MANUAL:BEGIN SpeedFromPCM -->
<!-- CARROT:REVIEW reviewed-for="826f2d40ddf5f91d56d0f427bee488abab5c3cb4e0d0c3487843d985b45560cc" reviewed-at="2026-10-09T18:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### ??

丰田/雷克萨斯的 `3` 使用原厂 SET/RES 设定速度作为基本控制目标，并显示原厂仪表设定速度。`1` 也使用原厂设定速度；`0` 和 `2` 保留现有 Carrot 速度选择。本田的 `3` 行为不变。此设置本身不切换纵向控制器或雷达可用性。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END SpeedFromPCM -->

<!-- CARROT:SETTING:END SpeedFromPCM -->
