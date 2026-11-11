<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_TORQUE_COEFF" param="NNFF" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# NNFF 扭矩控制

**菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 扭矩系数

---

<!-- CARROT:SETTING:BEGIN NNFF -->
<a id="NNFF"></a>

## NNFF 扭矩控制

`NNFF`

用于扭矩转向的神经网络前馈选项。开启后，非转角控制车辆使用扭矩控制调校，并在有匹配模型时应用 NNFF。支持 comma 自有 NNFF 的车型仍优先使用原有路径。关闭仅停用此 NNFF 选项，不改变 NNFFLite。默认关闭，仅在 Carrot Web 搜索中显示。更改在下次进入行车模式或设备重启后生效。不适用于转角控制车辆。

<!-- CARROT:AUTO:BEGIN NNFF -->
<!-- CARROT:AUTO:SOURCE facts="24ed81a6d63a2ee8a46a37619c165a44888a3867cc1de2eee92ba5b229ea82c7" semantic="bf1b67050f021288a3be062698bf0689878aedc8c326f0f30176feec716d40f2" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 扭矩系数
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END NNFF -->

<!-- CARROT:MANUAL:BEGIN NNFF -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END NNFF -->

<!-- CARROT:SETTING:END NNFF -->
