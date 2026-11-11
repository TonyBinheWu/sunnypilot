<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_DM" param="MuteSeatbelt" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 遮蔽安全帶感應

**選單:** 車輛與硬體 \> 駕駛員監控

---

<!-- CARROT:SETTING:BEGIN MuteSeatbelt -->
<a id="MuteSeatbelt"></a>

## 遮蔽安全帶感應

`MuteSeatbelt`

遮蔽安全帶感應

<!-- CARROT:AUTO:BEGIN MuteSeatbelt -->
<!-- CARROT:AUTO:SOURCE facts="31d5d7943b573e239054f6702454da2ba75b29976b8462d460bb913c6787e4f8" semantic="1ebf5b7d58dbd61bfd90f74ebd2f43ac41e416f817f1109e30249922d3cd775e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 車輛與硬體 \> 駕駛員監控
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MuteSeatbelt -->

<!-- CARROT:MANUAL:BEGIN MuteSeatbelt -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- **開啟：** 不將安全帶未扣狀態列為阻擋駕駛輔助運作的事件。
- **關閉：** 安全帶未扣妥時產生安全帶未扣事件。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

停妥後變更，並於下次行車確認駕駛監控及車輛警示狀態。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 啟用後，安全帶未扣狀態不會列為阻擋駕駛輔助運作的事件。請自行確認所有乘員都已繫妥安全帶。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MuteSeatbelt -->

<!-- CARROT:SETTING:END MuteSeatbelt -->
