<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_PATH" param="ShowPathColorCruiseOff" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 顯示路徑顏色: 巡航關閉 (1)

**選單:** 顯示 \> 路徑顯示

---

<!-- CARROT:SETTING:BEGIN ShowPathColorCruiseOff -->
<a id="ShowPathColorCruiseOff"></a>

## 顯示路徑顏色: 巡航關閉 (1)

`ShowPathColorCruiseOff`

(+10:stroke)0(R),1(O),2(Y),3(B),5(N),6(V),7(K),8(W),9(B)

<!-- CARROT:AUTO:BEGIN ShowPathColorCruiseOff -->
<!-- CARROT:AUTO:SOURCE facts="7bdd5bce2b6565cee39e11ad85087c954d14b49a55a8cd39b53090b08f9a9481" semantic="a49ee2ac59951411b6a5ff92f21e37706f20d0ab78df06c01f21fdaff8b23119" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** `1`
- **範圍:** `0` ~ `19`
- **步長:** `1`
- **選單:** 顯示 \> 路徑顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathColorCruiseOff -->

<!-- CARROT:MANUAL:BEGIN ShowPathColorCruiseOff -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

`0`–`9` 依序為巡航關閉路徑選擇紅、橙、黃、綠、藍、深藍、紫、棕、白、黑色。`10`–`19` 在對應顏色加上強調外框。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在行車畫面切換巡航及車道模式狀態，確認路徑形狀與顏色依預期改變。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathColorCruiseOff -->

<!-- CARROT:SETTING:END ShowPathColorCruiseOff -->
