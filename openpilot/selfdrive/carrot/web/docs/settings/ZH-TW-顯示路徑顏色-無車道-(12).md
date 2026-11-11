<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_PATH" param="ShowPathColor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 顯示路徑顏色: 無車道 (12)

**選單:** 顯示 \> 路徑顯示

---

<!-- CARROT:SETTING:BEGIN ShowPathColor -->
<a id="ShowPathColor"></a>

## 顯示路徑顏色: 無車道 (12)

`ShowPathColor`

(+10: 描邊) 0(紅), 1(橙), 2(黃), 3(藍), 5(深藍), 6(紫), 7(黑), 8(白), 9(藍), 20: 自動

<!-- CARROT:AUTO:BEGIN ShowPathColor -->
<!-- CARROT:AUTO:SOURCE facts="5e2b6f989daabadc3d7634f1202d29d0a5bb08f8f2c77ae051e5d94440b2ccb6" semantic="fb7730745b0900682cd27aff93d72dbb7d8d94329f9989bc2022c096a6e257db" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** `12`
- **範圍:** `0` ~ `20`
- **步長:** `1`
- **選單:** 顯示 \> 路徑顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathColor -->

<!-- CARROT:MANUAL:BEGIN ShowPathColor -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

`0`–`9` 依序選擇紅、橙、黃、綠、藍、深藍、紫、棕、白、黑色。`10`–`19` 在對應顏色加上強調外框，`20` 依行車狀態自動選色。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在行車畫面切換巡航及車道模式狀態，確認路徑形狀與顏色依預期改變。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathColor -->

<!-- CARROT:SETTING:END ShowPathColor -->
