<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_GAP" param="CruiseGapLevels" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 車距迴圈級數

**選單:** 駕駛控制 \> 巡航與車距 \> 車距

---

<!-- CARROT:SETTING:BEGIN CruiseGapLevels -->
<a id="CruiseGapLevels"></a>

## 車距迴圈級數

`CruiseGapLevels`

車距按鈕迴圈的級數，可選2級至車輛支援的最大級數，預設使用車輛最大級數。2使用TF1和TF2，3使用TF1至TF3。下次按車距按鈕時生效，保留未使用的TF和跟車響應性設定。僅在openpilot控制加減速時應用，不改變原廠ACC的級數。

<!-- CARROT:AUTO:BEGIN CruiseGapLevels -->
<!-- CARROT:AUTO:SOURCE facts="85d4dad7514e3c3657383c8910e12c67a9fb4286738edc547c893e0ed48811e1" semantic="0b2beba3c4ae3136707b59ae19b20a500b34caf419dd7fc699481622c446c9e1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 4級 (`4`)
- **範圍:** 2級 (`2`) ~ 4級 (`4`)
- **步長:** `1`
- **選項:** `2` 2級, `3` 3級, `4` 4級
- **選單:** 駕駛控制 \> 巡航與車距 \> 車距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseGapLevels -->

<!-- CARROT:MANUAL:BEGIN CruiseGapLevels -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CruiseGapLevels -->

<!-- CARROT:SETTING:END CruiseGapLevels -->
