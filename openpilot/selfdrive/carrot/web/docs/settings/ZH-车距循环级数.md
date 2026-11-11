<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_GAP" param="CruiseGapLevels" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 车距循环级数

**菜单:** 驾驶控制 \> 巡航与车距 \> 车距

---

<!-- CARROT:SETTING:BEGIN CruiseGapLevels -->
<a id="CruiseGapLevels"></a>

## 车距循环级数

`CruiseGapLevels`

车距按钮循环的级数，可选2级至车辆支持的最大级数，默认使用车辆最大级数。2使用TF1和TF2，3使用TF1至TF3。下次按车距按钮时生效，保留未使用的TF和跟车响应性设置。仅在openpilot控制加减速时应用，不改变原厂ACC的级数。

<!-- CARROT:AUTO:BEGIN CruiseGapLevels -->
<!-- CARROT:AUTO:SOURCE facts="736f6efb1531c6aad1e6c71200636d1122d202e76b5fc90b302061c65024dccc" semantic="0b2beba3c4ae3136707b59ae19b20a500b34caf419dd7fc699481622c446c9e1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 4级 (`4`)
- **范围:** 2级 (`2`) ~ 4级 (`4`)
- **步长:** `1`
- **选项:** `2` 2级, `3` 3级, `4` 4级
- **菜单:** 驾驶控制 \> 巡航与车距 \> 车距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseGapLevels -->

<!-- CARROT:MANUAL:BEGIN CruiseGapLevels -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CruiseGapLevels -->

<!-- CARROT:SETTING:END CruiseGapLevels -->
