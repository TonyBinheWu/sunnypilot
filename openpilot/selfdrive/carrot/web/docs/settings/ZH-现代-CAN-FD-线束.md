<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_CANFD" param="CanfdHDA2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 现代 CAN-FD 线束

**菜单:** 车辆与硬件 \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdHDA2 -->
<a id="CanfdHDA2"></a>

## 现代 CAN-FD 线束

`CanfdHDA2`

启动时生效。可自动检测或选择实际连接的线束。

<!-- CARROT:AUTO:BEGIN CanfdHDA2 -->
<!-- CARROT:AUTO:SOURCE facts="3b7c615d1cb302e45c1e60749d96cec68d48356e74259fcf95a27c8a809a23e0" semantic="a4d30a9a469e9c7a3be9b5bb5943a92f33fce83e193ba0e774e932a8a536e295" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 自动检测 (`2`)
- **范围:** 摄像头 (HDA1) (`0`) ~ 自动检测 (`2`)
- **步长:** `1`
- **选项:** `0` 摄像头 (HDA1), `1` ADAS ECU (HDA2), `2` 自动检测
- **菜单:** 车辆与硬件 \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdHDA2 -->

<!-- CARROT:MANUAL:BEGIN CanfdHDA2 -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CanfdHDA2 -->

<!-- CARROT:SETTING:END CanfdHDA2 -->
