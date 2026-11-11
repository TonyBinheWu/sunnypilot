<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_PATH" param="ShowPathColorLane" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 顯示路徑顏色: 車道模式 (3)

**選單:** 顯示 \> 路徑顯示

---

<!-- CARROT:SETTING:BEGIN ShowPathColorLane -->
<a id="ShowPathColorLane"></a>

## 顯示路徑顏色: 車道模式 (3)

`ShowPathColorLane`

(+10: 描邊) 0(紅), 1(橙), 2(黃), 3(藍), 5(深藍), 6(紫), 7(黑), 8(白), 9(藍), 20: 自動

<!-- CARROT:AUTO:BEGIN ShowPathColorLane -->
<!-- CARROT:AUTO:SOURCE facts="df4ff452d08c36f8c6da28fd7ad0b961b412e6f8253bf6f84a3bb299c0df8de9" semantic="d7455a9fd2a86afc0293993b98b72bc99a8a9c2a0375adef24f7a5d5888c9f38" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** `3`
- **範圍:** `0` ~ `20`
- **步長:** `1`
- **選單:** 顯示 \> 路徑顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathColorLane -->

<!-- CARROT:MANUAL:BEGIN ShowPathColorLane -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

`0`–`9` 依序為車道模式路徑選擇紅、橙、黃、綠、藍、深藍、紫、棕、白、黑色。`10`–`19` 加上強調外框，`20` 依行車狀態自動選色。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在行車畫面切換巡航及車道模式狀態，確認路徑形狀與顏色依預期改變。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathColorLane -->

<!-- CARROT:SETTING:END ShowPathColorLane -->
