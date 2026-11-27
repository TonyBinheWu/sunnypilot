<!-- CARROT:GENERATED schema="1" locale="zh" group="DAILY_DRIVING" param="DynamicExperimentalControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 动态实验模式控制（DEC）

**菜单:** 驾驶控制 \> 启动·自动 \> 日常驾驶

---

<!-- CARROT:SETTING:BEGIN DynamicExperimentalControl -->
<a id="DynamicExperimentalControl"></a>

## 动态实验模式控制（DEC）

`DynamicExperimentalControl`

使用 openpilot 纵向控制时，下次行程生效。默认关闭，确认前方无车后由模型在巡航上限内决定加速度。开启后依路况切换巡航跟车与模型协同。

<!-- CARROT:AUTO:BEGIN DynamicExperimentalControl -->
<!-- CARROT:AUTO:SOURCE facts="3ba642a647ee45f1e9a2d617fca928e4dfc801ddfcf25bbcec61255761ba0a3f" semantic="812cd842d2e82c6f1efab61b169f7a27f6ca8a20c4399a0143bf5fb7f7405fcd" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 启动·自动 \> 日常驾驶
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DynamicExperimentalControl -->

<!-- CARROT:MANUAL:BEGIN DynamicExperimentalControl -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END DynamicExperimentalControl -->

<!-- CARROT:SETTING:END DynamicExperimentalControl -->
