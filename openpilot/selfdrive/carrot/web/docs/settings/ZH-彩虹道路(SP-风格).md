<!-- CARROT:GENERATED schema="1" locale="zh" group="DISP_PATH" param="RainbowMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 彩虹道路（SP 风格）

**菜单:** 显示 \> 路径显示

---

<!-- CARROT:SETTING:BEGIN RainbowMode -->
<a id="RainbowMode"></a>

## 彩虹道路（SP 风格）

`RainbowMode`

横向控制启用时，在预测路径上显示 SP 风格的动态彩虹。0:关闭，1:开启。仅改变显示，不改变转向、速度或路径计算。无需重启。

<!-- CARROT:AUTO:BEGIN RainbowMode -->
<!-- CARROT:AUTO:SOURCE facts="5b7cf496ee33a101275e6ef0eea4f2772a24478e0de18004b76b0a89752bc384" semantic="1aba7ed0cb53ca634c206d22650345f906fe8d15486d15e502ccfad140063cfd" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 显示 \> 路径显示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RainbowMode -->

<!-- CARROT:MANUAL:BEGIN RainbowMode -->
<!-- CARROT:REVIEW reviewed-for="1aba7ed0cb53ca634c206d22650345f906fe8d15486d15e502ccfad140063cfd" reviewed-at="2026-11-15T15:32:12.239638+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 运作方式

开启后，横向控制启用时，机器预测路径会使用 SP 风格的动态彩虹渐变。关闭或横向控制未启用时，使用原有路径样式。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在机器的开关菜单操作，或在 Carrot Web / CarrotAssist 搜索 `RainbowMode`。C3/C3X 与 C4 不需要重启即可应用；关闭后恢复原有路径模式及颜色。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 补充说明

此功能只改变路径填色，不改变转向、巡航速度、模型输出或警示。网页 / APK 的彩虹显示另有 `vision_rainbow_lane` 设置。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END RainbowMode -->

<!-- CARROT:SETTING:END RainbowMode -->
