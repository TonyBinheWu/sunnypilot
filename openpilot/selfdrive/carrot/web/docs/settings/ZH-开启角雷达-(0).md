<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_RADAR" param="EnableCornerRadar" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 开启角雷达 (0)

**菜单:** 车辆与硬件 \> 雷达

---

<!-- CARROT:SETTING:BEGIN EnableCornerRadar -->
<a id="EnableCornerRadar"></a>

## 开启角雷达 (0)

`EnableCornerRadar`

1: 开启角雷达, 2: CCNC 车辆的切入检测

<!-- CARROT:AUTO:BEGIN EnableCornerRadar -->
<!-- CARROT:AUTO:SOURCE facts="4e0a01f35c9c9604da0eb04f87f4176525f446f3491c66c12d94935f0509c79c" semantic="f3344cc43f62d863ecb64a7db5ee5dc1890061598ea1a111001723780943390c" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `0`
- **范围:** `0` ~ `2`
- **步长:** `1`
- **菜单:** 车辆与硬件 \> 雷达
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END EnableCornerRadar -->

<!-- CARROT:MANUAL:BEGIN EnableCornerRadar -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 工作方式

EV6 HDA2 由 openpilot 控制纵向时，两种启用选项都能用角雷达连续确认的相邻车道移动目标补上仪表左前或右前的空位。后方位置采用原厂观测。使用原厂巡航时，仪表沿用原厂显示。

<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END EnableCornerRadar -->

<!-- CARROT:SETTING:END EnableCornerRadar -->
