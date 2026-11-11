<!-- CARROT:GENERATED schema="1" locale="zh" group="DISP_BRIGHT" param="ShowModelView" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 行车画面布局(C4)

**菜单:** 显示 \> 亮度与视图

---

<!-- CARROT:SETTING:BEGIN ShowModelView -->
<a id="ShowModelView"></a>

## 行车画面布局(C4)

`ShowModelView`

选择 C4 行车画面的摄像头视频和车道线/行驶路径图形。车道线/路径图形包含前车标记。 不受亮度设置影响，行车中更改后约 5 秒内生效。 即使隐藏两者，速度和警告仍会显示。连接外部 HUD 时，优先遵循“外部 HUD 连接时本机摄像头”设置。

<!-- CARROT:AUTO:BEGIN ShowModelView -->
<!-- CARROT:AUTO:SOURCE facts="63b460484c28053848be260ebb13b077f48b9f83e8d18781710f836ee79e5352" semantic="0fbb289950310b907ca1e85a973172fac18f0381fcd7718d1a6f3ebf584a61ce" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 0 摄像头 + 车道线/路径 (`0`)
- **范围:** 0 摄像头 + 车道线/路径 (`0`) ~ 3 隐藏两者 (`3`)
- **步长:** `1`
- **选项:** `0` 0 摄像头 + 车道线/路径, `1` 1 仅摄像头, `2` 2 仅车道线/路径, `3` 3 隐藏两者
- **菜单:** 显示 \> 亮度与视图
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowModelView -->

<!-- CARROT:MANUAL:BEGIN ShowModelView -->
<!-- CARROT:REVIEW reviewed-for="c8040075196baa91f6b37ffa483d6e1197e44f8bd97dd6bfca9c50ab762b41de" reviewed-at="2026-10-08T09:28:59.208385+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 动作

选择 C4 行车画面的视频和图形。车道线/路径图形包含前车标记。

- `0` — 在摄像头视频上显示车道线/路径。
- `1` — 仅显示摄像头视频。
- `2` — 在黑色背景上显示车道线/路径。
- `3` — 隐藏视频和车道线/路径，速度、警告和驾驶员状态仍会显示。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

不受亮度设置影响，进入行车模式后无需额外等待。行车中更改后约五秒内生效，无需重启。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

不适用于 C3/C3X。连接外部 HUD 且 `ShowCameraWithCluster=0` 时，无论此处如何选择，本机摄像头视频和车道线/路径都会隐藏。

不改变摄像头拍摄、驾驶判断或车辆控制。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ShowModelView -->

<!-- CARROT:SETTING:END ShowModelView -->
