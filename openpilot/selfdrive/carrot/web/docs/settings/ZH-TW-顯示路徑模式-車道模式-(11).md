<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_PATH" param="ShowPathModeLane" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 顯示路徑模式: 車道模式 (11)

**選單:** 顯示 \> 路徑顯示

---

<!-- CARROT:SETTING:BEGIN ShowPathModeLane -->
<a id="ShowPathModeLane"></a>

## 顯示路徑模式: 車道模式 (11)

`ShowPathModeLane`

0: 原廠, 1,2: 矩形, 3,4: ^^, 5,6: 矩形, 7,8: ^^, 9,10,11: 平滑^^, 12: 平滑2^^, 13: 3線, 14: 2線, 15: 1線

<!-- CARROT:AUTO:BEGIN ShowPathModeLane -->
<!-- CARROT:AUTO:SOURCE facts="a1014592b874fc4486d8f0944799ac50419d554bc3db20ec528bceb6e9398847" semantic="84dcae423af30a9d71a99b3233ad4685a33a27d494e4c726b488130eb594905c" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** `11`
- **範圍:** `0` ~ `15`
- **步長:** `1`
- **選單:** 顯示 \> 路徑顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathModeLane -->

<!-- CARROT:MANUAL:BEGIN ShowPathModeLane -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- `0` — 使用原廠路徑形狀。
- `1`–`8` — 使用矩形及箭頭樣式的動畫路徑。
- `9`–`12` — 使用平滑箭頭樣式的路徑。
- `13`、`14`、`15` — 分別使用三條、兩條及一條線的路徑。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在行車畫面切換巡航及車道模式狀態，確認路徑形狀與顏色依預期改變。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathModeLane -->

<!-- CARROT:SETTING:END ShowPathModeLane -->
