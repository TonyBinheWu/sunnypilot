<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_GAP" param="TFollowDecelBoost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 减速时车距余量 (0%)

**菜单:** 驾驶控制 \> 巡航与车距 \> 车距

---

<!-- CARROT:SETTING:BEGIN TFollowDecelBoost -->
<a id="TFollowDecelBoost"></a>

## 减速时车距余量 (0%)

`TFollowDecelBoost`

根据减速强度在基础目标车距上只增加一次余量，持续减速时不会重复累加。数值越高余量越大，减速减弱时逐渐释放。0%关闭额外余量，已施加的余量会逐渐解除。减速时仍保留基础车距缩短暂停功能。

<!-- CARROT:AUTO:BEGIN TFollowDecelBoost -->
<!-- CARROT:AUTO:SOURCE facts="f1b36d3b21adc1cc90dfe82e0295417216866d9d8b56ad112c13ff035ad89950" semantic="a003496b606637110045bb4c8096e6fd7af91b9b8c2778f41be61772125c46ca" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0%`
- **范围:** `0%` ~ `100%`
- **步长:** `10`
- **显示单位:** `%`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 车距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowDecelBoost -->

<!-- CARROT:MANUAL:BEGIN TFollowDecelBoost -->
<!-- CARROT:REVIEW reviewed-for="a003496b606637110045bb4c8096e6fd7af91b9b8c2778f41be61772125c46ca" reviewed-at="2026-09-09T08:56:50.274086+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 工作方式

根据减速强度在基础目标车距上只增加一次余量，持续制动时不会重复累加。数值越高额外空间越大，数值越低越小。

减速减弱时逐渐释放额外余量，减速增强时及时更新。关闭设置后已施加的余量逐渐解除，但保留制动期间基础车距缩短暂停功能。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

用于调整减速时的车距余量，不改变基础跟车时间设置。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:MANUAL:END TFollowDecelBoost -->

<!-- CARROT:SETTING:END TFollowDecelBoost -->
