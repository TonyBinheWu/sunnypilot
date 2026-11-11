<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SYS_SW" param="SoftwareMenu" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 開啟軟體選單

**選單:** 系統 \> 軟體

---

<!-- CARROT:SETTING:BEGIN SoftwareMenu -->
<a id="SoftwareMenu"></a>

## 開啟軟體選單

`SoftwareMenu`

記憶體錯誤時關閉

<!-- CARROT:AUTO:BEGIN SoftwareMenu -->
<!-- CARROT:AUTO:SOURCE facts="6fca012cc9ec5b71f8eeebf0bffee09247d60583e25c3c76713d3be066ad25d0" semantic="faefc012a681c0434720425d608a2393574213ba2bcc32f6be3bf2d32e939dff" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 系統 \> 軟體
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SoftwareMenu -->

<!-- CARROT:MANUAL:BEGIN SoftwareMenu -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- **開啟：** 停車狀態下執行軟體更新程序，並在 Carrot Web 顯示「軟體」分類。
- **關閉：** 不執行更新程序，並隱藏該分類。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

停車狀態下變更，重新開啟 Carrot Web，確認「軟體」群組是否顯示及更新程序狀態。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 這是用於診斷記憶體問題的程序配置設定。一般使用請保留預設值。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SoftwareMenu -->

<!-- CARROT:SETTING:END SoftwareMenu -->
