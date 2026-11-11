<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_DM" param="MuteDoor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 遮蔽車門感應

**選單:** 車輛與硬體 \> 駕駛員監控

---

<!-- CARROT:SETTING:BEGIN MuteDoor -->
<a id="MuteDoor"></a>

## 遮蔽車門感應

`MuteDoor`

遮蔽車門感應

<!-- CARROT:AUTO:BEGIN MuteDoor -->
<!-- CARROT:AUTO:SOURCE facts="c6774a9743f327df3474786786540f2e6f21453d65a0c2c660b8bc32f9e63b6c" semantic="2e4b627828fbc876d79a4469748d14cb1cd2ea8824c9f737817ecc770bcaf8db" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 車輛與硬體 \> 駕駛員監控
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MuteDoor -->

<!-- CARROT:MANUAL:BEGIN MuteDoor -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- **開啟：** 不將車門開啟狀態列為阻擋駕駛輔助運作的事件。
- **關閉：** 車門開啟時產生車門開啟事件。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

停妥後變更，並於下次行車確認駕駛監控及車輛警示狀態。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 啟用後，車門開啟狀態不會列為阻擋駕駛輔助運作的事件。起步前請自行確認所有車門已關妥。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MuteDoor -->

<!-- CARROT:SETTING:END MuteDoor -->
