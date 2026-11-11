<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_START" param="DisableMinSteerSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 解除最小轉向速度限制

**選單:** 駕駛控制 \> 啟動·自動 \> 起步動作

---

<!-- CARROT:SETTING:BEGIN DisableMinSteerSpeed -->
<a id="DisableMinSteerSpeed"></a>

## 解除最小轉向速度限制

`DisableMinSteerSpeed`

配備 smdps: 1

<!-- CARROT:AUTO:BEGIN DisableMinSteerSpeed -->
<!-- CARROT:AUTO:SOURCE facts="fc7887545e4c963c0897a5c3076d9b01f86ca58c28a7d2a2379ac9922db62d42" semantic="1e8fdd77dce60e211fb436b62a63f37b43a57d55ab7b465a438ac1459fdc1ca3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 啟動·自動 \> 起步動作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DisableMinSteerSpeed -->

<!-- CARROT:MANUAL:BEGIN DisableMinSteerSpeed -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- **開啟：** 將車輛介面的最低輔助轉向速度改為 `0`。
- **關閉：** 保留該車型的最低輔助轉向速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

安全停妥後變更，並於下次開始行車時確認轉向及巡航狀態是否依預期切換。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 僅限實際支援低速轉向的車輛使用，例如受支援的 SMDPS 配置。此設定不會移除車輛本身的物理或安全限制。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END DisableMinSteerSpeed -->

<!-- CARROT:SETTING:END DisableMinSteerSpeed -->
