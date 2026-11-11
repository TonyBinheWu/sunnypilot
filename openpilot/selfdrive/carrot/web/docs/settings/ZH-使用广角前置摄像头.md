<!-- CARROT:GENERATED schema="1" locale="zh" group="SYS_CAMERA" param="UseWideCamera" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 使用广角前置摄像头

**菜单:** 系统 \> 摄像头

---

<!-- CARROT:SETTING:BEGIN UseWideCamera -->
<a id="UseWideCamera"></a>

## 使用广角前置摄像头

`UseWideCamera`

默认开启。仅在广角前置摄像头故障的设备上关闭。关闭后，camerad 会将广角摄像头排除在同步之外，modeld 会将普通前置摄像头画面复用于两个模型输入。摄像范围和模型性能可能会变化。更改后请重启设备。

<!-- CARROT:AUTO:BEGIN UseWideCamera -->
<!-- CARROT:AUTO:SOURCE facts="89bf2275fc0668c17a336c1ffcd87d825352f96506e03a74f7860860bea435a5" semantic="98f6143429525738b1a1748e10af5089802e78c1eeeb632ec050ee74ca08fd18" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `1`
- **范围:** `0` ~ `1`
- **菜单:** 系统 \> 摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseWideCamera -->

<!-- CARROT:MANUAL:BEGIN UseWideCamera -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END UseWideCamera -->

<!-- CARROT:SETTING:END UseWideCamera -->
